"""
    钉钉机器人：Titan
"""
import hmac
import time
import base64
import hashlib
import requests
from loguru import logger
from palp import settings
from urllib.parse import quote


def get_sign() -> dict:
    """

    :return: 返回 sign
    """
    timestamp = str(round(time.time() * 1000))
    secret = settings.DING_TALK_SECRET
    secret_bytes = secret.encode()
    string_to_sign = f'{timestamp}\n{secret}'
    string_to_sign_bytes = string_to_sign.encode()
    hmac_code = hmac.new(secret_bytes, string_to_sign_bytes, digestmod=hashlib.sha256).digest()
    sign = quote(base64.b64encode(hmac_code))

    return {
        'timestamp': timestamp,
        'sign': sign
    }


def send_ding_talk(content: str, mobiles: list = None, user_ids: list = None, at_all: bool = None):
    """

    :param content: 发送的内容
    :param mobiles: 被 @ 人手机号
    :param user_ids: 被 @ 人用户 id
    :param at_all: 是否 @ 所有人
    :return:
    """
    access_token = settings.DING_TALK_ACCESS_TOKEN
    url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}'
    data = {
        "at": {
            "atMobiles": mobiles or settings.DING_TALK_AT_MOBILES or [],
            "atUserIds": user_ids or settings.DING_TALK_AT_USER_IDS or [],
            "isAtAll": at_all if at_all is not None else settings.DING_TALK_AT_ALL
        },
        "text": {
            "content": content
        },
        "msgtype": "text"
    }

    resp = requests.post(url, params=get_sign(), json=data)

    logger.debug(f"【ding talk】：{resp.json()}")

    return resp.json()
