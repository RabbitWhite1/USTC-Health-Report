# USTC Health Report

Windows-10 下的 USTC 健康上报脚本. 借助 Windows-10 自带的 `task schedule` 完成定时上报.

## Special Package Requirements

This script need `win10toast` to toast. run this to install:

```cmd
pip install win10toast
```

## Usage

### Install

To install the script into `task schedule`, run

```cmd
python install.py -i
```

and type in the username and passwd(**USTC统一验证**的用户名和密码), which will simply be stored in `login.txt`.

This command will create a task that run the report script `health_report.py` every 2 hours. (to set the frequence, see [this](#jump))

### Uninstall

just run

```cmd
python install.py -u
```

### <span id="jump">Others</span>

to get help, run

```cmd
python install.py -h
```