"""
    报警模块

    使用方式见 gsender 模块对应源码
"""
from palp import settings
from typing import Union, List
from gsender import EmailSender, DingTalkSender


def send_email(
        receiver: Union[List[str], str],
        subject: str = 'Palp 报警系统',
        content_text: str = None,
        content_html: Union[List[str], str] = None,
        files: Union[List[str], str] = None,
        headers: dict = None
):
    """
    发送邮件

    :param receiver: 接收者
    :param subject: 主题
    :param content_text: 文本内容（二选一）
    :param content_html: html 内容（二选一）
    :param files: 文件路径或路径列表
    :param headers: 额外标题
    :return:
    """
    email_sender = EmailSender(user=settings.EMAIL_USER, pwd=settings.EMAIL_PWD)

    return email_sender.send(
        receiver=receiver,
        subject=subject,
        content_text=content_text,
        content_html=content_html,
        files=files,
        headers=headers
    )


def send_dingtalk() -> DingTalkSender:
    """
    钉钉群聊发送器，支持多种消息类型

    :return:
    """
    return DingTalkSender(secret=settings.DING_TALK_SECRET, access_token=settings.DING_TALK_ACCESS_TOKEN)
