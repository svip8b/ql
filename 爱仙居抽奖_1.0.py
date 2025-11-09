import requests
import urllib.parse
import json
from urllib.parse import unquote
import time
import random
import os

TENANT_CODE = "xsb_xianju"
INITIAL_Q = "1GwxSBurLoUdKeZiyHuqn7u0cv2qTf081Qj/sdyPH2E="
LOTTERY_POST_DATA_TOKEN = "qE/ULGuZie9FcxVUBUKHw4J82kCDQqLT"
BASE_URL = "https://act.tmlyun.com"


def pretty_print(data):
    """格式化输出JSON"""
    print(json.dumps(data, indent=4, ensure_ascii=False))





def task_login(ACCOUNT_ID,SESSION_ID,session, q_value):
    url = f"{BASE_URL}/activity-api/task/h5/auth/userLogin"
    payload = {
        "q": q_value,
        "accountId": ACCOUNT_ID,
        "sessionId": SESSION_ID,
        "tenantCode": TENANT_CODE
    }
    try:
        response = session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            task_token = data["data"]["token"]
            print(f"任务系统登录成功！获取到任务Token。")
            return task_token
        else:
            print("任务系统登录失败:")
            pretty_print(data)
            return None
    except requests.RequestException as e:
        print(f"请求任务系统登录接口时发生错误: {e}")
        return None


def get_lottery_info(session, task_token):
    url = f"{BASE_URL}/activity-api/task/h5/activity/getActivityInfo"
    headers = {"Authorization": task_token}
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            lottery_url = data["data"]["activityStyle"]["lotteryButtonUrl"]
            parsed_url = urllib.parse.urlparse(lottery_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            new_q = query_params.get('q', [None])[0]
            if new_q:
                return new_q
            else:
                print("错误：在lotteryButtonUrl中未找到q值。")
                return None
        else:
            print("获取抽奖信息失败:")
            pretty_print(data)
            return None
    except requests.RequestException as e:
        print(f"请求活动信息接口时发生错误: {e}")
        return None


def lottery_login(ACCOUNT_ID,SESSION_ID,session, new_q_value):
    url = f"{BASE_URL}/activity-api/lottery/api/auth/userLogin"
    payload = {
        "q": new_q_value,
        "accountId": ACCOUNT_ID,
        "sessionId": SESSION_ID,
        "tenantCode": TENANT_CODE
    }
    try:
        response = session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            lottery_token = data["data"]["token"]
            lottery_activity_id = data["data"]["thirdId"]
            print(f"抽奖系统登录成功！")
            return lottery_token, lottery_activity_id
        else:
            print("抽奖系统登录失败:")
            pretty_print(data)
            return None, None
    except requests.RequestException as e:
        print(f"请求抽奖系统登录接口时发生错误: {e}")
        return None, None

original_cookie_value = "dxA2jxuFFRjq5pngScCY2mol9UwV37AiJRZzxSWH6ZUDF4q+IAHP3vlc1ThxdvFAwoH30tw34I71U5ckf7l56g%3D%3D"
x_token_from_cookie = unquote(original_cookie_value)

def generate_x_request_id():
  random_part = 10000 * random.random()
  timestamp_part = int(time.time() * 1000)
  return f"{random_part}|{timestamp_part}"
def do_lottery(session, lottery_token, lottery_activity_id,clientId,USER_AGENT):
    url = f"{BASE_URL}/activity-api/lottery/h5/activity/lottery/userActivityLottery"

    headers = {
        'User-Agent': USER_AGENT,
        'Accept': "application/json, text/plain, */*",
        'Accept-Encoding': "gzip, deflate",
        'Content-Type': "application/json",
        'X-TOKEN': x_token_from_cookie,
        'Authorization': lottery_token,
        'X-REQUEST-ID': generate_x_request_id(),
        'Origin': "https://act.tmlyun.com",
        'X-Requested-With': "com.increator.cc.xianjusmk",
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
         }
    payload = {0
        "activityId": lottery_activity_id,
        "clientId": clientId,
        "token": x_token_from_cookie
    }
    print("\n--- 正在执行抽奖... ---")

    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            lottery_data = result.get("data", {})
            is_prize = lottery_data.get("isPrize")

            if is_prize == 1:
                prize_name = lottery_data.get("prizeName")
                if prize_name:
                    print(f"🎉 抽奖结果: 恭喜！抽中【{prize_name}】")
                else:
                    print("🎉 抽奖结果: 中奖了！但服务器未返回奖品名称。")
            else:
                unlucky_message = lottery_data.get("prizeName")
                if unlucky_message:
                    print(f"😔 抽奖结果: {unlucky_message}")
                else:
                    print("😔 抽奖结果: 未中奖 (服务器未返回具体信息)")
        else:
            error_message = result.get("message")
            if error_message:
                print(f"❌ 抽奖结果: {error_message}")
            else:
                print("❌ 抽奖失败，且服务器未返回错误信息。")

    except requests.RequestException as e:
        print(f"请求抽奖接口时发生严重错误: {e}")
    except json.JSONDecodeError:
        print("解析抽奖响应失败，服务器可能返回了非JSON内容。")


def main():
    """
    主执行函数
    """

    print("--- 爱仙居抽奖 ---")
    cook = os.getenv("aixianju")
    if not cook:
        print(f"请将爱仙居抽奖token填入环境变量axj，X-ACCOUNT-ID#X-ACCOUNT-ID#clientId#ua多账号&分割或新建同名变量")
    else:
        cook = cook.split("&")
        print(f"共找到{len(cook)}个账号")
        for i in cook:
            SESSION_ID,ACCOUNT_ID,clientId,USER_AGENT = i.split("#")
            session = requests.Session()
            session.headers.update({"User-Agent": USER_AGENT})
            task_token = task_login(ACCOUNT_ID,SESSION_ID,session, INITIAL_Q)
            if not task_token:
                return
            lottery_q = get_lottery_info(session, task_token)
            if not lottery_q:
                return
            lottery_token, lottery_activity_id = lottery_login(ACCOUNT_ID,SESSION_ID,session, lottery_q)
            if not lottery_token or not lottery_activity_id:
                return
            do_lottery(session, lottery_token, lottery_activity_id, clientId,USER_AGENT)
            print(f"运行结束进入下一个账号")
            pause_time = random.uniform(30, 70)
            print(f"等待 {pause_time:.2f} 秒...")
            time.sleep(pause_time)


if __name__ == "__main__":
    main()