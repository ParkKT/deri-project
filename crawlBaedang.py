from builtins import print
from bs4 import BeautifulSoup

from utils import get_dbcon, close_dbcon
from utils import get_driver, close_driver
from utils import get_num

import sys
import time, timeit
import re


# dart 문서번호
def get_rcpNo(jm_code, keywod, st_dt, ed_dt):
    driver = get_driver('C:\\Users\\admin\\PycharmProjects\\webCrawl\\chromedriver.exe',
                        'http://dart.fss.or.kr/dsab002/main.do#')                                   # 드라이버 로드
    driver.implicitly_wait(10)

    driver.find_element_by_name('textCrpNm').send_keys(jm_code)                                     # 종목코드
    driver.find_element_by_xpath('//*[@id="searchForm"]/fieldset/div/p[3]/span[2]/a[7]').click()    # 기간
    #driver.find_element_by_name('startDate').send_keys(st_dt)                                         # 기간_시작
    #driver.find_element_by_name('endDate').send_keys(ed_dt)                                           # 기간_종료
    driver.find_element_by_name('reportName').send_keys(keywod)                                       # 검색어
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="searchForm"]/fieldset/div/p[8]/input').click()           # 검색

    res_list = driver.find_elements_by_xpath('//*[@id="listContents"]/div[1]/table/tbody/tr')       # 결과 리스트

    # 최상위 데이터만 수집 ( => 짧은 주기로 수집해야 함)
    # 결과 리스트에서 가용 데이터 추출
    if len(res_list) == 0:
        print('검색 결과가 없습니다.')
        return 0
    else:
        item = res_list[0]

    # 문서번호
    rcp_no = item.find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').get_attribute('href')[-14:]
    # 기재정정
    rcp_yn = item.find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').find_element_by_tag_name('span').text
    # 시장구분
    rcp_gb = item.find_elements_by_tag_name('td')[5].find_element_by_tag_name('img').get_attribute('title')
    if '유가' in rcp_gb:
        rcp_gb = 'K'
    else:
        rcp_gb = 'Q'

    if len(rcp_no) != 14:
        print('rcpNo 형식이 다릅니다.')
        return 0

    if '첨부' in rcp_yn:
        print('첨부정정은 수집대상 제외')
        return 0

    close_driver(driver)

    return rcp_no

# 사업목적 변경 데이터
def get_bd_table(driver):
    # 주총결의 데이터 세팅
    driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))

    bd_gubun = ''
    bd_kind = ''
    bd_gijun_ymd = ''
    bd_gum = 0
    bd_total = 0

    # 배당금 테이블
    bd_tb = driver.find_elements_by_xpath('//*[@id="XFormD1_Form0_Table0"]/tbody/tr')
    for i in range(0, 15):
        td_title = bd_tb[i].find_elements_by_tag_name('td')[0].text.replace(' ', '')
        if '배당구분' in td_title:
            bd_gubun = bd_tb[i].find_elements_by_tag_name('td')[1].text
        if '배당종류' in td_title:
            bd_kind = bd_tb[i].find_elements_by_tag_name('td')[1].text
        if '주당배당금' in td_title:
            bd_gum = get_num(bd_tb[i].find_elements_by_tag_name('td')[2].text)
        if '배당금총액' in td_title:
            bd_total = get_num(bd_tb[i].find_elements_by_tag_name('td')[1].text)
        if '배당기준일' in td_title:
            bd_gijun_ymd = get_num(bd_tb[i].find_elements_by_tag_name('td')[1].text)

    return bd_gubun, bd_kind, bd_gum, bd_total, bd_gijun_ymd

# 결의문 전체 + DB 삽입
def bd_main(jm_code, rcp_no):
    try:
        # driver 세팅(결의, 공고)
        driver = get_driver('C:\\Users\\admin\\PycharmProjects\\webCrawl\\chromedriver.exe',
                            'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={0}'.format(rcp_no))

        driver.implicitly_wait(10)

        bd_gubun, bd_kind, bd_gum, bd_total, bd_gijun_ymd = get_bd_table(driver)

        conn = get_dbcon('esg')
        cursor = conn.cursor()

        # 중복 체크 및 DB 삽입
        dup_select = """select * from proxy080 where jm_code = '{0}' and bd_gijun_ymd = '{1}'
                     """.format(jm_code, bd_gijun_ymd)

        cursor.execute(dup_select)

        if cursor.rowcount > 0:
            insert_qry = """update proxy080
                            set bd_gubun = '{2}', bd_kind = '{3}', bd_gum = {4}, bd_total = {5}
                            where jm_code = '{0}' and bd_gijun_ymd = '{1}'
                         """.format(jm_code, bd_gijun_ymd, bd_gubun, bd_kind, bd_gum, bd_total)
        else:
            insert_qry = """insert into proxy080 values('{0}', '{1}', '{2}', '{3}', {4}, {5})
                         """.format(jm_code, bd_gijun_ymd, bd_gubun, bd_kind, bd_gum, bd_total)

        cursor.execute(insert_qry)
    finally:
        cursor.close()
        close_dbcon(conn)
        close_driver(driver)

if __name__== "__main__":
    yy = time.strftime("%Y")
    st_dt = '20180101'
    ed_dt = '20181231'
    jm_code = ['001210','002680','003470','005030','007280','008040','008110','009540','010140','011810','013990','016600','017650','018620','019170','027710','028050','030210','030720','031820','032580','033050','033250','037400','038060','042660','044780','046970','050110','053660','058220','064290','064800','067000','071970','073490','076080','080580','083650','085310','085810','088290','091340','091970','093240','096640','100030','101390','105330','105550','106520','111820','114190','114810','115530','123420','124500','137400','139050','141070','142280','151910','161570','170790','191420','214370']
    cnt = 1
    for c in jm_code:
        time.sleep(1)
        try:
            rcp_no = get_rcpNo(c, '현금ㆍ현물배당결정', st_dt, ed_dt)
            bd_main(c, rcp_no)
            print(cnt, ' : ', c)
        except:
            f = open("C:\\Users\\admin\\PycharmProjects\\log\\baedang_error_log3.txt", 'a')
            f.write(c + '\n')
            f.close()

        cnt = cnt + 1
