from utils import get_dbcon, close_dbcon
from utils import get_comp

# 종목코드, 이사명으로 조회
def get_pecode(jm_code, name):
    try:
        conn = get_dbcon('esg')
        cursor = conn.cursor()

        qry = """SELECT t1.pe_code FROM ( 
                    SELECT c.pe_code 
                    FROM nps_gpemb002 a , ( SELECT * FROM gcoga000 WHERE jm_code = '{0}' ) b, nps_gpemb001 c 
                    WHERE a.pe_code IN (SELECT pe_code FROM nps_gpemb001 WHERE REPLACE(pe_nm, ' ', '') LIKE '%{1}%' OR REPLACE(pe_nm_eng, ' ', '') LIKE '%{2}%')
                    AND a.up_cd = b.co_code 
                    AND a.pe_code = c.pe_code 
                 UNION ALL 
                    SELECT b.pe_code 
                    FROM nps_gpemb005 a, nps_gpemb001 b, nps_gpemb002 c 
                    WHERE a.pe_code IN (SELECT pe_code FROM nps_gpemb001 WHERE REPLACE(pe_nm, ' ', '') LIKE '%{3}%' OR REPLACE(pe_nm_eng, ' ', '') LIKE '%{4}%')
                    AND a.pe_code = b.pe_code 
                    AND b.pe_code = c.pe_code 
                    AND c.up_cd = (SELECT co_code FROM gcoga000 WHERE jm_code = '{5}') 
                 UNION ALL 
                    SELECT a.pe_code 
                    FROM nps_gco0i491 a, gcoga000 b, nps_gpemb001 c 
                    WHERE a.pe_code IN (SELECT pe_code FROM nps_gpemb001 WHERE REPLACE(pe_nm, ' ', '') LIKE '%{6}%' OR REPLACE(pe_nm_eng, ' ', '') LIKE '%{7}%')
                    AND a.co_code = b.co_code 
                    AND a.pe_code = c.pe_code 
                    AND b.jm_code = '{8}' 
                    AND a.gijun_ymd = (SELECT MAX(gijun_ymd) FROM nps_gco0i491 WHERE co_code = (SELECT co_code FROM gcoga000 WHERE jm_code = '{9}'))
                    GROUP BY a.pe_code 
                 UNION ALL 
                    SELECT a.pe_code 
                    FROM nps_gpemb001 a, gcoaa001 b 
                    WHERE a.upche_gb = b.co_code 
                    AND (REPLACE(a.pe_nm, ' ', '') LIKE '%{10}%' OR REPLACE(a.pe_nm_eng, ' ', '') LIKE '%{11}%') 
                    AND a.upche_gb = (SELECT co_code FROM gcoga000 WHERE jm_code = '{12}') 
                    ) t1 GROUP BY t1.pe_code 
              """.format(jm_code, name, name, name, name, jm_code, name, name, jm_code, jm_code, name, name, jm_code)
        cursor.execute(qry)

        rows = cursor.rowcount

        # pe_code 세팅
        pe_code = ''
        if rows == 1:
            pe_code = cursor.fetchall()[0][0]

        cursor.close()

        return pe_code
    finally:
        close_dbcon(conn)

# 이사명, 생년월, 경력으로 조회
def get_pecode_career(name, birth, keyword):
    # 경력 분리
    lines = keyword.split('\n')
    keywords = [0 for x in range(len(lines))]
    check_keywords = ['전', '현', '前', '現']
    name = name.replace("'", "").replace(" ", "")
    null_cnt = []

    for i in range(0, len(keywords)):
        tmp = get_comp(lines[i]).split(' ')
        keywords[i] = tmp[0]
        if keywords[i] in check_keywords:
            keywords[i] = tmp[1]

        if keywords[i] == '-' or keywords[i] == '':
            null_cnt.append(i)

    if len(keywords) <= 1 and (keywords[0] == '-' or keywords[0] == ''):
        return ''

    try:
        conn = get_dbcon('esg')
        cursor = conn.cursor()

        # 경력 쿼리 세팅
        cont = ''
        for i in range(0, len(keywords)):
            # 빈값 or 하이픈은 패스
            if i in null_cnt:
                continue

            if i == len(keywords) - 1:
                cont += "a.content LIKE '%{0}%' ".format(keywords[i])
            else:
                cont += "a.content LIKE '%{0}%' OR ".format(keywords[i])

        qry = """SELECT c.pe_code 
                 FROM nps_gpemb005 a ,nps_gpemb001 c 
                 WHERE (REPLACE(c.pe_nm, ' ', '') LIKE '%{0}%' OR REPLACE(c.pe_nm_eng, ' ', '') LIKE '%{1}%')
                 AND c.pe_birth LIKE '{2}%'
                 AND ({3})
                 AND a.pe_code = c.pe_code 
                 GROUP BY c.pe_code
              """.format(name, name, birth, cont)

        cursor.execute(qry)

        rows = cursor.rowcount

        # pe_code 세팅
        pe_code = ''
        if rows == 1:
            pe_code = cursor.fetchall()[0][0]

        cursor.close()

        return pe_code
    finally:
        close_dbcon(conn)
