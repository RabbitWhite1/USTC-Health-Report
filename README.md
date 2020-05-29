# USTC Health Report

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/RabbitWhite1/USTC-Health-Report/blob/master/LICENSE)

Windows-10 下的 USTC 健康上报脚本. 借助 Windows-10 自带的 `task schedule` 完成定时上报.

**本脚本纯属娱乐, 请认真完成健康信息上报. 本人不负责任何损失.**

由于使用的是 win10 的 `task schedule`, 需要任务执行时保证电脑在线.

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

and type in the username and passwd(**USTC统一验证**的用户名和密码), as well as the postal codes, which will simply be stored in `login.txt`.

This command will create a task that run the report script `health_report.py` every 2 hours. (to set the frequence, see [this](#jump))

Before reporting, `report.log` will be checked to prevent a duplicate report.

Don't move your `health_report.py` after installed. Or you can reinstall after that.

### Uninstall

just run

```cmd
python install.py -u
```

### <span id="jump">Set Frequence</span>

report every 3 hours:

```cmd
python install.py -i -f hourly -c 3
```

report every 1 minute:

```cmd
python install.py -i -f minute -c 1
```

### help

to get help, run

```cmd
python install.py -h
```