import sys
import os
import argparse
import datetime

def get_parser():
    parser = argparse.ArgumentParser(description="* Auto Health Report Installer *")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--install', help='install into task schedule', action='store_true')
    group.add_argument('-u', '--uninstall', help='uninstall from task schedule', action='store_true')
    parser.add_argument('-f', '--frequence', help='the frequence mode. hourly by default', choices=['hourly', 'minute'])
    parser.add_argument('-c', '--cycle', help='the interval in units of frequence(-f to specify). 2 by default', type=int)
    parser.add_argument('-t', '--terminal', help='show the terminal each time it runs. No show by default', action='store_true')
    parser.add_argument('-k', '--keep', help='still use the username and passwd in login.txt', action='store_true')
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

        # create login.txt for username and password
        if not args.keep:
            login = open('login.txt', 'w')
            username = input('username: ') + '\n'
            login.write(username)
            passwd = input('passwd: ') + '\n'
            login.write(passwd)
            province = input('省行政编号: ') + '\n'
            login.write(province)
            city = input('市行政编号: ') + '\n'
            login.write(city)
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
