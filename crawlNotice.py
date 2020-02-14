from builtins import print
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException

from utils import get_dbcon, close_dbcon
from utils import get_driver, close_driver
from utils import get_notice_cont, get_contetc, get_table, get_unit, get_article, get_isa, get_bosu, get_table_sn, del_table_column, set_isa_bosu_table
from utils import get_article_code, get_num, dis_stockoption, get_bosu_edit_per, get_isa_act_head, set_isa_table, set_border_table, check_empty_table, set_transaction_table
from utils import get_rcpno_list, make_ymd, get_full_ymdstr
from financialUtil import get_table_format
from monitorUtil import set_crawl_time, get_crawl_time, get_rcplist
from ann_regul import make_angun
from sql import notice_mst_ins, act_cont_ins, act_isa_ins, isa_rt_ins, isa_border_ins, isa_comt_member_ins, isa_bosu_ins
from sql import transaction_single_ins, transaction_total_ins, finance_ins, isa_elect_ins, isa_career_ins, isa_bosuhando_ins, new_isa_bosuhando_ins
from sql import stock_list_ins, stock_method_ins, stock_extra_ins, stock_use_ins, aoi_ins, aoi_tag_ins, deri_ins
from logger import get_info_logger_nt, get_error_logger_nt

import time


# 로그
info_logger = get_info_logger_nt()
error_logger = get_error_logger_nt()
# 로딩시간
delay = 10


# 주총소집공고 내용
def get_notice_data(rcp_no, driver):
    try:
        #print('------------------------- 주총공고 -------------------------')
        # #### 주총 소집공고 목차 클릭 ####
        if '주주총회' in driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[3]/div/a').text:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[3]/div/a').click()
        else:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[2]/div/a').click()

        #WebDriverWait(driver, delay).until(expected_conditions.presence_of_element_located((By.TAG_NAME, "body")))
        driver.implicitly_wait(10)
        time.sleep(1)

        # 주총공고 참고사항
        notice_ref = driver.find_element_by_xpath('//*[@id="chamgoNoticeContents"]/table/tbody/tr/td').text
        notice_ref = notice_ref.replace("'", "")

        # 주총공고 내용 수집
        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))           # iframe 가져오기
        # 주총 구분(정기/임시)
        notice_gb = driver.find_element_by_xpath('/html/body/table/tbody/tr/td').text

        # 추후에 정기/임시/없을 경우 추가하여 구분!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if '정기' in notice_gb:
            notice_gb = '1'
        else:
            notice_gb = '2'

        body = driver.find_element_by_xpath('/html/body')
        cont = body.find_elements_by_tag_name('p')

        notice_tb = [0 for x in range(6)]
        notice_tb[0] = get_notice_cont(0, cont).strip()  # 일자
        notice_tb[1] = get_notice_cont(1, cont).strip()  # 시간
        notice_tb[2] = get_notice_cont(2, cont).strip()  # 장소
        notice_tb[3] = get_notice_cont(3, cont).strip()  # 회의목적사항
        notice_tb[4] = get_notice_cont(4, cont).strip()  # 기타 공고사항
        notice_tb[5] = notice_ref
        # ########################### 4번 사항 수집 시, 패턴 추가 필요
        etc_cont = get_contetc(notice_tb[4])

        info_logger.info('[1] Announcement information success.')

        return notice_gb, notice_tb, notice_ref, ''
    except Exception as e:
        error_logger.error('[1] Announcement information fail. [{0}] : {1}'.format(rcp_no, e))


# 사외이사 활동내역
def get_isa_act(driver, meet_seq, rcp_no, cursor):
    try:
        #print('------------------------- 이사 및 위원회 활동내역 -------------------------')
        # #### 사외이사 활동내역 목차 클릭 ####
        if '사외이사' in driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[3]/div/a').text:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[3]/ul/li[1]/div/a').click()
        else:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[4]/ul/li[1]/div/a').click()

        time.sleep(1)

        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))           # iframe 가져오기
        # 활동내역 표 개수
        body = driver.find_element_by_xpath('/html/body')
        tables = body.find_elements_by_tag_name('table')

        # 사외이사 활동내역
        isa_num = set_isa_table(tables)
        isa_cnt = 0
        if len(isa_num) > 0:
            for isa in isa_num:
                head_arr, head_arr_raw, is_gagyul = get_isa_act_head(tables[isa])
                isa_tb = get_table_sn(tables[isa])      # 표 정리
                if check_empty_table(isa_tb) == 0:
                    continue
                isa_act_db(meet_seq, rcp_no, head_arr, head_arr_raw, is_gagyul, isa_tb, cursor)    # db
                isa_cnt = isa_cnt + 1
        else:
            isa_cnt = 0

        # 위원회 활동내역
        border_num = set_border_table(tables)
        border_cnt = 0
        if len(border_num) > 0:
            for border in border_num:
                border_tb = get_table_sn(tables[border])    # 표 정리
                if check_empty_table(border_tb) == 0:
                    continue
                border_act_db(meet_seq, rcp_no, border_tb, cursor)     # db
                border_cnt = border_cnt + 1
        else:
            border_cnt = 0

        info_logger.info('[2] Nonexecutive director success.')
        info_logger.info('[2] Nonexecutive director table count[{0}] | border table count[{1}]'.format(isa_cnt, border_cnt))
    except Exception as e:
        error_logger.error('[2] Nonexecutive director fail. [{0}] : {1}'.format(rcp_no, e))

def isa_act_db(meet_seq, rcp_no, head_arr, head_arr_raw, is_gagyul, isa_tb, cursor):
    agno = 1    # 안건번호
    del_columns = []    # 불필요한 열 삭제
    if head_arr_raw:
        for i in range(0, len(head_arr_raw)):
            if 'no' in head_arr_raw[i].lower():     # 불필요 열 case1 : No
                del_columns.append(i)

    # 불필요 열 삭제
    for col in del_columns:
        del head_arr_raw[col]
        del head_arr[col]
    del_table_column(isa_tb, del_columns)
    # 헤드라인 표 정리
    headline = " ".join(head_arr_raw)
    if '의안' in headline:
        if is_gagyul == 1:
            head_arr_raw = head_arr_raw[4:]
            head_arr = head_arr[4:]
        else:
            head_arr_raw = head_arr_raw[3:]
            head_arr = head_arr[3:]

    # 출석률
    arr_rt = []
    if head_arr_raw:
        for i in range(0, len(head_arr_raw)):
            arr_rt.append(head_arr_raw[i])

    if isa_tb:
        for i in range(0, len(isa_tb)):
            if i != 0:
                if isa_tb[i][1] == isa_tb[i - 1][1]:
                    agno = agno + 1
                else:
                    agno = 1
            # 이사회 안건
            c_qry = act_cont_ins(isa_tb[i], meet_seq, rcp_no, agno, is_gagyul)
            cursor.execute(c_qry)

            # 사외이사 활동내역 & 출석률
            if head_arr:
                for j in range(0, len(head_arr)):
                    # 출석률
                    if i == 0:
                        rt_qry = isa_rt_ins(meet_seq, rcp_no, arr_rt[j], j, head_arr[j])
                        cursor.execute(rt_qry)
                    # 활동내역
                    h_qry = act_isa_ins(head_arr[j], isa_tb[i], meet_seq, rcp_no, agno, j, is_gagyul)
                    cursor.execute(h_qry)

def border_act_db(meet_seq, rcp_no, border_tb, cursor):
    if border_tb:
        # 위원회 위원
        border_isa = []

        # 개최 순번
        hold_seq = 1
        for i in range(0, len(border_tb)):
            if i == 0:
                tmp = [border_tb[i][0], border_tb[i][1]]
                border_isa.append(tmp)
            else:
                if border_tb[i][2] == border_tb[i - 1][2]:
                    hold_seq = hold_seq + 1
                else:
                    hold_seq = 1

                if border_tb[i][0] != border_tb[i - 1][0]:
                    tmp = [border_tb[i][0], border_tb[i][1]]
                    border_isa.append(tmp)

            border_qry = isa_border_ins(border_tb[i], meet_seq, rcp_no, hold_seq)
            cursor.execute(border_qry)

        for border, isas in border_isa:
            isa = isas.replace("\n", ",").split(",")
            for i in range(0, len(isa)):
                border_mem_qry = isa_comt_member_ins([border, isa[i]], meet_seq, rcp_no, i)
                cursor.execute(border_mem_qry)


# 사외이사 보수현황
def get_isa_bosu(driver, meet_seq, rcp_no, cursor):
    try:
        #print('------------------------- 사외이사보수 -------------------------')
        # #### 사외이사 보수 목차 클릭 ####
        if '사외이사' in driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[3]/div/a').text:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[3]/ul/li[2]/div/a').click()
        else:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[4]/ul/li[2]/div/a').click()

        time.sleep(1)

        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))  # iframe 가져오기
        # 이사보수현황 테이블
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')

        # 이사보수현황
        isa_bosu_num = set_isa_bosu_table(tables)
        isa_bosu_cnt = 0
        if len(isa_bosu_num) > 0:
            # 단위
            if isa_bosu_num[0] > 0:
                bosu_unit = get_unit(tables[0].text)
            else:
                bosu_unit = '원'

            for bosu in isa_bosu_num:
                num_arr = [1, 2, 3, 4]
                isa_bosu_tb = get_bosu_edit_per(get_table(tables[bosu]), num_arr)
                if check_empty_table(isa_bosu_tb) == 0:
                    continue
                isa_bosu_db(meet_seq, rcp_no, isa_bosu_tb, bosu_unit, cursor)
                isa_bosu_cnt = isa_bosu_cnt + 1
        else:
            isa_bosu_cnt = 0

        info_logger.info('[3] directors pay success.')
        info_logger.info('[3] directors pay table count[{0}]'.format(isa_bosu_cnt))
    except Exception as e:
        error_logger.error('[3] directors pay fail. [{0}] : {1}'.format(rcp_no, e))

def isa_bosu_db(meet_seq, rcp_no, isa_bosu, bosu_unit, cursor):
    if isa_bosu:
        for i in range(0, len(isa_bosu)):
            isa_bosu_qry = isa_bosu_ins(isa_bosu[i], meet_seq, rcp_no, bosu_unit)
            cursor.execute(isa_bosu_qry)


# 최대주주등과의 거래내역_단일 거래규모가 일정규모 이상인 거래
def get_transaction_single(driver, meet_seq, rcp_no, cursor):
    try:
        #print('------------------------- 단일 거래규모 일정규모 이상 거래 -------------------------')
        # #### 최대주주등과의 거래내역 목차 클릭 ####
        if '최대주주' in driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[4]/div/a').text:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[4]/ul/li[1]/div/a').click()
        else:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[5]/ul/li[1]/div/a').click()

        time.sleep(1)

        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))  # iframe 가져오기
        # 테이블 개수
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')

        # 단일거래
        trans_single_num = set_transaction_table(tables)
        trans_single_cnt = 0
        if len(trans_single_num) > 0:
            # 단위
            if trans_single_num[0] > 0:
                trans_unit = get_unit(tables[0].text)
            else:
                trans_unit = '원'

            for trans in trans_single_num:
                num_arr = [3, 4]
                trans_tb = get_bosu_edit_per(get_table(tables[trans]), num_arr)
                if check_empty_table(trans_tb) == 0:
                    continue
                tans_single_db(meet_seq, rcp_no, trans_unit, trans_tb, cursor)
                trans_single_cnt = trans_single_cnt + 1
        else:
            trans_single_cnt = 0

        info_logger.info('[4] single transaction success.')
        info_logger.info('[4] single transaction table count[{0}]'.format(trans_single_cnt))
    except Exception as e:
        error_logger.error('[4] single transaction fail. [{0}] : {1}'.format(rcp_no, e))

def tans_single_db(meet_seq, rcp_no, transaction_unit, transaction_single, cursor):
    if transaction_single:
        for i in range(0, len(transaction_single)):
            transaction_single_qry = transaction_single_ins(transaction_single[i], meet_seq, rcp_no, transaction_unit, i)
            cursor.execute(transaction_single_qry)


# 최대주주등과의 거래내역_해당 사업연도중에 특정인과 해당 거래를 포함한 거래총액이 일정규모이상인 거래
def get_transaction_total(driver, meet_seq, rcp_no, cursor):
    try:
        #print('------------------------- 거래총액 일정규모 이상 거래 -------------------------')
        # #### 최대주주등과의 거래내역 목차 클릭 ####
        if '최대주주' in driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[4]/div/a').text:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[4]/ul/li[2]/div/a').click()
        else:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[5]/ul/li[2]/div/a').click()

        time.sleep(1)

        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))  # iframe 가져오기
        # 테이블
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')

        # 거래총액
        trans_total_num = set_transaction_table(tables)
        trans_total_cnt = 0
        if len(trans_total_num) > 0:
            # 단위
            if trans_total_num[0] > 0:
                trans_unit = get_unit(tables[0].text)
            else:
                trans_unit = '원'

            for trans in trans_total_num:
                num_arr = [3, 4]
                trans_tb = get_bosu_edit_per(get_table(tables[trans]), num_arr)
                if check_empty_table(trans_tb) == 0:
                    continue
                trans_total_db(meet_seq, rcp_no, trans_unit, trans_tb, cursor)
                trans_total_cnt = trans_total_cnt + 1
        else:
            trans_total_cnt = 0

        info_logger.info('[5] total transaction success.')
        info_logger.info('[5] total transaction table count[{0}]'.format(trans_total_cnt))
    except Exception as e:
        error_logger.error('[5] total transaction fail. [{0}] : {1}'.format(rcp_no, e))

def trans_total_db(meet_seq, rcp_no, transaction_unit2, transaction_total, cursor):
    if transaction_total:
        for i in range(0, len(transaction_total)):
            transaction_total_qry = transaction_total_ins(transaction_total[i], meet_seq, rcp_no, transaction_unit2, i)
            cursor.execute(transaction_total_qry)


# 주총 재무제표
def get_financial_table(driver, meet_seq, rcp_no, cursor):
    try:
        #print('------------------------- 재무제표 -------------------------')
        # #### 주총 목적사항별 기재사항 목차 클릭 ####
        if '경영참고' in driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[5]/div/a').text:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[5]/ul/li[2]/div/a').click()
        else:
            driver.find_element_by_xpath('//*[@id="ext-gen10"]/div/li[6]/ul/li[2]/div/a').click()

        time.sleep(1)

        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))  # iframe 가져오기
        # 재무상태표, 포괄손익계산서, 현금흐름표
        (con_balance_df, con_income_df, con_cashflow_df, sep_balance_df, sep_income_df, sep_cashflow_df,
         con_balance_unit, con_income_unit, con_cashflow_unit, sep_balance_unit, sep_income_unit, sep_cashflow_unit) = get_table_format(driver)

        #print('---------- 연결재무상태표 ----------')
        con_bal_col = con_balance_df.index
        con_bal_tb = con_balance_df.values
        #con_bal_tb = set_num(con_bal_tb)
        if len(con_bal_col) != len(con_bal_tb):
            con_bal_col = []
            con_bal_tb = []
        fin_loop(meet_seq, rcp_no, con_bal_tb, con_bal_col, con_balance_unit, 1, 1, cursor)
        #if con_bal_tb.all():
        #    print('테이블 없을 경우 status 확인')

        #print('---------- 연결손익계산서 ----------')
        con_inc_tot_col = con_income_df.index
        con_inc_tot_tb = con_income_df.values
        #con_inc_tot_tb = set_num(con_inc_tot_tb)
        if len(con_inc_tot_col) != len(con_inc_tot_tb):
            con_inc_tot_col = []
            con_inc_tot_tb = []
        fin_loop(meet_seq, rcp_no, con_inc_tot_tb, con_inc_tot_col, con_income_unit, 1, 2, cursor)

        #print('---------- 연결현금흐름표 ----------')
        con_cashflow_col = con_cashflow_df.index
        con_cashflow_tb = con_cashflow_df.values
        #con_cashflow_tb = set_num(con_cashflow_tb)
        if len(con_cashflow_col) != len(con_cashflow_tb):
            con_cashflow_col = []
            con_cashflow_tb = []
        fin_loop(meet_seq, rcp_no, con_cashflow_tb, con_cashflow_col, con_cashflow_unit, 1, 3, cursor)

        #print('---------- 개별재무상태표 ----------')
        sep_bal_col = sep_balance_df.index
        sep_bal_tb = sep_balance_df.values
        #sep_bal_tb = set_num(sep_bal_tb)
        if len(sep_bal_col) != len(sep_bal_tb):
            sep_bal_col = []
            sep_bal_tb = []
        fin_loop(meet_seq, rcp_no, sep_bal_tb, sep_bal_col, sep_balance_unit, 2, 1, cursor)

        #print('---------- 개별손익계산서 ----------')
        sep_inc_tot_col = sep_income_df.index
        sep_inc_tot_tb = sep_income_df.values
        #sep_inc_tot_tb = set_num(sep_inc_tot_tb)
        if len(sep_inc_tot_col) != len(sep_inc_tot_tb):
            sep_inc_tot_col = []
            sep_inc_tot_tb = []
        fin_loop(meet_seq, rcp_no, sep_inc_tot_tb, sep_inc_tot_col, sep_income_unit, 2, 2, cursor)

        #print('---------- 개별현금흐름표 ----------')
        sep_cashflow_col = sep_cashflow_df.index
        sep_cashflow_tb = sep_cashflow_df.values
        #sep_cashflow_tb = set_num(sep_cashflow_tb)
        if len(sep_cashflow_col) != len(sep_cashflow_tb):
            sep_cashflow_col = []
            sep_cashflow_tb = []
        fin_loop(meet_seq, rcp_no, sep_cashflow_tb, sep_cashflow_col, sep_cashflow_unit, 2, 3, cursor)

        info_logger.info('[6] financial statement success.')
    except Exception as e:
        error_logger.error('[6] financial statement fail. [{0}] : {1}'.format(rcp_no, e))

def fin_loop(meet_seq, rcp_no, fin_tb, fin_col_tb, fin_unit, con_gb, finance_gb, cursor):
    for i in range(0, len(fin_tb)):
        for j in range(1, 3):
            fin_qry = finance_ins(fin_tb[i], fin_col_tb[i], meet_seq, rcp_no, fin_unit, i, con_gb, finance_gb, j)
            cursor.execute(fin_qry)


# 정관변경의 건
def get_change_article(driver, meet_seq, rcp_no, cursor):
    try:
        #print('------------------------- 정관의 변경 -------------------------')
        # 정관 변경(j:집중투표제 표, e:그외 표)
        try:
            jipjung_tb, jipjung_tb_tag, etc_tb, etc_tb_tag = get_article(driver)
        except:
            jipjung_tb = []
            jipjung_tb_tag = []
            etc_tb = []
            etc_tb_tag = []

        code_j_tb = get_article_code(jipjung_tb)
        code_e_tb = get_article_code(etc_tb)

        if check_empty_table(jipjung_tb) != 0:
            jipjung_aoi_db(meet_seq, rcp_no, jipjung_tb, jipjung_tb_tag, cursor)
        if check_empty_table(etc_tb) != 0:
            etc_aoi_db(meet_seq, rcp_no, etc_tb, etc_tb_tag, cursor)

        info_logger.info('[7] chagne article of incorporation success.')
    except Exception as e:
        error_logger.error('[7] chagne article of incorporation fail. [{0}] : {1}'.format(rcp_no, e))

def jipjung_aoi_db(meet_seq, rcp_no, jipjung_tb, jipjung_tb_tag, cursor):
    if jipjung_tb:
        for i in range(0, len(jipjung_tb)):
            jipjung_aoi_qry = aoi_ins(jipjung_tb[i], meet_seq, rcp_no, i, 1)
            cursor.execute(jipjung_aoi_qry)

    if jipjung_tb_tag:
        for i in range(0, len(jipjung_tb_tag)):
            jipjung_aoi_qry = aoi_tag_ins(jipjung_tb_tag[i], meet_seq, rcp_no, i, 1)
            cursor.execute(jipjung_aoi_qry)

def etc_aoi_db(meet_seq, rcp_no, etc_tb, etc_tb_tag, cursor):
    if etc_tb:
        for i in range(0, len(etc_tb)):
            etc_aoi_qry = aoi_ins(etc_tb[i], meet_seq, rcp_no, i, 2)
            cursor.execute(etc_aoi_qry)

    if etc_tb_tag:
        for i in range(0, len(etc_tb_tag)):
            etc_aoi_qry = aoi_tag_ins(etc_tb_tag[i], meet_seq, rcp_no, i, 2)
            cursor.execute(etc_aoi_qry)


# 이사선임의 건
def get_elect_isa(driver, meet_seq, rcp_no, cursor):
    try:
        #print('------------------------- 이사선임 -------------------------')
        # 이사선임
        isa_tb, car_tb, job_is_new = get_isa(driver)
        elect_isa_db(meet_seq, rcp_no, isa_tb, cursor)
        career_isa_db(meet_seq, rcp_no, car_tb, job_is_new, cursor)

        info_logger.info('[8] director election success.')
    except Exception as e:
        error_logger.error('[8] director election fail. [{0}] : {1}'.format(rcp_no, e))

def elect_isa_db(meet_seq, rcp_no, isa_tb, cursor):
    if isa_tb:
        for i in range(0, len(isa_tb)):
            isa_elect_qry = isa_elect_ins(isa_tb[i], meet_seq, rcp_no, i)
            cursor.execute(isa_elect_qry)

def career_isa_db(meet_seq, rcp_no, car_tb, job_is_new, cursor):
    if car_tb:
        for i in range(0, len(car_tb)):
            isa_carrer_qry = isa_career_ins(car_tb[i], meet_seq, rcp_no, job_is_new, i)
            cursor.execute(isa_carrer_qry)


# 보수한도의 건
def get_limit_bosu(driver, meet_seq, rcp_no, cursor):
    try:
        #print('------------------------- 이사보수한도 -------------------------')
        # 이사보수한도
        isa_bosu_tb, gamsa_bosu_tb, isa_bosu_unit, gamsa_bosu_unit, isa_chk_first, gamsa_chk_first, is_new = get_bosu(driver)
        if is_new:
            if isa_bosu_tb:
                isa_bosu_limit_db_new(meet_seq, rcp_no, isa_bosu_tb, isa_bosu_unit, cursor)
            if gamsa_bosu_tb:
                gamsa_bosu_limit_db_new(meet_seq, rcp_no, gamsa_bosu_tb, gamsa_bosu_unit, cursor)
        else:
            if isa_bosu_tb:
                isa_bosu_limit_db(meet_seq, rcp_no, isa_bosu_tb, isa_bosu_unit, isa_chk_first, cursor)
            if gamsa_bosu_tb:
                gamsa_bosu_limit_db(meet_seq, rcp_no, gamsa_bosu_tb, gamsa_bosu_unit, gamsa_chk_first, cursor)

        info_logger.info('[9] pay limit success.')
    except Exception as e:
        error_logger.error('[9] pay limit fail. [{0}] : {1}'.format(rcp_no, e))

def isa_bosu_limit_db(meet_seq, rcp_no, isa_bosu_tb, isa_bosu_unit, isa_chk_first, cursor):
    # 보수한도 행렬 전치
    i_bosu_tb = pd.DataFrame(isa_bosu_tb).T
    i_bosu_tb = i_bosu_tb.values.tolist()[1:]

    # 보수한도 당기/전기 순서 정렬
    if isa_chk_first == 1:
        tmp = i_bosu_tb[0]
        i_bosu_tb[0] = i_bosu_tb[1]
        i_bosu_tb[1] = tmp

    if isa_bosu_tb:
        for i in range(0, len(i_bosu_tb)):
            isa_bosuhando_qry = isa_bosuhando_ins(i_bosu_tb[i], meet_seq, rcp_no, isa_bosu_unit, i, 1)
            cursor.execute(isa_bosuhando_qry)

def gamsa_bosu_limit_db(meet_seq, rcp_no, gamsa_bosu_tb, gamsa_bosu_unit, gamsa_chk_first, cursor):
    # 보수한도 행렬 전치
    g_bosu_tb = pd.DataFrame(gamsa_bosu_tb).T
    g_bosu_tb = g_bosu_tb.values.tolist()[1:]

    # 보수한도 당기/전기 순서 정렬
    if gamsa_chk_first == 1:
        tmp = g_bosu_tb[0]
        g_bosu_tb[0] = g_bosu_tb[1]
        g_bosu_tb[1] = tmp

    if gamsa_bosu_tb:
        for i in range(0, len(g_bosu_tb)):
            gamsa_bosuhando_qry = isa_bosuhando_ins(g_bosu_tb[i], meet_seq, rcp_no, gamsa_bosu_unit, i, 2)
            cursor.execute(gamsa_bosuhando_qry)

def isa_bosu_limit_db_new(meet_seq, rcp_no, isa_bosu_tb, isa_bosu_unit, cursor):
    # 보수한도 테이블 구분
    jun_bosu_tb = []
    dang_bosu_tb = []
    for isa in isa_bosu_tb:
        if isa[2] == '1':
            dang_bosu_tb.append(isa)
        else:
            jun_bosu_tb.append(isa)

    if dang_bosu_tb:
        dang_bosu_tb = pd.DataFrame(dang_bosu_tb).T.values.tolist()[1]
        dang_bosu_tb.insert(2, '0')
        isa_bosuhando_qry = new_isa_bosuhando_ins(dang_bosu_tb, meet_seq, rcp_no, isa_bosu_unit, 1, 1)
        cursor.execute(isa_bosuhando_qry)
    if jun_bosu_tb:
        jun_bosu_tb = pd.DataFrame(jun_bosu_tb).T.values.tolist()[1]
        isa_bosuhando_qry = new_isa_bosuhando_ins(jun_bosu_tb, meet_seq, rcp_no, isa_bosu_unit, 1, 2)
        cursor.execute(isa_bosuhando_qry)

def gamsa_bosu_limit_db_new(meet_seq, rcp_no, gamsa_bosu_tb, gamsa_bosu_unit, cursor):
    # 보수한도 테이블 구분
    jun_bosu_tb = []
    dang_bosu_tb = []
    for gamsa in gamsa_bosu_tb:
        if gamsa[2] == '1':
            dang_bosu_tb.append(gamsa)
        else:
            jun_bosu_tb.append(gamsa)

    if dang_bosu_tb:
        dang_bosu_tb = pd.DataFrame(dang_bosu_tb).T.values.tolist()[1]
        dang_bosu_tb.insert(1, '0')
        dang_bosu_tb.insert(2, '0')
        gamsa_bosuhando_qry = new_isa_bosuhando_ins(dang_bosu_tb, meet_seq, rcp_no, gamsa_bosu_unit, 2, 1)
        cursor.execute(gamsa_bosuhando_qry)
    if jun_bosu_tb:
        jun_bosu_tb = pd.DataFrame(jun_bosu_tb).T.values.tolist()[1]
        jun_bosu_tb.insert(1, '0')
        gamsa_bosuhando_qry = new_isa_bosuhando_ins(jun_bosu_tb, meet_seq, rcp_no, gamsa_bosu_unit, 2, 2)
        cursor.execute(gamsa_bosuhando_qry)


# 주식매수선택권
def get_stockoption(driver, meet_seq, rcp_no, cursor):
    try:
        #print('------------------------- 주식매수선택권 -------------------------')
        person_arr, method_arr, extra_stock_arr, use_stock_arr = dis_stockoption(driver)
        # 부여받을 자의 성명 등
        if person_arr:
            for i in range(0, len(person_arr)):
                person_arr[i][4] = get_num(person_arr[i][4])

        stockoption_db(meet_seq, rcp_no, person_arr, method_arr, extra_stock_arr, use_stock_arr, cursor)

        info_logger.info('[10] stock option success.')
    except Exception as e:
        error_logger.error('[10] stock option fail. [{0}] : {1}'.format(rcp_no, e))

def stockoption_db(meet_seq, rcp_no, stock_person, stock_method, stock_extra, stock_use, cursor):
    # 테이블 행렬 전치
    stock_method = pd.DataFrame(stock_method).T
    stock_method = stock_method.values.tolist()[1:]

    if stock_person:
        for i in range(0, len(stock_person)):
            stock_person_list_qry = stock_list_ins(stock_person[i], meet_seq, rcp_no, i)
            cursor.execute(stock_person_list_qry)

    if stock_method:
        for i in range(0, len(stock_method)):
            method_list_qry = stock_method_ins(stock_method[i], meet_seq, rcp_no, i)
            cursor.execute(method_list_qry)

    if stock_extra:
        for i in range(0, len(stock_extra)):
            stock_extra_qry = stock_extra_ins(stock_extra[i], meet_seq, rcp_no)
            cursor.execute(stock_extra_qry)

    if stock_use:
        for i in range(0, len(stock_use)):
            stock_use_qry = stock_use_ins(stock_use[i], meet_seq, rcp_no)
            cursor.execute(stock_use_qry)

# 공고 수집
def get_notice(jm_code, rcp_no, cursor):
    try:
        # driver 세팅
        driver = get_driver('C:\\Users\\admin\\PycharmProjects\\webCrawl\\chromedriver.exe',
                            'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={0}'.format(rcp_no))

        # 주총 공고의 rcpno 히스토리
        rcpno_list = get_rcpno_list(driver)
        # 최초 문서의 공고년도
        first_rcp_no = rcpno_list[0]
        first_rcp_yy = first_rcp_no[:4]
        # 이전 rcp_no
        pre_rcp_no = ''
        for i in range(0, len(rcpno_list)):
            if rcp_no == rcpno_list[i] and i > 0:
                pre_rcp_no = rcpno_list[i - 1]
                break
        print(rcpno_list, pre_rcp_no)
        # ------------------------- 주총공고 -------------------------
        try:
            notice_gb, notice_tb, notice_ref, notice_etc = get_notice_data(rcp_no, driver)

            # 중복체크
            dup_select = """select * from proxy011 where rcp_no = '{0}'""".format(rcp_no)
            cursor.execute(dup_select)
            dup_cnt = cursor.rowcount
            if dup_cnt > 0:
                return 0

            res_rcpno = ''
            # 결의문 rcpno 가져오기
            if len(notice_tb[0]) == 8:
                res_select = """select first_rcpno from proxy001 where jm_code = '{0}' and meet_ymd = '{1}' and meet_gb = '{2}' and meet_time = '{3}'
                             """.format(jm_code, notice_tb[0], notice_gb, notice_tb[1])

                cursor.execute(res_select)
                if cursor.rowcount > 0:
                    res_rcpno = cursor.fetchone()[0]

            # 회차 max 값
            max_select = """select * from proxy011 where left(first_rcpno, 4) = '{0}' and jm_code = '{1}' group by meet_seq
                         """.format(first_rcp_yy, jm_code)

            cursor.execute(max_select)
            max_seq = cursor.rowcount

            # meet_seq 생성
            seq_select = """select meet_seq from proxy011 where first_rcpno = '{0}'
                         """.format(first_rcp_no)

            cursor.execute(seq_select)
            seq = cursor.fetchone()

            if cursor.rowcount < 1:
                seq = str(max_seq + 1).zfill(2)
            else:
                seq = "".join(seq)
                seq = seq[-2:]

            yyyy = make_ymd(notice_tb[0])
            if yyyy is not None and yyyy != '':
                yyyy = yyyy[:4]
            else:
                yyyy = time.strftime('%Y')

            meet_seq = jm_code + yyyy + seq

            notice_qry = notice_mst_ins(meet_seq, rcp_no, jm_code, notice_gb, rcpno_list[0], notice_tb, notice_ref, res_rcpno)
            cursor.execute(notice_qry)

            # crawling to deri
            ymdstr = get_full_ymdstr(notice_tb[0], notice_tb[1])
            deri_qry = deri_ins(meet_seq, rcp_no, pre_rcp_no, jm_code, notice_tb[0], notice_gb, ymdstr, notice_tb[2])
            cursor.execute(deri_qry)

            driver.switch_to_default_content()

            info_logger.info('[0] Key creation success.')
        except Exception as e:
            error_logger.error('[0] Key creation fail. [{0}] : {1}'.format(rcp_no, e))

        # ------------------------- 이사 및 위원회 활동내역 -------------------------
        get_isa_act(driver, meet_seq, rcp_no, cursor)
        driver.switch_to_default_content()

        # ------------------------- 사외이사보수 -------------------------
        get_isa_bosu(driver, meet_seq, rcp_no, cursor)
        driver.switch_to_default_content()

        # ------------------------- 단일 거래규모 일정규모 이상 거래 -------------------------
        get_transaction_single(driver, meet_seq, rcp_no, cursor)
        driver.switch_to_default_content()

        # ------------------------- 거래총액 일정규모 이상 거래 -------------------------
        get_transaction_total(driver, meet_seq, rcp_no, cursor)
        driver.switch_to_default_content()

        # ------------------------- 재무제표 -------------------------
        get_financial_table(driver, meet_seq, rcp_no, cursor)

        # ------------------------- 정관의 변경 -------------------------
        get_change_article(driver, meet_seq, rcp_no, cursor)

        # ------------------------- 이사선임 -------------------------
        get_elect_isa(driver, meet_seq, rcp_no, cursor)

        # ------------------------- 이사보수한도 -------------------------
        get_limit_bosu(driver, meet_seq, rcp_no, cursor)

        # ------------------------- 주식매수선택권 -------------------------
        get_stockoption(driver, meet_seq, rcp_no, cursor)

    except Exception as e:
        error_logger.error('[Notice] crawling fail. [{0}] : {1}'.format(rcp_no, e))
    finally:
        close_driver(driver)

# 주총공고수집
def notice_main(conn):
    start_time = get_crawl_time('N')
    end_time = start_time

    #rcpnos = get_rcplist(start_time, 'N')
    #rcpnos = [['054630', '주주총회소집공고', '20200210000239', '20200205101010', 'K'], ['114090', '주주총회소집공고', '20200211000292', '20200205101011', 'Y'], ['263540', '주주총회소집공고', '20200211000229', '20200205101012', 'K'], ['004310', '주주총회소집공고', '20200131000566', '20200205101015', 'Y']]
    rcpnos = [['054630', '주주총회소집공고', '20200207000341', '20200205101011', 'K']]

    for rcpno in rcpnos:
        info_logger.info('---------- rcp_no : [{0}] ----------'.format(rcpno[2]))
        cursor = conn.cursor()

        get_notice(rcpno[0], rcpno[2], cursor)
        end_time = rcpno[3]
        conn.commit()

        # 안건 분리(by 민철)
        make_angun(rcpno[2])

        cursor.close()
        time.sleep(1)

    set_crawl_time(end_time, 'N')


if __name__ == "__main__":
    conn = get_dbcon('esg')
    notice_main(conn)
    close_dbcon(conn)
