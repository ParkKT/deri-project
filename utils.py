from builtins import print

from selenium import webdriver as wd
from bs4 import BeautifulSoup

import re
import pymysql as db
import pandas as pd
import time
import datetime


# db connect
def get_dbcon(dbnm):
    #con = db.connect(host='127.0.0.1', user='root', password='qwer1234', db=dbnm, charset='utf8')
    con = db.connect(host='103.60.127.15', user='esg',passwd='esg',db=dbnm, charset='utf8')
    return con

# db close
def close_dbcon(con):
    con.commit()
    con.close()


# get driver
def get_driver(path, addr):
    driver = wd.Chrome(path)

    driver.implicitly_wait(3)

    driver.get(addr)

    return driver

# close driver
def close_driver(driver):
    if driver is not None:
        driver.quit()


# 날짜 정규화 : YYYYMMDD
def make_ymd(ymd):
    ymd = ymd.replace(' ', '')

    pttn_ymd = re.compile('[0-9 ]+[-_/.,:\'년월일][0-9 ]+[-_/.,:\'년월일][0-9 ]+')
    pttn_md = re.compile('[0-9 ]+[-_/.,:\'년월일][0-9 ]+')
    pttn_rpc = '[-_/.,:\'년월일]'

    if "".join(pttn_ymd.findall(ymd)) == '' and "".join(pttn_md.findall(ymd)) == '':
        ymd = ymd.replace(' ', '')
        ymd = get_num(ymd)

        if ymd == 'null':
            return time.strftime("%Y") + '0000'

        if len(ymd) == 8:
            yy = ymd[:-4]
            mm = ymd[-4:-2]
            dd = ymd[-2:]
        elif len(ymd) == 6:
            yy = ymd[:-4]
            if len(yy) == 2:
                yy = '20' + yy
            mm = ymd[-4:-2]
            dd = ymd[-2:]
        elif len(ymd) == 4:
            yy = time.strftime("%Y")
            mm = ymd[:2]
            dd = ymd[-2:]
        else:
            yy = time.strftime("%Y")
            mm = '00'
            dd = '00'
    else:
        tmp_ymd = "".join(pttn_ymd.findall(ymd))
        if tmp_ymd == '':
            tmp_ymd = "".join(pttn_md.findall(ymd))
        tmp_ymd = re.sub(pttn_rpc, ' ', tmp_ymd)

        tmp = tmp_ymd.split(' ')

        if len(tmp) > 2:
            yy = tmp[0]
            mm = tmp[1].zfill(2)
            dd = tmp[2].zfill(2)
        elif len(tmp) == 2:
            yy = time.strftime("%Y")
            mm = tmp[0].zfill(2)
            dd = tmp[1].zfill(2)
        elif len(tmp) < 2:
            yy = time.strftime("%Y")
            mm = '00'
            dd = '00'

        if len(yy) == 2:
            yy = '20' + yy

    return yy + mm + dd

# 시간 정규화 : hhmm
def make_time(tm):
    pttn_colon = re.compile('[0-9 ]+:[0-9 ]+')           #hh:mm
    pttn_colon2 = re.compile('[0-9 ]+:[0-9 ]+:[0-9 ]+')  #hh:mm:ss
    pttn_hh = re.compile('[0-9 ]+시')                   #hh시
    pttn_mm = re.compile('[0-9 ]+분')                   #mm분
    tm = tm.replace(' ', '')

    if "".join(pttn_colon.findall(tm)) != '' or "".join(pttn_colon2.findall(tm)) != '':
        colon_hm = "".join(pttn_colon.findall(tm))
        if colon_hm == '':
            colon_hm = "".join(pttn_colon2.findall(tm))

        hh = int(colon_hm.split(':')[0])
        mm = int(colon_hm.split(':')[1])

        if ('오후' in tm or 'pm' in tm.lower() or 'p.m' in tm.lower() or 'p.m.' in tm.lower()) and hh < 12:
            hh = hh + 12
    elif "".join(pttn_hh.findall(tm)) != '':
        hh = int("".join(pttn_hh.findall(tm)).replace('시', ''))
        if '분' in tm:
            mm = int("".join(pttn_mm.findall(tm)).replace('분', ''))
        else:
            mm = 0

        if ('오후' in tm or 'pm' in tm.lower() or 'p.m' in tm.lower() or 'p.m.' in tm.lower()) and hh < 12:
            hh = hh + 12
    else:
        hh = 0
        mm = 0

    return str(hh).zfill(2) + str(mm).zfill(2)

# 생년월 정규화 : YYYYMM
def make_birth(tm):
    pttn_hyp = re.compile('[0-9 ]+[-_/.,:\'년월일][0-9 ]+')  # YYYY-MM
    pttn_han = re.compile('[0-9 ]+년[0-9 ]+월')              # YYYY년MM월
    pttn_rpc = '[-_/.,:\'년월일]'

    if tm.isdigit():
        return tm

    tmp_birth = "".join(pttn_hyp.findall(tm))
    if tmp_birth == '':
        tmp_birth = "".join(pttn_han.findall(tm))

    tmp_birth = re.sub(pttn_rpc, ' ', tmp_birth)
    tmp_birth = tmp_birth.strip()

    yy = tmp_birth.split(' ')[0]
    mm = tmp_birth.split(' ')[1]

    return yy + mm.zfill(2)

# 생년월 정규화 : YYYYMMDD
def make_birth_ymd(tm):
    tm = tm.replace(" ", "")
    pttn_hyp = re.compile('[0-9 ]+[-_/.,:\'년월일][0-9 ]+[-_/.,:\'년월일][0-9 ]+')  # YYYY-MM
    pttn_han = re.compile('[0-9 ]+년[0-9 ]+월[0-9 ]+일')              # YYYY년MM월
    pttn_rpc = '[-_/.,:\'년월일]'

    if tm.isdigit():
        return tm

    tmp_birth = "".join(pttn_hyp.findall(tm))
    if tmp_birth == '':
        tmp_birth = "".join(pttn_han.findall(tm))

    tmp_birth = re.sub(pttn_rpc, ' ', tmp_birth)
    tmp_birth = tmp_birth.strip()

    yy = tmp_birth.split(' ')[0]
    mm = tmp_birth.split(' ')[1]
    dd = tmp_birth.split(' ')[2]

    return yy + mm.zfill(2) + dd.zfill(2)


# 숫자 추출
def get_num(str):
    pttn_num = re.compile('[0-9]')

    if str == '':
        return 'null'

    num = "".join(pttn_num.findall(str))

    if num == '':
        return 'null'

    return num

# 숫자, 소수점 추출
def get_num_per(str):
    pttn_num = re.compile('[.0-9]')

    if str == '':
        return 'null'

    no = "".join(pttn_num.findall(str))

    if no == '':
        return 'null'

    return no

# 정수 추출
def get_num_int(str):
    pttn_num = re.compile('[0-9]')
    sign = ''

    if str == '':
        return 'null'

    if str[0] == '-' and len(str) > 1:
        sign = '-'

    num = "".join(pttn_num.findall(str))

    if num == '':
        return 'null'

    return sign + num

# String에서공백 및 쿼테이션 제거
def del_space_quot(param):
    param = param.replace("'", "")
    param = param.replace(" ", "")

    return param

# 임기
def get_imgi(param):
    param = del_space_quot(param)
    pttn_ym = re.compile('[0-9]년[0-9][개]*월')
    pttn_y = re.compile('[0-9]년$')
    pttn_m = re.compile('^[0-9][개]*월')

    if param == '' or param == '-':
        return '0'

    imgi = '0'
    if pttn_ym.search(param):
        ym = imgi.split("년")
        y = int(get_num(ym[0]))
        m = int(get_num(ym[1]))
        imgi = str(round((y + m) / 12, 1))
    elif pttn_y.search(param):
        imgi = get_num(param)
    elif pttn_m.search(param):
        m = int(get_num(param))
        imgi = str(round(m / 12, 1))
    else:
        imgi = get_num_per(param)

    return imgi

# 회차 정리
def get_round(rnd):
    # case1 : 년월 제거
    pttn_ym = '20[1-9][0-9]'
    pttn_hyphen = '[0-9]*-'
    rnd = re.sub(pttn_hyphen, '', rnd)
    rnd = re.sub(pttn_ym, '', rnd)

    return rnd

# 이름 정리
def get_nm(nm):
    # case1 : 이름 뒤에 이사 제거
    pttn_isa = '[ \t\n\r\f\v]*이사$'
    nm = re.sub(pttn_isa, '', nm)
    nm = nm.replace("'", "")

    return nm

# 신규선임여부
def get_new(param):
    param = del_space_quot(param)
    if '신규' in param:
        return 'Y'
    elif '재' in param:
        return 'N'
    else:
        return 'E'

# 상근여부
def get_fulltime(param):
    param = del_space_quot(param)
    if param == '상근':
        return 'Y'
    elif param == '비상근' or '비' in param:
        return 'N'
    else:
        return 'E'

# 사외이사여부
def get_outYn(param):
    param = del_space_quot(param)
    if '사외이사인' in param or '인' in param or '사외이사' == param:
        return '1'
    elif param == '0':
        return '0'
    else:
        return '2'

# 겸직여부
def get_dup(param):
    param = del_space_quot(param)
    if ('-' in param and len(param) == 1) or '' == param or len(param) < 2 or ('없음' in param and len(param) == 2):
        return 'N'
    else:
        return 'Y'

# 감사 참석여부
def get_atnYn(str):
    if '참석' in str:
        return 'Y'
    elif '불참' in str or '-' in str:
        return 'N'
    else:
        return 'E'

# 주총 구분
def get_regYn(str):
    if '정기' in str:
        return '1'
    else:
        return '2'

# 이사 참석수
def get_antCnt(str):
    pttn_num = re.compile('[1-9]')

    num = "".join(pttn_num.findall(str))

    if num == '':
        return '0'

    return num

# 쿼테이션 제거
def del_quot(arr):
    for i in range(0, len(arr)):
        for j in range(0, len(arr[i])):
            arr[i][j] = str(arr[i][j]).replace("'", "")

    return arr

# 빈칸 확인
def chk_no_data(param):
    # trim 추가
    if '-' == param:
        return False
    elif '' == param:
        return False
    elif len(param) < 2:
        return False
    elif '없음' in param and '해당' in param:
        return False
    else:
        return True

# 기업명 추출
def get_comp(str):
    str = str.strip()

    pttn = re.compile('[a-zA-Z가-힣& ]')  # 문자만

    pttn_txt = [0 for x in range(4)]
    pttn_txt[0] = '-[전현前現주. ]'       # - 전. 삭제
    pttn_txt[1] = '\([전현前現주 ]\)'     # (전) 삭제
    pttn_txt[2] = '[전현前現주 ]\)'       # 전) 삭제
    pttn_txt[3] = '\([전현前現주 ]'       # (전 삭제

    for i in range(0, len(pttn_txt)):
        str = re.sub(pttn_txt[i], '', str)

    str = "".join(pttn.findall(str))

    return str.strip()

# 주총공고 내용 주출
def get_notice_cont(no, arr):
    res = ''
    pttn_dat = re.compile('^[1Ⅰ가I][.][개최총회 ]*일시')
    pttn_loc = re.compile('^[2Ⅱ나II][.][개최총회 ]*장소')
    pttn_con = re.compile('^[3Ⅲ다III][.][ 정기임시주주총회회의목적사항주요의안내용보고]+')
    pttn_tit = re.compile('^[4ⅣIV라Ⅳ][.][ 가-힣]*')
    #pttn_tit2 = re.compile('[※][ 가-힣]*')

    cont_list = []
    for i in range(0, len(arr)):
        list_tmp = arr[i].text.split('\n')
        for item in list_tmp:
            cont_list.append(item)

    arr = cont_list

    for i in range(0, len(arr)):
        tmp = str(del_entity(arr[i].replace("'", ""))).replace(' ', '')
        if no == 0:
            if "".join(pttn_dat.findall(tmp)) != '':
                res = make_ymd(str(del_entity(arr[i])).replace("'", "").strip())
        elif no == 1:
            if "".join(pttn_dat.findall(tmp)) != '':
                res = make_time(str(del_entity(arr[i])).replace("'", "").strip()[-15:])
        elif no == 2:
            if "".join(pttn_loc.findall(tmp)) != '':
                tmp = str(del_entity(arr[i])).replace("'", "").strip().split(':')
                res = "".join(tmp[1:])
        elif no == 3:
            if "".join(pttn_con.findall(tmp)) != '':
                for j in range(i, len(arr)):
                    if "".join(pttn_tit.findall(str(del_entity(arr[j])))) != '':
                        break
                    if j == i:
                        if ':' not in str(del_entity(arr[j])):
                            continue
                        else:
                            res += "".join(str(del_entity(arr[j])).replace("'", "").strip().split(':')[1:])
                    else:
                        res += str(del_entity(arr[j])).replace("'", "").strip() + '\n'
        elif no == 4:
            if "".join(pttn_tit.findall(str(del_entity(arr[i])))) != '':
                for j in range(i, len(arr)):
                    res += str(del_entity(arr[j])).replace("'", "").strip() + '\n'

    return res

# 주총공고 기타 내용 편집
def get_contetc(str):
    arr = str.split('\n')
    num_arr = []
    res_arr = []
    # 자세하게 수정 필요!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    pttn_tit = re.compile('[4-90ⅣⅤⅥⅦⅧⅨⅩ][.][ 가-힣]+')
    pttn_ymd = re.compile('[0-9 ]+년[0-9 ]+월')

    # 제목라인 체크
    for i in range(0, len(arr)):
        if "".join(pttn_tit.findall(arr[i])) != '':
            num_arr.append(i)

    # 맺음말 삭제
    # 수정 필요!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for i in range(0, len(num_arr)):
        tmp = ''
        if i == len(num_arr) - 1:
            for j in range(num_arr[i], len(arr)):
                if "".join(pttn_ymd.findall(arr[j])) != '':
                    break
                tmp += arr[j] + '\n'
        else:
            for j in range(num_arr[i], num_arr[i + 1]):
                tmp += arr[j] + '\n'

        res_arr.append(tmp.strip())

    return res_arr

# 표 헤더
def get_table_head(act_tb):
    try:
        act_tr = act_tb.find_element_by_tag_name('thead').find_elements_by_tag_name('tr')            # 열별 데이터
        # 헤드라인이 1라인인 경우 체크
        if act_tr[0].find_elements_by_tag_name('th')[0].get_attribute('rowspan') is not None:
            tds_g = act_tr[0].find_elements_by_tag_name('th')
            tds = act_tr[1].find_elements_by_tag_name('th')
        else:
            tds_g = act_tr[0].find_elements_by_tag_name('th')
            tds = act_tr[0].find_elements_by_tag_name('th')
    except:
        act_tr = act_tb.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')            # 열별 데이터
        # 헤드라인이 1라인인 경우 체크
        if act_tr[0].find_elements_by_tag_name('td')[0].get_attribute('rowspan') is not None:
            tds_g = act_tr[0].find_elements_by_tag_name('td')
            tds = act_tr[1].find_elements_by_tag_name('td')
        else:
            tds_g = act_tr[0].find_elements_by_tag_name('td')
            tds = act_tr[0].find_elements_by_tag_name('td')

    return tds, tds_g

# 사외이사 활동내역 표
def set_isa_table(tables):
    # 사외이사 활동내역
    pttn_seq = re.compile("회[ \s]*차")
    pttn_date = re.compile("일[ \s]*자|개[ \s]*최[ \s]*일[ \s]*자")
    pttn_cont = re.compile("의[ \s]*안[ \s]*내[ \s]*용|주[ \s]*요[ \s]*내[ \s]*용")

    cnt = 0
    isa_num = []
    for table in tables:
        if pttn_seq.search(table.text) and pttn_date.search(table.text) and pttn_cont.search(table.text):
            isa_num.append(cnt)
        cnt = cnt + 1

    return isa_num

# 위원회 활동내역 표
def set_border_table(tables):
    # 위원회 활동내역
    pttn_border = re.compile("위[ \s]*원[ \s]*회[ \s]*명|위[ \s]*원[ \s]*회")
    pttn_member = re.compile("구[ \s]*성[ \s]*원|인[ \s]*원")
    pttn_gagyul = re.compile("가[ \s]*결|가[ \s]*결[ \s]*여[ \s]*부")
    pttn_date = re.compile("일[ \s]*자|개[ \s]*최[ \s]*일[ \s]*자")
    pttn_cont = re.compile("의[ \s]*안[ \s]*내[ \s]*용|주[ \s]*요[ \s]*내[ \s]*용")

    cnt = 0
    border_num = []
    for table in tables:
        if (pttn_border.search(table.text) and pttn_member.search(table.text) and pttn_gagyul.search(table.text)
                and pttn_date.search(table.text) and pttn_cont.search(table.text)):
            border_num.append(cnt)
        cnt = cnt + 1

    return border_num

# 사외이사 활동내역 표 헤더
def get_isa_act_head(act_tb):
    tds, tds_g = get_table_head(act_tb)

    res_arr = []  # 결과 배열
    res_arr_raw = []  # 결과 배열(출석률 포함)
    for i in range(0, len(tds)):
        nm = str(tds[i].text).replace(" ", "")
        res_arr_raw.append(nm.strip())
        if '(' in nm or '출석' in nm:
            if nm.index('(') > -1:
                nm = nm[:nm.index('(')]
            elif nm.index('출석') > -1:
                nm = nm[:nm.index('출석')]

        res_arr.append(nm.strip())

    is_gagyul = 0  # 가결여부 포함 여부
    for i in range(0, len(tds_g)):
        gagyul = str(tds_g[i].text).replace(" ", "")
        if '가결여부' in gagyul or '의결현황' in gagyul:
            is_gagyul = 1
            break

    return res_arr, res_arr_raw, is_gagyul

# 사외이사 등의 보수현황 표
def set_isa_bosu_table(tables):
    # 위원회 활동내역
    pttn_gubun = re.compile("구[ \s]*분")
    pttn_member = re.compile("인[ \s]*원")
    pttn_amt = re.compile("승[ \s]*인[ \s]*금[ \s]*액")
    pttn_peramt = re.compile("지[ \s]*급[ \s]*액")

    cnt = 0
    isa_bosu_num = []
    for table in tables:
        if (pttn_gubun.search(table.text) and pttn_member.search(table.text)
                and pttn_amt.search(table.text) and pttn_peramt.search(table.text)):
            isa_bosu_num.append(cnt)
        cnt = cnt + 1

    return isa_bosu_num

# 단일거래 표
def set_transaction_table(tables):
    # 위원회 활동내역
    pttn_transaction = re.compile("거[ \s]*래")
    pttn_relation = re.compile("상[ \s]*대[ \s]*방")
    pttn_period = re.compile("기[ \s]*간")
    pttn_amt = re.compile("금[ \s]*액")

    cnt = 0
    transaction_num = []
    for table in tables:
        if (pttn_transaction.search(table.text) and pttn_relation.search(table.text)
                and pttn_period.search(table.text) and pttn_amt.search(table.text)):
            transaction_num.append(cnt)
        cnt = cnt + 1

    return transaction_num


# 표 편집
def get_table(act_tb):
    col_cnt = len(act_tb.find('colgroup').find_all('col'))  # 행 길이
    act_tr = act_tb.find('tbody').find_all('tr')            # 열별 데이터
    # act_th = act_tb.find_element_by_tag_name('thead').find_elements_by_tag_name('tr')          # 가결여부열 유무
    #gagyul_yn = act_th[0].find_elements_by_tag_name('th')[3].text

    res_arr = [[0 for y in range(col_cnt)] for x in range(len(act_tr))]     # 결과 배열
    tmp_arr = []                                                            # rowspan 배열
    for i in range(0, len(res_arr)):
        tds = act_tr[i].find_all('td')
        cnt = 0
        for chk in range(0, len(tmp_arr)):
            if tmp_arr[chk][0] < i < tmp_arr[chk][2]:
                cnt = cnt + 1
        for j in range(0, len(tds)):
            # rowspan이 있는 행과 열을 tmp에 저장
            if tds[j].get('rowspan') is not None:
                tmp_arr.append([i, j + cnt, i + int(tds[j].get('rowspan'))])

    tmp_arr.sort(key=lambda x: (x[1], x[2]))     # rowspan 정렬

    for i in range(0, len(res_arr)):
        tds = act_tr[i].find_all('td')
        for j in range(0, len(tds)):
            res_arr[i][j] = del_entity(tds[j].text).replace("'", "")

        if col_cnt != len(tds):
            for chk in range(0, len(tmp_arr)):
                if tmp_arr[chk][0] < i < tmp_arr[chk][2]:
                    res_arr[i].insert(tmp_arr[chk][1], res_arr[tmp_arr[chk][0]][tmp_arr[chk][1]])
                    res_arr[i].pop()

    head_len = 0
    table_len = len(act_tb.find_all('tr'))
    tbody_len = len(act_tr)
    if table_len == tbody_len:
        first_td = act_tb.find('tbody').find_all('tr')[0].find_all('td')[0]
        if first_td.get('rowspan') is None:
            head_len = 1
        else:
            head_len = int(first_td.get('rowspan'))

    del res_arr[0:head_len]

    return res_arr

# 표 편집 (태그 포함)
def get_table_tag(act_tb):
    col_cnt = len(act_tb.find('colgroup').find_all('col'))  # 행 길이
    act_tr = act_tb.find('tbody').find_all('tr')            # 열별 데이터

    res_arr = [[0 for y in range(col_cnt)] for x in range(len(act_tr))]     # 결과 배열
    tmp_arr = []                                                            # rowspan 배열
    for i in range(0, len(res_arr)):
        tds = act_tr[i].find_all('td')
        cnt = 0
        for chk in range(0, len(tmp_arr)):
            if tmp_arr[chk][0] < i < tmp_arr[chk][2]:
                cnt = cnt + 1
        for j in range(0, len(tds)):
            # rowspan이 있는 행과 열을 tmp에 저장
            if tds[j].get('rowspan') is not None:
                tmp_arr.append([i, j + cnt, i + int(tds[j].get('rowspan'))])

    tmp_arr.sort(key=lambda x: (x[1], x[2]))     # rowspan 정렬

    for i in range(0, len(res_arr)):
        tds = act_tr[i].find_all('td')
        for j in range(0, len(tds)):
            res_arr[i][j] = str(tds[j]).strip().replace("'", "")

        if col_cnt != len(tds):
            for chk in range(0, len(tmp_arr)):
                if tmp_arr[chk][0] < i < tmp_arr[chk][2]:
                    res_arr[i].insert(tmp_arr[chk][1], res_arr[tmp_arr[chk][0]][tmp_arr[chk][1]])
                    res_arr[i].pop()

    head_len = 0
    table_len = len(act_tb.find_all('tr'))
    tbody_len = len(act_tr)
    if table_len == tbody_len:
        first_td = act_tb.find('tbody').find_all('tr')[0].find_all('td')[0]
        if first_td.get('rowspan') is None:
            head_len = 1
        else:
            head_len = int(first_td.get('rowspan'))

    del res_arr[0:head_len]

    return res_arr

# 표 편집 : 셀레늄
def get_table_sn(act_tb):
    col_cnt = len(act_tb.find_element_by_tag_name('colgroup').find_elements_by_tag_name('col'))  # 행 길이
    act_tr = act_tb.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')            # 열별 데이터
    # act_th = act_tb.find_element_by_tag_name('thead').find_elements_by_tag_name('tr')          # 가결여부열 유무
    #gagyul_yn = act_th[0].find_elements_by_tag_name('th')[3].text

    res_arr = [[0 for y in range(col_cnt)] for x in range(len(act_tr))]     # 결과 배열
    tmp_arr = []                                                            # rowspan 배열
    for i in range(0, len(res_arr)):
        tds = act_tr[i].find_elements_by_tag_name('td')
        cnt = 0
        for chk in range(0, len(tmp_arr)):
            if tmp_arr[chk][0] < i < tmp_arr[chk][2]:
                cnt = cnt + 1
        for j in range(0, len(tds)):
            # rowspan이 있는 행과 열을 tmp에 저장
            if tds[j].get_attribute('rowspan') is not None:
                tmp_arr.append([i, j + cnt, i + int(tds[j].get_attribute('rowspan'))])

    tmp_arr.sort(key=lambda x: (x[1], x[2]))     # rowspan 정렬

    for i in range(0, len(res_arr)):
        tds = act_tr[i].find_elements_by_tag_name('td')
        for j in range(0, len(tds)):
            res_arr[i][j] = del_entity(tds[j].text).replace("'", "")

        if col_cnt != len(tds):
            for chk in range(0, len(tmp_arr)):
                if tmp_arr[chk][0] < i < tmp_arr[chk][2]:
                    res_arr[i].insert(tmp_arr[chk][1], res_arr[tmp_arr[chk][0]][tmp_arr[chk][1]])
                    res_arr[i].pop()

    head_len = 0
    table_len = len(act_tb.find_elements_by_tag_name('tr'))
    tbody_len = len(act_tr)
    if table_len == tbody_len:
        first_td = act_tb.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')[0].find_elements_by_tag_name('td')[0]
        if first_td.get_attribute('rowspan') is None:
            head_len = 1
        else:
            head_len = int(first_td.get_attribute('rowspan'))

    del res_arr[0:head_len]

    return res_arr

# 주총공고 사외이사 보수현황_금액단위
def get_unit(unit_tb):
    unit_txt = del_entity(unit_tb.text)
    unit_txt = unit_txt.replace(" ","").replace("△","-").replace("(-)","-").replace("(","-").replace(")","").replace(",","").replace("=","")

    unit = '원'
    re_unit1 = re.compile('단위[ \s]*:[ \s]*원')
    re_unit11 = re.compile('[ 0-9]+원')
    re_unit2 = re.compile('단위[ \s]*:[ \s]*천[ \s]*원')
    re_unit22 = re.compile('[ 0-9]+[ 천원]')
    re_unit3 = re.compile('단위[ \s]*:[ \s]*만[ \s]*원')
    re_unit33 = re.compile('[ 0-9]+[ 만원]')
    re_unit4 = re.compile('단위[ \s]*:[ \s]*백[ \s]*만[ \s]*원')
    re_unit44 = re.compile('[ 0-9]+[ 백만원]')
    re_unit5 = re.compile('단위[ \s]*:[ \s]*억[ \s]*원')
    re_unit55 = re.compile('[ 0-9]+[ 억원]')

    # 원
    if len("".join(re_unit1.findall(unit_txt))) != 0 or len("".join(re_unit11.findall(unit_txt))) != 0:
        unit = '원'
    # 천원
    elif len("".join(re_unit2.findall(unit_txt))) != 0 or len("".join(re_unit22.findall(unit_txt))) != 0:
        unit = '천원'
    # 만원
    elif len("".join(re_unit3.findall(unit_txt))) != 0 or len("".join(re_unit33.findall(unit_txt))) != 0:
        unit = '만원'
    # 백만원
    elif len("".join(re_unit4.findall(unit_txt))) != 0 or len("".join(re_unit44.findall(unit_txt))) != 0:
        unit = '백만원'
    # 억원
    elif len("".join(re_unit5.findall(unit_txt))) != 0 or len("".join(re_unit55.findall(unit_txt))) != 0:
        unit = '억원'
    else:
        unit = '원'

    return unit

def get_unit(unit_tb):
    unit_txt = del_entity(unit_tb)
    unit_txt = unit_txt.replace(" ","").replace("△","-").replace("(-)","-").replace("(","-").replace(")","").replace(",","").replace("=","")

    unit = '원'
    re_unit1 = re.compile('단위[ \s]*:[ \s]*원')
    re_unit11 = re.compile('[ 0-9]+원')
    re_unit2 = re.compile('단위[ \s]*:[ \s]*천[ \s]*원')
    re_unit22 = re.compile('[ 0-9]+[ 천원]')
    re_unit3 = re.compile('단위[ \s]*:[ \s]*만[ \s]*원')
    re_unit33 = re.compile('[ 0-9]+[ 만원]')
    re_unit4 = re.compile('단위[ \s]*:[ \s]*백[ \s]*만[ \s]*원')
    re_unit44 = re.compile('[ 0-9]+[ 백만원]')
    re_unit5 = re.compile('단위[ \s]*:[ \s]*억[ \s]*원')
    re_unit55 = re.compile('[ 0-9]+[ 억원]')

    # 원
    if len("".join(re_unit1.findall(unit_txt))) != 0 or len("".join(re_unit11.findall(unit_txt))) != 0:
        unit = '원'
    # 천원
    elif len("".join(re_unit2.findall(unit_txt))) != 0 or len("".join(re_unit22.findall(unit_txt))) != 0:
        unit = '천원'
    # 만원
    elif len("".join(re_unit3.findall(unit_txt))) != 0 or len("".join(re_unit33.findall(unit_txt))) != 0:
        unit = '만원'
    # 백만원
    elif len("".join(re_unit4.findall(unit_txt))) != 0 or len("".join(re_unit44.findall(unit_txt))) != 0:
        unit = '백만원'
    # 억원
    elif len("".join(re_unit5.findall(unit_txt))) != 0 or len("".join(re_unit55.findall(unit_txt))) != 0:
        unit = '억원'
    else:
        unit = '원'

    return unit

# 테이블 특정 열 숫자만 추출
def get_bosu_edit(bosu_tb, arr):
    for i in range(0, len(bosu_tb)):
        for j in range(0, len(bosu_tb[i])):
            if j in arr:
                bosu_tb[i][j] = get_num(bosu_tb[i][j])

    return bosu_tb

# 테이블 특정 열 퍼센테이지만 추출
def get_bosu_edit_per(bosu_tb, arr):
    for i in range(0, len(bosu_tb)):
        for j in range(0, len(bosu_tb[i])):
            if j in arr:
                bosu_tb[i][j] = get_num_per(bosu_tb[i][j])

    return bosu_tb

# 정관변경 테이블 파싱
def get_article(driver):
    # 정관 변경 표 패턴
    pttn_before_change = re.compile("변[ \s]*경[ \s]*전[ \s]*내[ \s]*용|변[ \s]*경[ \s]*전|현[ \s]*행|현[ \s]*황")
    pttn_after_change = re.compile("변[ \s]*경[ \s]*후[ \s]*내[ \s]*용|변[ \s]*경[ \s]*후|개[ \s]*정[ \s]*안[ \s]*|개[ \s]*정|변[ \s]*경[ \s]*안[ \s]*|변[ \s]*경[ \s]*안|변[ \s]*경")
    pttn_cus_change = re.compile("변[ \s]*경[ \s]*의[ \s]*목[ \s]*적|변[ \s]*경[ \s]*목[ \s]*적|비[ \s]*고")

    # 집중투표 배제 표 유무
    pttn_jipjung_baeje1 = re.compile("집[ \s]*중[ \s]*투[ \s]*표[ \s]*배[ \s]*제")
    pttn_jipjung_baeje2 = re.compile("정[ \s]*관[ \s]*의[ \s]*변[ \s]*경")

    # 정관변경 전체 테이블
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')

    cnt = 0
    change_num = []
    for table in tables:
        if (pttn_before_change.search(table.text) and pttn_after_change.search(table.text) and
                pttn_cus_change.search(table.text)):
            change_num.append(cnt)
        cnt = cnt + 1

    # 정관변경 테이블 분류( 집중투표 / 그외)
    res_jipjung_tag = []
    res_jipjung = []
    res_etc_tag = []
    res_etc = []
    if len(change_num) < 2:
        ps = soup.find_all('p')
        jipjung_yn = 1
        for i in range(0, len(ps)):
            if i != len(ps) - 1:
                if (pttn_jipjung_baeje1.search(ps[i].text) and pttn_jipjung_baeje2.search(ps[i].text) and ('-' in str(del_entity(ps[i + 1].text)).replace(' ', '') or '없음' in str(del_entity(ps[i + 1].text)).replace(' ', ''))) or (
                        pttn_jipjung_baeje1.search(ps[i].text) and pttn_jipjung_baeje2.search(ps[i].text) and ('-' in str(del_entity(ps[i].text)).replace(' ', '') or '없음' in str(del_entity(ps[i].text)).replace(' ', ''))):
                    jipjung_yn = 2

        if jipjung_yn == 1:
            res_jipjung_tag = get_table_tag(tables[change_num[0]])
            res_jipjung = get_table(tables[change_num[0]])
            res_etc_tag = []
            res_etc = []
        else:
            res_jipjung_tag = []
            res_jipjung = []
            res_etc_tag = get_table_tag(tables[change_num[0]])
            res_etc = get_table(tables[change_num[0]])
    else:
        res_jipjung_tag = get_table_tag(tables[change_num[0]])
        res_jipjung = get_table(tables[change_num[0]])
        #for i in range(1, len(change_num)):
        res_etc_tag.extend(get_table_tag(tables[change_num[0] + 1]))
        res_etc.extend(get_table(tables[change_num[0] + 1]))

    return res_jipjung, res_jipjung_tag, res_etc, res_etc_tag

# 정관변경 테이블 파싱 : 첫행 코드화
def get_article_code(tb):
    # 정관 변경 표 패턴
    pttn_johang = re.compile("제[ 0-9]+조")
    pttn_buchik = re.compile("부[ \s]*칙")

    # 정관변경 전체 테이블
    res_arr = []
    for i in range(0, len(tb)):
        tmp = []
        for j in range(0, len(tb[i])):
            first_line = tb[i][j].split('\n')[0]
            if pttn_johang.search(first_line):
                tmp.append(pttn_johang.findall(first_line)[0])
            elif pttn_buchik.search(tb[i][j]):
                tmp.append(pttn_buchik.findall(first_line)[0])
            else:
                tmp.append('')
        res_arr.append(tmp)

    return res_arr

# td 태그 삭제
def del_td(str):
    pttn_td = "<[/]*.*>"
    if str == '':
        return ''

    str = re.sub(pttn_td, '', str)

    return str

# 이사선임 테이블 파싱
def get_isa(driver):
    # 이사선임 표 제목 패턴
    pttn_isa = re.compile("□[ \s]*이[ \s]*사[ \s]*의[ \s]*선[ \s]*임|□[ \s]*이[ \s]*사[ \s]*선[ \s]*임")
    #pttn_isa = re.compile("이[ \s]*사[ \S]*선[ \s]*임")
    pttn_gamsawiwon = re.compile("□[ \s]*감[ \s]*사[ \s]*위[ \s]*원[ \s]*회[ \s]*위[ \s]*원[ \s]*의[ \s]*선[ \s]*임|□[ \s]*감[ \s]*사[ \s]*위[ \s]*원[ \s]*회[ \s]*위[ \s]*원[ \s]*선[ \s]*임|□[ \s]*감[ \s]*사[ \s]*위[ \s]*원[ \s]*이[ \s]*되[ \s]*는")
    #pttn_gamsawiwon = re.compile("감[ \s]*사[ \s]*위[ \s]*원[ \s]*회[ \s]*위[ \s]*원[ \S]*선[ \s]*임")
    pttn_gamsa = re.compile("□[ \s]*감[ \s]*사[ \s]*의[ \s]*선[ \s]*임|□[ \s]*감[ \s]*사[ \s]*선[ \s]*임")
    #pttn_gamsa = re.compile("감[ \s]*사[ \s]*의[ \S]*선[ \s]*임|□[ \s]*감[ \s]*사[ \s]*선[ \s]*임")

    # 이사선임 표 제목 패턴
    pttn_p_nm = re.compile("후[ \s]*보[ \s]*자[ \s]*성[ \s]*명|후[ \s]*보[ \s]*자|성[ \s]*명|이[ \s]*사[ \s]*성[ \s]*명")
    pttn_p_birth = re.compile("생[ \s]*년[ \s]*월[ \s]*일|생[ \s]*년[ \s]*월")
    pttn_p_rel = re.compile("최[ \s]*대[ \s]*주[ \s]*주[ \s]*와[ \s]*의[ \s]*관[ \s]*계|최대주주[ \S]*관계")
    pttn_p_recom = re.compile("추[ \s]*천[ \s]*인")

    # 이사선임 표 패턴
    pttn_isa_nm = re.compile("후[ \s]*보[ \s]*자[ \s]*성[ \s]*명|후[ \s]*보[ \s]*자|성[ \s]*명|이[ \s]*사[ \s]*성[ \s]*명|이[ \s]*사")
    pttn_isa_birth = re.compile("생[ \s]*년[ \s]*월[ \s]*일|생[ \s]*년[ \s]*월")
    pttn_isa_rel = re.compile("최[ \s]*대[ \s]*주[ \s]*주[ \s]*와[ \s]*의[ \s]*관[ \s]*계|최대주주[ \S]*관계")
    pttn_isa_recom = re.compile("추[ \s]*천[ \s]*인")

    # 이사선임 약력표 제목 패턴
    pttn_p_job = re.compile("주[ \s]*된[ \s]*직[ \s]*업")
    pttn_p_car = re.compile("약[ \s]*력|경[ \s]*력")
    pttn_p_3y = re.compile("해[ \s]*당[ \s]*법[ \s]*인[ \s]*과[ \s]*의[ \s]*최[ \s]*근[ \s]*3년[ \s]*간[ \s]*거[ \s]*래[ \s]*내[ \s]*역|당[ \s]*해[ \s]*법[ \s]*인[ \s]*과[ \s]*의[ \s]*최[ \s]*근[ \s]*3년[ \s]*간[ \s]*거[ \s]*래[ \s]*내[ \s]*역|해당법인[ \S]*3년[ \S]*거래내역|당해법인[ \S]*3년[ \S]*거래내역")
    # 이사선임 약력표 제목 패턴_신규
    pttn_p_car_new = re.compile("세[ \s]*부[ \s]*경[ \s]*력")

    # 이사선임 약력표 패턴
    pttn_isa_job = re.compile("주[ \s]*된[ \s]*직[ \s]*업")
    pttn_isa_car = re.compile("약[ \s]*력|경[ \s]*력")
    pttn_cus_3y = re.compile("해[ \s]*당[ \s]*법[ \s]*인[ \s]*과[ \s]*의[ \s]*최[ \s]*근[ \s]*3년[ \s]*간[ \s]*거[ \s]*래[ \s]*내[ \s]*역|당[ \s]*해[ \s]*법[ \s]*인[ \s]*과[ \s]*의[ \s]*최[ \s]*근[ \s]*3년[ \s]*간[ \s]*거[ \s]*래[ \s]*내[ \s]*역|해당법인[ \S]*3년[ \S]*거래내역|당해법인[ \S]*3년[ \S]*거래내역")
    # 이사선임 약력표 패턴_신규
    pttn_isa_car_new = re.compile("세[ \s]*부[ \s]*경[ \s]*력")

    # 총인원 삭제 패턴
    pttn_cnt = re.compile("총[ \S]*[0-9]*[ \S]*명")
    # 불필요 열 제거
    pttn_ho = re.compile('제[ \S]*호')

    # 이사/감사/감사위원
    body = driver.find_element_by_xpath('/html/body')
    isa_gb = []
    tb_isa = []
    tb_car = []
    isa_ptag = body.find_elements_by_tag_name('p')
    for p in range(0, len(isa_ptag)):
        if pttn_isa.search(del_entity(isa_ptag[p].text)):
            isa_gb.append([1, p])
        if pttn_gamsawiwon.search(del_entity(isa_ptag[p].text)):
            isa_gb.append([2, p])
        if pttn_gamsa.search(del_entity(isa_ptag[p].text)):
            isa_gb.append([3, p])

        if (pttn_p_nm.search(isa_ptag[p].text) and pttn_p_birth.search(isa_ptag[p].text) and
                pttn_p_recom.search(isa_ptag[p].text) and pttn_p_rel.search(isa_ptag[p].text)):
            tb_isa.append(p)

        if pttn_p_job.search(isa_ptag[p].text) and pttn_p_car.search(isa_ptag[p].text) and pttn_p_3y.search(isa_ptag[p].text) and not pttn_p_car_new.search(isa_ptag[p].text):
            tb_car.append(p)
        elif pttn_p_job.search(isa_ptag[p].text) and pttn_p_car_new.search(isa_ptag[p].text) and pttn_p_3y.search(isa_ptag[p].text):
            tb_car.append(p)

    isa_gb.sort(key=lambda x: x[1])

    if len(tb_isa) < 1:
        return [], [], False

    # 이사/감사위원/감사 구분
    isa_gubun = [0 for y in range(len(tb_isa))]
    for i in range(0, len(isa_gb)):
        for j in range(0, len(tb_isa)):
            if isa_gb[i][1] < tb_isa[j]:
                isa_gubun[j] = isa_gb[i][0]

    isa_car_gubun = [0 for y in range(len(tb_car))]
    for i in range(0, len(isa_gb)):
        for j in range(0, len(tb_car)):
            if isa_gb[i][1] < tb_car[j]:
                isa_car_gubun[j] = isa_gb[i][0]

    # 이사선임 전체 테이블
    tables = body.find_elements_by_tag_name('table')

    # 이사선임 정보 테이블
    cnt = 0
    isa_num = []
    for table in tables:
        if (pttn_isa_nm.search(table.text) and pttn_isa_birth.search(table.text) and
                pttn_isa_rel.search(table.text) and pttn_isa_recom.search(table.text)):
            isa_num.append(cnt)
        cnt = cnt + 1

    isa_arr = []
    # if len(isa_num) > 0 and len(isa_num) == len(isa_gb):
    if len(isa_num) > 0:
        for i in range(0, len(isa_num)):
            tmp_tb = get_table_sn(tables[isa_num[i]])
            # 총 인원 행 삭제
            for d in range(0, len(tmp_tb)):
                if not pttn_cnt.search(str(tmp_tb[d][0])):
                    isa_arr.append(tmp_tb[d])
            # 의안, 호 등과 같은 불필요한 열 삭제
            del_col = -1
            for j in range(0, len(tmp_tb)):
                for d in range(0, len(tmp_tb[j])):
                    if pttn_ho.search(str(tmp_tb[j][d])):
                        del_col = d
            if del_col != -1:
                for j in range(0, len(tmp_tb)):
                    del tmp_tb[j][del_col]
            # 감사일 경우 1열 추가하여 삽입
            if isa_gubun[i] == 3:
                for j in range(0, len(tmp_tb)):
                    tmp_tb[j].insert(2, '감사')
                    tmp_tb[j].insert(5, isa_gubun[i])
            else:
                for j in range(0, len(tmp_tb)):
                    tmp_tb[j].insert(5, isa_gubun[i])

    # 이사선임 약력 테이블
    cnt = 0
    car_num = []
    job_is_new = False
    for table in tables:
        if pttn_isa_job.search(table.text) and pttn_isa_car.search(table.text) and pttn_cus_3y.search(table.text) and not pttn_p_car_new.search(table.text):
            car_num.append(cnt)
        elif pttn_isa_job.search(table.text) and pttn_isa_car_new.search(table.text) and pttn_cus_3y.search(table.text):
            car_num.append(cnt)
            job_is_new = True
        cnt = cnt + 1

    car_arr = []
    # if len(car_num) > 0 and len(car_num) == len(isa_gb):
    if len(car_num) > 0:
        for i in range(0, len(car_num)):
            tmp_tb = get_table_sn(tables[car_num[i]])
            # 총 인원 행 삭제
            for d in range(0, len(tmp_tb)):
                if not pttn_cnt.search(str(tmp_tb[d][0])):
                    car_arr.append(tmp_tb[d])

            # 의안, 호 등과 같은 불필요한 열 삭제
            del_col = -1
            for j in range(0, len(tmp_tb)):
                for d in range(0, len(tmp_tb[j])):
                    if pttn_ho.search(str(tmp_tb[j][d])):
                        del_col = d
            if del_col != -1:
                for j in range(0, len(tmp_tb)):
                    del tmp_tb[j][del_col]

            # 이사 구분 삽입
            if job_is_new:
                for j in range(0, len(tmp_tb)):
                    tmp_tb[j].insert(5, isa_car_gubun[i])
            else:
                for j in range(0, len(tmp_tb)):
                    tmp_tb[j].insert(4, isa_car_gubun[i])

    return isa_arr, car_arr, job_is_new

# 보수한도 테이블 파싱
def get_bosu(driver):
    # 보수한도 표 제목 패턴
    pttn_isa = re.compile("□[ \s]*이[ \s]*사[ \s]*의[ \s]*보[ \s]*수[ \s]*한[ \s]*도|□[ \s]*이[ \s]*사[ \s]*보[ \s]*수[ \s]*한[ \s]*도")
    pttn_gamsa = re.compile("□[ \s]*감[ \s]*사[ \s]*의[ \s]*보[ \s]*수[ \s]*한[ \s]*도|□[ \s]*감[ \s]*사[ \s]*보[ \s]*수[ \s]*한[ \s]*도")

    # 이사보수한도 표 패턴
    pttn_isa_nm = re.compile("이[ \s]*사[ \s]*의[ \s]*수|사[ \s]*외[ \s]*이[ \s]*사[ \s]*수")
    pttn_isa_now = re.compile("당[ \s]*기")
    pttn_isa_last = re.compile("전[ \s]*기")
    # 이사보수한도 표 패턴_신규
    pttn_isa_hando = re.compile("보[ \s]*수[ \s]*총[ \s]*액|최[ \s]*고[ \s]*한[ \s]*도[ \s]*액")
    pttn_isa_jigup = re.compile("지[ \s]*급")

    # 감사보수한도 표 패턴
    pttn_gamsa_nm = re.compile("감[ \s]*사[ \s]*의[ \s]*수|감[ \s]*사[ \s]*수")
    pttn_gamsa_now = re.compile("당[ \s]*기")
    pttn_gamsa_last = re.compile("전[ \s]*기")
    # 감사보수한도 표 패턴
    pttn_gamsa_hando = re.compile("보[ \s]*수[ \s]*총[ \s]*액|최[ \s]*고[ \s]*한[ \s]*도[ \s]*액")
    pttn_gamsa_jigup = re.compile("지[ \s]*급")

    # 예외 표 패턴
    pttn_isa_ext = re.compile("현[ \s]*재[ \s]*보[ \s]*수[ \s]*한[ \s]*도|변[ \s]*경[ \s]*승[ \s]*인[ \s]*보[ \s]*수[ \s]*한[ \s]*도")

    # 이사수, 금액
    pttn_num = re.compile('[0-9]')
    pttn_unit = re.compile('[ 0-9]+[ \w]*원')

    # 이사/감사/감사위원 존재유무 확인(1:있음, 2없음)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    isa_chk_first = 0   # 당기, 전기 순서 체크 (당기먼저:0, 전기먼저:1)
    gamsa_chk_first = 0  # 당기, 전기 순서 체크 (당기먼저:0, 전기먼저:1)
    hando_is_new = False
    isa_p = 0
    gamsa_p = 0
    isa_ptag = soup.find_all('p')
    for p in range(0, len(isa_ptag)):
        if pttn_isa.search(del_entity(isa_ptag[p].text)):
            isa_p = 1
        if pttn_gamsa.search(del_entity(isa_ptag[p].text)):
            gamsa_p = 1

    if isa_p == 0 and gamsa_p == 0:
        return [], [], '원', '원', 0, 0, []

    # 이사선임 전체 테이블
    tables = soup.find_all('table')

    # 이사보수한도 테이블
    cnt = 0
    isa_num = 0
    isa_num_dang = 0
    isa_num_jun = 0
    isa_ext_yn = 0
    isa_unit = ''
    unit_check = 0
    for table in tables:
        if ((pttn_isa_nm.search(table.text) and pttn_isa_now.search(table.text) and pttn_isa_last.search(table.text)) or
                (pttn_isa_nm.search(table.text) and pttn_isa_ext.search(table.text))):
            isa_num = cnt
            if table.text.replace(" ", "").find("당") > table.text.replace(" ", "").find("전"):
                isa_chk_first = 1
            if pttn_isa_ext.search(table.text):
                isa_ext_yn = 1
            break
        elif pttn_isa_nm.search(table.text) and pttn_isa_hando.search(table.text) and pttn_isa_jigup.search(table.text):
            isa_num_jun = cnt
            hando_is_new = True
        elif pttn_isa_nm.search(table.text) and pttn_isa_hando.search(table.text) and not pttn_isa_jigup.search(table.text):
            isa_num_dang = cnt
            hando_is_new = True

        cnt = cnt + 1

    isa_arr = []
    if hando_is_new:
        if isa_num_dang > 0 and isa_p == 1:
            tmp_tb = pd.DataFrame(to_table(tables[isa_num_dang])).values.tolist()
            for tb in tmp_tb:
                tb.append('1')
            isa_arr.extend(tmp_tb)
        if isa_num_jun > 0 and isa_p == 1:
            tmp_tb = pd.DataFrame(to_table(tables[isa_num_jun])).values.tolist()
            for tb in tmp_tb:
                tb.append('2')
            isa_arr.extend(tmp_tb)
    else:
        if isa_num > 0 and isa_p == 1:
            tmp_tb = get_table(tables[isa_num])
            if isa_ext_yn == 1 or len(tmp_tb[0]) < 3:
                tmp_tb = []
            isa_arr.extend(tmp_tb)

    # 신규 단위 및 표정리
    if hando_is_new:
        isa_arr = separate_isa(isa_arr, hando_is_new)
        if isa_arr:
            tmp = ''
            for isa in isa_arr:
                if pttn_unit.search(tmp):
                    unit_check = 1
                tmp = tmp + "".join(isa)
            isa_unit = get_unit(tmp)

        for i in range(len(isa_arr)):
            if pttn_num.search(isa_arr[i][1]):
                isa_arr[i][1] = "".join(pttn_num.findall(isa_arr[i][1]))
            else:
                isa_arr[i][1] = '0'

        if len(isa_arr) > 3:
            isa_arr[0][1] = str(int(isa_arr[0][1]) - int(isa_arr[1][1]))
            isa_arr[3][1] = str(int(isa_arr[3][1]) - int(isa_arr[4][1]))
        else:
            isa_arr[0][1] = str(int(isa_arr[0][1]) - int(isa_arr[1][1]))
    else:
        isa_arr = separate_isa(isa_arr, hando_is_new)
        if isa_arr:
            tmp = ''
            for isa in isa_arr:
                tmp = tmp + "".join(isa)
            isa_unit = get_unit(tmp)

        for i in range(len(isa_arr)):
            for j in range(len(isa_arr[i])):
                if j > 0:
                    if pttn_num.search(isa_arr[i][j]):
                        isa_arr[i][j] = "".join(pttn_num.findall(isa_arr[i][j]))
                    else:
                        isa_arr[i][j] = '0'

        isa_arr[0][1] = str(int(isa_arr[0][1]) - int(isa_arr[1][1]))
        isa_arr[0][2] = str(int(isa_arr[0][2]) - int(isa_arr[1][2]))

    # 감사보수한도 테이블
    cnt = 0
    gamsa_num = 0
    gamsa_num_dang = 0
    gamsa_num_jun = 0
    gamsa_ext_yn = 0
    gamsa_unit = ''
    for table in tables:
        if ((pttn_gamsa_nm.search(table.text) and pttn_gamsa_now.search(table.text) and pttn_gamsa_last.search(table.text)) or
                (pttn_gamsa_nm.search(table.text) and pttn_isa_ext.search(table.text))):
            gamsa_num = cnt
            if table.text.replace(" ", "").find("당") > table.text.replace(" ", "").find("전"):
                gamsa_chk_first = 1
            if pttn_isa_ext.search(table.text):
                gamsa_ext_yn = 1
        elif pttn_gamsa_nm.search(table.text) and pttn_gamsa_hando.search(table.text) and pttn_gamsa_jigup.search(table.text):
            gamsa_num_jun = cnt
            hando_is_new = True
        elif pttn_gamsa_nm.search(table.text) and pttn_gamsa_hando.search(table.text) and not pttn_gamsa_jigup.search(table.text):
            gamsa_num_dang = cnt
            hando_is_new = True

        cnt = cnt + 1

    gamsa_arr = []
    if hando_is_new:
        if gamsa_num_dang > 0 and gamsa_p == 1:
            tmp_tb = pd.DataFrame(to_table(tables[gamsa_num_dang])).values.tolist()
            for tb in tmp_tb:
                tb.append('1')
            gamsa_arr.extend(tmp_tb)
        if gamsa_num_jun > 0 and gamsa_p == 1:
            tmp_tb = pd.DataFrame(to_table(tables[gamsa_num_jun])).values.tolist()
            for tb in tmp_tb:
                tb.append('2')
            gamsa_arr.extend(tmp_tb)
    else:
        if gamsa_num > 0 and gamsa_p == 1:
            tmp_tb = get_table(tables[gamsa_num])
            if gamsa_ext_yn == 1 or len(tmp_tb[0]) < 3:
                tmp_tb = []
            gamsa_arr.extend(tmp_tb)

    # 신규 단위 및 표정리
    if hando_is_new:
        if gamsa_arr:
            tmp = ''
            for gamsa in gamsa_arr:
                if pttn_unit.search(tmp):
                    unit_check = 1
                tmp = tmp + "".join(gamsa)
            gamsa_unit = get_unit(tmp)

        for i in range(len(gamsa_arr)):
            if pttn_num.search(gamsa_arr[i][1]):
                gamsa_arr[i][1] = "".join(pttn_num.findall(gamsa_arr[i][1]))
            else:
                gamsa_arr[i][1] = '0'
    else:
        if gamsa_arr:
            tmp = ''
            for gamsa in gamsa_arr:
                tmp = tmp + "".join(gamsa)
            gamsa_unit = get_unit(tmp)

        for i in range(len(gamsa_arr)):
            for j in range(len(gamsa_arr[i])):
                if j > 0:
                    if pttn_num.search(gamsa_arr[i][j]):
                        gamsa_arr[i][j] = "".join(pttn_num.findall(gamsa_arr[i][j]))
                    else:
                        gamsa_arr[i][j] = '0'

    # 단위 신규
    isa_unit_txt = ''
    gamsa_unit_txt = ''

    if hando_is_new and unit_check == 0:
        for p in range(0, len(isa_ptag)):
            if pttn_isa.search(del_entity(isa_ptag[p].text)):
                for i in range(1, 10):
                    isa_unit_txt = isa_unit_txt + isa_ptag[p + i].text
                isa_unit = get_unit(isa_unit_txt)
            if pttn_gamsa.search(del_entity(isa_ptag[p].text)):
                for i in range(1, 10):
                    gamsa_unit_txt = gamsa_unit_txt + isa_ptag[p + i].text
                gamsa_unit = get_unit(gamsa_unit_txt)

    return isa_arr, gamsa_arr, isa_unit, gamsa_unit, isa_chk_first, gamsa_chk_first, hando_is_new

# 이사보수한도 사외이사 분리
def separate_isa(arr, is_new):
    arr_len = len(arr)

    if arr_len < 2:
        return arr

    pttn_add = re.compile("\(.*\)")
    pttn_del = "\(.*\)"
    tb_text = ' '.join(arr[0])

    if is_new:
        if '사외' not in tb_text:
            arr.insert(1, ['사외이사 수', '0'])
            arr.insert(4, ['사외이사 수', '0'])
            return arr

        tmp = []
        for i in range(len(arr)):
            if "".join(pttn_add.findall((arr[i][0].replace(" ", "")))) != "":
                col_tmp = []
                for j in range(len(arr[i])):
                    item = "".join(pttn_add.findall((arr[i][j].replace(" ", ""))))
                    col_tmp.append(item.replace('(', '').replace(')', ''))
                    arr[i][j] = re.sub(pttn_del, '', arr[i][j])
                col_tmp[2] = arr[i][j]
                tmp.append(col_tmp)

        arr.insert(1, tmp[0])
        arr.insert(4, tmp[1])
    else:
        if '사외' not in tb_text:
            arr.insert(1, ['사외이사 수', 0, 0])
            return arr

        tmp = []
        for i in range(0, 3):
            str = "".join(pttn_add.findall(arr[0][i].replace(" ", "")))
            tmp.append(str.replace('(', '').replace(')', ''))
            arr[0][i] = re.sub(pttn_del, '', arr[0][i])

        arr.insert(1, tmp)

    return arr

# web content to table
def to_table(cont):
    table = []
    trs = cont.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        tmp = []
        for td in tds:
            tmp.append(del_entity(td.text))
        table.append(tmp)

    return table

# html &nbsp; 삭제
def del_entity(ent):
    ent = ent.replace(u'\xa0', u' ').strip()

    return ent

# 주식매수선택권 테이블 파싱
def dis_stockoption(driver):
    # 주식매수선택권 표 제목 패턴
    pttn_stock = re.compile("□[ \s]*주[ \s]*식[ \s]*매[ \s]*수[ \s]*선[ \s]*택[ \s]*권|□[ \s]*주[ \s]*식[ \s]*매[ \s]*수[ \s]*선[ \s]*택[ \s]*권[ \S]*[ \s]*부[ \s]*여")

    # 주식매수선택권 부여받을 자 표 패턴
    pttn_nm = re.compile("성[ \s]*명")
    pttn_position = re.compile("직[ \s]*위|직[ \s]*책")
    pttn_stock_cnt = re.compile("교[ \s]*부[ \S]*주[ \s]*식|교[ \s]*부[ \s]*할[ \s]*주[ \s]*식|주[ \s]*식[ \s]*의[ \s]*종[ \s]*류|주[ \s]*식[ \s]*수")

    # 주식매수선택권 부여방법 표 패턴
    pttn_method = re.compile("부[ \s]*여[ \s]*방[ \s]*법")
    pttn_stock_kind = re.compile("교[ \s]*부[ \s]*할[ \s]*주[ \s]*식[ \s]*종[ \s]*류[ \s]*및[ \s]*수|교[ \s]*부[ \s]*할[ \s]*주[ \s]*식[ \S]*[ \s]*종[ \s]*류")
    pttn_period = re.compile("행[ \s]*사[ \s]*가[ \s]*격[ \s]*및[ \s]*행[ \s]*사[ \s]*기[ \s]*간|행[ \s]*사[ \s]*가[ \s]*격[ \S]*[ \s]*행[ \s]*사[ \s]*기[ \s]*간")
    pttn_etc = re.compile("기[ \s]*타[ \s]*조[ \s]*건[ \s]*의[ \s]*개[ \s]*요|기[ \s]*타[ \s]*조[ \s]*건[ \S]*개[ \s]*요")

    # 주식매수선택권 잔여주식 표 패턴
    pttn_total_cnt = re.compile("총[ \s]*발[ \s]*행[ \s]*주[ \s]*식[ \s]*수")
    pttn_available_period = re.compile("부[ \s]*여[ \s]*가[ \s]*능[ \s]*주[ \s]*식[ \s]*의[ \s]*범[ \s]*위|부[ \s]*여[ \s]*가[ \s]*능[ \s]*주[ \s]*식[ \S]*범[ \s]*위")
    pttn_available_kind = re.compile("부[ \s]*여[ \s]*가[ \s]*능[ \s]*주[ \s]*식[ \s]*의[ \s]*종[ \s]*류|부[ \s]*여[ \s]*가[ \s]*능[ \s]*주[ \s]*식[ \S]*종[ \s]*류")
    pttn_available_cnt = re.compile("부[ \s]*여[ \s]*가[ \s]*능[ \s]*주[ \s]*식[ \s]*수")
    pttn_extra_cnt = re.compile("잔[ \s]*여[ \s]*주[ \s]*식[ \s]*수")

    # 주식매수선택권 실효내역 표 패턴
    pttn_yyyy = re.compile("사[ \s]*업[ \s]*년[ \s]*도|사[ \s]*업[ \s]*연[ \s]*도")
    pttn_dis_ymd = re.compile("부[ \s]*여[ \s]*일")
    pttn_dis_person = re.compile("부[ \s]*여[ \s]*인[ \s]*원")
    pttn_dis_cnt = re.compile("부[ \s]*여[ \s]*주[ \s]*식[ \s]*수|부[ \s]*여[ \s]*주[ \s]*식[ \S]*수")
    pttn_use_cnt = re.compile("행[ \s]*사[ \s]*주[ \s]*식[ \s]*수|행[ \s]*사[ \s]*주[ \s]*식[ \S]*수")
    pttn_act_cnt = re.compile("실[ \s]*효[ \s]*주[ \s]*식[ \s]*수|실[ \s]*효[ \s]*주[ \s]*식[ \S]*수")

    # 총인원 삭제 패턴
    pttn_cnt = re.compile("총[ \S]*[0-9]*[ \S]*명")

    # 주식매수선택권 표
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')

    # 주식매수선택권 부여받을 자 테이블
    cnt = 0
    distribution_num = []
    for table in tables:
        if pttn_nm.search(table.text) and pttn_position.search(table.text) and pttn_stock_cnt.search(table.text):
            distribution_num.append(cnt)
        cnt = cnt + 1

    distribution_arr = []
    if len(distribution_num) > 0:
        for i in range(len(distribution_num)):
            tmp_tb = get_table(tables[distribution_num[i]])
            for d in range(0, len(tmp_tb)):
                if not pttn_cnt.search(tmp_tb[d][0]):
                    distribution_arr.append(tmp_tb[d])

    # 주식매수선택권 부여방법 테이블
    cnt = 0
    dis_method_num = []
    for table in tables:
        if (pttn_method.search(table.text) and pttn_stock_kind.search(table.text)
                and pttn_period.search(table.text) and pttn_etc.search(table.text)):
            dis_method_num.append(cnt)
        cnt = cnt + 1

    dis_method_arr = []
    if len(dis_method_num) > 0:
        for i in range(len(dis_method_num)):
            tmp_tb = get_table(tables[dis_method_num[i]])
            dis_method_arr = tmp_tb

    # 주식매수선택권 잔여주식 테이블
    cnt = 0
    extra_stock_num = []
    for table in tables:
        if (pttn_total_cnt.search(table.text) and pttn_available_period.search(table.text)
                and pttn_available_kind.search(table.text) and pttn_available_cnt.search(table.text)
                and pttn_extra_cnt.search(table.text)):
            extra_stock_num.append(cnt)
        cnt = cnt + 1

    extra_stock_arr = []
    if len(extra_stock_num) > 0:
        for i in range(len(extra_stock_num)):
            tmp_tb = get_table(tables[extra_stock_num[i]])
            extra_stock_arr = tmp_tb

    # 주식매수선택권 실효내역 테이블
    cnt = 0
    use_stock_num = []
    for table in tables:
        if (pttn_yyyy.search(table.text) and pttn_dis_ymd.search(table.text) and pttn_dis_person.search(table.text)
                and pttn_dis_cnt.search(table.text) and pttn_use_cnt.search(table.text) and pttn_act_cnt.search(table.text)):
            use_stock_num.append(cnt)
        cnt = cnt + 1

    use_stock_arr = []
    if len(use_stock_num) > 0:
        for i in range(len(use_stock_num)):
            tmp_tb = get_table(tables[use_stock_num[i]])
            for d in range(0, len(tmp_tb)):
                if not pttn_cnt.search(tmp_tb[d][2]):
                    use_stock_arr.append(tmp_tb[d])

    return distribution_arr, dis_method_arr, extra_stock_arr, use_stock_arr

# 표에서 필요없는 열 제거
def del_table_column(tb, columns):
    for t in tb:
        for col in columns:
            del t[col]

# 표 내역없음 체크
def check_empty_table(tb):
    # case1 : -, 공백으로 이루어진 표
    pttn_empty = '[ \t\n\r\f\v-]'
    pttn_null = 'null'
    cnt_empty = 0
    if len(tb) > 0:
        for td in tb[0]:
            td = re.sub(pttn_empty, '', td)
            td = re.sub(pttn_null, '', td)
            if td != '':
                cnt_empty = cnt_empty + 1

    if cnt_empty > 0:
        return 1

    return 0

# 괄호 안의 내용 제거
def del_gwalho(cont):
    pttn_prts = re.compile("[({<\[]")
    if pttn_prts.search(cont):
        prts = "".join(pttn_prts.findall(cont))
        postion_x = cont.find(prts)
        return cont[:postion_x]
    else:
        return cont

# 단위 표
def check_unit(table):
    pttn_unit_1 = re.compile("단[ \s]*위")
    pttn_unit_2 = re.compile("단[ \s]*위[ \s]*:")

    if pttn_unit_1.search(table.text) or pttn_unit_2.search(table.text):
        return 1

    return 0

# rcpno_list
def get_rcpno_list(driver):
    # 공고문 본문 드롭다운
    select_box = driver.find_element_by_xpath('//select[@id="family"]')
    select_options = select_box.find_elements_by_tag_name('option')
    rcpno_list = []

    for i in range(1, len(select_options)):
        option_xpath = '//select[@id="family"]/option[{0}]'.format(i + 1)
        rcpno = str(driver.find_element_by_xpath(option_xpath).get_attribute('value')).replace("rcpNo=", "")
        rcpno_list.append(rcpno)
    rcpno_list.reverse()

    return rcpno_list

# 재무제표에서 nps 값 가져오기(1: 당기순이익, 2: 부채총계, 3: 자본총계)
def get_nps_finanacial_item(fin_tb, account_gb):
    pttn_korean = re.compile("[가-힣]")
    str_sunik = ["당기순이익", "당기순손실", "당기순손익", "당기순이익손실", "당기순손실이익", "당기순손익이익", "당기순손익손실"]
    str_buche = ["부채총계"]
    str_jabon = ["자본총계"]
    account_num = -1

    if account_gb == 1:
        for i in range(0, len(fin_tb)):
            account_nm = "".join(pttn_korean.findall(fin_tb[i]))
            for sunik in str_sunik:
                if account_nm == sunik:
                    account_num = i
    elif account_gb == 2:
        for i in range(0, len(fin_tb)):
            account_nm = "".join(pttn_korean.findall(fin_tb[i]))
            for buche in str_buche:
                if account_nm == buche:
                    account_num = i
    elif account_gb == 3:
        for i in range(0, len(fin_tb)):
            account_nm = "".join(pttn_korean.findall(fin_tb[i]))
            for jabon in str_jabon:
                if account_nm == jabon:
                    account_num = i

    return account_num

# 한글
def get_hangul(param):
    pttn_han = re.compile("[가-힣]")
    result = "".join(pttn_han.findall(param))

    return result

# 일시 변경
def get_full_ymdstr(ymd, hm):
    ymd_len = len(ymd)
    hm_len = len(hm)
    ymdstr = ''
    hmstr = ''

    if ymd_len == 8 and hm_len == 4:
        yy = int(ymd[:4])
        mm = int(ymd[4:6])
        dd = int(ymd[6:])

        week = ['월', '화', '수', '목', '금', '토', '일']
        dt = datetime.datetime(yy, mm, dd)
        day = week[dt.weekday()]

        ymdstr = str(yy) + '년 ' + str(mm) + '월 ' + str(dd) + '일(' + day + ') '

        hh = int(hm[:2])
        mi = int(hm[2:])
        apm = '오전 '
        if hh > 12:
            hh = hh - 12
            apm = '오후 '

        hmstr = apm + str(hh) + '시 '
        if mi != 0:
            hmstr = hmstr + str(mi) + '분'
    else:
        return ymd + ' ' + hm

    return ymdstr + hmstr
