import sys
import os
import argparse
import datetime
import json

def get_parser():
    parser = argparse.ArgumentParser(description="* Auto Health Report Installer *")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--install', help='install into task schedule', action='store_true')
    group.add_argument('-u', '--uninstall', help='uninstall from task schedule', action='store_true')
    parser.add_argument('-f', '--frequence', help='the frequence mode. hourly by default', choices=['hourly', 'minute'])
    parser.add_argument('-c', '--cycle', help='the interval in units of frequence(-f to specify). 2 by default', type=int)
    parser.add_argument('-t', '--terminal', help='show the terminal each time it runs. No show by default', action='store_true')
    parser.add_argument('-k', '--keep', help='still use the username and passwd in etc/data.json', action='store_true')
    parser.add_argument('-a', '--abroad', help='if you are abroad', action='store_true')
    parser.add_argument('-s', '--school', help="if you are at school(I assume students living in non-west campus won't use this script.)", action='store_true')
    parser.add_argument('-o', '--home', help="if you are at home", action='store_true')
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    # set frequence
    frequence = 'hourly'
    if args.frequence:
        frequence = args.frequence

    # set cycle
    cycle = 2
    if args.cycle:
        cycle = args.cycle

    # check is pythonw.exe accessible
    executable = sys.executable
    executable_w = executable[:-4] + 'w.exe'
    if os.access(executable_w, os.F_OK) and not args.terminal:
        executable = executable_w
        
    # do command
    if args.install:
        # check win10toast
        try:
            import win10toast
        except ModuleNotFoundError as e:
            print(e)
            print('please install win10toast: pip install win10toast')
            return 1

        # create etc/data.json for username and password
        if not args.keep:
            location = input("abroad|school|home: ")
            if location == 'abroad':
                args.abroad = True
            elif location == 'school':
                args.school = True
            elif location == 'home':
                args.home = True
            else:
                print('wrong input!')
            login = open('etc/data.json', 'w', encoding='utf-8')
            data = {}
            username = input('username: ')
            data['username'] = username
            passwd = input('passwd: ')
            data['passwd'] = passwd
            if args.abroad:
                data['data_template'] = 'abroad'
                data['country'] = input('所在国家/地区: ')
                data['abroad_status_detail'] = input('在国外详细情况: ')
            else:
                if args.school:
                    data['data_template'] = 'school'
                else:
                    data['data_template'] = 'home'
                    province = input('省行政编号(好像是身份证前六位相关): ')
                    data['province_postcode'] = province
                    city = input('市行政编号(好像是身份证前六位相关): ')
                    data['city_postcode'] = city
                    town = input('县行政编号(好像是身份证前六位): ')
                    data['town_postcode'] = town
            login.write(json.dumps(data, ensure_ascii=False))
            login.close()

        # get the path of install.py to get the path of health_report.py
        path = os.path.split(os.path.realpath(__file__))[0]
        if not os.access(path, os.F_OK):
            print('cannot access the health_report.py')
            return 1
        print('using', executable)

        # create the task
        command = 'schtasks /create /sc {} /mo {} /tn "Health Report" /tr "{} {}"'.format(frequence, cycle, executable, path + '\health_report.py')
        os.system(command)
        f = open('report.log', 'a')
        f.write('[ ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ]\t' + 'installed the task!\n')
        f.close()
    elif args.uninstall:
        command = 'schtasks /delete /tn "Health Report"'
        os.system(command)
        f = open('report.log', 'a')
        f.write('[ ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ]\t' + 'uninstalled the task!\n')
        f.close()

    return 0



if __name__ == '__main__':
    main()
