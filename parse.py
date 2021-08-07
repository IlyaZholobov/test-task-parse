from os import name
import requests
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re 

import sqlite3
from sqlite3 import Error

result = []

names = []
with open('name.csv', newline='' ,encoding="UTF-8") as File:  
    reader = csv.reader(File)
    for row in reader:
        names.append(row[0].replace(";",""))

driver = webdriver.Chrome()
for name in names:
    page = 1
    while True:
        driver.get(f"https://focus.kontur.ru/search?query={name}&country=RU&page={page}")
        time.sleep(5)
        next = driver.find_element_by_xpath("//span[contains(text(), 'Дальше')]")
        if len(driver.find_elements_by_xpath("//span[@data-tid='entityTitle']")):
            titles = [title_el.text for title_el in driver.find_elements_by_xpath("//span[@data-tid='entityTitle']")] 
            inns =  [inn_el.text for inn_el in driver.find_elements_by_xpath("//span[@data-tid='entityRequisites_ИНН']")]
            igrns =  [igrn_el.text for igrn_el in driver.find_elements_by_xpath("//span[@data-tid='entityRequisites_ОГРН']")]
            reg_dates = [reg_date_el.text.replace(" — ","") for reg_date_el in driver.find_elements_by_xpath("//span[@data-tid='entityRequisites_Дата_регистрации']")]
            page_result =[[titles[i], inns[i],igrns[i],reg_dates[i]] for i in range(len(titles))]
            result.extend(page_result)
            next.click()
            print(result)
            page += 1
        else:
            break
    driver.close()
driver.close()

conn = None
try:
    conn = sqlite3.connect(r"sql/task.db")
    sql_create_test_table = """CREATE TABLE IF NOT EXISTS test (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        inn text NOT NULL,
                                        ogrn text NOT NULL,
                                        reg_date text NOT NULL
                                    ); """
    cur = conn.cursor()
    cur.execute(sql_create_test_table)

    sql = ''' INSERT INTO test(name,inn,ogrn,reg_date)
              VALUES(?,?,?,?) '''
    for row in  result:
        cur.execute(sql,row)
        conn.commit()
except Error as e:
    print(e)
finally:
    if conn:
        conn.close()
