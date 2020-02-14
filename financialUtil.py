import re
from builtins import print

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

from utils import get_unit


def get_table_format(driver):
    # 재무제표 표별 패턴
    re_income_find1 = re.compile("법[ \s]*인[ \s]*세[ \s]*비[ \s]*용(\(이익\))*[ \s]*차[ \s]*감[ \s]*전[ \s]*순[ \s]*((이[ \s]*익)|(손[ \s]*실))|법[ \s]*인[ \s]*세[ \s]*차[ \s]*감[ \s]*전[ \s]*계[ \s]*속[ \s]*영[ \s]*업[ \s]*순[ \s]*이[ \s]*익|법인세[ \s]*차감전[ \s]*순이익|법인세차감전계속영업이익|법인세비용차감전이익|법인세비용차감전계속영업[순]*이익|법인세비용차감전당기순이익|법인세(비용차감|손익가감)전순이익|법인세비용차감전[ \s]*계속사업이익|법인세비용차감전순손익|[ \s]*기[ \s]*본[ \s]*주[ \s]*당[ \s]*이[ \s]*익[ \s]")
    re_income_find2 = re.compile("영[ \s]*업[ \s]*수[ \s]*익|수[ \s]*익[ \s]*매[ \s]*출[ \s]*액[ \s]|매[ \s]*출[ \s]*액[ \s]|매[ \s]*출[ \s]|매[ \s]*출[ \s]*및[ \s]*지[ \s]*분[ \s]*법[ \s]*손[ \s]*익[ \s]|매[ \s]*출[ \s]*총[ \s]*이[ \s]*익[ \s]|영[ \s]*업[ \s]*이[ \s]*익")

    re_cashflow_find1 = re.compile("영업활동[ \s]*현금[ \s]*흐름|영업활동으로[ \s]*인한[ \s]*[순]*현금[ \s]*흐름|영업활동으로부터의[ \s]*현금흐름|영업활동으로 인한 자산부채의 변동|영[ \s]*업[ \s]*에[ \s]*서[ \s]*창[ \s]*출[ \s]*된[ \s]*현[ \s]*금[ \s]|영업활동으로 인한 현금흐름")
    re_cashflow_find2 = re.compile("당[ \s]*기[ \s]*말[ \s]*의[ \s]*현[ \s]*금[ \s]|당[ \s]*기[ \s]*말[ \s]*의[ \s]*현[ \s]*금[ \s]*및[ \s]*현[ \s]*금[ \s]*성[ \s]*자[ \s]*산[ \s]|당[ \s]*기[ \s]*말[ \s]*현[ \s]*금[ \s]*및[ \s]*현[ \s]*금[ \s]*성[ \s]*자[ \s]*산[ \s]|기[ \s]*말[ \s]*현[ \s]*금|기[ \s]*말[ \s]*의[ \s]*현[ \s]*금[ \s]*및[ \s]*현[ \s]*금[ \s]*성[ \s]*자[ \s]*산[ \s]|기[ \s]*말[ \s]*의[ \s]*현[ \s]*금|기[ \s]*말[ \s]*현[ \s]*금[ \s]*및[ \s]*현[ \s]*금[ \s]*성[ \s]*자[ \s]*산[ \s]|기[ \s]*말[ \s]*의[ \s]*현[ \s]*금[ \s]")
    # re_cashflow_find3 = re.compile("법[ \s]*인[ \s]*세[ \s]*지[ \s]*급|배[ \s]*당[ \s]*금[ \s]*수[ \s]*취|배[ \s]*당[ \s]*금[ \s]*수[ \s]*입|법[ \s]*인[ \s]*세[ \s]*납[ \s]*부[ \s]*액|법[ \s]*인[ \s]*세[ \s]*의[ \s]*지[ \s]*급|법[ \s]*인[ \s]*세[ \s]*의[ \s]*납[ \s]*부|법[ \s]*인[ \s]*세[ \s]*납[ \s]*부|이[ \s]*자[ \s]*의[ \s]*수[ \s]*취")

    re_balance_sheet_find1 = re.compile("현[ \s]*금[ \s]*및[ \s]*현[ \s]*금[ \s]*((성[ \s]*자[ \s]*산)|(등[ \s]*가[ \s]*물))|현[ \s]*금[ \s]*및[ \s]*예[ \s]*치[ \s]*금[ \s]")
    # re_balance_sheet_find = re.compile("유[ \s]*동[ \s]*부[ \s]*채|부[ \s]*채[ \s]*총[ \s]*계[ \s]")
    re_balance_sheet_find2 = re.compile("총[ \s]*자[ \s]*산[ \s]|자[ \s]*산[ \s]*총[ \s]*계|자[ \s]*산[ \s]*계[ \s]|자[ \s]*산[ \s]*총[ \s]*액|자[ \s]*산[ \s]*합[ \s]*계")
    re_balance_sheet_find3 = re.compile("부[ \s]*채[ \s]*합[ \s]*계[ \s]|부[ \s]*채[ \s]*총[ \s]*액[ \s]|부[ \s]*채[ \s]*계[ \s]|부[ \s]*채[ \s]*총[ \s]*계[ \s]|총[ \s]*부[ \s]*채[ \s]")

    re_balance_sheet_find4 = re.compile("자[ \s]*본[ \s]*총[ \s]*계[ \s]|자[ \s]*본[ \s]*총[ \s]*액[ \s]|총[ \s]*자[ \s]*본[ \s]|자[ \s]*본[ \s]*계[ \s]|자[ \s]*본[ \s]*합[ \s]*계[ \s]")
    re_balance_sheet_find5 = re.compile("유[ \s]*동[ \s]*자[ \s]*산[ \s]|유[ \s]*형[ \s]*자[ \s]*산[ \s]")

    # re_cashflow_find = re.compile("법[ \s]*인[ \s]*세[ \s]*지[ \s]*급[ \s]|배[ \s]*당[ \s]*금[ \s]*수[ \s]*취[ \s]|배[ \s]*당[ \s]*금[ \s]*수[ \s]*입[ \s]|법[ \s]*인[ \s]*세[ \s]*납[ \s]*부[ \s]*액[ \s]")
    # re_cashflow_find = re.compile("법[ \s]*인[ \s]*세[ \s]*((지[ \s]*급)[ \s]|(납[ \s]*부))|배[ \s]*당[ \s]*금[ \s]*((수[ \s]*취)|(수[ \s]*입))")

    # re_retained_earnings_find1 = re.compile("[ \s]결[ \s]*손[ \s]*금[ \s]*처[ \s]*리[ \s]*액[ \s]|[ \s]이[ \s]*익[ \s]*준[ \s]*비[ \s]*금[ \s]|[ \s]임[ \s]*의[ \s]*적[ \s]*립[ \s]*금[ \s]|[ \s]미[ \s]*처[ \s]*분[ \s]*이[ \s]*익[ \s]*잉[ \s]*여[ \s]*금[ \s]|[ \s]미[ \s]*처[ \s]*리[ \s]*결[ \s]*손[ \s]*금|[ \s]처[ \s]*분[ \s]*전[ \s]*이[ \s]*익[ \s]*잉[ \s]*여[ \s]*금[ \s]")
    # re_retained_earnings_find1 = re.compile("미[ \s]*처[ \s]*리[ \s]*이[ \s]*익[ \s]*잉[ \s]*여[ \s]*금[ \s]*(\(결손금\))|결[ \s]*손[ \s]*금[ \s]*처[ \s]*리[ \s]*액[ \s]|이[ \s]*익[ \s]*준[ \s]*비[ \s]*금[ \s]|임[ \s]*의[ \s]*적[ \s]*립[ \s]*금[ \s]|미[ \s]*처[ \s]*분[ \s]*이[ \s]*익[ \s]*잉[ \s]*여[ \s]*금[ \s]|미[ \s]*처[ \s]*리[ \s]*결[ \s]*손[ \s]*금|처[ \s]*분[ \s]*전[ \s]*이[ \s]*익[ \s]*잉[ \s]*여[ \s]*금[ \s]")
    # re_retained_earnings_find = re.compile("차[ \s]*기[ \s]*이[ \s]*월[ \s]*미[ \s]*처[ \s]*분[ \s]*이[ \s]*익[ \s]*잉[ \s]*여[ \s]*금[ \s]")
    # re_retained_earnings_find2 = re.compile("[ \s]당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]*(\(손실\))|[ \s]당[ \s]*기[ \s]*순[ \s]*손[ \s]*실[ \s]*((이[ \s]*익)|(손[ \s]*실))|[ \s]당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]|[ \s]연[ \s]*결[ \s]*당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]|[ \s]연[ \s]*결[ \s]*당[ \s]*기[ \s]*순[ \s]*손[ \s]*익[ \s]|[ \s]당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]*손[ \s]*실[ \s]|[ \s]당[ \s]*기[ \s]*순[ \s]*손[ \s]*익[ \s]|[ \s]당[ \s]*기[ \s]*순[ \s]*손[ \s]*실[ \s]|[ \s]연[ \s]*결[ \s]*당[ \s]*기[ \s]*순[ \s]*손[ \s]*실[ \s]|[ \s]총[ \s]*당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]")

    # re_retained_earnings_find2 = re.compile("당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]*(\(손실\))|당[ \s]*기[ \s]*순[ \s]*손[ \s]*실[ \s]*((이[ \s]*익)|(손[ \s]*실))|당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]|연[ \s]*결[ \s]*당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]|연[ \s]*결[ \s]*당[ \s]*기[ \s]*순[ \s]*손[ \s]*익[ \s]|당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]*손[ \s]*실[ \s]|당[ \s]*기[ \s]*순[ \s]*손[ \s]*익[ \s]|당[ \s]*기[ \s]*순[ \s]*손[ \s]*실[ \s]|\b연[ \s]*결[ \s]*당[ \s]*기[ \s]*순[ \s]*손[ \s]*실[ \s]|총[ \s]*당[ \s]*기[ \s]*순[ \s]*이[ \s]*익[ \s]|당[ \s]*기[ \s]*순[ \s]*손[ \s]*실[ \s]*(\(이익\))")

    re_total_income_find4 = re.compile("매[ \s]*출[ \s]*액|매[ \s]*출[ \s]*원[ \s]*가|영[ \s]*업[ \s]*이[ \s]*익")
    re_total_income_find1 = re.compile("당[ \s]*기[ \s]*순[ \s]*이[ \s]*익|당[ \s]*기[ \s]*순[ \s]*손[ \s]*실|당[ \s]*기[ \s]*순[ \s]*손[ \s]*익")
    #re_total_income_find2 = re.compile("기[ \s]*타[ \s]*포[ \s]*괄[ \s]*손[ \s]*익|기[ \s]*타[ \s]*포[ \s]*괄[ \s]*이[ \s]*익")
    re_total_income_find2 = re.compile("주[ \s]*당[ \s]*손[ \s]*익|주[ \s]*당[ \s]*순[ \s]*이[ \s]*익|주[ \s]*당[ \s]*순[ \s]*손[ \s]*실|주[ \s]*당[ \s]*이[ \s]*익|주[ \s]*당[ \s]*손[ \s]*실")
    #re_total_income_find3 = re.compile("총[ \s]*포[ \s]*괄[ \s]*이[ \s]*익|당[ \s]*기[ \s]*총[ \s]*포[ \s]*괄[ \s]*이[ \s]*익|총[ \s]*포[ \s]*괄[ \s]*손[ \s]*실|총[ \s]*포[ \s]*괄[ \s]*손[ \s]*익")
    re_total_income_find3 = re.compile("법[ \s]*인[ \s]*세[ \s]*비[ \s]*용[ \s]*차[ \s]*감[ \s]*전[ \s]*순[ \s]*이[ \s]*익|법[ \s]*인[ \s]*세[ \s]*비[ \s]*용[ \s]*차[ \s]*감[ \s]*전[ \s]*이[ \s]*익|법[ \s]*인[ \s]*세[ \s]*비[ \s]*용[ \s]*차[ \s]*감[ \s]*전[ \s]*순[ \s]*손[ \s]*실|법[ \s]*인[ \s]*세[ \s]*비[ \s]*용[ \s]*차[ \s]*감[ \s]*전[ \s]*손[ \s]*실|법[ \s]*인[ \s]*세[ \s]*차[ \s]*감[ \s]*전[ \s]*이[ \s]*익|법[ \s]*인[ \s]*세[ \s]*차[ \s]*감[ \s]*전[ \s]*손[ \s]*실|법[ \s]*인[ \s]*세[ \s]*차[ \s]*감[ \s]*전[ \s]*순[ \s]*손[ \s]*실|법[ \s]*인[ \s]*세[ \s]*차[ \s]*감[ \s]*전[ \s]*순[ \s]*이[ \s]*익")

    # 목적사항별 기재사항 전체 테이블
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    "--------------------------------연결 재무제표---------------------------"
    cnt = 0
    con_balance_num = 0
    tb_yn = -1
    for table in tables:
        if (re_balance_sheet_find4.search(table.text) and re_balance_sheet_find2.search(table.text) and
                re_balance_sheet_find3.search(table.text) and re_balance_sheet_find5.search(table.text) and re_balance_sheet_find1.search(table.text)):
            con_balance_num = cnt
            tb_yn = 0
            break
        cnt = cnt + 1
    if tb_yn == 0:
        con_balance_table = tables[con_balance_num]
        con_balance_unit = get_unit(tables[con_balance_num - 1].text)
    else:
        con_balance_table = []
        con_balance_unit = '원'
    print("연결 재무상태표: ", con_balance_num, "Tables", len(tables))

    cnt = 0
    con_total_income_table_num = 0
    tb_yn = -1
    for table in tables:
        if (re_total_income_find1.search(table.text) and re_total_income_find2.search(table.text)
                and re_total_income_find3.search(table.text) and re_total_income_find4.search(table.text)):
            con_total_income_table_num = cnt
            tb_yn = 0
            break
        cnt = cnt + 1
    if tb_yn == 0:
        con_total_income_table = tables[con_total_income_table_num]
        con_total_income_unit = get_unit(tables[con_total_income_table_num - 1].text)
    else:
        con_total_income_table = []
        con_total_income_unit = '원'
    print("연결 손익계산서: ", con_total_income_table_num, "Tables", len(tables))

    cnt = 0
    con_cash_table_num = 0
    tb_yn = -1
    for table in tables:
        if re_cashflow_find1.search(table.text) and re_cashflow_find2.search(table.text):
            con_cash_table_num = cnt
            tb_yn = 0
            break
        cnt = cnt + 1
    if tb_yn == 0:
        con_cashflow_table = tables[con_cash_table_num]
        con_cashflow_unit = get_unit(tables[con_cash_table_num - 1].text)
    else:
        con_cashflow_table = []
        con_cashflow_unit = '원'
    print("연결 현금흐름표: ", con_cash_table_num, "Tables", len(tables))

    "--------------------------------별도 재무제표---------------------------"
    cnt = 0
    sep_balance_num = 0
    tb_yn = -1
    for table in tables:
        if (re_balance_sheet_find4.search(table.text) and re_balance_sheet_find2.search(table.text) and
                re_balance_sheet_find3.search(table.text) and re_balance_sheet_find5.search(table.text) and re_balance_sheet_find1.search(table.text)):
            sep_balance_num = cnt
            if sep_balance_num == con_balance_num or (con_cash_table_num != 0 and sep_balance_num < con_cash_table_num):
                cnt = cnt + 1
                continue
            tb_yn = 0
            break
        cnt = cnt + 1
    if tb_yn == 0:
        sep_balance_table = tables[sep_balance_num]
        sep_balance_unit = get_unit(tables[sep_balance_num - 1].text)
    else:
        sep_balance_table = []
        sep_balance_unit = '원'
    print("개별 재무상태표: ", sep_balance_num, "Tables", len(tables))

    cnt = 0
    sep_income_table_num = 0
    tb_yn = -1
    for table in tables:
        if (re_total_income_find1.search(table.text) and re_total_income_find2.search(table.text)
                and re_total_income_find3.search(table.text) and re_total_income_find4.search(table.text)):
            sep_income_table_num = cnt
            if sep_income_table_num == con_total_income_table_num or (sep_balance_num != 0 and sep_income_table_num < sep_balance_num):
                cnt = cnt + 1
                continue
            tb_yn = 0
            break
        cnt = cnt + 1
    if tb_yn == 0:
        sep_income_table = tables[sep_income_table_num]
        sep_income_unit = get_unit(tables[sep_income_table_num - 1].text)
    else:
        sep_income_table = []
        sep_income_unit = '원'
    print("개별 손익계산서: ", sep_income_table_num, "Tables", len(tables))

    cnt = 0
    sep_cash_table_num = 0
    tb_yn = -1
    for table in tables:
        if re_cashflow_find1.search(table.text) and re_cashflow_find2.search(table.text):
            sep_cash_table_num = cnt
            if sep_cash_table_num == con_cash_table_num or (sep_income_table_num != 0 and sep_cash_table_num < sep_income_table_num):
                cnt = cnt + 1
                continue
            tb_yn = 0
            break
        cnt = cnt + 1
    if tb_yn == 0:
        sep_cashflow_table = tables[sep_cash_table_num]
        sep_cashflow_unit = get_unit(tables[sep_cash_table_num - 1].text)
    else:
        sep_cashflow_table = []
        sep_cashflow_unit = '원'
    print("개별 현금흐름표: ", sep_cash_table_num, "Tables", len(tables))

    "--------------------------------연결 재무제표---------------------------"

    try:
        con_balance_sheet_df = scrape_balance_sheet(con_balance_table)
    except:
        con_balance_sheet_df = pd.DataFrame()
        print('연결 재무상태표 없음')

    try:
        con_total_income_df = scrape_income_statement(con_total_income_table)
    except:
        con_total_income_df = pd.DataFrame()
        print('연결 손익계산서 없음')

    try:
        con_cashflow_df = scrape_cashflows(con_cashflow_table)
    except:
        con_cashflow_df = pd.DataFrame()
        print('연결 현금흐름표 없음')

    "--------------------------------별도 재무제표---------------------------"
    try:
        sep_balance_sheet_df = scrape_balance_sheet(sep_balance_table)
    except:
        sep_balance_sheet_df = pd.DataFrame()
        print('개별재무상태표 없음')

    try:
        sep_income_statement_df = scrape_income_statement(sep_income_table)
    except:
        sep_income_statement_df = pd.DataFrame()
        print('개별 손익계산서 없음')

    try:
        sep_cashflow_df = scrape_cashflows(sep_cashflow_table)
    except:
        sep_cashflow_df = pd.DataFrame()
        print('개별 현금흐름표 없음')

    return (con_balance_sheet_df, con_total_income_df, con_cashflow_df, sep_balance_sheet_df, sep_income_statement_df, sep_cashflow_df,
            con_balance_unit, con_total_income_unit, con_cashflow_unit, sep_balance_unit, sep_income_unit, sep_cashflow_unit)


# 연결재무상태표
def scrape_balance_sheet(balance_sheet_table):
    trs = balance_sheet_table.find_all('tr')
    trs_len = len(trs)
    pattern = re.compile(r'\s+')
    pattern_no = re.compile("[ 0-9]+기")
    pattern_ho = re.compile("[ 당전]+기")
    pattern_str = re.compile("[A-Za-z가-힣0-9()]")
    # Balance sheet statement
    if len(trs) != 2:
        balance_df = pd.DataFrame()
        for tr in trs:
            tds = tr.find_all('td')
            account_line = []
            # thead 없을 경우 헤드라인 제거
            if len(tds) < 3 or tds[0].get('rowspan'):
                continue
            for i in range(len(tds)):
                td = tds[i].text.strip().replace("\n", "")
                if i != 0 and (pattern_no.search(td) or pattern_ho.search(td)):
                    td = ''
                account_line.append(td)
            balance_df = pd.concat([balance_df, pd.DataFrame(account_line).T], axis=0)

        balance_df = edit_df(balance_df, len(balance_df.columns), pattern, trs, trs_len)

    new_account_name_list = []
    for i, row_index in enumerate(list(balance_df.index)):
        #account_name = ''.join(filter(str.isalnum, row_index))
        account_name = pattern_str.findall(row_index)
        account_name = ''.join([k for k in account_name if not k.isdigit()])

        if len(account_name) > 0:
            if account_name[-1] == '주':
                account_name = account_name[:-1]
            if account_name[-2:] == '주석':
                account_name = account_name[:-2]

        for j in account_name:
            if j in ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ', 'ⅩⅠ', 'ⅩⅠⅠ',
                     'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'XI', 'X', 'XII', 'ㆍ']:
                account_name = account_name.replace(j, '')

        # 괄호 제거
        if account_name[0] == ')':
            account_name = account_name[1:]
        account_name = account_name.replace('()', '')

        new_account_name_list.append(account_name)

        new_row = []
        for k in balance_df.iloc[i]:
            if isinstance(k, str):
                if "원" in k:
                    newstr = k.replace("원", "")
                    new_row.append(newstr)
                else:
                    new_row.append(k)
            else:
                new_row.append(k)
        balance_df.iloc[i] = new_row

    balance_df.index = new_account_name_list
    return balance_df


# 연결손익계산서
def scrape_income_statement(income_total_table):
    trs = income_total_table.find_all('tr')
    trs_len = len(trs)
    pattern = re.compile(r'\s+')
    pattern_no = re.compile("[ 0-9]+기")
    pattern_ho = re.compile("[ 당전]+기")
    pattern_str = re.compile("[A-Za-z가-힣0-9()]")
    # Income statement
    if len(trs) != 2:
        income_total_df = pd.DataFrame()
        for income_tr in trs:
            tds = income_tr.find_all('td')
            account_line = []
            if len(tds) < 3 or tds[0].get('rowspan'):
                continue
            for i in range(len(tds)):
                td = tds[i].text.strip().replace("\n", "")
                if i != 0 and (pattern_no.search(td) or pattern_ho.search(td)):
                    td = ''
                account_line.append(td)
            income_total_df = pd.concat([income_total_df, pd.DataFrame(account_line).T], axis=0)

        income_total_df = edit_df(income_total_df, len(income_total_df.columns), pattern, trs, trs_len)

    new_account_name_list = []
    for i, row_index in enumerate(list(income_total_df.index)):
        #account_name = ''.join(filter(str.isalnum, row_index))
        account_name = ''.join(pattern_str.findall(row_index))
        account_name = ''.join([k for k in account_name if not k.isdigit()])

        if len(account_name) > 0:
            if account_name[-1] == '주':
                account_name = account_name[:-1]
            if account_name[-2:] == '주석':
                account_name = account_name[:-2]

        for j in account_name:
            if j in ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ', 'ⅩⅠ', 'ⅩⅠⅠ',
                     'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'XI', 'X', 'XII', 'ㆍ']:
                account_name = account_name.replace(j, '')

        # 괄호 제거
        if account_name[0] == ')':
            account_name = account_name[1:]
        account_name = account_name.replace('()', '')

        new_account_name_list.append(account_name)

        new_row = []
        for k in income_total_df.iloc[i]:
            if isinstance(k, str):
                if "원" in k:
                    newstr = k.replace("원", "")
                    new_row.append(newstr)
                else:
                    new_row.append(k)
            else:
                new_row.append(k)
        income_total_df.iloc[i] = new_row

    income_total_df.index = new_account_name_list
    return income_total_df


# 연결현금흐름표
def scrape_cashflows(cashflow_table):
    trs = cashflow_table.find_all('tr')
    trs_len = len(trs)
    pattern = re.compile(r'\s+')
    pattern_no = re.compile("[ 0-9]+기")
    pattern_ho = re.compile("[ 당전]+기")
    pattern_str = re.compile("[A-Za-z가-힣0-9()]")
    # CASHFLOW statement
    if len(trs) != 2:
        cashflow_df = pd.DataFrame()
        for tr in trs:
            tds = tr.find_all('td')
            account_line = []
            if len(tds) < 3 or tds[0].get('rowspan'):
                continue
            for i in range(len(tds)):
                td = tds[i].text.strip().replace("\n", "")
                if i != 0 and (pattern_no.search(td) or pattern_ho.search(td)):
                    td = ''
                account_line.append(td)
            cashflow_df = pd.concat([cashflow_df, pd.DataFrame(account_line).T], axis=0)

        cashflow_df = edit_df(cashflow_df, len(cashflow_df.columns), pattern, trs, trs_len)

    new_account_name_list = []
    for i, row_index in enumerate(list(cashflow_df.index)):
        #account_name = ''.join(filter(str.isalnum, row_index))
        account_name = ''.join(pattern_str.findall(row_index))
        account_name = ''.join([k for k in account_name if not k.isdigit()])

        if len(account_name) > 0:
            if account_name[-1] == '주':
                account_name = account_name[:-1]
            if account_name[-2:] == '주석':
                account_name = account_name[:-2]

        for j in account_name:
            if j in ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ', 'ⅩⅠ', 'ⅩⅠⅠ',
                     'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'XI', 'X', 'XII', 'ㆍ']:
                account_name = account_name.replace(j, '')

        # 괄호 제거
        if account_name[0] == ')':
            account_name = account_name[1:]
        account_name = account_name.replace('()', '')

        new_account_name_list.append(account_name)

        new_row = []
        for k in cashflow_df.iloc[i]:
            if isinstance(k, str):
                if "원" in k:
                    newstr = k.replace("원", "")
                    new_row.append(newstr)
                else:
                    new_row.append(k)
            else:
                new_row.append(k)
        cashflow_df.iloc[i] = new_row

    cashflow_df.index = new_account_name_list
    return cashflow_df


def edit_df(cur_df, column_len, pattern, trs, trs_len):
    if column_len == 6:
        cur_df = cur_df.drop(cur_df.columns[1], axis=1)
        if trs_len == 3:
            col_names = trs[1].find_all('th')
        else:
            col_names = trs[0].find_all('th')
        if not col_names:
            col_names = trs[0].find_all('td')
        del col_names[1]
        cur_df.columns = [re.sub(pattern, '', col_names[0].text.strip()),
                          col_names[1].text.strip(), col_names[1].text.strip() + str(2),
                          col_names[2].text.strip(), col_names[2].text.strip() + str(2)]

        cur_df = cur_df.set_index(cur_df.columns[0])
        cur_df = cur_df.replace('', np.nan, inplace=False)
        cur_df = cur_df.dropna(axis=0, how='all', thresh=None, subset=None, inplace=False)
        cur_df = cur_df.fillna(method='bfill', axis=1)
        cur_df = cur_df.iloc[:, [0, 2]]
    elif column_len == 3:
        if trs_len == 3:
            col_names = trs[1].find_all('th')
        else:
            col_names = trs[0].find_all('th')
        if not col_names:
            col_names = trs[0].find_all('td')
        cur_df.columns = [re.sub(pattern, '', col_names[0].text.strip()),
                          col_names[1].text.strip(),
                          col_names[2].text.strip()]

        cur_df = cur_df.set_index(cur_df.columns[0])
        cur_df = cur_df.replace('', np.nan, inplace=False)
        cur_df = cur_df.dropna(axis=0, how='all', thresh=None, subset=None, inplace=False)
        cur_df = cur_df.fillna(method='bfill', axis=1)
        cur_df = cur_df

    elif column_len == 4:
        if trs_len == 3:
            col_names = trs[1].find_all('th')
        else:
            col_names = trs[0].find_all('th')
        if not col_names:
            col_names = trs[0].find_all('td')
        cur_df.columns = [re.sub(pattern, '', col_names[0].text.strip()), col_names[1].text.strip(),
                          col_names[2].text.strip(), col_names[3].text.strip()]

        cur_df = cur_df.set_index(cur_df.columns[0])
        cur_df = cur_df.replace('', np.nan, inplace=False)
        cur_df = cur_df.dropna(axis=0, how='all', thresh=None, subset=None, inplace=False)
        cur_df = cur_df.fillna(method='bfill', axis=1)
        cur_df = cur_df.iloc[:, [1, 2]]

    else:
        if trs_len == 3:
            col_names = trs[1].find_all('th')
        else:
            col_names = trs[0].find_all('th')
        if not col_names:
            col_names = trs[0].find_all('td')

        cur_df.columns = [re.sub(pattern, '', col_names[0].text.strip()),
                          col_names[1].text.strip(), col_names[1].text.strip() + str(2),
                          col_names[2].text.strip(), col_names[2].text.strip() + str(2)]

        cur_df = cur_df.set_index(cur_df.columns[0])
        cur_df = cur_df.replace('', np.nan, inplace=False)
        cur_df = cur_df.dropna(axis=0, how='all', thresh=None, subset=None, inplace=False)
        cur_df = cur_df.fillna(method='bfill', axis=1)
        cur_df = cur_df.iloc[:, [0, 2]]

    return cur_df

# 숫자만 남기기
def set_num(arr):
    re_num = re.compile("[0-9]")

    for i in range(0, len(arr)):
        for j in range(0, len(arr[i])):
            amt = str(arr[i][j]).replace(" ", "").strip()
            num = "".join(re_num.findall(amt))
            if '(' in amt:
                arr[i][j] = '-' + num
            else:
                arr[i][j] = num
                if '-' in amt and len(amt) > 1:
                    arr[i][j] = '-' + num

    return arr
