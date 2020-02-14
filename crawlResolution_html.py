from builtins import print

from utils import get_dbcon, close_dbcon
from utils import get_driver, close_driver
from utils import get_regYn, make_ymd, chk_no_data
from sql import resolution_mst_ins, isa_car_ins, isa_dup_ins, biz_ins
import requests
from bs4 import BeautifulSoup

import sys
import time


jm_code = '095570'
# dart 문서번호
def get_rcpNo(jm_code, keywod):
    driver = get_driver('C:\\Users\\admin\\PycharmProjects\\webCrawl\\chromedriver.exe',
                        'http://dart.fss.or.kr/dsab002/main.do#')                                   # 드라이버 로드

    driver.find_element_by_name('textCrpNm').send_keys(jm_code)                                     # 종목코드
    driver.find_element_by_xpath('//*[@id="searchForm"]/fieldset/div/p[3]/span[2]/a[4]').click()    # 기간 : 1년
    checked = driver.find_element_by_xpath('//*[@id="finalReport"]').get_attribute('checked')       # 최종보고서 여부
    if checked:
        driver.find_element_by_xpath('//*[@id="finalReport"]').click()                              # 최종보고서 체크 해제
    driver.find_element_by_id('reportName').send_keys(keywod)                                       # 검색구분 : 결의

    driver.find_element_by_xpath('//*[@id="searchForm"]/fieldset/div/p[8]/input').click()           # 검색

    res_list = driver.find_elements_by_xpath('//*[@id="listContents"]/div[1]/table/tbody/tr')       # 결과 리스트

    # 최상위 데이터만 수집 ( => 짧은 주기로 수집해야 함)
    # 결과 리스트에서 가용 데이터 추출
    if len(res_list) == 0:
        print('검색 결과가 없습니다.')
        sys.exit(0)
    else:
        item = res_list[0]
    # 문서번호
    rcp_no = item.find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').get_attribute('href')[-14:]
    # 기재정정
    rcp_yn = item.find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').find_element_by_tag_name('span').text
    # 시장구분
    rcp_gb = item.find_elements_by_tag_name('td')[5].find_element_by_tag_name('img').get_attribute('title')

    if len(rcp_no) != 14:
        print('rcpNo 형식이 다릅니다.')
        sys.exit(0)

    if '첨부' in rcp_yn:
        print('첨부정정은 수집대상 제외')
        sys.exit(0)

    close_driver(driver)

    return rcp_no, rcp_yn, rcp_gb

# html 파일 저장
def get_html(rcp_no):
    # driver 세팅(결의, 공고)
    driver = get_driver('C:\\Users\\admin\\PycharmProjects\\webCrawl\\chromedriver.exe',
                        'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={0}'.format(rcp_no))
    # 주총결의 데이터 세팅
    driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))

    html = driver.page_source
    print(html)

    f_nm = 'C:\\Users\\admin\\Desktop\\html\\{0}.html'.format(rcp_no)
    f = open(f_nm, 'w')
    f.write(html)
    f.close()

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
        res_arr[i - 1][0] = tb_isa[i].find_eelemnts_by_tag_name('td')[0].text   # 성명
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
def resolution_main(jm_code, rcp_no, rcp_yn, rcp_gb):
    # driver 세팅(결의, 공고)
    driver = get_driver('C:\\Users\\admin\\PycharmProjects\\webCrawl\\chromedriver.exe',
                        'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={0}'.format(rcp_no))

    # 주총결의 데이터 세팅
    driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
    # 상장 구분
    if '유가' in rcp_gb:
        tb_mst = driver.find_elements_by_xpath('//*[@id="XFormD52_Form0_Table0"]/tbody/tr')
    else:
        tb_mst = driver.find_elements_by_xpath('//*[@id="XFormD2_Form0_Table0"]/tbody/tr')

    # 주총 결의
    meet_tb = [0 for x in range(9)]
    if '유가' in rcp_gb:
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

    # 이사선임 & 사업목적
    isa_arr = []
    biz_arr = []
    if '유가' in rcp_gb:
        # 이사선임
        isa_1 = driver.find_elements_by_xpath('//*[@id="LIB_L9019"]')  # 이사선임 div 유무
        isa_2 = driver.find_elements_by_xpath('//*[@id="LIB_L9018"]')  # 사외이사선임 div 유무
        isa_3 = driver.find_elements_by_xpath('//*[@id="LIB_L9016"]')  # 감사위원선임 div 유무
        isa_4 = driver.find_elements_by_xpath('//*[@id="LIB_L9015"]')  # 감사선임 div 유무

        if isa_1 != '' and isa_1:
            isa_arr.extend(get_isa(driver, 'LIB_L9019'))
        if isa_2 != '' and isa_2:
            isa_arr.extend(get_isa(driver, 'LIB_L9018'))
        if isa_3 != '' and isa_3:
            isa_arr.extend(get_isa(driver, 'LIB_L9016'))
        if isa_4 != '' and isa_4:
            isa_arr.extend(get_isa(driver, 'LIB_L9015'))

        # 사업목적
        tb_biz = driver.find_elements_by_xpath('//*[@id="LIB_L9017"]')  # 사업목적 div 유무

        if tb_biz != '' and tb_biz:
            biz_arr.extend(get_biz(driver, 'LIB_L9017'))
    elif '코스닥' in rcp_gb:
        # 이사선임
        isa_1 = driver.find_elements_by_xpath('//*[@id="LIB_L7021"]')  # 이사선임 div 유무
        isa_2 = driver.find_elements_by_xpath('//*[@id="LIB_L7020"]')  # 사외이사선임 div 유무
        isa_3 = driver.find_elements_by_xpath('//*[@id="LIB_L7018"]')  # 감사위원선임 div 유무
        isa_4 = driver.find_elements_by_xpath('//*[@id="LIB_L7017"]')  # 감사선임 div 유무

        if isa_1 != '' and isa_1:
            isa_arr.extend(get_isa(driver, 'LIB_L7021'))
        if isa_2 != '' and isa_2:
            isa_arr.extend(get_isa(driver, 'LIB_L7020'))
        if isa_3 != '' and isa_3:
            isa_arr.extend(get_isa(driver, 'LIB_L7018'))
        if isa_4 != '' and isa_4:
            isa_arr.extend(get_isa(driver, 'LIB_L7017'))

        # 사업목적
        tb_biz = driver.find_elements_by_xpath('//*[@id="LIB_L7019"]')  # 사업목적 div 유무

        if tb_biz != '' and tb_biz:
            biz_arr.extend(get_biz(driver, 'LIB_L7019'))
    else:
        # 이사선임
        isa_1 = driver.find_elements_by_xpath('//*[@id="LIB_L3025"]')  # 이사선임 div 유무
        isa_2 = driver.find_elements_by_xpath('//*[@id="LIB_L3024"]')  # 사외이사선임 div 유무
        isa_3 = driver.find_elements_by_xpath('//*[@id="LIB_L3022"]')  # 감사위원선임 div 유무
        isa_4 = driver.find_elements_by_xpath('//*[@id="LIB_L3021"]')  # 감사선임 div 유무

        if isa_1 != '' and isa_1:
            isa_arr.extend(get_isa(driver, 'LIB_L3025'))
        if isa_2 != '' and isa_2:
            isa_arr.extend(get_isa(driver, 'LIB_L3024'))
        if isa_3 != '' and isa_3:
            isa_arr.extend(get_isa(driver, 'LIB_L3022'))
        if isa_4 != '' and isa_4:
            isa_arr.extend(get_isa(driver, 'LIB_L3021'))

        # 사업목적
        tb_biz = driver.find_elements_by_xpath('//*[@id="LIB_L3023"]')  # 사업목적 div 유무

        if tb_biz != '' and tb_biz:
            biz_arr.extend(get_biz(driver, 'LIB_L3023'))

    # DB 삽입
    try:
        conn = get_dbcon('esg')
        cursor = conn.cursor()

        try:
            # 조회용 주총 값
            ymd = make_ymd(meet_tb[0])
            gb = get_regYn(meet_tb[8])
            seq_select = """select * from proxy001 where meet_ymd = '{0}' and jm_code = '{1}' and meet_gb = '{2}'
                         """.format(ymd, jm_code, gb)

            cursor.execute(seq_select)
            rows = cursor.rowcount

            # 기재정정이 아닐 경우 중복체크
            if rcp_yn == '' and rows > 0:
                print('중복 데이터가 있습니다.')
                sys.exit(0)

            # report_ver 키값 생성(개정일 + seq)
            report_ver = rcp_no[:8] + str(rows + 1).zfill(2)

            # 결의 mst 삽입
            in_qry = resolution_mst_ins(meet_tb, jm_code, report_ver, rcp_no)
            cursor.execute(in_qry)
            print(in_qry)

            # 이사선임 삽입
            if isa_arr:
                ins_isa, dup_isa = isa_mst_ins(isa_arr, meet_tb[0], jm_code, gb, report_ver)       # 이사선임
                for i in range(0, len(ins_isa)):
                    # 이사 중복 체크
                    cursor.execute(dup_isa[i])
                    dup_cnt = cursor.rowcount
                    if dup_cnt > 0:
                        print('중복된 이사가 있습니다.')
                        continue

                    cursor.execute(ins_isa[i])
                    print(str(i) + " : " + ins_isa[i])

                    if chk_no_data(isa_arr[i][4]):
                        ins_isa_car = isa_car_ins(isa_arr[i], meet_tb[0], jm_code, gb, report_ver, i)     # 이사선임_경력
                        cursor.execute(ins_isa_car)
                        print(str(i) + " : " + ins_isa_car)

                    if chk_no_data(isa_arr[i][5]):
                        ins_isa_dup = isa_dup_ins(isa_arr[i], meet_tb[0], jm_code, gb, report_ver, i)     # 이사선임_겸직
                        cursor.execute(ins_isa_dup)
                        print(str(i) + " : " + ins_isa_dup)

            # 사업목적 변경 삽입
            if biz_arr:
                for i in range(0, len(biz_arr)):
                    ins_biz = biz_ins(biz_arr, meet_tb[0], jm_code, gb, report_ver)
                    cursor.execute(ins_biz[i])
                    print(str(i) + " : " + str(ins_biz[i]))
        except:
            f = open("C:\\Users\\rmffo\\PycharmProjects\\log\\error_log.txt", 'a')
            f.write(jm_code + '\n')
            f.close()

        cursor.close()
    finally:
        close_dbcon(conn)

    # driver close
    close_driver(driver)

if __name__== "__main__":
    yy = time.strftime("%Y")

    #rcp_no_gyul, rcp_yn_gyul, rcp_gb_gyul = get_rcpNo(jm_code, '주주총회소집결의')
    get_html('20190329003006')
    #resolution_main(jm_code, rcp_no_gyul, rcp_yn_gyul, rcp_gb_gyul)
