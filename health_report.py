import requests
import re
import datetime
import os
from win10toast import ToastNotifier
import platform

headers = {
            'user-agent':
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/79.0.3945.117 '
                    'Safari/537.36'
                                            }

session = requests.session()
session.headers.update(headers)

error = False

path = os.path.split(os.path.realpath(__file__))[0] + '\\'

# login
f = open(path + 'login.txt', 'r')
username = f.readline().strip(" \n\t\r")
password = f.readline().strip(" \n\t\r")
f.close()
data = {'username': username, 'password': password}
try:
    response = session.post("https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin", data=data)
    print(response)
    # print(response.text)
    # get the token
    # the format is like: <input type="hidden" name="_token" value="3RC1qDj08YCj9DXIwjGXXCaz45fLjQxm6LEX4dFt">

    raw_token = re.search(r'<input type="hidden" name="_token" value=".*">', response.text).group(0)
    str_value = 'value="'
    token = raw_token[raw_token.find(str_value) + len(str_value) : -2]
    print(token)

    param = {"_token":token,
            "now_address":"1","gps_now_address":"",
            "now_province":"350000","gps_province":"",
            "now_city":"350500","gps_city":"",
            "now_detail":"",
            "body_condition":"1","body_condition_detail":"",
            "now_status":"2","now_status_detail":"", 
            "has_fever":"0",
            "last_touch_sars":"0","last_touch_sars_date":"","last_touch_sars_detail":"",
            "last_touch_hubei":"0","last_touch_hubei_date":"","last_touch_hubei_detail":"",
            "last_cross_hubei":"0","last_cross_hubei_date":"","last_cross_hubei_detail":"",
            "return_dest":"1","return_dest_detail":"","other_detail":""}

    response = session.post("https://weixine.ustc.edu.cn/2020/daliy_report", data=param)
    print(response)
except Exception as e:
    message = str(e) + '\n'
    f = open(path + 'report.log', 'a')
    f.write('[ ' + datetime.datetime.now().__str__() + ' ]\t' + message)
    f.close()
    
    if platform.platform().find('Windows-10') != -1:
        toaster = ToastNotifier()
        toaster.show_toast("中国科大健康打卡",
                        "出现错误！" + message,
                        icon_path=None,
                        duration=5,
                        threaded=True)
else:
    message = ('succeed!' if response.status_code == 200 else 'failed(status code: )!'.format(response.sstatus_code)) + '\n'
    f = open(path + 'report.log', 'a')
    f.write('[ ' + datetime.datetime.now().__str__() + ' ]\t' + message)
    f.close()
    
    if platform.platform().find('Windows-10') != -1:
        toaster = ToastNotifier()
        toaster.show_toast("中国科大健康打卡",
                        message,
                        icon_path=None,
                        duration=5,
                        threaded=True)

