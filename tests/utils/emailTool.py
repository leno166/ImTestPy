"""
@文件: emailTool.py
@作者: 雷小鸥
@日期: 2025/12/9 11:38
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from pathlib import Path
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.header import Header
from email import encoders
import smtplib
from typing import TypedDict
from tests.utils.configuration import CONFIGURATION
from tests.utils.logger import logger
from functools import partial

TEST_PATH = Path('./tests')

EMAIL_CONF = CONFIGURATION['EMAIL']


class EmailMsg(TypedDict):
    From: str
    To: str
    Subject: str


def _send(
        subject: str, body: str, attachments: list[str],
        receiver: str, receiver_name: str,
        smtp_server: str, sender: str, sender_name: str, authorization: str,
        encoding: str = 'utf-8'
) -> None:
    logger.info('📧 准备发送邮件: %s → %s', subject, receiver)

    # 创建多部分消息（支持附件）
    if attachments:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, 'plain', encoding))
    else:
        msg = MIMEText(body, 'plain', encoding)

    msg['From'] = formataddr((sender_name, sender), charset=encoding)
    msg['To'] = formataddr((receiver_name, receiver), charset=encoding)
    msg['Subject'] = Header(subject, encoding)  # 邮件主题

    if attachments:
        for attachment_path in attachments:
            path = Path(attachment_path)
            if not path.exists():
                logger.warning("⚠️ 附件不存在，跳过: %s", path)
                continue

            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{Header(path.name, encoding).encode()}"'
            )
            msg.attach(part)

    smtp = smtplib.SMTP_SSL(smtp_server)
    smtp.login(sender, authorization)
    smtp.sendmail(sender, [msg['To']], msg.as_string())
    logger.info("✅ 邮件已成功发送到目标邮箱！")
    smtp.quit()


_default_send = partial(
    _send,
    smtp_server=EMAIL_CONF['smtp_server'],
    sender=EMAIL_CONF['sender'], sender_name=EMAIL_CONF['sender_name'], authorization=EMAIL_CONF['authorization'],
    encoding=EMAIL_CONF['encoding']
)


def send(subject: str, body: str, attachments: list[str] = None,
         receiver: str = None, receiver_name: str = None) -> None:
    _receiver = receiver or EMAIL_CONF['receiver']
    _receiver_name = receiver_name or EMAIL_CONF["receiver_name"]
    return _default_send(subject, body, attachments, _receiver, _receiver_name)


if __name__ == '__main__':
    # send(subject='subject', body='body', attachments=[r'D:\workflow\ImTestPy\tests\conftest.py'], )
    send(subject='subject', body='body', receiver='v-wuzhengfeng@immotors.com', receiver_name='xxx')
