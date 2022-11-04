"""
    邮件发送
"""
import zmail
from palp import settings


def send_email(sender, subject, content):
    """

    :param sender: 发送者
    :param subject: 主题
    :param content: 发送内容
    :return:
    """
    server = zmail.server(settings.EMAIL_USER, settings.EMAIL_PWD)

    info = {
        'from': sender,
        'subject': subject,
        'content_text': content,
    }

    server.send_mail(settings.EMAIL_RECEIVER, info)
