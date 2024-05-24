import requests  # http请求
import json  # json数据处理
import traceback  # 错误捕获
import urllib.request
import time  # 延时
import websocket  # ws接口链接
import base64  # 请求体编码
import threading
import queue
from pygments import highlight  # 高亮
from pygments.lexers import JsonLexer  # 高亮
from pygments.formatters import TerminalFormatter  # 高亮
from colorama import init, Fore, Back, Style  # 高亮
import urllib.request
list = [595164589344542720, 543395863498969088]
lingpai = 'cd418c735f05ae975ce8480b8e0e0ca578b81e277904f8f061286f1798200a61e009bca7d93ec3051bae27181afcdd56'  # bot token
bot_id = '537579193463320576'  # bot_id
websocket_url = 'wss://gateway-bot.fanbook.mobi/websocket'
requests_url = 'https://a1.fanbook.mobi/api/bot/'
post_headers = {'Content-Type': 'application/json'}


def sendMessage(channel_id, msg):
    global lingpai
    Data = json.dumps({"chat_id": channel_id, "text": msg})
    postdata = requests.post(requests_url + f'{lingpai}/sendMessage', headers=post_headers, data=Data)
    return json.loads(postdata.text)


init(autoreset=True)  # 初始化，并且设置颜色设置自动恢复


def addmsg(msg, color="white"):
    if color == "white":
        print(msg)
    elif color == "red":
        print("\033[31m" + msg + "\033[39m")
    elif color == "yellow":
        print("\033[33m" + msg + "\033[39m")
    elif color == "green":
        print("\033[32m" + msg + "\033[39m")
    elif color == "aqua":
        print("\033[36m" + msg + "\033[39m")


def colorprint(smg2, pcolor):
    if pcolor == 'red':
        print(Fore.RED + smg2)
    elif pcolor == 'bandg':
        print(Back.GREEN + smg2)
    elif pcolor == 'd':
        print(Style.DIM + smg2)
    # 如果未设置autoreset=True，需要使用如下代码重置终端颜色为初始设置
    # print(Fore.RESET + Back.RESET + Style.RESET_ALL)  autoreset=True


def colorize_json(smg2, pcolor=''):
    json_data = smg2
    try:
        try:
            parsed_json = json.loads(json_data)  # 解析JSON数据
        except:
            pass
        formatted_json = json.dumps(parsed_json, indent=4)  # 格式化JSON数据

        # 使用Pygments库进行语法高亮
        colored_json = highlight(formatted_json, JsonLexer(), TerminalFormatter())

        print(colored_json)
    except:
        print(json_data)


false = False
data_queue = queue.Queue()


def on_message(ws, message):
    # 处理接收到的消息
    addmsg('收到消息', color='green')
    colorize_json(message)
    message = json.loads(message)
    if message["action"] == "push":
        if message["data"]["author"]["bot"] == false:
            content = json.loads(message["data"]["content"])
            if json.loads(message['data']['guild_id']) in list:
                if "${@!" + bot_id + "}" in content['text']:
                    # text=json.loads(content)
                    print(content['text'])
                    print(content['text'][23:])

                    response = requests.get(f"https://api.lolimi.cn/API/AI/wx.php?msg={content['text'][23:]}")
                    output = response.json()['data']['output']

                    print('提问了', content['text'][23:])
                    colorize_json(sendMessage(int(message["data"]["channel_id"]), output))


def on_error(ws, error):
    # 处理错误
    addmsg("发生错误:" + str(error), color='red')


def on_close(ws):
    # 连接关闭时的操作
    addmsg("连接已关闭", color='red')


def on_open(ws):
    # 连接建立时的操作
    addmsg("连接已建立", color='green')

    # 发送心跳包
    def send_ping():
        print('发送：{"type":"ping"}')
        ws.send('{"type":"ping"}')

    send_ping()  # 发送第一个心跳包

    # 定时发送心跳包
    def schedule_ping():
        send_ping()
        # 每25秒发送一次心跳包
        websocket._get_connection()._connect_time = 0  # 重置连接时间，避免过期
        ws.send_ping()
        websocket._get_connection().sock.settimeout(70)
        ws.send('{"type":"ping"}')

    websocket._get_connection().run_forever(ping_interval=25, ping_payload='{"type":"ping"}',
                                            ping_schedule=schedule_ping)


# 替换成用户输入的BOT令牌
lingpai = lingpai
url = requests_url + f"{lingpai}/getMe"
# 发送HTTP请求获取基本信息
response = requests.get(url)
data = response.json()


def send_data_thread():
    while True:
        # 在这里编写需要发送的数据
        time.sleep(25)
        ws.send('{"type":"ping"}')
        addmsg('发送心跳包：{"type":"ping"}', color='green')


if response.ok and data.get("ok"):
    user_token = data["result"]["user_token"]
    device_id = "your_device_id"
    version_number = "1.6.60"
    super_str = base64.b64encode(json.dumps({
        "platform": "bot",
        "version": version_number,
        "channel": "office",
        "device_id": device_id,
        "build_number": "1"
    }).encode('utf-8')).decode('utf-8')
    ws_url = websocket_url + f"?id={user_token}&dId={device_id}&v={version_number}&x-super-properties={super_str}"
    threading.Thread(target=send_data_thread, daemon=True).start()
    # 建立WebSocket连接
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
else:
    addmsg("无法获取BOT基本信息，请检查令牌是否正确。", color='red')