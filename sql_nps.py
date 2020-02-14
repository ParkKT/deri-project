import time


create_dt = time.strftime('%Y%m%d%H%M%S')
# proxy_nps001
def select_nps001(rcpno):
    select = """select (select jm_nm from gcoga000 where jm_code = a.jm_code) jm_nm, a.meet_ymd, a.meet_gb 
                from proxy011 a 
                where a.rcp_no = '{0}'""".format(rcpno)

    return select

# proxy_nps002
def select_nps002(rcpno):
    select = """
                where a.rcp_no = '{0}'""".format(rcpno)

    return select

# proxy_nps003
def select_nps003(rcpno):
    select = """select con_gb, finance_gb, year_gb, sub_seq, sub_nm, sub_amt, amt_unit 
                from proxy020 
                where rcp_no = '{0}'""".format(rcpno)

    #배당 select 추가

    return select

# proxy_nps004
def select_nps004(rcpno):
    select = """select aoi_gb, aoi_seq, aoi_chg_before, aoi_chg_after, aoi_chg_purpose 
                from proxy028 
                where rcp_no = '{0}'""".format(rcpno)

    return select

# proxy_nps005
def select_nps005(rcpno, res_rcpno):
    select = """select a.isa_gb, a.pe_seq, a.pe_code, a.pe_nm, a.pe_birth, a.is_out, 
                (select pe_imgi, is_new proxy003 where rcp_no = (select max(rcp_no) from proxy001 where first_rcpno = '{0}')) 
                from proxy021 a 
                where a.rcp_no = '{1}'""".format(res_rcpno, rcpno)

    return select

# proxy_nps007
def select_nps007(rcpno):
    # 당기 보수한도
    select_1 = """select isa_cnt, isa_out_cnt, bosu_amt 
                  from proxy023 
                  where rcp_no = '{0}' and isa_gb = '1' and con_gb = '1'""".format(rcpno)
    # 전기 보수한도
    select_2 = """select isa_cnt, isa_out_cnt, bosu_amt 
                  from proxy023 
                  where rcp_no = '{0}' and isa_gb = '1' and con_gb = '2'""".format(rcpno)

    return select_1, select_2

# proxy_nps008
def select_nps008(rcpno):
    # 당기 보수한도
    select_1 = """select isa_cnt, bosu_amt 
                  from proxy023 
                  where rcp_no = '{0}' and isa_gb = '2' and con_gb = '1'""".format(rcpno)
    # 전기 보수한도
    select_2 = """select isa_cnt, bosu_amt 
                  from proxy023 
                  where rcp_no = '{0}' and isa_gb = '2' and con_gb = '2'""".format(rcpno)

    return select_1, select_2

# proxy_nps009
def select_nps009(rcpno):
    select = """select (select sum(stock_cnt) from proxy024 where rcp_no = '{0}'), stock_total_cnt 
                from proxy026 
                where rcp_no = '{1}'""".format(rcpno, rcpno)

    return select

# proxy_nps010
def select_nps010(rcpno):
    select = """select pe_nm, pe_jikwi, pe_jikchek, stock_kind, stock_cnt 
                from proxy024 
                where rcp_no = '{0}'""".format(rcpno)

    return select
