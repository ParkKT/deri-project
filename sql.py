from utils import make_birth, make_birth_ymd, make_ymd, make_time
from utils import get_imgi, get_new, get_outYn, get_fulltime, get_dup, get_atnYn, get_regYn, get_antCnt
from utils import del_quot, get_num, get_round, get_nm, get_num_int, get_num_per
from pecodeUtil import get_pecode, get_pecode_career

import time


create_dt = time.strftime('%Y%m%d%H%M%S')
# 결의 마스터
def resolution_mst_ins(meet_seq, meet_tb, jm_code, rcp_no, first_rcpno):
    # 주총 결의_데이터 변환
    meet_tb[0] = make_ymd(meet_tb[0]).replace("'", "")          # 주총일자 YYYYMMDD
    meet_tb[1] = make_time(meet_tb[1]).replace("'", "")         # hhmm
    meet_tb[2] = meet_tb[2].replace("'", "")                    # 주주총회 장소
    meet_tb[3] = str(meet_tb[3]).replace("'", "")               # 의안내용 쿼테이션 제거
    meet_tb[4] = make_ymd(meet_tb[4]).replace("'", "")          # 이사회 결의일 YYYYMMDD
    meet_tb[5] = get_antCnt(meet_tb[5]).replace("'", "")        # 참석수
    meet_tb[6] = get_antCnt(meet_tb[6]).replace("'", "")        # 불참석수
    meet_tb[7] = get_atnYn(meet_tb[7]).replace("'", "")         # 감사 참석여부
    meet_tb[8] = get_regYn(meet_tb[8]).replace("'", "")         # 1:정기, 2:임시

    in_qry = """ insert into proxy001(meet_seq, rcp_no, jm_code, meet_gb, first_rcpno, meet_ymd, meet_time, meet_location,
                                      meet_content, meet_result_dt, isa_atn, isa_abs, gamsa_atn, create_dt, modify_dt)
                               values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}',
                                      '{11}', '{12}', '{13}', '{14}')
             """.format(meet_seq, rcp_no, jm_code, meet_tb[8], first_rcpno, meet_tb[0], meet_tb[1], meet_tb[2],
                        meet_tb[3], meet_tb[4], meet_tb[5], meet_tb[6], meet_tb[7], create_dt, create_dt)

    return in_qry

# 이사선임
def isa_info_ins(meet_seq, isa_arr, rcp_no, seq):
    # 인물코드 세팅
    jm_code = meet_seq[:6]
    pe_code = get_pecode(jm_code, isa_arr[0])
    if pe_code == '' or pe_code is None:
        pe_code = get_pecode_career(isa_arr[0], make_birth(isa_arr[1]), str(isa_arr[4]).replace("'", ""))

    in_qry = """insert into proxy003(meet_seq, rcp_no, isa_gb, pe_seq, pe_code, pe_nm, pe_birth, pe_imgi, is_new,
                                        is_dup, is_fulltime, is_out, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}',
                                        '{9}', '{10}', '{11}', '{12}', '{13}')
             """.format(meet_seq, rcp_no, isa_arr[8], jm_code + str(seq + 1).zfill(4), pe_code, isa_arr[0],
                        make_birth(isa_arr[1]), get_imgi(isa_arr[2]), get_new(isa_arr[3]), get_dup(isa_arr[5]),
                        get_fulltime(isa_arr[7]), get_outYn(isa_arr[6]), create_dt, create_dt)

    return in_qry

# 이사선임_경력
def isa_car_ins(meet_seq, isa_arr, rcp_no, seq):
    # 인물코드 세팅
    jm_code = meet_seq[:6]
    pe_code = get_pecode(jm_code, isa_arr[0])
    if pe_code == '' or pe_code is None:
        pe_code = get_pecode_career(isa_arr[0], make_birth(isa_arr[1]), str(isa_arr[4]).replace("'", ""))

    in_arr = """insert into proxy004(meet_seq, rcp_no, pe_seq, pe_code, content, create_dt, modify_dt)
                              values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')
             """.format(meet_seq, rcp_no, jm_code + str(seq + 1).zfill(4), pe_code, str(isa_arr[4]).replace("'", ""), create_dt, create_dt)

    return in_arr

# 이사선임_겸직
def isa_dup_ins(meet_seq, isa_arr, rcp_no, seq):
    # 인물코드 세팅
    jm_code = meet_seq[:6]
    pe_code = get_pecode(jm_code, isa_arr[0])
    if pe_code == '' or pe_code is None:
        pe_code = get_pecode_career(isa_arr[0], make_birth(isa_arr[1]), str(isa_arr[4]).replace("'", ""))

    in_arr = """insert into proxy005(meet_seq, rcp_no, pe_seq, pe_code, content, create_dt, modify_dt)
                              values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')
             """.format(meet_seq, rcp_no, jm_code + str(seq + 1).zfill(4), pe_code, str(isa_arr[5]).replace("'", ""), create_dt, create_dt)

    return in_arr

# 사업목적 변경
def biz_ins(meet_seq, biz_arr, rcp_no):
    in_qry = """insert into proxy006(meet_seq, rcp_no, gubun, cont_bfr, cont_aft, correct_cus, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')
                """.format(meet_seq, rcp_no, biz_arr[0], biz_arr[1], biz_arr[2], biz_arr[3], create_dt, create_dt)

    return in_qry


##################### 주총공고 #####################
# 주총 공고
def notice_mst_ins(meet_seq, rcp_no, jm_code, meet_gb, rirst_rcpno, mst_tb, refer, res_rcpno):
    in_qry = """insert into proxy011(meet_seq, rcp_no, jm_code, meet_gb, first_rcpno, res_first_rcpno, meet_ymd, meet_time, meet_location, 
                                     meet_content, refer_content, correct_cus, create_dt, modify_dt)
                              values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}')
             """.format(meet_seq, rcp_no, jm_code, meet_gb, rirst_rcpno, res_rcpno, mst_tb[0], mst_tb[1], mst_tb[2], mst_tb[3], refer, '', create_dt, create_dt)

    return in_qry

# 사외이사 이사회 활동내역 : 이사회 안건
def act_cont_ins(c_arr, meet_seq, rcp_no, agno, is_gagyul):
    # 회차
    act_seq = c_arr[0]
    """보류
    if '임시' in act_seq:
        act_seq = '0'
    else:
        act_seq = get_num(get_round(act_seq))
    """

    # 가결여부
    if is_gagyul == 1:
        act_rst = c_arr[3]
    else:
        act_rst = ''
    """보류
    if '가결' in act_rst or '찬성' in act_rst or '승인' in act_rst:
        act_rst = 'Y'
    elif '부결' in act_rst or '반대' in act_rst or '미승인' in act_rst:
        act_rst = 'N'
    elif '보고' in act_rst:
        act_rst = 'B'
    else:
        act_rst = 'E'
    """

    in_qry = """insert into proxy012(meet_seq, rcp_no, act_seq, act_ymd, act_agno, act_content, act_rst, create_dt, modify_dt)
                                values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')
               """.format(meet_seq, rcp_no, act_seq, make_ymd(c_arr[1]), agno, c_arr[2], act_rst, create_dt, create_dt)

    return in_qry

# 사외이사 이사회 활동내역 : 사외이사 활동
def act_isa_ins(isa_nm, c_arr, meet_seq, rcp_no, agno, seq, is_gagyul):
    # 회차
    act_seq = c_arr[0]
    """보류
    if '임시' in act_seq:
        act_seq = '0'
    else:
        act_seq = get_num(get_round(act_seq))
    """

    # 찬반여부
    yn_num = 4
    if is_gagyul == 0:
        yn_num = 3
    appr_yn = c_arr[seq + yn_num]
    attn_yn = c_arr[seq + yn_num]
    """ 보류
    if '찬성' in appr_yn or '가결' in appr_yn:
        appr_yn = 'Y'
    elif '반대' in appr_yn or '부결' in appr_yn:
        appr_yn = 'N'
    elif '보류' in appr_yn:
        appr_yn = 'B'
    elif '제한' in appr_yn:
        appr_yn = 'J'
    elif '해당' in appr_yn or '없음' in appr_yn or '퇴임' in appr_yn or '선임' in appr_yn or '만료' in appr_yn:
        appr_yn = ''
    else:
        appr_yn = 'E'
    # 참석여부
    if '참석' in attn_yn or '찬성' in attn_yn or '반대' in attn_yn or '가결' in attn_yn or '부결' in attn_yn:
        attn_yn = 'Y'
    elif '불참' in attn_yn or '미참' in attn_yn or '-' == attn_yn:
        attn_yn = 'N'
    elif '해당' in attn_yn or '없음' in attn_yn or '퇴임' in attn_yn or '선임' in attn_yn or '만료' in attn_yn:
        attn_yn = ''
    else:
        attn_yn = 'E'
    """

    # 성명 / 이물코드
    name = get_nm(isa_nm.replace(" ", ""))
    jm_code = meet_seq[:6]
    pe_code = get_pecode(jm_code, name)

    in_qry = """insert into proxy013(meet_seq, rcp_no, act_seq, act_ymd, act_agno, pe_seq, pe_code, isa_nm, appr_yn, attn_yn, create_dt, modify_dt)
                                   values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}')
                  """.format(meet_seq, rcp_no, act_seq, make_ymd(c_arr[1]), agno, jm_code + str(seq + 1).zfill(4), pe_code, name, appr_yn, attn_yn, create_dt, create_dt)

    return in_qry

# 사외이사 출석률
def isa_rt_ins(meet_seq, rcp_no, rt, seq, isa_nm):
    rt = get_num_per(rt)
    if not rt.isdigit:
        rt = 'null'

    # 성명 / 이물코드
    name = get_nm(isa_nm.replace(" ", ""))
    jm_code = meet_seq[:6]
    pe_code = get_pecode(jm_code, name)

    in_qry = """insert into proxy014(meet_seq, rcp_no, pe_seq, pe_code, chul_rt, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', {4}, '{5}', '{6}')
                """.format(meet_seq, rcp_no, jm_code + str(seq + 1).zfill(4), pe_code, rt, create_dt, create_dt)

    return in_qry

# 사외이사 위워회 활동내역
def isa_border_ins(arr, meet_seq, rcp_no, hold_seq):
    # 가결여부
    act_rst = arr[4]
    """보류
    if '가결' in act_rst or '찬성' in act_rst or '승인' in act_rst:
        act_rst = 'Y'
    elif '부결' in act_rst or '반대' in act_rst or '미승인' in act_rst:
        act_rst = 'N'
    elif '보고' in act_rst:
        act_rst = 'B'
    elif '심의완료' in act_rst:
        act_rst = 'C'
    else:
        act_rst = 'E'
    """

    # 위원회명, 코드
    comt_nm = arr[0].replace("\n", "").replace(" ", "")
    """보류
    if comt_nm == '사외이사후보추천위원회':
        comt_nm = '사추위'
    comt_cd_sel = "select cd_val from ssg00011 where com_cd_tp_cd = 'comt_cd' and cd_nm = '{0}'".format(comt_nm)
    """

    in_qry = """insert into proxy015(meet_seq, rcp_no, comt_cd, comt_nm, comt_member, comt_dt, comt_hold_seq, comt_cont, comt_rstyn, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}')
                """.format(meet_seq, rcp_no, comt_nm, comt_nm, arr[1], make_ymd(arr[2]), hold_seq, arr[3], act_rst, create_dt, create_dt)

    return in_qry

# 사외이사 위워회 활동내역 이사 구성원
def isa_comt_member_ins(arr, meet_seq, rcp_no, hold_seq):
    # 위원회명, 코드
    comt_nm = arr[0].replace("\n", "").replace(" ", "")
    """보류
    if comt_nm == '사외이사후보추천위원회':
        comt_nm = '사추위'
    comt_cd_sel = "select cd_val from ssg00011 where com_cd_tp_cd = 'comt_cd' and cd_nm = '{0}'".format(comt_nm)
    """

    # 성명 / 이물코드
    name = get_nm(arr[1].replace(" ", ""))
    jm_code = meet_seq[:6]
    pe_code = get_pecode(jm_code, name)

    in_qry = """insert into proxy016(meet_seq, rcp_no, comt_cd, pe_seq, pe_code, pe_nm, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')
                """.format(meet_seq, rcp_no, comt_nm, jm_code + str(hold_seq + 1).zfill(4), pe_code, name, create_dt, create_dt)

    return in_qry

# 금액 단위
def make_danwi(gum):
    gum = gum.replace("\n", "").replace(" ", "")
    if '억' in gum:
        unit = 100000000
    elif '백만' in gum:
        unit = 1000000
    elif gum == '만원':
        unit = 10000
    elif '천' in gum:
        unit = 1000
    elif '백원' in gum:
        unit = 100
    else:
        unit = 1

    return unit

# 사외이사 보수
def isa_bosu_ins(arr, meet_seq, rcp_no, gum):
    # 이사 구분
    isa_gb = str(arr[0]).replace("\n", "").replace(" ", "")
    if '사외이사' in isa_gb or '사외' in isa_gb:
        isa_gb = '1'
    elif '사내이사' in isa_gb or isa_gb == '이사':
        isa_gb = '0'
    elif '기타비상무이사' in isa_gb:
        isa_gb = '2'
    else:
        isa_gb = '3'

    # 금액 단위
    unit = make_danwi(gum)

    appr_amt = arr[2]
    if appr_amt != 'null':
        appr_amt = float(appr_amt) * unit
    total_amt = arr[3]
    if total_amt != 'null':
        total_amt = float(total_amt) * unit
    avg_amt = arr[4]
    if avg_amt != 'null':
        avg_amt = float(avg_amt) * unit

    in_qry = """insert into proxy017(meet_seq, rcp_no, isa_gb, isa_cnt, appr_amt, total_amt, avg_amt, bigo, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', {3}, {4}, {5}, {6}, '{7}', '{8}', '{9}')
                """.format(meet_seq, rcp_no, isa_gb, arr[1], appr_amt, total_amt, avg_amt, arr[5], create_dt, create_dt)

    return in_qry

# 단일거래 규모 이상
def transaction_single_ins(arr, meet_seq, rcp_no, gum, seq):
    # 개행 제거
    for i in range(0, len(arr)):
        arr[i] = str(arr[i]).replace("\n", "")

    # 금액 단위 변환
    unit = make_danwi(gum)

    trst_amt = arr[3]
    if trst_amt != 'null':
        trst_amt = float(trst_amt) * unit

    in_qry = """insert into proxy018(meet_seq, rcp_no, trst_seq, trst_gb, trst_rel, trst_period, trst_amt, trst_rt, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', {6}, {7}, '{8}', '{9}')
                """.format(meet_seq, rcp_no, seq, arr[0], arr[1], arr[2], trst_amt, arr[4], create_dt, create_dt)

    return in_qry

# 거래총액 규모 이상
def transaction_total_ins(arr, meet_seq, rcp_no, gum, seq):
    # 개행 제거
    for i in range(0, len(arr)):
        arr[i] = str(arr[i]).replace("\n", "")

    # 금액 단위
    unit = make_danwi(gum)

    trst_amt = arr[3]
    if trst_amt != 'null':
        trst_amt = float(trst_amt) * unit

    in_qry = """insert into proxy019(meet_seq, rcp_no, trst_seq, trst_rel, trst_gb, trst_period, trst_amt, trst_rt, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', {6}, {7}, '{8}', '{9}')
                """.format(meet_seq, rcp_no, seq, arr[0], arr[1], arr[2], trst_amt, arr[4], create_dt, create_dt)

    return in_qry

# 재무제표
def finance_ins(arr, col, meet_seq, rcp_no, gum, seq, con_gb, finance_gb, year_gb):
    # 개행 제거
    for i in range(0, len(arr)):
        arr[i] = str(arr[i]).replace("\n", "")
        if arr[i] == '':
            arr[i] = '0'
    col = str(col).replace("\n", "")

    # 금액 단위
    unit = make_danwi(gum)

    sub_amt = arr[year_gb - 1]
    #if sub_amt != 'null':
    #    sub_amt = float(sub_amt) * unit

    in_qry = """insert into proxy020(meet_seq, rcp_no, con_gb, finance_gb, year_gb, sub_seq, sub_nm, sub_amt, amt_unit, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}')
                """.format(meet_seq, rcp_no, con_gb, finance_gb, year_gb, seq, col, sub_amt, gum, create_dt, create_dt)

    return in_qry

# 이사선임
def isa_elect_ins(arr, meet_seq, rcp_no, seq):
    # 개행 제거
    for i in range(0, len(arr)):
        arr[i] = str(arr[i]).replace("\n", "")

    is_out = arr[2]
    if '사외이사' in is_out or is_out == '예' or is_out == 'Y' or is_out == 'y' or is_out == '해당' or is_out == 'O' or is_out == 'o' or is_out == '○':
        is_out = '2'
    elif '감사' == is_out:
        is_out = '3'
    elif '기타비상무' in is_out or '비상무' in is_out or '기타' in is_out:
        is_out = '4'
    else:
        is_out = '1'

    # 생년월/생년월일 구분
    birth = arr[1]
    if len(get_num(birth)) < 7:
        birth = make_birth(birth)
    else:
        birth = make_birth_ymd(birth)

    # 이름 띄어쓰기 제거
    pe_nm = str(arr[0]).replace(" ", "")
    pe_nm = get_nm(pe_nm)
    jm_code = meet_seq[:6]
    pe_code = get_pecode(jm_code, pe_nm)

    in_qry = """insert into proxy021(meet_seq, rcp_no, isa_gb, pe_seq, pe_code, pe_nm, pe_birth, is_out, juju_rel, recommender, bigo, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}')
                """.format(meet_seq, rcp_no, arr[5], jm_code + str(seq + 1).zfill(4), pe_code, pe_nm, birth, is_out, arr[3], arr[4], '', create_dt, create_dt)

    return in_qry

# 이사선임_경력
def isa_career_ins(arr, meet_seq, rcp_no, job_is_new, seq):
    # 이름 띄어쓰기 제거
    pe_nm = str(arr[0]).replace(" ", "")
    pe_nm = get_nm(pe_nm)
    jm_code = meet_seq[:6]
    pe_code = get_pecode(jm_code, pe_nm)

    if job_is_new:
        in_qry = """insert into proxy022(meet_seq, rcp_no, isa_gb, pe_seq, pe_code, pe_nm, main_job, career_period, career, deal_3y, bigo, create_dt, modify_dt)
                                     values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}')
                    """.format(meet_seq, rcp_no, arr[5], jm_code + str(seq + 1).zfill(4), pe_code, pe_nm, arr[1], arr[2], arr[3], arr[4], '', create_dt, create_dt)
    else:
        in_qry = """insert into proxy022(meet_seq, rcp_no, isa_gb, pe_seq, pe_code, pe_nm, main_job, career_period, career, deal_3y, bigo, create_dt, modify_dt)
                                     values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}')
                    """.format(meet_seq, rcp_no, arr[4], jm_code + str(seq + 1).zfill(4), pe_code, pe_nm, arr[1], '', arr[2], arr[3], '', create_dt, create_dt)

    return in_qry

# 이사선임_보수한도
def isa_bosuhando_ins(arr, meet_seq, rcp_no, gum, chk, isa_gb):
    # 이사/감사 구분
    if isa_gb == 1: # 이사
        bosu_amt = arr[2]
        isa_out_cnt = arr[1]
    else:
        bosu_amt = arr[1]
        isa_out_cnt = '0'

    # 금액 단위
    unit = make_danwi(gum)

    if bosu_amt != 'null':
        bosu_amt = float(bosu_amt) * unit

    in_qry = """insert into proxy023(meet_seq, rcp_no, isa_gb, con_gb, isa_cnt, isa_out_cnt, bosu_amt, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', {4}, {5}, {6}, '{7}', '{8}')
                """.format(meet_seq, rcp_no, isa_gb, chk + 1, arr[0], isa_out_cnt, bosu_amt, create_dt, create_dt)

    return in_qry

# 이사선임_보수한도
def new_isa_bosuhando_ins(arr, meet_seq, rcp_no, gum, isa_gb, con_gb):
    # 금액 단위
    unit = make_danwi(gum)

    in_qry = """insert into proxy023(meet_seq, rcp_no, isa_gb, con_gb, isa_cnt, isa_out_cnt, bosu_amt, bosu_jigup, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}')
                """.format(meet_seq, rcp_no, isa_gb, con_gb, arr[0], arr[1], float(arr[3]) * unit, float(arr[2]) * unit, create_dt, create_dt)

    return in_qry

# 주식매수선택권_부여받을 자의 리스트
def stock_list_ins(arr, meet_seq, rcp_no, seq):
    # 개행 제거
    for i in range(0, len(arr)):
        arr[i] = str(arr[i]).replace("\n", "")

    # 이름 띄어쓰기 제거
    pe_nm = str(arr[0]).replace(" ", "")

    in_qry = """insert into proxy024(meet_seq, rcp_no, pe_seq, pe_nm, pe_jikwi, pe_jikchek, stock_kind, stock_cnt, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7}, '{8}', '{9}')
                """.format(meet_seq, rcp_no, seq, pe_nm, arr[1], arr[2], arr[3], arr[4], create_dt, create_dt)

    return in_qry

# 주식매수선택권_부여방법 등
def stock_method_ins(arr, meet_seq, rcp_no, seq):
    in_qry = """insert into proxy025(meet_seq, rcp_no, content_gb, stock_method, stock_kind_cnt, stock_period, stock_gita, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')
                """.format(meet_seq, rcp_no, seq + 1, arr[0], arr[1], arr[2], arr[3], create_dt, create_dt)

    return in_qry

# 주식매수선택권_부여방법 등
def stock_extra_ins(arr, meet_seq, rcp_no):
    stock_total_cnt = get_num(arr[0])
    if stock_total_cnt == 'null':
        stock_total_cnt = '0'
    stock_avl_cnt = get_num(arr[3])
    if stock_avl_cnt == 'null':
        stock_avl_cnt = '0'
    stock_ext_cnt = get_num(arr[4])
    if stock_ext_cnt == 'null':
        stock_ext_cnt = '0'

    in_qry = """insert into proxy026(meet_seq, rcp_no, stock_total_cnt, stock_avl_range, stock_kind, stock_avl_cnt, stock_ext_cnt, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', {5}, {6}, '{7}', '{8}')
                """.format(meet_seq, rcp_no, stock_total_cnt, arr[1], arr[2], stock_avl_cnt, stock_ext_cnt, create_dt, create_dt)

    return in_qry

# 주식매수선택권_실효내역
def stock_use_ins(arr, meet_seq, rcp_no):
    stock_gijun_yy = get_num(arr[0])
    if stock_gijun_yy == 'null':
        stock_gijun_yy = '0000'
    stock_ymd = arr[1]
    stock_pe_cnt = get_num(arr[2])
    if stock_pe_cnt == 'null':
        stock_pe_cnt = '0'
    stock_give_cnt = get_num(arr[4])
    if stock_give_cnt == 'null':
        stock_give_cnt = '0'
    stock_use_cnt = get_num(arr[5])
    if stock_use_cnt == 'null':
        stock_use_cnt = '0'
    stock_actual_cnt = get_num(arr[6])
    if stock_actual_cnt == 'null':
        stock_actual_cnt = '0'
    stock_extra_cnt = get_num_int(arr[7])
    if stock_extra_cnt == 'null':
        stock_extra_cnt = '0'

    in_qry = """insert into proxy027(meet_seq, rcp_no, stock_gijun_yy, stock_ymd, stock_pe_cnt, 
                                     stock_kind, stock_give_cnt, stock_use_cnt, stock_actual_cnt, stock_extra_cnt, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', {4}, '{5}', {6}, {7}, {8}, {9}, '{10}', '{11}')
                """.format(meet_seq, rcp_no, stock_gijun_yy, stock_ymd, stock_pe_cnt, arr[3],
                           stock_give_cnt, stock_use_cnt, stock_actual_cnt, stock_extra_cnt, create_dt, create_dt)

    return in_qry

# 정관의 변경
def aoi_ins(arr, meet_seq, rcp_no, seq, aoi_gb):
    in_qry = """insert into proxy028(meet_seq, rcp_no, aoi_gb, aoi_seq, aoi_chg_before, aoi_chg_after, aoi_chg_purpose, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')
                """.format(meet_seq, rcp_no, aoi_gb, seq, arr[0], arr[1], arr[2], create_dt, create_dt)

    return in_qry

# 정관의 변경_태그 포함
def aoi_tag_ins(arr, meet_seq, rcp_no, seq, aoi_gb):
    in_qry = """insert into proxy029(meet_seq, rcp_no, aoi_gb, aoi_seq, aoi_chg_before, aoi_chg_after, aoi_chg_purpose, create_dt, modify_dt)
                                 values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')
                """.format(meet_seq, rcp_no, aoi_gb, seq, arr[0], arr[1], arr[2], create_dt, create_dt)

    return in_qry

# to deri
def deri_ins(meet_seq, rcp_no, pre_rcp_no, jm_code, meet_ymd, notice_gb, meet_ymdstr, meet_area):
    jm_nm = "select jm_nm from gcoga000 where jm_code = '{0}'".format(jm_code)
    in_qry = """insert into proxy_deri001(meet_seq, rcp_no, rcp_no_pre, jm_code, jm_name, meet_ymd, meet_gb, meet_ymdstr, meet_area, data_yn)
                                 values('{0}', '{1}', '{2}', '{3}', ({4}), '{5}', '{6}', '{7}', '{8}', 'N')
                """.format(meet_seq, rcp_no, pre_rcp_no, jm_code, jm_nm, make_ymd(meet_ymd), notice_gb, meet_ymdstr, meet_area.replace("'", ""))

    return in_qry
