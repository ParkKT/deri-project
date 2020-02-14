"""""""""""""""""""""""""""""""""""""""""""""""""""
의안보고서를 위한 주주총회소집공고 의안 정규화 모듈
"""""""""""""""""""""""""""""""""""""""""""""""""""

import pandas as pd
import numpy as np
import pymysql
import angunUtil
import re

import time
import sys

from logger import get_info_logger_nt, get_error_logger_nt

# 로그
info_logger = get_info_logger_nt()
error_logger = get_error_logger_nt()


# proxy011 테이블 내의 meet_seq 모두 조회 후 리스트로 반환 (key.value) 조회로
# 문서번호도 같이 조회 필요, 붙여서 DB 저장
def make_meet_seq_list():

    conn = angunUtil.conn()
    # Dict cur -> key, value 값
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # meet_seq(jm_code+YYYY+회차)
    sql = "SELECT meet_seq FROM proxy011"
    curs.execute(sql)
    col = curs.fetchall()
    df = pd.DataFrame(col)
    # meet_seq 를 리스트로
    meet_seq_list = df.meet_seq.tolist()

    # 주총고유번호 리스트 반환
    return meet_seq_list


# meet_seq_list를 받아서 meet_content를 조회 후 리턴
def get_meet_cont(rcp_no):
    meet_seq = ''
    meet_content = ''
    meet_gb = ''

    conn = angunUtil.conn()
    cursor = conn.cursor()
    # proxy011 내의 meet_cont 조회 SQL
    sql = "SELECT meet_seq, meet_content, meet_gb FROM proxy011 WHERE rcp_no = '{0}'" .format(rcp_no)

    # meet_seq 를 이용하여 proxy011 내의 다른 정보들을 붙여서 반환
    cursor.execute(sql)
    # 조회된 데이타 Fetch
    row = cursor.fetchall()
    meet_seq = row[0][0]
    meet_content = row[0][1]
    meet_gb = row[0][2]

    cursor.close()
    conn.close()

    # meet_seq 까지 리턴시켜준다
    return meet_seq, meet_content, meet_gb


# meet_cont 정규화 1단계
def make_cont_as_list(cont):
    meet_cont = cont
    # \n 및 : 기준으로 나누어 리스트화
    split_text = re.split('[\n:]', meet_cont)

    # strip 및 공백 제거
    split_text = list(map(lambda x: x.strip(), split_text))
    split_text = list(filter(lambda x: x != '', split_text))

    return split_text


#  부의사항 이후에 나오는 데이터들만 살리고 나머지 kill, 의안만 return
def just_get_bill(split_text):
    # 지역변수 j
    j = 0
    bill = []
    lst = split_text
    # 의안부분만 건져내기 위한 정규식
    ptn_cont = re.compile('(결의사항)|(부의안건)|(부의사항)|(의결안건)|(의결사항)|(부의 안건)|(결의 안건)|(부 의 안 건)|'
                          '(결의 사항)|(상정의안)|( 의결 사항)|(부 의 사 항)')
    ptn_ho = re.compile('(호 의안)|(호의안)|(호안건)|(호 안건)|( 호 의안)')

    for i in range(0, len(lst), 1):
        m = ptn_cont.search(lst[i])
        if m:
            j = lst.index(lst[i])+1
            break
        else:
            j = 0

    for k in range(j, len(lst), 1):
        bill.append(lst[k])

    # 호의안 -> 호로 치환
    for l in range(len(bill)):
        bill[l] = re.sub(ptn_ho, '호', bill[l])

    return bill


# 의안 부분만 넘겨받아 2차 정규화 '제','호' 생성
def reg_bill(bill):

    tmp_str = ''
    ptn_ho = re.compile(r'(^\d-\d)|(^\d-\d-\d)|(^\d)$|(^\d-\d.)')
    ptn_ho2 = re.compile('제제')
    ptn_ho3 = re.compile('호호')

    # 단순하게 1-1,1-1-1...1)...등의 형태로 되어 있는 패턴을 잡는다.
    for i in range(len(bill)):
        match = re.search(ptn_ho, bill[i])
        if match:
            tmp_str = match.group()
            bill[i] = re.sub(ptn_ho, '제' + tmp_str + '호', bill[i])
        else:
            bill[i] = bill[i]
    # 위의 단계를 거쳤을 때 제제0호...의 형태를 잡아준다.
    for j in range(len(bill)):
        match = re.search(ptn_ho2, bill[j])
        if match:
            bill[j] = re.sub(ptn_ho2, '제', bill[j])
        else:
            bill[j] = bill[j]
    # 위의 단계를 거쳤을 때 제0호호...의 형태를 잡아준다.
    for k in range(len(bill)):
        match = re.search(ptn_ho3, bill[k])
        if match:
            bill[k] = re.sub(ptn_ho3, '호', bill[k])
        else:
            bill[k] = bill[k]

    return bill

# 정규화 2단계, 제0호 이외 특수기호 제거, 공백기준 전부 split, bill return
def reg_bill2(bill):

    tmp_str = ''
    bill_tmp = []

    # 공백기준으로 전부 자르기 호\s (ho+space)
    ptn_sp = re.compile(r'(^제\s*\d\s*호\s*$)|(^제\s*\d\s*호\s*$)|(^건\s*제\s*\d*호$)|(^제\d*-\d*호\s$)')

    for j in range (0, len(bill), 1):
        match = re.search(ptn_sp, bill[j])
        if match:
            # 호뒤에 붙는 공백을 기준으로 나누고
            splited_text = re.split(' ',bill[j])
            # 임시 bill_tmp 쪽에 쪼개진 리스트를 extend
            bill_tmp.extend(splited_text)
        else:
            bill[j] = bill[j]
            bill_tmp.append(bill[j])

# 이 부분 떼어내서 따로함수화 필요
    # 제0호 앞의 다양한 문자들을 치환하기 위해 ex) - 제...\S : 공백문자가 아닌것, \s : 공백문자
    ptn_ho = re.compile(r'(^\S\s*제)|(^[가-하].\s*제)|^\d[)]\s*제')

    for i in range(len(bill_tmp)):
        match = re.search(ptn_ho, bill_tmp[i])
        if match:
            bill_tmp[i] = re.sub(ptn_ho, '제', bill_tmp[i])
        else:
            bill_tmp[i] = bill_tmp[i]

    # 제
    bill_tmp2 = []
    ptn_dot = re.compile(r'(^제\d호.)|(^제\d-\d호.)|(^제\d-\d-\d호.)')

    for k in range(len(bill_tmp)):
        match = re.search(ptn_dot, bill_tmp[k])
        if match:
            splited_text2 = re.split('[.]', bill_tmp[k])
            bill_tmp2.extend(splited_text2)
        else:
            bill_tmp[k] = bill_tmp[k]
            bill_tmp2.append(bill_tmp[k])

    return bill_tmp2


# 제0호, 제0-0호, 제0-0-0호의 패턴을 이용하여 병합 중간에 공백 있을수 있음
def merge_by_ptn(bill):
    ann_bill = []
    tmp_str = ''
    ptn_jeho = re.compile(r'(^제\s*\d\s*호)|(^제\s*\d\s*-\s*\d\s*호)|(^제\s*\d\s*-\s*\d\s*-\s*\d\s*호)')

    if len(bill) == 0 :
        return bill
    else:
        for i in range(len(bill)):
            match = re.search(ptn_jeho, bill[i])
            if match:
                ann_bill.append(bill[i])
            else:
                if i+1 >= len(bill):
                    break
                else:
                    match = re.search(ptn_jeho, bill[i+1])
                    if match:
                        ann_bill.append(tmp_str + bill[i])
                        tmp_str = ''
                    else:
                        tmp_str = tmp_str + ' ' + bill[i]

        ann_bill.append(tmp_str + bill[-1])

    return ann_bill


# 제 \d 호 찾아서 중간 공백 다 없애기
def del_void_je_ho(bill):

    bill_tmp =[]
    # 제 1 호, 제 1호, 제1 호 등 중간에 공백있는 경우를 모두 찾아냄
    ptn = re.compile(r'(제\s*\d\s*호)|(제\s*\d-\d\s*호)|(제\s*\d-\d-\d\s*호)')
    for i in range(len(bill)):
        match = re.search(ptn, bill[i])
        if match:
            tmp_str = match.group()
            tmp_str = tmp_str.replace(" ","")
            bill_tmp.append(tmp_str)
            bill_tmp.append(re.sub(ptn, ' ', bill[i]))
        else:
            bill_tmp.append(bill[i])

    return bill_tmp

# 건 제\d 호 case 분리
def seperate_bill(bill):
    bill_tmp = []

    ptn = re.compile(r'(^건\s*제\s*\d\s*호$)')
    for i in range(0, len(bill), 1):
        match = re.search(ptn, bill[i])
        if match:
            splited_text= re.split('[ ]', bill[i])
            bill_tmp.extend(splited_text)
        else:
            bill_tmp.append(bill[i])

        return bill_tmp


def del_either(bill):

    bill_tmp = []
    # 이 부분 떼어내서 따로함수화 필요
    # 제0호 앞의 다양한 문자들을 치환하기 위해 ex) - 제...\S : 공백문자가 아닌것, \s : 공백문자
    ptn_ho = re.compile(r'(^\S\s*제)|(^[가-하].\s*제)|^\d[)]\s*제')
    bill_tmp = bill
    for i in range(len(bill_tmp)):
        match = re.search(ptn_ho, bill_tmp[i])
        if match:
            bill_tmp[i] = re.sub(ptn_ho, '제', bill_tmp[i])
        else:
            bill_tmp[i] = bill_tmp[i]

    # 제
    bill_tmp2 = []
    ptn_dot = re.compile(r'(^제\d호.)|(^제\d-\d호.)|(^제\d-\d-\d호.)')

    for k in range(len(bill_tmp)):
        match = re.search(ptn_dot, bill_tmp[k])
        if match:
            splited_text2 = re.split('[.]', bill_tmp[k])
            bill_tmp2.extend(splited_text2)
        else:
            bill_tmp[k] = bill_tmp[k]
            bill_tmp2.append(bill_tmp[k])

    return bill_tmp2

# 01.21 코드추가 => 의안 2개씩 쪼개서 담기
def split_bill(cont, rcp_no, meet_gb, meet_seq):
    n = 2

    result = [cont[i*n:(i+1)*n] for i in range((len(cont)+n-1)//n)]

    # 주총 문서번호
    for j in result:
        j.insert(0, rcp_no)

    # 주총구분
    for k in result:
        k.insert(1, meet_gb)

    for l in result:
        l.insert(0, meet_seq)

    return result


# insert_DB 함수 필요 DB에 값 insert
def insert_db(cont):
    conn = angunUtil.conn()
    # Dict cur -> key, value 값
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if len(cont) == '0':
        pass
    else:
        try:
            for i in range(len(cont)):
                #db에 삽입하는 코드
                sql = "INSERT INTO proxyt001(meet_seq, rcp_no, meet_gb, ho, bill) " \
                      "VALUES ('{}', '{}', '{}', '{}', '{}') " \
                      .format(cont[i][0], cont[i][1], cont[i][2], cont[i][3], cont[i][4])
                curs.execute(sql)
                conn.commit()


        # 인덱스 에러 처리  필요
        except IndexError as e:
            # list index out of range
            print(e)

# DB 넘겨주는 코드 작성, meet_seq 기준으로 데이터 조회해서 붙이고 리스트 만들어서 insert (rcpno 필요)

def make_angun(rcp_no):
    try:
        meet_seq, meet_content, meet_gb = get_meet_cont(rcp_no)
        cont = make_cont_as_list(meet_content)
        # 부의안건, 의결사항만 추출
        cont = just_get_bill(cont)
        cont = reg_bill(cont)
        cont = del_either(cont)
        # bill = reg_bill2(bill)
        # 2칸이상 띄어쓰기 1칸으로 만들기
        cont = del_void_je_ho(cont)
        cont = merge_by_ptn(cont)
        cont = del_void_je_ho(cont)
        cont = angunUtil.lstrip_bill(cont)
        cont = angunUtil.rem_space(cont)
        cont = angunUtil.del_void(cont)
        # 의안 [호, 의안] 으로 묶어서 출력
        cont = split_bill(cont, rcp_no, meet_gb, meet_seq)
        insert_db(cont)

        info_logger.info('[11] Separating success.')
    except Exception as e:
        error_logger.error('[Notice] Separating fail. {0}'.format(e))


"""if __name__ == "__main__":

    meet_seq_lst = make_meet_seq_list()

    for i in range(0, len(meet_seq_lst), 1):
        meet_seq, meet_content, meet_gb = get_meet_cont(meet_seq_lst, i)
        bill = make_cont_as_list(meet_content)
        # 부의안건, 의결사항만 추출
        bill = just_get_bill(bill)
        bill = reg_bill(bill)
        bill = del_either(bill)
        # bill = reg_bill2(bill)
        # 2칸이상 띄어쓰기 1칸으로 만들기
        bill = del_void_je_ho(bill)
        bill = merge_by_ptn(bill)
        bill = del_void_je_ho(bill)
        bill = angunUtil.lstrip_bill(bill)
        bill = angunUtil.rem_space(bill)
        bill = angunUtil.del_void(bill)
        # 의안 [호, 의안] 으로 묶어서 출력
        bill = split_bill(bill, rcp_no, meet_gb, meet_seq)
        insert_db(bill)
        #print(bill)"""