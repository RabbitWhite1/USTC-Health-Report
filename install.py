import sys
import os
import os.path as osp
import argparse
import json
from utils.logger import Logger

logger = Logger.get_logger()

def get_parser():
    parser = argparse.ArgumentParser(description="* Auto Health Report Installer *")
    parser.add_argument('action', help='install|update|uninstall. Here update is for setting frequency.', choices=['install', 'update', 'uninstall'])
    parser.add_argument('-f', '--frequence', default='hourly', help='the frequence mode. hourly by default', choices=['hourly', 'minute'])
    parser.add_argument('-c', '--cycle', default=2, help='the interval in units of frequence(-f to specify). 2 by default', type=int)
    parser.add_argument('-t', '--terminal', help='show the terminal each time it runs. No show by default', action='store_true')
    parser.add_argument('-k', '--keep', help='still use the username and passwd in etc/data.json', action='store_true')
    parser.add_argument('-l', '--location', default='school', help='abroad|school|home', choices=['abroad', 'school', 'home'])
    return parser


def create_task(args):
    # check is pythonw.exe accessible
    executable_path = sys.executable
    executable_w_path = executable_path[:-4] + 'w.exe'
    if os.access(executable_w_path, os.F_OK) and not args.terminal:
        executable_path = executable_w_path
    # get the path of install.py to get the path of health_report.py
    path = os.path.split(os.path.realpath(__file__))[0]
    if not os.access(path, os.F_OK):
        logger.error('cannot access the health_report.py')
        return 1
    logger.info(f'using {executable_path}')
    # create the task
    path = osp.join(path, 'health_report.py')
    logger.info(f'汇报频率: {args.cycle} {args.frequence}')
    command = f'schtasks /create /sc {args.frequence} /mo {args.cycle} /tn "Health Report" /tr "{executable_path} {path}"'
    os.system(command)
    logger.info('installed the task')
    logger.info('记得在 etc/baidu_api.json 中写入相应的 key 噢!(否则如需验证码会失败)')


def main():
    parser = get_parser()
    args = parser.parse_args()    
        
    # do command
    if args.action == 'install':
        # create etc/data.json for username and password
        args.location = input("abroad|school|home: ")
        login = open('etc/data.json', 'w', encoding='utf-8')
        data = {}
        data['username'] = input('学号: ')
        data['passwd'] = input('密码: ')
        data['dorm_building'] = input('宿舍楼号: ')
        data['dorm'] = input('宿舍房号: ')
        data['jinji_lxr'] = input('紧急联系人: ')
        data['jinji_guanxi'] = input('与本人关系: ')
        data['jiji_mobile'] = input('紧急联系人电话: ')
        if args.location == 'abroad':
            data['data_template'] = 'abroad'
            data['country'] = input('所在国家/地区: ')
            data['abroad_status_detail'] = input('在国外详细情况: ')
        elif args.location == 'school':
            data['data_template'] = 'school'
        else:
            assert args.location == 'home'
            data['data_template'] = 'home'
            data['province_postcode'] = input('省行政编号(好像是身份证前六位相关): ')
            data['city_postcode'] = input('市行政编号(好像是身份证前六位相关): ')
            data['town_postcode'] = input('县行政编号(好像是身份证前六位): ')
        login.write(json.dumps(data, ensure_ascii=False))
        login.close()
        logger.info(f'configurations writen to "etc/data.json"')
        create_task(args)
    elif args.action == 'update':
        create_task(args)
    elif args.action == 'uninstall':
        command = 'schtasks /delete /tn "Health Report"'
        os.system(command)
        logger.info('uninstalled the task')

    return 0


if __name__ == '__main__':
    main()
