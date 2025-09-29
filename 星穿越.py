#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
#【免责声明】
# 本脚本仅供学习和交流使用，严禁用于任何商业用途或非法用途。
# 使用本脚本所带来的一切后果由使用者本人承担，作者不对因使用本脚本造成的任何损失或法律责任负责。
# 请遵守相关法律法规，尊重目标平台的服务条款。
# 若您不同意本声明，请立即停止使用并删除本脚本。
# 学习交流频道t.me/fxmbb
#环境变量xcy=账号#密码多账号换行
import os
import requests
from datetime import datetime
from notify import send


class XingChuanYue:
    def __init__(self):
        self.base_url = "https://console.frp.api.xhuzim.top/api/v1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="140", "Edge";v="140"',
            'sec-ch-ua-mobile': '?0',
            'Origin': 'https://console.xhfrp.xhuzim.top',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://console.xhfrp.xhuzim.top/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }

    def get_accounts(self):
        """获取账号列表"""
        accounts = []

        # 从环境变量读取账号
        xcy_accounts = os.getenv('xcy', '')
        if xcy_accounts:
            for line in xcy_accounts.strip().split('\n'):
                if '#' in line:
                    account, password = line.split('#', 1)
                    accounts.append((account.strip(), password.strip()))


        return accounts

    def login(self, account, password):
        """登录获取token"""
        url = f"{self.base_url}/users/login"
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'

        data = {
            "account": account,
            "password": password
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                return result['data']['token']
            else:
                print(f"登录失败: {result.get('msg', '未知错误')}")
                return None
        except Exception as e:
            print(f"登录请求异常: {str(e)}")
            return None

    def get_user_info(self, token):
        """获取用户信息"""
        url = f"{self.base_url}/users/info"
        headers = self.headers.copy()
        headers['Authorization'] = token

        try:
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                return result['data']
            else:
                print(f"获取用户信息失败: {result.get('msg', '未知错误')}")
                return None
        except Exception as e:
            print(f"获取用户信息请求异常: {str(e)}")
            return None

    def get_checkin_status(self, token):
        """获取签到状态"""
        url = f"{self.base_url}/users/checkin/status"
        headers = self.headers.copy()
        headers['Authorization'] = token

        try:
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                return result['data']
            else:
                print(f"获取签到状态失败: {result.get('msg', '未知错误')}")
                return None
        except Exception as e:
            print(f"获取签到状态请求异常: {str(e)}")
            return None

    def checkin(self, token):
        """执行签到"""
        url = f"{self.base_url}/users/checkin"
        headers = self.headers.copy()
        headers['Authorization'] = token
        headers['Content-Length'] = '0'
        headers['Pragma'] = 'no-cache'
        headers['Cache-Control'] = 'no-cache'

        try:
            response = requests.post(url, headers=headers, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                return result
            else:
                print(f"签到失败: {result.get('msg', '未知错误')}")
                return None
        except Exception as e:
            print(f"签到请求异常: {str(e)}")
            return None

    def format_traffic(self, bytes_value):
        """格式化流量显示"""
        if bytes_value < 1024:
            return f"{bytes_value} B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value / 1024:.2f} KB"
        elif bytes_value < 1024 * 1024 * 1024:
            return f"{bytes_value / (1024 * 1024):.2f} MB"
        else:
            return f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"

    def run(self):
        """主运行函数"""
        print("星穿越签到脚本开始运行...")

        accounts = self.get_accounts()
        print(f"共找到 {len(accounts)} 个账号")

        success_count = 0
        total_count = len(accounts)

        for i, (account, password) in enumerate(accounts, 1):
            print(f"\n处理第 {i}/{total_count} 个账号: {account}")

            # 登录获取token
            token = self.login(account, password)
            if not token:
                print(f"账号 {account} 登录失败，跳过")
                send(f"星穿越签到失败 - {account}", f"账号 {account} 登录失败")
                continue

            # 获取用户信息
            user_info = self.get_user_info(token)
            if not user_info:
                print(f"账号 {account} 获取用户信息失败，跳过")
                send(f"星穿越签到失败 - {account}", f"账号 {account} 获取用户信息失败")
                continue

            print(f"用户: {user_info.get('Username', 'N/A')} ({user_info.get('Email', 'N/A')})")
            print(
                f"流量使用: {self.format_traffic(user_info.get('UsedTraffic', 0))} / {self.format_traffic(user_info.get('Traffic', 0))}")
            print(f"隧道数量: {user_info.get('Tunnels', 'N/A')}")

            # 检查签到状态
            checkin_status = self.get_checkin_status(token)
            if not checkin_status:
                print(f"账号 {account} 获取签到状态失败，跳过")
                send(f"星穿越签到失败 - {account}", f"账号 {account} 获取签到状态失败")
                continue

            last_checkin = checkin_status.get('last_checkin', '')
            has_checked = checkin_status.get('has_checked', False)
            continuity_days = checkin_status.get('continuity_days', 0)
            checkin_count = checkin_status.get('checkin_count', 0)

            print(f"上次签到: {last_checkin}")
            print(f"连续签到天数: {continuity_days}")
            print(f"总签到次数: {checkin_count}")

            # 判断是否需要签到
            today = datetime.now().strftime('%Y-%m-%d')
            if last_checkin == today or has_checked:
                print(f"账号 {account} 今日已签到，跳过")
                success_count += 1
                send(f"星穿越签到 - {account}",
                     f"账号 {account} 今日已签到\n连续签到: {continuity_days}天\n总签到: {checkin_count}次\n流量: {self.format_traffic(user_info.get('UsedTraffic', 0))} / {self.format_traffic(user_info.get('Traffic', 0))}")
                continue

            # 执行签到
            print(f"账号 {account} 开始签到...")
            checkin_result = self.checkin(token)
            if checkin_result:
                print(f"账号 {account} 签到成功!")
                success_count += 1

                # 签到后重新获取用户信息
                new_user_info = self.get_user_info(token)
                if new_user_info:
                    print(
                        f"签到后流量: {self.format_traffic(new_user_info.get('UsedTraffic', 0))} / {self.format_traffic(new_user_info.get('Traffic', 0))}")
                    send(f"星穿越签到成功 - {account}",
                         f"账号 {account} 签到成功！\n连续签到: {continuity_days + 1}天\n总签到: {checkin_count + 1}次\n流量: {self.format_traffic(new_user_info.get('UsedTraffic', 0))} / {self.format_traffic(new_user_info.get('Traffic', 0))}")
            else:
                print(f"账号 {account} 签到失败")
                send(f"星穿越签到失败 - {account}", f"账号 {account} 签到失败")

        # 输出最终统计
        result_msg = f"所有账号处理完成！成功: {success_count}/{total_count}"
        print(f"\n{result_msg}")


def main():
    xcy = XingChuanYue()
    xcy.run()


if __name__ == "__main__":
    main()
