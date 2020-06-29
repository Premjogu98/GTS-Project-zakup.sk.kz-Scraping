from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import Global_var
import sys, os
import re
import ctypes
import pymysql.cursors
from datetime import datetime
import requests
import html
# import urllib.request
# import urllib.parse
# from googletrans import Translator


def Local_connection_links():
    a = 0
    while a == 0:
        try:
            # File_Location = open("D:\\0 PYTHON EXE SQL CONNECTION & DRIVER PATH\\zakup_sk_kz\\Location For Database & Driver.txt", "r")
            # TXT_File_AllText = File_Location.read()

            # Local_host = str(TXT_File_AllText).partition("Local_host_link=")[2].partition(",")[0].strip()
            # Local_user = str(TXT_File_AllText).partition("Local_user_link=")[2].partition(",")[0].strip()
            # Local_password = str(TXT_File_AllText).partition("Local_password_link=")[2].partition(",")[0].strip()
            # Local_db = str(TXT_File_AllText).partition("Local_db_link=")[2].partition(",")[0].strip()
            # Local_charset = str(TXT_File_AllText).partition("Local_charset_link=")[2].partition("\")")[0].strip()

            connection = pymysql.connect(host='185.142.34.92',
                user='ams',
                password='TgdRKAGedt%h',
                db='tenders_db',
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)
            return connection
        except pymysql.connect  as e:
            exc_type , exc_obj , exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" , fname ,
                  "\n" , exc_tb.tb_lineno)
            a = 0
            time.sleep(10)


# def Translate_close(text_without_translate):
#     String2 = ""
#     try:
#         String2 = str(text_without_translate)
#         url = "https://translate.google.com/m?hl=en&sl=auto&tl=en&ie=UTF-8&prev=_m&q=" + str(String2) + ""
#         response1 = requests.get(str(url))
#         response2 = response1.url
#         user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
#         headers = {'User-Agent': user_agent, }
#         request = urllib.request.Request(response2, None, headers)  # The assembled request
#         time.sleep(2)
#         response = urllib.request.urlopen(request)
#         htmldata: str = response.read().decode('utf-8')
#         trans_data = re.search(r'(?<=dir="ltr" class="t0">).*?(?=</div>)', htmldata).group(0)
#         trans_data = html.unescape(str(trans_data))
#         return trans_data
#     except:
#         return String2


def Chromedriver():
    # File_Location = open("D:\\0 PYTHON EXE SQL CONNECTION & DRIVER PATH\\zakup_sk_kz\\Location For Database & Driver.txt", "r")
    # TXT_File_AllText = File_Location.read()
    # Chromedriver = str(TXT_File_AllText).partition("Driver=")[2].partition("\")")[0].strip()
    # browser = webdriver.Chrome(Chromedriver)
    browser = webdriver.Chrome(executable_path=str(f"C:\\chromedriver.exe"))
    browser.get('https://zakup.sk.kz/')
    browser.set_window_size(1024, 600)
    browser.maximize_window()
    time.sleep(2)
    Collected_T_Number = []
    # translator = Translator()
    dis_Collected_T_Number = []
    TotalTenders1 = ''
    for TotalTenders in browser.find_elements_by_xpath("//*[@id=\"infinityScroll\"]/div[13]/div[1]/jhi-item-count/div/span"):
        TotalTenders = TotalTenders.get_attribute('innerText')
        # translator_text = translator.translate(str(TotalTenders))
        # TotalTenders = translator_text.text
        TotalTenders = TotalTenders.replace("Показано", "Showing").strip()
        TotalTenders = TotalTenders.replace("элементов", "items").strip()
        TotalTenders = TotalTenders.replace("elements.", "").strip()
        TotalTenders = TotalTenders.replace("elements", "").strip()
        TotalTenders = TotalTenders.replace("elements.", "").strip()
        TotalTenders = TotalTenders.replace(",", "").strip()
        TotalTenders = TotalTenders.partition("of")[2].partition("item")[0].strip()
        TotalTenders1 = str(TotalTenders)
    for i in range(350):
        try:
            for Tender_no in browser.find_elements_by_class_name("m-found-item__num"):
                Tender_no = Tender_no.get_attribute('innerText').replace("№" , "").strip()
                Collected_T_Number.append(Tender_no)
            try:
                for Next in browser.find_elements_by_xpath("//*[@aria-label=\"Next\"]"):
                    Next.click()
                    time.sleep(3)
                    break
            except:pass

            if TotalTenders1 == len(Collected_T_Number):
                break
        except:pass
    print("Total Links : " , len(Collected_T_Number))
       # Remove Duplicates Number or Links
    for i in Collected_T_Number:
        if i not in dis_Collected_T_Number:
            dis_Collected_T_Number.append(i)

    Insert_process(dis_Collected_T_Number,browser)


def Insert_process(dis_Collected_T_Number,browser):
    global a
    a = False
    while a == False:
        try:
            print('Collected Links: ', len(dis_Collected_T_Number))
            mydb_Local = Local_connection_links()
            mycursorLocal = mydb_Local.cursor()
            for Link in dis_Collected_T_Number:
                Global_var.Total += 1
                Tender_link = "https://zakup.sk.kz/#/ext(popup:item/" + str(Link) + "/advert)"
                commandText = "SELECT ID from zakupskkz_temptbl where doc_links = '" + str(Tender_link) + "'"
                mycursorLocal.execute(commandText)
                results = mycursorLocal.fetchall()
                if len(results) > 0:
                    print('Duplicate Tender')
                    Global_var.duplicate += 1
                    a = True
                else:
                    print('Live Tender')
                    print(Tender_link)
                    sql = "INSERT INTO zakupskkz_temptbl(doc_links)VALUES(%s)"  # Collected Link Inserting on Database
                    print('Inserted')
                    val = (str(Tender_link))
                    database_error = False
                    while database_error == False:
                        try:
                            mycursorLocal.execute(sql, val)
                            mydb_Local.commit()
                            Global_var.links_Insert_On_Database += 1
                            Global_var.Collected_link += 1
                            database_error = True
                        except Exception as e:
                            print('Error While Inserting Data On Database: ', str(e))
                            database_error = False
            print("No More Link Available !!! DONE")
            ctypes.windll.user32.MessageBoxW(0, "Collected link: " + str(
                Global_var.Collected_link) + "\n""Total: " + str(
                Global_var.Total) + "\n""Duplicate: " + str(Global_var.duplicate) + "\n""Inserted: " + str(
                Global_var.links_Insert_On_Database) + "", "Zakup.sk.kz(Links)", 1)
            Global_var.Process_End()
            a = True
            browser.close()
            sys.exit()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",
                  exc_tb.tb_lineno)
            a = False

Chromedriver()



