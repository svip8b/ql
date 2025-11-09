import os
import requests
import json
import time
import random
from datetime import datetime
import asyncio
from notify import send

# --- Configuration ---
NOTIFY_ENABLED = 1  # 0 for off, 1 for on
GMJK_COOKIE_ENV_VAR = 'GMJK_Cookie'
HOST = 'api.digital4danone.com.cn'
HOSTNAME = f'https://{HOST}'

# Global variables
msg = ""
user_cookie_arr = []
ck = []  # [remark, X-Access-Token, openId, unionId]
mobile = ''
current_task_date = ''

# --- Helper Functions ---

def double_log(data):
    """打印日志到控制台"""
    print(data)

def add_notify(data):
    """添加通知消息"""
    global msg
    print(data)
    msg += data + "\n"

def get_ua():
    """生成随机User-Agent"""
    os_version_major = random.randint(13, 14)
    os_version_minor = random.randint(3, 6)
    os_version_patch = random.randint(1, 3)
    os_version = f"{os_version_major}.{os_version_minor}.{os_version_patch}"
    return f"Mozilla/5.0 (iPhone; CPU iPhone OS {os_version.replace('.', '_')} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0(0x18000000)"

def random_num(min_val, max_val):
    """生成指定范围内的随机数"""
    return random.randint(min_val, max_val)

async def send_notification(message):
    """异步发送通知（含完整错误处理）"""
    if not message or not NOTIFY_ENABLED:
        return
    
    try:
        account_messages = {}
        current_account = ''
        lines = message.split('\n')

        for line in lines:
            if line.startswith('👤'):
                current_account = line.strip()
                account_messages[current_account] = []
            elif current_account and line.strip():
                account_messages[current_account].append(line.strip())

        formatted_msg = ''
        accounts = list(account_messages.keys())

        for i, account in enumerate(accounts):
            formatted_msg += f"{account}\n"
            formatted_msg += '\n'.join(account_messages[account])

            if i < len(accounts) - 1:
                formatted_msg += '\n------------------------------\n'

        # 实际场景中这里应集成通知服务（如Server酱、PushPlus等）
        print("\n--- 通知汇总 ---\n")
        print(formatted_msg)
        print("\n-------------------\n")
        send('达能益生',f'{formatted_msg}\n————————————\n')
        return True  # 明确返回成功状态
    except Exception as e:
        add_notify(f"❌ 通知发送异常: {str(e)}")
        return False  # 异常时返回失败状态

# --- API交互函数（优化异步调用与错误处理）---

def get_member_info(timeout=2):
    """查询会员信息（同步函数）"""
    global mobile
    url = f"{HOSTNAME}/healthyaging/danone/wx/ha/haUser/info"
    headers = {
        'Host': HOST,
        'Connection': 'keep-alive',
        'User-Agent': get_ua(),
        'X-Access-Token': ck[1],
        'Content-Type': 'application/json',
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 200:
            mobile = result['result']['mobile']
            add_notify(f"👤 {ck[0] or '未备注'}")
        else:
            add_notify(f"❌ {ck[0] or '未备注'} 获取信息失败: {result.get('message', '未知错误')}")
    except requests.exceptions.RequestException as e:
        add_notify(f"❌ {ck[0] or '未备注'} 信息请求异常: {str(e)}")
    except json.JSONDecodeError:
        add_notify(f"❌ {ck[0] or '未备注'} 信息解析异常")

def report_event(timeout=2):
    """上报事件（同步函数）"""
    url = f"{HOSTNAME}/healthyaging/danone/wx/config/eventReport"
    headers = {
        'Host': HOST,
        'Connection': 'keep-alive',
        'User-Agent': get_ua(),
        'X-Access-Token': ck[1],
        'Content-Type': 'application/json',
    }
    payload = {
        "content": "挑战页-浏览",
        "name": "maievent-page-view",
        "type": "view",
        "mobile": mobile,
        "openId": ck[2],
        "unionId": ck[3],
        "page": "/pages/challenge3/challenge3",
        "source": "wechat-default",
        "sdk": "ha-default"
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 200:
            double_log("✅ 事件上报成功")
        else:
            add_notify(f"⚠️ 上报失败: {result.get('message', '未知错误')}")
    except requests.exceptions.RequestException as e:
        add_notify(f"❌ 上报请求异常: {str(e)}")
    except json.JSONDecodeError:
        add_notify(f"❌ 上报异常")

async def get_user_tasks(timeout=2):
    """获取用户任务列表并执行（异步函数）"""
    global current_task_date
    url = f"{HOSTNAME}/healthyaging/danone/wx/ha/selfcare/getCalendar"
    headers = {
        'Host': HOST,
        'Connection': 'keep-alive',
        'User-Agent': get_ua(),
        'X-Access-Token': ck[1],
        'Content-Type': 'application/json',
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 200 and result.get('result') and result['result'].get('taskCalendarList'):
            today_tasks = next((task for task in result['result']['taskCalendarList'] if task.get('istoday')), None)

            if today_tasks and today_tasks.get('taskDetailsVoList'):
                current_task_date = today_tasks['taskDate']
                add_notify(f"✅ 获取{current_task_date}的任务成功")

                tasks = today_tasks['taskDetailsVoList']
                for task in tasks:
                    if task.get('status') == 1:  # 处理未完成任务
                        await execute_task_based_on_type(task)
                        await asyncio.sleep(random_num(3, 5))  # 改用asyncio.sleep
                    else:
                        add_notify(f"✅ 已完成 {task.get('simpleName', '未知任务')}")
            else:
                add_notify("🔍 今日无可用任务")
        else:
            add_notify("🔍 今日无可用任务")
    except requests.exceptions.RequestException as e:
        add_notify(f"❌ 任务获取请求异常: {str(e)}")
    except json.JSONDecodeError:
        add_notify(f"❌ 任务获取异常")

async def execute_task_based_on_type(task):
    """根据任务类型执行任务（异步函数）"""
    try:
        rule_ids = []
        task_data_value = None

        view_code = task.get('viewCode')
        option_list = task.get('optionList', [])
        rule_list = task.get('ruleList', [])

        if view_code == "PICKER":
            picker_option = next((opt for opt in option_list if opt.get('checkinStatus') == 1), None)
            if picker_option:
                rule_ids = [picker_option['id']]
                task_data_value = picker_option['name']
        elif view_code == "WATER":
            water_option = option_list[-1] if option_list else None
            if water_option:
                rule_ids = [water_option['id']]
                task_data_value = water_option['name']
        elif view_code == "MULTI":
            multi_options = [opt for opt in option_list if opt.get('checkinStatus') == 1]
            if multi_options:
                rule_ids = [opt['id'] for opt in multi_options]
                task_data_value = ','.join([opt['name'] for opt in multi_options])
        else:  # 处理"FOOD", "WERUN"等类型
            if rule_list and rule_list[0].get('id'):
                rule_ids = [rule_list[0]['id']]
            else:
                rule_ids = [task['id']]

        if not rule_ids:
            if rule_list and rule_list[0].get('id'):
                rule_ids = [rule_list[0]['id']]
            else:
                rule_ids = [task['id']]

        await execute_task(
            rule_ids[0],
            task.get('userTaskDetailId'),
            task.get('simpleName', ''),
            rule_ids,
            task_data_value
        )

    except Exception as e:
        add_notify(f"❌ 执行 {task.get('simpleName', '未知任务')} 异常: {str(e)}")

async def execute_task(rule_id, task_id, task_name="", rule_ids=None, task_data_value=None, timeout=2):
    """执行具体任务（异步函数）"""
    if rule_ids is None:
        rule_ids = []

    url = f"{HOSTNAME}/healthyaging/danone/wx/clockin/clickIn"
    headers = {
        'Host': HOST,
        'Connection': 'keep-alive',
        'User-Agent': get_ua(),
        'X-Access-Token': ck[1],
        'Content-Type': 'application/json',
    }
    payload = {
        "ruleIds": rule_ids if rule_ids else [rule_id],
        "taskDataCode": "Auto",
        "taskDataValue": task_data_value,
        "userTaskDetailId": task_id
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 200:
            add_notify(f"✅ 执行 {task_name or '任务'} 成功")
        else:
            add_notify(f"⚠️ 执行 {task_name or '任务'} 失败: {result.get('message', '未知错误')}")
    except requests.exceptions.RequestException as e:
        add_notify(f"❌ 执行 {task_name or '任务'} 请求异常: {str(e)}")
    except json.JSONDecodeError:
        add_notify(f"❌ 执行 {task_name or '任务'} 异常")

# --- 主逻辑优化 ---

async def check_environments():
    """检查环境变量（异步函数）"""
    global user_cookie_arr
    user_cookie = os.getenv(GMJK_COOKIE_ENV_VAR)
    if not user_cookie:
        double_log(f"❌ 请先设置环境变量 {GMJK_COOKIE_ENV_VAR}")
        double_log("格式：备注#X-Access-Token#openId#unionId，多账号换行")
        return False

    user_cookie_arr = [item.strip() for item in user_cookie.split("\n") if item.strip()]
    if not user_cookie_arr:
        double_log("❌ 未找到有效的账号配置")
        return False

    double_log(f"✅ 共找到 {len(user_cookie_arr)} 个账号")
    return True

async def execute_all_tasks():
    """多账号任务执行主循环（异步函数）"""
    global ck, msg

    if not await check_environments():
        return

    for index, user_data in enumerate(user_cookie_arr):
        num = index + 1
        ck = user_data.split("#")
        remark = ck[0] if len(ck) > 0 else f"账号{num}"
        double_log(f"\n======== 开始 {remark} ========")
        msg = ""  # 重置当前账号的消息
        try:
            await execute_tasks()
        except Exception as e:
            add_notify(f"❌ 任务执行异常: {str(e)}")

        # 发送当前账号的通知
        if msg and NOTIFY_ENABLED:
            await send_notification(msg)
        
        if index < len(user_cookie_arr) - 1:
            await asyncio.sleep(5)  # 改用asyncio.sleep

async def execute_tasks():
    """单个账号的任务执行（异步函数）"""
    try:
        get_member_info()
        await asyncio.sleep(random_num(3, 5))  # 改用asyncio.sleep
        report_event()
        await asyncio.sleep(random_num(3, 5))  # 改用asyncio.sleep
        await get_user_tasks()
    except Exception as e:
        add_notify(f"❌ 任务执行异常: {str(e)}")

# --- 入口点 ---
if __name__ == "__main__":
    asyncio.run(execute_all_tasks())