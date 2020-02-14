from utils import get_dbcon, close_dbcon


#
def nps001_select(rcpno):
    try:
        conn = get_dbcon('esg')
        cursor = conn.cursor()


    finally:
        cursor.close()
        close_dbcon(conn)
