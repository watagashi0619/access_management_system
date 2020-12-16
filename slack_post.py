from datetime import datetime

import requests
import yaml

yaml_dict = yaml.load(open("key.yaml").read())

URL = "https://slack.com/api/chat.postMessage"
TOKEN = yaml_dict["slack_token"]
CHANNEL = yaml_dict["slack_channel"]


def enter(time, student_name):
    data = {
        "token": TOKEN,
        "username": u"入室通知",
        "icon_emoji": u":gorilla:",
        "channel": CHANNEL,
        "text": time.strftime("%Y/%m/%d %H:%M:%S")
        + " に "
        + student_name
        + " さんが入室しました。",
    }
    requests.post(URL, data=data)


def leave(time, student_name):
    data = {
        "token": TOKEN,
        "username": u"退室通知",
        "icon_emoji": u":gorilla:",
        "channel": CHANNEL,
        "text": time.strftime("%Y/%m/%d %H:%M:%S")
        + " に "
        + student_name
        + " さんが退室しました。",
    }
    requests.post(URL, data=data)


def balance_check(balance):
    data = {
        "token": TOKEN,
        "username": u"Suica残高",
        "icon_emoji": u":penguin:",
        "channel": CHANNEL,
        "text": "交通系icカードの残高は" + str(balance) + "円です。",
    }
    requests.post(URL, data=data)


def miss():
    data = {
        "token": TOKEN,
        "username": u"入退室通知",
        "icon_emoji": u":gorilla:",
        "channel": CHANNEL,
        "text": "うまく認識できませんでした。もう一度タッチしてください。",
    }
    requests.post(URL, data=data)
