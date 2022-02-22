import requests
import re
import datetime
import os
import os.path as osp
import platform
import json
import traceback
from bs4 import BeautifulSoup
from pprint import pprint
from utils import *


win10 = False
if platform.platform().find('Windows-10') != -1:
    win10 = True
    from win10toast import ToastNotifier
logger = Logger.get_logger()
dirname = osp.split(osp.realpath(__file__))[0]


def done_today(log_path):
    if not os.access(log_path, os.F_OK):
        return False
    log = open(log_path, 'r', encoding='utf-8')
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
        
        # read data.json
        with open(osp.join(dirname, 'etc', 'data.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        username = data['username']
        password = data['passwd']
        data_template = data['data_template']
        jinji_lxr = data['jinji_lxr']
        jinji_guanxi = data['jinji_guanxi']
        jiji_mobile = data['jiji_mobile']
        if data_template == 'abroad':
            country = data['country']
            abroad_status_detail = data['abroad_status_detail']
        elif data_template == 'home':
            province = data['province_postcode']
            city = data['city_postcode']
            town = data['town_postcode']
            if len(province) != 6 or len(city) != 6:
                logger.info(f'邮政编码格式有误, 请确认. (povince={province}, city={city}, town={town})')
                toast(f'邮政编码格式有误, 请确认. (povince={province}, city={city}, town={town})')
                return 1

        # 登录
        response_html = login(session, username, password)
        # print(response_html)
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
                "has_fever": "0", "last_touch_sars": "0", "last_touch_sars_date": "", "last_touch_sars_detail": "", 
                "is_danger": "0",
                "is_goto_danger": "0",
                # 注: 这傻逼命名法是健康打卡系统 POST 参数的傻逼命名
                'jinji_lxr': jinji_lxr, 'jinji_guanxi': jinji_guanxi, "jiji_mobile": jiji_mobile,
                "other_detail": "",
            }
        elif data_template == 'home':   
            # 在国内且不在学校
            # now_status 2 表示在家, 6 表示其他
            param = {
                "_token": token,
                "now_address": "1", "gps_now_address": "",
                "now_province": province, "gps_province": "",
                "now_city": city, "gps_city": "", 
                "now_country": town, "gps_country": "", "now_detail": "",
                "body_condition": "1", "body_condition_detail": "",  "now_status": "2", "now_status_detail": "",
                "has_fever": "0", "last_touch_sars": "0", "last_touch_sars_date": "", "last_touch_sars_detail": "",
                "is_danger": "0", "is_goto_danger": "0",
                # 注: 这傻逼命名法是健康打卡系统 POST 参数的傻逼命名
                'jinji_lxr': jinji_lxr, 'jinji_guanxi': jinji_guanxi, "jiji_mobile": jiji_mobile, "other_detail": ""
            }
        else:
            # 默认在校, 且西校区
            # TODO: 未补充 Town 相关.
            province = '340000'
            city = '340100'
            town = '340104'
            param = {
                "_token": token,
                "now_address": "1", "gps_now_address": "", "now_province": province, # 安徽省编码
                "gps_province": "", "now_city": city, "gps_city": "",
                "now_country": town, "gps_country": "",
                "now_detail": "",
                "is_inschool": "6", # 西校区
                "body_condition": "1", "body_condition_detail": "",
                "now_status": "1", "now_status_detail": "",
                "has_fever": "0",
                "last_touch_sars": "0", "last_touch_sars_date": "", "last_touch_sars_detail": "",
                "is_danger": "0", "is_goto_danger": "0",
                # 注: 这傻逼命名法是健康打卡系统 POST 参数的傻逼命名
                'jinji_lxr': jinji_lxr, 'jinji_guanxi': jinji_guanxi, "jiji_mobile": jiji_mobile,
                "other_detail": "",

            }
        print('Using these post data:')
        print(param)
        response = session.post("https://weixine.ustc.edu.cn/2020/daliy_report", data=param)
        print(f'上报结果: {response}')
    except Exception as e:
        print(str(e))
        logger.info(traceback.format_exc())
        toast('出现错误!' + str(e) + '\n')
        return 1
    else:
        if response.status_code == 200:
            message = 'succeed!'
        else:
            message = f'failed(status code: {response.status_code})! '
        if data_template == 'abroad':
            message += f'(country: {country})'
        else:
            message += f'(province: {province}, city: {city}, town: {town})'
        logger.info(message)
        toast(message)

    return 0


if __name__ == '__main__':
    main()