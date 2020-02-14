import pymysql
import re


# 지배구조연구소 connect
def conn():

    conn = pymysql.connect(host='103.60.127.15',user='esg', password='esg',db='esg',charset='utf8')
    return conn


# 2칸이상 공백 제거 함수
def rem_space(lst):
    for i in range(len(lst)):
        str = lst[i]
        lst[i] = " ".join(str.split())

    return lst


# 위의 단계가 지난 후에 의안 맨 왼쪽에 ' ' 들어갈 수 있음, 모두 제거하는 코드
def lstrip_bill(bill):
    for i in range(len(bill)):
        bill[i] = bill[i].lstrip()

    return bill


# 리스트를 순회하면서 빈 엘리멘트 삭제
def del_void(bill):
    a_lst = bill
    b_list = [x for x in a_lst if x]

    return b_list