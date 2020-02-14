from utils import get_dbcon, close_dbcon
from logger import get_info_logger_rs, get_error_logger_rs, get_info_logger_nt, get_error_logger_nt
import sys
import time


info_logeer_rs = get_info_logger_rs()
error_logeer_rs = get_error_logger_rs()
info_logeer_nt = get_info_logger_nt()
error_logeer_nt = get_error_logger_nt()

# 변수 세팅
resolution = '주주총회소집결의'
notice = '주주총회소집공고'
jm_code = """SELECT jm_code 
                    from gcoga000 
                    where mkt_gubun not in ('04') 
                    and pyeji_gubun = '1' 
                    and substr(jm_code, 6,1) = '0' 
                    and jm_gb_code not in ( '08', '09', '11', '13' ) 
                    order by jm_nm
          """
start_msg_rs = """------------------------------ Start Crawl rs ------------------------------"""
start_msg_nt = """------------------------------ Start Crawl nt ------------------------------"""
end_msg_rs = """------------------------------ End Crawl rs ------------------------------"""
end_msg_nt = """------------------------------ End Crawl nt ------------------------------"""

def get_crawl_time(gubun):
    try:
        conn = get_dbcon('esg')
        cursor = conn.cursor()

        ld_select = "select c_time from proxy000 where notice_gb = '{0}'".format(gubun)

        cursor.execute(ld_select)
        last_date = cursor.fetchone()

        return last_date[0]
    finally:
        cursor.close()
        close_dbcon(conn)

def set_crawl_time(time, gubun):
    try:
        conn = get_dbcon('esg')
        cursor = conn.cursor()

        upd_ctime = """update proxy000
                       set c_time = '{0}'
                       where notice_gb = '{1}'
                    """.format(time, gubun)

        cursor.execute(upd_ctime)
    finally:
        cursor.close()
        close_dbcon(conn)

# 주총결의/공고 문서번호
def get_rcplist(time, gubun):
    if gubun == 'R':
        document_gb = resolution
        info_logeer_rs.info(start_msg_rs)
    else:
        document_gb = notice
        info_logeer_nt.info(start_msg_nt)

    try:
        conn = get_dbcon('esg')
        cursor = conn.cursor()
        # 수집 기간은 [last_time] ~ [수집 시작 시점]
        rcp_select = """SELECT crp_cd, rpt_nm, rcp_no, date_format(regdate, '%Y%m%d%H%i%s'), crp_cls FROM gsmda000 WHERE crp_cd IN ({0})
                    AND regdate > '{1}'
                    AND rpt_nm LIKE '%{2}%'
                    AND rpt_nm NOT LIKE '%첨부정정%'
                    ORDER BY regdate
              """.format(jm_code, time, document_gb)
        rcp_test = "select crp_cd, rpt_nm, rcp_no, date_format(regdate, '%Y%m%d%H%i%s'), crp_cls from gsmda000 where rcp_no = '20190320800644'"

        cursor.execute(rcp_select)
        rcpnos = cursor.fetchall()

        result = []
        jm_list = []
        for rcpno in rcpnos:
            # 중복체크
            dup_select = "select * from proxy011 where rcp_no = '{0}'".format(rcpno[2])
            cursor.execute(dup_select)
            if cursor.rowcount > 0:
                dup_msg = 'Duplicated rcp_no. (jm_code : [{0}])'.format(rcpno[0])
                if gubun == 'R':
                    info_logeer_rs.info(dup_msg)
                else:
                    info_logeer_nt.info(dup_msg)
                continue

            # 수집 목록 리스트
            result.append(rcpno)
            jm_list.append(rcpno[0])
        if gubun == 'R':
            info_logeer_rs.info('jm_code list : {0}'.format(jm_list))
        else:
            info_logeer_nt.info('jm_code list : {0}'.format(jm_list))

        return result
    except Exception as e:
        if gubun == 'R':
            error_logeer_rs.error(e)
        else:
            error_logeer_nt.error(e)
    finally:
        cursor.close()
        close_dbcon(conn)

#if __name__ == '__main__':
#    rcp_nos = get_rcplist(time)
