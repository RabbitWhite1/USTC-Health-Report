import base64
import requests
import os
import time
import json
import os.path as osp
from bs4 import BeautifulSoup
from utils.logger import *

tmp_dir = osp.join(osp.dirname(__file__), '..', 'tmp')
tmp_img_path = osp.join(tmp_dir, 'tmp.jpg')
logger = Logger.get_logger()


baidu_api_keys = json.load(open(osp.join(osp.dirname(__file__), '..', 'etc', 'baidu_api.json')))
API_KEY = baidu_api_keys['API_KEY'] # API Key
SECRET_KEY = baidu_api_keys['SECRET_KEY'] # Secret Key
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'  # 获取token请求url
OCR_URL = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic' # 文字识别OCRAPI

def baidu_text_api(img: bytes):
    data = {
        'grant_type': 'client_credentials',
        'client_id': API_KEY,
        'client_secret': SECRET_KEY
    }
    r = requests.post(TOKEN_URL, data=data)
    if 'access_token' in r.json():
        access_token = r.json().get('access_token')
    else:
        logger.info('Please check your APP_ID, SECRET_KEY!')
        toast('Please check your APP_ID, SECRET_KEY!')
        exit(-1)

    print(access_token)
    img = base64.b64encode(open(tmp_img_path, 'rb').read())
    params = {"image": img}
    access_token = access_token
    request_url = OCR_URL + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    try:
        print(response.json())
        verification_code = response.json()['words_result'][0]['words']
    except:
        verification_code = None
    print(f'recognized code: {verification_code}')
    return verification_code


def get_verification_code(session):
    for _ in range(3):
        img = session.get(f"https://passport.ustc.edu.cn/validatecode.jsp?type=login&x={int(time.time())}").content
        if not osp.exists(tmp_dir):
            os.makedirs(tmp_dir)
        with open(tmp_img_path, 'wb') as f:
            f.write(img)
        
        # TODO: 图像识别
        verification_code = baidu_text_api(img)
        if verification_code:
            break
    
    return verification_code

def login(session, username, password):
    # login
    # 1. get `CAS_LT`
    response = session.get("https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin")
    response = BeautifulSoup(response.content, 'lxml')
    login_form = response.find_all(class_='loginForm form-style')[0]
    CAS_LT = login_form.find_next(id='CAS_LT')['value']
    # 2. get and crack the verification code
    verification_code = get_verification_code(session)
    data = {'username': username, 'password': password, 
            'showCode': '1', 'LT': verification_code, 'CAS_LT': CAS_LT,
            'service': "https://weixine.ustc.edu.cn/2020/caslogin", 'model': "uplogin.jsp",
            'warn': '', 'showCode': '', 'button': ''}
    response = session.post("https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin", data=data)
    response_html = BeautifulSoup(response.content, 'lxml').__str__()
    print(f'登陆结果: {response}')
    return response_html