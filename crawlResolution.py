from builtins import print

from utils import get_dbcon, close_dbcon
from utils import get_driver, close_driver
from utils import chk_no_data, get_rcpno_list, check_empty_table, make_ymd
from monitorUtil import set_crawl_time, get_rcplist, get_crawl_time
from sql import resolution_mst_ins, isa_info_ins, isa_car_ins, isa_dup_ins, biz_ins
from logger import get_info_logger_rs, get_error_logger_rs

import sys
import time

# 로그
info_logger = get_info_logger_rs()
error_logger = get_error_logger_rs()


# 문서번호 리스트 생성
def get_rcpNo(rcpno):
    try:
        jm_code = rcpno[0]
        rcp_yn = rcpno[1]
        rcp_no = rcpno[2]
        rcp_gb = rcpno[4]

        if '기재정정' in rcp_yn or '기재 정정' in rcp_yn:
            rcp_yn = 'y'
        else:
            rcp_yn = 'n'

        return jm_code, rcp_no, rcp_yn, rcp_gb
    except Exception as e:
        error_logger.error('Failed rcp_no creation. : {0}'.format(e))

# 이사선임 데이터
def get_isa(driver, tbnm):
    # 이사선임 구분별 테이블 개수 체크
    tb_tmp = driver.find_elements_by_xpath('//*[@id="{0}"]/div/div/table'.format(tbnm))

    if len(tb_tmp) > 1:
        if tbnm == 'LIB_L7021' or tbnm == 'LIB_L9019' or tbnm == 'LIB_L3025':
            tb_isa = [['1', '2', '3', '4', '5']]
        else:
            tb_isa = [['1', '2', '3', '4', '5', '6']]

        for i in range(0, len(tb_tmp)):
            tb_tmp_tr_len = len(tb_tmp[i].find_element_by_tag_name('tbody').find_elements_by_tag_name('tr'))

            for j in range(1, tb_tmp_tr_len):
                tb_isa.extend(driver.find_elements_by_xpath('//*[@id="{0}"]/div/div/table[{1}]/tbody/tr[{2}]'.format(tbnm, i + 1, j + 1)))
    else:
        tb_isa = driver.find_elements_by_xpath('//*[@id="{0}"]/div/div/table/tbody/tr'.format(tbnm))

    # 테이블은 있으나 데이터 없는 경우
    if tb_isa[1].find_elements_by_tag_name('td')[0].text == '' or tb_isa[1].find_elements_by_tag_name('td')[0].text == '-':
        return []

    # 테이블 row, col 세팅
    row = len(tb_isa)
    col = 9

    # 결과 담을 배열
    res_arr = [[0 for y in range(col)] for x in range(row - 1)]
    for i in range(1, row):
        res_arr[i - 1][0] = tb_isa[i].find_elements_by_tag_name('td')[0].text   # 성명
        res_arr[i - 1][1] = tb_isa[i].find_elements_by_tag_name('td')[1].text   # 생년월
        res_arr[i - 1][2] = tb_isa[i].find_elements_by_tag_name('td')[2].text   # 임기
        res_arr[i - 1][3] = tb_isa[i].find_elements_by_tag_name('td')[3].text   # 신규선임

        if tbnm == 'LIB_L7021' or tbnm == 'LIB_L9019' or tbnm == 'LIB_L3025':       # #사내이사
            res_arr[i - 1][4] = tb_isa[i].find_elements_by_tag_name('td')[4].text   # 경력
            res_arr[i - 1][5] = '0'                                                 # 겸직
            res_arr[i - 1][6] = '0'                                                 # 사외이사여부(감사의 경우)
            res_arr[i - 1][7] = '0'                                                 # 상근여부
            res_arr[i - 1][8] = '1'                                                 # 이사구분
        elif tbnm == 'LIB_L7020' or tbnm == 'LIB_L9018'or tbnm == 'LIB_L3024':      # #사외이사
            res_arr[i - 1][4] = tb_isa[i].find_elements_by_tag_name('td')[4].text
            res_arr[i - 1][5] = tb_isa[i].find_elements_by_tag_name('td')[5].text
            res_arr[i - 1][6] = '0'
            res_arr[i - 1][7] = '0'
            res_arr[i - 1][8] = '2'
        elif tbnm == 'LIB_L7018' or tbnm == 'LIB_L9016' or tbnm == 'LIB_L3022':     # #감사위원
            res_arr[i - 1][4] = tb_isa[i].find_elements_by_tag_name('td')[5].text
            res_arr[i - 1][5] = '0'
            res_arr[i - 1][6] = tb_isa[i].find_elements_by_tag_name('td')[4].text
            res_arr[i - 1][7] = '0'
            res_arr[i - 1][8] = '3'
        elif tbnm == 'LIB_L7017' or tbnm == 'LIB_L9015' or tbnm == 'LIB_L3021':     # #감사
            res_arr[i - 1][4] = tb_isa[i].find_elements_by_tag_name('td')[5].text
            res_arr[i - 1][5] = '0'
            res_arr[i - 1][6] = '0'
            res_arr[i - 1][7] = tb_isa[i].find_elements_by_tag_name('td')[4].text
            res_arr[i - 1][8] = '4'
        else:                                                                       # #기타
            res_arr[i - 1][4] = tb_isa[i].find_elements_by_tag_name('td')[4].text
            res_arr[i - 1][5] = '0'
            res_arr[i - 1][6] = '0'
            res_arr[i - 1][7] = '0'
            res_arr[i - 1][8] = '5'

    if check_empty_table(res_arr) == 0:
        res_arr = []

    return res_arr

# 사업목적 변경 데이터
def get_biz(driver, tbnm):
    tb_biz = driver.find_elements_by_xpath('//*[@id="{0}"]/div/div/table/tbody/tr'.format(tbnm))
    # 테이블은 있으나 데이터 없는 경우
    if tb_biz[1].find_elements_by_tag_name('td')[0].text == '' or tb_biz[1].find_elements_by_tag_name('td')[0].text == '-':
        return []

    # 테이블 row, col 세팅
    row = len(tb_biz)
    col = 4

    # 결과 담을 배열
    res_arr = [[0 for y in range(col)] for x in range(row - 1)]
    for i in range(1, row):
        if tbnm == 'LIB_L9017':
            if i == 1:                                                                      # 추가
                res_arr[i - 1][0] = '1'
                res_arr[i - 1][1] = tb_biz[i].find_elements_by_tag_name('td')[1].text
                res_arr[i - 1][2] = ''
                res_arr[i - 1][3] = tb_biz[i].find_elements_by_tag_name('td')[2].text
            elif i == 2:                                                                    # 삭제
                res_arr[i - 1][0] = '3'
                res_arr[i - 1][1] = tb_biz[i].find_elements_by_tag_name('td')[1].text
                res_arr[i - 1][2] = ''
                res_arr[i - 1][3] = tb_biz[i].find_elements_by_tag_name('td')[2].text
            elif i == 4:                                                                    # 변경
                res_arr[i - 1][0] = '2'
                res_arr[i - 1][1] = tb_biz[i].find_elements_by_tag_name('td')[0].text
                res_arr[i - 1][2] = tb_biz[i].find_elements_by_tag_name('td')[1].text
                res_arr[i - 1][3] = tb_biz[i].find_elements_by_tag_name('td')[2].text
            else:
                continue
        else:
            if i == 1:                                                                      # 추가
                res_arr[i - 1][0] = '1'
                res_arr[i - 1][1] = tb_biz[i].find_elements_by_tag_name('td')[1].text
                res_arr[i - 1][2] = ''
                res_arr[i - 1][3] = tb_biz[i].find_elements_by_tag_name('td')[2].text
            elif i == 3:                                                                    # 변경
                res_arr[i - 1][0] = '2'
                res_arr[i - 1][1] = tb_biz[i].find_elements_by_tag_name('td')[0].text
                res_arr[i - 1][2] = tb_biz[i].find_elements_by_tag_name('td')[1].text
                res_arr[i - 1][3] = tb_biz[i].find_elements_by_tag_name('td')[2].text
            elif i == 4:                                                                    # 삭제
                res_arr[i - 1][0] = '3'
                res_arr[i - 1][1] = tb_biz[i].find_elements_by_tag_name('td')[1].text
                res_arr[i - 1][2] = ''
                res_arr[i - 1][3] = tb_biz[i].find_elements_by_tag_name('td')[2].text
            else:
                continue

    # 타이틀 제거
    if tbnm == 'LIB_L9017':
        res_arr.pop(2)
    else:
        res_arr.pop(1)

    # 빈 데이터 제거
    ################################# 변경전이 - 인 예외 경우 체크
    minus = 0
    res_len = len(res_arr)
    for i in range(0, res_len):
        cnt = i - minus
        if not chk_no_data(res_arr[cnt][1]):
            res_arr.pop(cnt)
            minus = minus + 1

    return res_arr

# 결의문 전체 + DB 삽입
def get_resolution(jm_code, rcp_no, rcp_gb, cursor):
    try:
        # driver 세팅(결의, 공고)
        driver = get_driver('C:\\Users\\admin\\PycharmProjects\\webCrawl\\chromedriver.exe',
                            'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={0}'.format(rcp_no))

        driver.implicitly_wait(10)

        # 주총 공고의 rcpno 히스토리
        rcpno_list = get_rcpno_list(driver)
        # 최초 문서의 공고년도
        first_rcp_no = rcpno_list[0]
        first_rcp_yy = first_rcp_no[:4]

        # 주총결의 데이터 세팅
        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
        # 상장 구분
        if 'Y' in rcp_gb:
            tb_mst = driver.find_elements_by_xpath('//*[@id="XFormD52_Form0_Table0"]/tbody/tr')
        else:
            tb_mst = driver.find_elements_by_xpath('//*[@id="XFormD2_Form0_Table0"]/tbody/tr')

        # 주총 결의
        meet_tb = [0 for x in range(9)]
        if 'Y' in rcp_gb:
            meet_tb[0] = tb_mst[1].find_elements_by_tag_name('td')[1].text      # 일자
            meet_tb[1] = tb_mst[1].find_elements_by_tag_name('td')[2].text      # 시간
            meet_tb[8] = tb_mst[0].find_elements_by_tag_name('td')[1].text      # 주총구분
        else:
            meet_tb[0] = tb_mst[0].find_elements_by_tag_name('td')[2].text      # 일자
            meet_tb[1] = tb_mst[1].find_elements_by_tag_name('td')[1].text      # 시간
            meet_tb[8] = tb_mst[8].find_elements_by_tag_name('td')[1].text      # 주총구분

        meet_tb[2] = tb_mst[2].find_elements_by_tag_name('td')[1].text      # 장소
        meet_tb[3] = tb_mst[3].find_elements_by_tag_name('td')[1].text      # 의안내용
        meet_tb[4] = tb_mst[4].find_elements_by_tag_name('td')[1].text      # 이사회결의일
        meet_tb[5] = tb_mst[5].find_elements_by_tag_name('td')[2].text      # 사외이사_참
        meet_tb[6] = tb_mst[6].find_elements_by_tag_name('td')[1].text      # 사외이사_불참
        meet_tb[7] = tb_mst[7].find_elements_by_tag_name('td')[1].text      # 감사참석여부

        # 사외이사 선임 및 사업목적 테이블 유무 확인
        """isa_1, isa_2, isa_3, isa_4, tb_biz = False, False, False, False, False
        spans = driver.find_elements_by_tag_name('span')
        for span in spans:
            title = span.text
            title = get_hangul(title)
            if title == '이사선임세부내역':
                isa_1 = True
            elif title == '사외이사선임세부내역':
                isa_2 = True
            elif title == '감사위원선임세부내역':
                isa_3 = True
            elif title == '감사선임세부내역':
                isa_4 = True
            elif title == '사업목적변경세부내역':
                tb_biz = True
        """

        # 이사선임 & 사업목적
        isa_arr = []
        biz_arr = []
        if 'Y' in rcp_gb:
            # 이사선임
            isa_1 = driver.find_elements_by_xpath('//*[@id="LIB_L9019"]')  # 이사선임 div 유무
            isa_2 = driver.find_elements_by_xpath('//*[@id="LIB_L9018"]')  # 사외이사선임 div 유무
            isa_3 = driver.find_elements_by_xpath('//*[@id="LIB_L9016"]')  # 감사위원선임 div 유무
            isa_4 = driver.find_elements_by_xpath('//*[@id="LIB_L9015"]')  # 감사선임 div 유무

            if isa_1:
                isa_arr.extend(get_isa(driver, 'LIB_L9019'))
            if isa_2:
                isa_arr.extend(get_isa(driver, 'LIB_L9018'))
            if isa_3:
                isa_arr.extend(get_isa(driver, 'LIB_L9016'))
            if isa_4:
                isa_arr.extend(get_isa(driver, 'LIB_L9015'))

            # 사업목적
            tb_biz = driver.find_elements_by_xpath('//*[@id="LIB_L9017"]')  # 사업목적 div 유무

            if tb_biz:
                biz_arr.extend(get_biz(driver, 'LIB_L9017'))
        elif 'K' in rcp_gb:
            # 이사선임
            isa_1 = driver.find_elements_by_xpath('//*[@id="LIB_L7021"]')  # 이사선임 div 유무
            isa_2 = driver.find_elements_by_xpath('//*[@id="LIB_L7020"]')  # 사외이사선임 div 유무
            isa_3 = driver.find_elements_by_xpath('//*[@id="LIB_L7018"]')  # 감사위원선임 div 유무
            isa_4 = driver.find_elements_by_xpath('//*[@id="LIB_L7017"]')  # 감사선임 div 유무

            if isa_1:
                isa_arr.extend(get_isa(driver, 'LIB_L7021'))
            if isa_2:
                isa_arr.extend(get_isa(driver, 'LIB_L7020'))
            if isa_3:
                isa_arr.extend(get_isa(driver, 'LIB_L7018'))
            if isa_4:
                isa_arr.extend(get_isa(driver, 'LIB_L7017'))

            # 사업목적
            tb_biz = driver.find_elements_by_xpath('//*[@id="LIB_L7019"]')  # 사업목적 div 유무

            if tb_biz:
                biz_arr.extend(get_biz(driver, 'LIB_L7019'))
        else:
            # 이사선임
            isa_1 = driver.find_elements_by_xpath('//*[@id="LIB_L3025"]')  # 이사선임 div 유무
            isa_2 = driver.find_elements_by_xpath('//*[@id="LIB_L3024"]')  # 사외이사선임 div 유무
            isa_3 = driver.find_elements_by_xpath('//*[@id="LIB_L3022"]')  # 감사위원선임 div 유무
            isa_4 = driver.find_elements_by_xpath('//*[@id="LIB_L3021"]')  # 감사선임 div 유무

            if isa_1:
                isa_arr.extend(get_isa(driver, 'LIB_L3025'))
            if isa_2:
                isa_arr.extend(get_isa(driver, 'LIB_L3024'))
            if isa_3:
                isa_arr.extend(get_isa(driver, 'LIB_L3022'))
            if isa_4:
                isa_arr.extend(get_isa(driver, 'LIB_L3021'))

            # 사업목적
            tb_biz = driver.find_elements_by_xpath('//*[@id="LIB_L3023"]')  # 사업목적 div 유무

            if tb_biz:
                biz_arr.extend(get_biz(driver, 'LIB_L3023'))

        # --------------------------------------------------------------------------------- #
        # DB 삽입
        # 중복체크
        dup_select = """select * from proxy001 where rcp_no = '{0}'""".format(rcp_no)
        cursor.execute(dup_select)
        dup_cnt = cursor.rowcount
        if dup_cnt > 0:
            return 0

        # 회차 max 값
        max_select = """select * from proxy001 where left(first_rcpno, 4) = '{0}' and jm_code = '{1}' group by meet_seq
                             """.format(first_rcp_yy, jm_code)

        cursor.execute(max_select)
        max_seq = cursor.rowcount

        # meet_seq 생성
        seq_select = """select meet_seq from proxy001 where first_rcpno = '{0}'
                             """.format(first_rcp_no)

        cursor.execute(seq_select)
        seq = cursor.fetchone()

        if cursor.rowcount < 1:
            seq = str(max_seq + 1).zfill(2)
        else:
            seq = "".join(seq)
            seq = seq[-2:]

        yyyy = make_ymd(meet_tb[0][:4])
        if yyyy is not None and yyyy != '':
            yyyy = yyyy[:4]
        else:
            yyyy = time.strftime('%Y')

        meet_seq = jm_code + yyyy + seq

        # 결의 mst 삽입
        in_qry = resolution_mst_ins(meet_seq, meet_tb, jm_code, rcp_no, rcpno_list[0])
        cursor.execute(in_qry)
        #print(in_qry)

        # 이사선임 삽입
        if isa_arr:
            #print(isa_arr)
            for i in range(0, len(isa_arr)):
                ins_isa_info = isa_info_ins(meet_seq, isa_arr[i], rcp_no, i)
                cursor.execute(ins_isa_info)
                #print(str(i), '번째 이사 쿼리 : ', ins_isa_info)

                if chk_no_data(isa_arr[i][4]):
                    ins_isa_car = isa_car_ins(meet_seq, isa_arr[i], rcp_no, i)     # 이사선임_경력
                    cursor.execute(ins_isa_car)
                    #print(str(i), '번째 이사 경력 쿼리 : ', ins_isa_car)

                if chk_no_data(isa_arr[i][5]):
                    ins_isa_dup = isa_dup_ins(meet_seq, isa_arr[i], rcp_no, i)     # 이사선임_겸직
                    cursor.execute(ins_isa_dup)
                    #print(str(i), '번째 이사 겸직 쿼리 : ', ins_isa_dup)

        # 사업목적 변경 삽입
        if biz_arr:
            for i in range(0, len(biz_arr)):
                #print(biz_arr[i])
                ins_biz = biz_ins(meet_seq, biz_arr[i], rcp_no)
                cursor.execute(ins_biz)
                #print("사업목적 변경 쿼리 : ", ins_biz)
    except Exception as e:
        error_logger.error('Resolution crawling fail. : [{0}] [{1}] {2}'.format(jm_code, rcp_no, e))
    finally:
        close_driver(driver)

def resolution_main(conn):
    start_time = get_crawl_time('R')
    end_time = start_time

    rcpnos = get_rcplist(start_time, 'R')
    #rcpnos = [['010050', '주주총회소집결의', '20200130800253', '20200213180755', 'Y']]

    for rcpno in rcpnos:
        info_logger.info('---------- rcp_no : [{0}] ----------'.format(rcpno[2]))
        cursor = conn.cursor()

        jm_code, rcp_no, rcp_yn, rcp_gb = get_rcpNo(rcpno)
        get_resolution(jm_code, rcp_no, rcp_gb, cursor)
        end_time = rcpno[3]

        cursor.close()
        conn.commit()
        time.sleep(1)

    set_crawl_time(end_time, 'R')


if __name__== "__main__":
    conn = get_dbcon('esg')
    resolution_main(conn)
    close_dbcon(conn)
