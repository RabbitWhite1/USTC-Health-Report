import requests
import re
import datetime
import os
import os.path as osp
import platform
import time
from bs4 import BeautifulSoup
win10 = False
if platform.platform().find('Windows-10') != -1:
    win10 = True
    from win10toast import ToastNotifier

dirname = osp.split(osp.realpath(__file__))[0]


def done_today(log_path):
    if not os.access(log_path, os.F_OK):
        return False
    log = open(log_path, 'r')
    lines = log.readlines()
    last = None
    for line in lines[::-1]:
        if line.find('succeed') != -1:
            date_str = line[2: 21]
            last = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            break
    if last:
        if last.date() == datetime.datetime.now().date():
            return True

    return False


def toast_log(message, log_path):
    f = open(log_path, 'a')
    f.write('[ ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ]\t' + message)
    f.close()
    
    if win10:
        toaster = ToastNotifier()
        toaster.show_toast('中国科大健康打卡',
                        message,
                        icon_path=None,
                        duration=5,
                        threaded=True)

def main():
    if done_today(osp.join(dirname, 'report.log')):
        return 0

    error = False
    
    try:
        headers = {
            'user-agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/79.0.3945.117 '
                'Safari/537.36',
            'connection': 'close'}

        session = requests.session()
        session.headers.update(headers)
        session.trust_env = False
        
        # login
        f = open(osp.join(dirname, 'login.txt'), 'r')
        username = f.readline().strip(" \n\t\r")
        password = f.readline().strip(" \n\t\r")
        province = f.readline().strip(" \n\t\r")
        city = f.readline().strip(" \n\t\r")
        # 默认用西校区代码
        is_inschool = "6"
        f.close()
        if len(province) != 6 or len(city) != 6:
            toast_log('邮政编码有误, 请确认. (povince={}, city={})'.format(province, city), path + 'report.log')
            return 1

        # 登录
        data = {'username': username, 'password': password,
                'service': "https://weixine.ustc.edu.cn/2020/caslogin", 'model': "uplogin.jsp",
                'warn': '', 'showCode': '', 'button': ''}
        response = session.post("https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin", data=data)
        response_html = BeautifulSoup(response.content, 'lxml').__str__()
        print(f'登陆结果: {response}')
                
        # 获取 token
        # the format is like: <input name="_token" type="hidden" value="oZxXvuJav4tIWy7nHrdR6VuOsV9WS2tgdIluFdWM"/>
        token = re.search(r'<input name="_token" type="hidden" value="(.*)"/>', response_html).group(1)
        print(token)

        # 在校的话用这个
        param = {
            "_token": token,
            "now_address": "1",
            "gps_now_address": "",
            "now_province": "340000", # 安徽省编码
            "gps_province": "",
            "now_city": "340100", # 合肥市编码
            "gps_city": "",
            "now_detail": "",
            "is_inschool": "6", # 西校区
            "body_condition": "1",
            "body_condition_detail": "",
            "now_status": "1",
            "now_status_detail": "",
            "has_fever": "0",
            "last_touch_sars": "0",
            "last_touch_sars_date": "",
            "last_touch_sars_detail": "",
            "other_detail": ""
        }
                 
        # 在家用这个
        """param = {
            "_token": token,
            "now_address": "1", "gps_now_address": "", "now_province": province, "gps_province": "",
            "now_city": city, "gps_city": "", "now_detail": "",
            "body_condition": "1", "body_condition_detail": "",  "now_status": "2", "now_status_detail": "",
            "has_fever": "0", "last_touch_sars": "0", "last_touch_sars_date": "", "last_touch_sars_detail": "", "other_detail": ""
        }"""

        province = param["now_province"]
        city = param["now_city"]
        print(f'province: {province}, city: {city}')
        response = session.post("https://weixine.ustc.edu.cn/2020/daliy_report", data=param)
        print(f'上报结果: {response}')
    except Exception as e:
        print(str(e))
        toast_log('出现错误!' + str(e) + '\n', osp.join(dirname, 'report.log'))
        return 1
    else:
        message = ('succeed!' if response.status_code == 200 else f'failed(status code: {response.sstatus_code})!') + f' (province: {province}, city: {city})\n'
        toast_log(message, osp.join(dirname, 'report.log'))

    return 0


if __name__ == '__main__':
    main()