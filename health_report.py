import requests
import re
import datetime
import os
import os.path as osp
import platform
import time
import json
from bs4 import BeautifulSoup
from pprint import pprint
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
        with open(osp.join(dirname, 'data.json'), 'r', encoding='utf-8') as f:
            data = json.load(f, encoding='utf-8')
        username = data['username']
        password = data['passwd']
        data_template = data['data_template']
        if data_template == 'abroad':
            country = data['country']
            abroad_status_detail = data['abroad_status_detail']
        else:
            province = data['province_postcode']
            city = data['city_postcode']
            if len(province) != 6 or len(city) != 6:
                toast_log('邮政编码格式有误, 请确认. (povince={}, city={})'.format(province, city), osp.join(dirname, 'report.log'))
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
        print(f'token: {token}')

        if data_template == 'abroad':
            # 在国外
            param = {
                "_token": token,
                "now_address": "3", "gps_now_address": "", "gps_province": "",
                "gps_city": "", "now_detail": country,
                "body_condition": "1", "body_condition_detail": "",  "now_status": "6", "now_status_detail": abroad_status_detail,
                "has_fever": "0", "last_touch_sars": "0", "last_touch_sars_date": "", "last_touch_sars_detail": "", "other_detail": ""
            }
        elif data_template == 'home':   
            # 在国内且不在学校
            # now_status 2 表示在家, 6 表示其他
            param = {
                "_token": token,
                "now_address": "1", "gps_now_address": "", "now_province": province, "gps_province": "",
                "now_city": city, "gps_city": "", "now_detail": "",
                "body_condition": "1", "body_condition_detail": "",  "now_status": "2", "now_status_detail": "",
                "has_fever": "0", "last_touch_sars": "0", "last_touch_sars_date": "", "last_touch_sars_detail": "", "other_detail": ""
            }
        else:
            # 默认在校, 且西校区
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
        print('Using these post data:')
        pprint(param)
        response = session.post("https://weixine.ustc.edu.cn/2020/daliy_report", data=param)
        print(f'上报结果: {response}')
    except Exception as e:
        print(str(e))
        toast_log('出现错误!' + str(e) + '\n', osp.join(dirname, 'report.log'))
        return 1
    else:
        if response.status_code == 200:
            message = 'succeed!'
        else:
            message = f'failed(status code: {response.status_code})! '
        if data_template == 'abroad':
            message += f'(country: {country})\n'
        else:
            message += f'(province: {province}, city: {city})\n'
        toast_log(message, osp.join(dirname, 'report.log'))

    return 0


if __name__ == '__main__':
    main()