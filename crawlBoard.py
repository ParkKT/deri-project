from builtins import print
from bs4 import BeautifulSoup

from utils import get_dbcon, close_dbcon
from utils import get_driver, close_driver
from utils import get_regYn, make_ymd, chk_no_data, get_rcpno_list, check_empty_table, get_hangul
from sql import resolution_mst_ins, isa_info_ins, isa_car_ins, isa_dup_ins, biz_ins

import sys
import time, timeit


# dart 문서번호
def get_rcpNo(jm_code, keywod):
    driver = get_driver('C:\\Users\\admin\\PycharmProjects\\webCrawl\\chromedriver.exe',
                        'http://dart.fss.or.kr/dsab002/main.do#')                                   # 드라이버 로드

    driver.find_element_by_name('textCrpNm').send_keys(jm_code)                                     # 종목코드
    driver.find_element_by_xpath('//*[@id="searchForm"]/fieldset/div/p[3]/span[2]/a[4]').click()    # 기간 : 1년
    checked = driver.find_element_by_xpath('//*[@id="finalReport"]').get_attribute('checked')       # 최종보고서 여부
    #if checked:
    #    driver.find_element_by_xpath('//*[@id="finalReport"]').click()                              # 최종보고서 체크 해제
    driver.find_element_by_id('reportName').send_keys(keywod)                                       # 검색구분 : 결의

    driver.find_element_by_xpath('//*[@id="searchForm"]/fieldset/div/p[8]/input').click()           # 검색

    res_list = driver.find_elements_by_xpath('//*[@id="listContents"]/div[1]/table/tbody/tr')       # 결과 리스트

    # 최상위 데이터만 수집 ( => 짧은 주기로 수집해야 함)
    # 결과 리스트에서 가용 데이터 추출
    if len(res_list) == 0:
        print('검색 결과가 없습니다.')
        return 0
    else:
        item = res_list[0]
        for i in range(0, len(res_list)):
            if '2018.12' in res_list[i].find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').text:
                item = res_list[i]
    # 문서번호
    rcp_no = item.find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').get_attribute('href')[-14:]
    # 기재정정
    rcp_yn = item.find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').find_element_by_tag_name('span').text

    if len(rcp_no) != 14:
        print('rcpNo 형식이 다릅니다.')
        return 0

    if '첨부' in rcp_yn:
        print('첨부정정은 수집대상 제외')
        return 0

    close_driver(driver)

    return rcp_no

# 탭 전환
def get_tab(driver, board):
    tab_list = driver.find_elements_by_xpath('//*[@id="ext-gen10"]/div/li')
    tab_no = 0
    for i in range(0, len(tab_list)):
        if '이사회등회사' in tab_list[i].text.replace(" ", ""):
            if board == 'b':
                tab_list[i].find_elements_by_tag_name('li')[0].find_element_by_tag_name('a').click()
                time.sleep(1)
            else:
                tab_list[i].find_elements_by_tag_name('li')[1].find_element_by_tag_name('a').click()
                time.sleep(1)

# 사업목적 변경 데이터
def get_board_yn(driver, board):
    board_bosang = ['보상위원회', '보수위원회', '평가보상위원회', '평가위원회', '보상심의위원회', '성과보상위원회']
    board_gamsa = ['감사위원회위원을선임하고있으', '감사위원회를운영하고있습', '감사위원회를구성하여운영하고있습', '감사위원회위원으로선임하고', '감사위원회위원의인적사항', '감사위원회의구성',
                   '감사위원회를별도로설치하고있습', '감사위원회를둔다', '감사위원회위원은', '감사위원회를설치하고있으', '감사위원회가감사업무를수행하고있습', '감사위원회를도입하였으며',
                   '감사위원회를설치하였', '감사위원회를별도로설치하고있으', '감사위원회를설치하여운영하고있으', '감사위원회를설치하여', '감사위원회위원인적사항', '감사위원회를두며',
                   '감사위원회위원의독립성', '감사위원회를별도로설치하였으며']
    board_no_gamsa = ['감사위원회를별도로설치하고있지아니', '감사위원회를별도로설치하고있지않', '감사위원회가설치되어있지않', '감사위원회는구성하고있지않', '감사위원회를설치하고있지않',
                      '감사위원회를별도로구성하고있지않', '감사위원회를별도로설치하지않', '감사위원회가설립되어있지않', '감사위원회는별도로설치하고있지아니', '감사위원회를설치하여운영하지않고']
    board_yn = 'N'

    # 주총결의 데이터 세팅
    driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))

    # 전체 텍스트
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    board_text = soup.find_all('p')

    if board == 'b':
        for line in board_text:
            for bosang in board_bosang:
                if bosang in line.text.replace(" ", ""):
                    board_yn = 'Y'
    else:
        for line in board_text:
            for gamsa in board_gamsa:
                if gamsa in line.text.replace(" ", ""):
                    board_yn = 'Y'
            for nogamsa in board_no_gamsa:
                if nogamsa in line.text.replace(" ", ""):
                    board_yn = 'N'

    return board_yn

# 결의문 전체 + DB 삽입
def report_main(jm_code, rcp_no):
    try:
        # driver 세팅(결의, 공고)
        driver = get_driver('C:\\Users\\admin\\PycharmProjects\\webCrawl\\chromedriver.exe',
                            'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={0}'.format(rcp_no))

        # 주총 결의의 rcpno 히스토리
        rcpno_list = get_rcpno_list(driver)
        # 최초 문서의 공고년도
        first_rcp_yy = rcpno_list[0][:4]

        conn = get_dbcon('esg')
        cursor = conn.cursor()

        # 보상위원회 유무 확인
        get_tab(driver, 'b')
        bosang_yn = get_board_yn(driver, 'b')
        print(bosang_yn)
        driver.switch_to_default_content()
        # 감사위원회 유무 확인
        get_tab(driver, 'g')
        gamsa_yn = get_board_yn(driver, 'g')
        print(gamsa_yn)

        # --------------------------------------------------------------------------------- #
        # DB 삽입
        # 중복체크
        insert_qry = """insert into proxy700_tmp values('{0}', '{1}', '{2}', '{3}')""".format(jm_code, '2018', bosang_yn, gamsa_yn)
        cursor.execute(insert_qry)
    finally:
        cursor.close()
        close_dbcon(conn)
        close_driver(driver)

if __name__== "__main__":
    yy = time.strftime("%Y")
    jm_code = ['069460','127120','134580','141080','016100','140410','267790','035890','159910','122800','009810','079190','089150','054450','208340','032800','009520','214270','180640','065510','030610','053260','001130','215600','298690','319400','313750','044060','120030','317030','319660','270520','317240','036460','317320','012330','001450']
    cnt = 1
    for c in jm_code:
        time.sleep(2)
        try:
            rcp_no = get_rcpNo(c, '사업보고서')
            report_main(c, rcp_no)
            print(cnt, ' : ', c)
        except:
            f = open("C:\\Users\\admin\\PycharmProjects\\log\\bosang_error_log_3.txt", 'a')
            f.write(c + '\n')
            f.close()

        cnt = cnt + 1
