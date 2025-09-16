import requests
import json
import time
import sys
from datetime import datetime, timezone, timedelta

infourl = "https://ajax.unileverfoodsolutions.com.cn/api/ufscmcmall/member/level-info"
inforurl1 = "https://consumer-api.unileverfoodsolutions.com.cn/v2/getMember"
tasklist = "https://consumer-api.unileverfoodsolutions.com.cn/v2/memberTasks"
comreward = "https://consumer-api.unileverfoodsolutions.com.cn/modules/ufscmcmall/loyalty/task/simple-complete"
receive = "https://consumer-api.unileverfoodsolutions.com.cn/modules/ufscmcmall/loyalty/task/reward"


def get_current_score(access_token=""):
    params1 = {
        "maijsVersion": "1.51.0",
        "clientId": "019950c7-ca1a-3821-361e-4b346d26d1ea",
        "appName": "家乐好礼屋",
        "envVersion": "release",
        "clientTime": ""
    }
    header1 = {
        "Host": "consumer-api.unileverfoodsolutions.com.cn",
        "Connection": "keep-alive",
        "X-Account-Id": "577c98c4905e88311f8b474a",
        "Accept": "application/json, text/plain, */*",
        "xweb_xhr": "1",
        "X-Requested-With": "XMLHttpRequest",
        "X-Access-Token": access_token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13)XWEB/14315",
        "Content-Type": "application/x-www-form-urlencoded",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wx57048525e48315b4/193/page-frame.html",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    try:
        params1["clientTime"] = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
        resp = requests.post(inforurl1, headers=header1, params=params1, data={})
        data = resp.json()
        score = int(data.get("score", 0) or 0)
        return score
    except Exception:
        return 0


def complete_task(code, task_name="", reward_score=None, access_token=""):
    params = {
        "maijsVersion": "1.51.0",
        "clientId": "01995244-878a-87e0-ec76-b73723b236b2",
        "appName": "家乐质选",
        "envVersion": "release",
        "clientTime": ""
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit(537.36) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13)XWEB/14315",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Account-Id": "577c98c4905e88311f8b474a",
        "xweb_xhr": "1",
        "X-Requested-With": "XMLHttpRequest",
        "X-Access-Token": access_token,
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wx41739acc7c0aca05/181/page-frame.html",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    payload = {"code": code}
    name_part = task_name if task_name else code
    reward_part = str(reward_score) if reward_score is not None else "未知"
    print(f"正在做{name_part} 奖励为{reward_part}", flush=True)
    try:
        params["clientTime"] = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
        resp = requests.post(comreward, headers=headers, params=params, json=payload)
        print(f"完成接口状态码：{resp.status_code}", flush=True)
        try:
            body = resp.json()
            print(json.dumps(body, ensure_ascii=False), flush=True)
            return 200 <= resp.status_code < 300
        except json.JSONDecodeError:
            print(resp.text, flush=True)
            return resp.ok
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}", flush=True)
    return False


def receive_reward(code, task_name="", access_token=""):
    params = {
        "maijsVersion": "1.51.0",
        "clientId": "01995244-878a-87e0-ec76-b73723b236b2",
        "appName": "%E5%AE%B6%E4%B9%90%E5%A5%BD%E7%A4%BC%E5%B1%8B",
        "envVersion": "release",
        "clientTime": ""
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13)XWEB/14315",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Account-Id": "577c98c4905e88311f8b474a",
        "xweb_xhr": "1",
        "X-Requested-With": "XMLHttpRequest",
        "X-Access-Token": access_token,
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wx57048525e48315b4/193/page-frame.html",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    payload = {"code": code}
    name_part = task_name if task_name else code
    print(f"正在领取{name_part}任务的奖励", flush=True)
    try:
        params["clientTime"] = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
        resp = requests.post(receive, headers=headers, params=params, json=payload)
        print(f"领取接口状态码：{resp.status_code}", flush=True)
        try:
            print(json.dumps(resp.json(), ensure_ascii=False), flush=True)
        except json.JSONDecodeError:
            print(resp.text, flush=True)
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}", flush=True)


def complete_first_doable_n_times(times=10):
    params = {
        "maijsVersion": "1.51.0",
        "clientId": "019950c7-ca1a-3821-361e-4b346d26d1ea",
        "appName": "家乐好礼屋",
        "envVersion": "release",
        "listCondition.page": "1",
        "listCondition.perPage": "100",
        "isEnabled.value": "true",
        "clientTime": "2025-09-16T19:13:56.270+08:00"
    }
    header = {
        "Host": "consumer-api.unileverfoodsolutions.com.cn",
        "Connection": "keep-alive",
        "X-Account-Id": "577c98c4905e88311f8b474a",
        "Accept": "application/json, text/plain, */*",
        "xweb_xhr": "1",
        "X-Requested-With": "XMLHttpRequest",
        "X-Access-Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhaWQiOiI1NzdjOThjNDkwNWU4ODMxMWY4YjQ3NGEiLCJhdWQiOiJtb2JpbGUiLCJleHAiOjE3NTgwNDQ5MDEsImlhdCI6MTc1ODAyMzMwMSwiaXNzIjoibW9iaWxlIiwic3ViIjoibWVtYmVyOjY3ODc4NjQ1MzRlMWJiMDAyYTdiZmFlYSJ9.v_osPu37dhVWPM5FF9nX5U1XFKTjfB869RUXPQkUsGg",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13)XWEB/14315",
        "Content-Type": "application/json",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wx57048525e48315b4/193/page-frame.html",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    try:
        re = requests.get(tasklist, headers=header, params=params)
        data = re.json() if re is not None else {}
    except requests.exceptions.RequestException as e:
        print(f"获取任务列表失败：{e}")
        return

    items = data.get("items", []) if isinstance(data, dict) else []
    first = None
    for it in items:
        if not isinstance(it, dict):
            continue
        if not it.get("isEnabled", False):
            continue
        member = it.get("memberReward", {}) or {}
        if not member.get("hasLeftTaskRewards", False):
            continue
        first = it
        break

    if not first:
        print("没有可做的任务")
        return

    name = first.get("name") or ""
    code = first.get("code") or ""
    reward = 0
    try:
        reward = ((first.get("rewards") or [{}])[0].get("score") or {}).get("value", 0)
    except Exception:
        reward = 0

    for _ in range(times):
        success = complete_task(code, task_name=name, reward_score=reward)
        print("完成成功，准备领取...", flush=True) if success else None
        time.sleep(1.5)
        if success:
            receive_reward(code, task_name=name)
        else:
            print(f"跳过领取（完成失败）：{name}({code})", flush=True)


def complete_all_doable_once(access_token=""):
    params = {
        "maijsVersion": "1.51.0",
        "clientId": "019950c7-ca1a-3821-361e-4b346d26d1ea",
        "appName": "家乐好礼屋",
        "envVersion": "release",
        "listCondition.page": "1",
        "listCondition.perPage": "100",
        "isEnabled.value": "true",
        "clientTime": "2025-09-16T19:13:56.270+08:00"
    }
    header = {
        "Host": "consumer-api.unileverfoodsolutions.com.cn",
        "Connection": "keep-alive",
        "X-Account-Id": "577c98c4905e88311f8b474a",
        "Accept": "application/json, text/plain, */*",
        "xweb_xhr": "1",
        "X-Requested-With": "XMLHttpRequest",
        "X-Access-Token": access_token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13)XWEB/14315",
        "Content-Type": "application/json",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wx57048525e48315b4/193/page-frame.html",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    try:
        re = requests.get(tasklist, headers=header, params=params)
        data = re.json() if re is not None else {}
    except requests.exceptions.RequestException as e:
        print(f"获取任务列表失败：{e}")
        return

    items = data.get("items", []) if isinstance(data, dict) else []
    candidates = []
    for it in items:
        if not isinstance(it, dict):
            continue
        if not it.get("isEnabled", False):
            continue
        member = it.get("memberReward", {}) or {}
        if not member.get("hasLeftTaskRewards", False):
            continue
        code = it.get("code") or ""
        name = it.get("name") or code
        try:
            reward = ((it.get("rewards") or [{}])[0].get("score") or {}).get("value", 0)
        except Exception:
            reward = 0
        if not code:
            continue
        candidates.append((code, name, reward))

    print(f"开始处理可做任务，共{len(candidates)}个", flush=True)
    for code, name, reward in candidates:
        print(f"将处理：{name}({code})，奖励{reward}", flush=True)
        success = complete_task(code, task_name=name, reward_score=reward, access_token=access_token)
        print("完成成功，准备领取...", flush=True) if success else print("完成失败，跳过领取", flush=True)
        time.sleep(1.5)
        if success:
            receive_reward(code, task_name=name, access_token=access_token)


if __name__ == '__main__':
    token = ""
    before = get_current_score(token)
    print(f"执行前积分：{before}")
    complete_all_doable_once(token)
    after = get_current_score(token)
    print(f"执行后积分：{after}")
    print(f"本次积分增加：{after - before}")

