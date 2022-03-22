# USTC Health Report

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/RabbitWhite1/USTC-Health-Report/blob/master/LICENSE)

Windows 下的 USTC 健康上报脚本. 借助 Windows 自带的 `task schedule` 完成定时上报, 并用 Windows 的消息提示来提醒上报成功与否.

**本脚本纯属娱乐, 请认真完成健康信息上报. 本人不负责任何损失.**

由于使用的是 Windows 的 `task schedule`, 需要任务执行时保证电脑在线. 可以通过修改上报频率提高上报成功率. 

## Special Package Requirements

This script need `win10toast` to toast. run this to install:

```cmd
# necessary
pip install urllib3==1.25.8
# for fancy
pip install win10toast
pip install rich
```

## Usage

### Install

To install the script into `task schedule`, 
1. run

```cmd
python install.py install
```

and type in the username and passwd(**USTC统一验证**的用户名和密码), as well as the postal codes, which will simply be stored in `data.json`.

2. put a json file in `etc/baidu_api.json`, with the following format: 
```json
{
    "API_KEY": "AAAAAAAAAAAAAAAAAAAAAAAA",
    "SECRET_KEY": "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
}
```

That's all!

This command will create a task that run the report script `health_report.py` every 2 hours. (to set the frequence, see [this](#jump))

Before reporting, `report.log` will be checked to prevent a duplicate report.

Don't move your `health_report.py` after installed. Or you can reinstall after that.

### Uninstall

just run

```cmd
python install.py uninstall
```

### <span id="jump">Set Frequence</span>

report every 3 hours:

```cmd
# if you need to re type-in your information
python install.py install -f hourly -c 3
# if you want to keep config, run
python install.py update -f hourly -c 3
```

report every 1 minute:

```cmd
python install.py install -f minute -c 1
# if you want to keep config, run
python install.py update -f minute -c 1
```

### help

to get help, run

```cmd
python install.py -h
```
