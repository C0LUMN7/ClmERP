# -*- coding: utf-8 -*-
"""显式测试结果通知入口。"""
import base64
import hmac
import smtplib
import time
import urllib.parse
import xml.etree.ElementTree as ET
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import requests

from config.settings import (
    DINGTALK_SECRET,
    DINGTALK_WEBHOOK,
    EMAIL_ADDRESSEE,
    EMAIL_HOST,
    EMAIL_PASSWORD,
    EMAIL_SUBJECT,
    EMAIL_USER,
)
from shared.logger import logs


def generate_test_summary(terminalreporter):
    """生成 pytest 执行摘要字符串。"""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    duration = time.time() - getattr(terminalreporter, '_sessionstarttime', time.time())

    summary = f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    """
    print(summary)
    return summary


def _junit_counts(report_path):
    root = ET.parse(report_path).getroot()
    if root.tag == 'testsuite':
        suites = [root]
    else:
        suites = root.findall('testsuite')
    total = sum(int(suite.attrib.get('tests', 0)) for suite in suites)
    failed = sum(int(suite.attrib.get('failures', 0)) for suite in suites)
    error = sum(int(suite.attrib.get('errors', 0)) for suite in suites)
    skipped = sum(int(suite.attrib.get('skipped', 0)) for suite in suites)
    duration = sum(float(suite.attrib.get('time', 0)) for suite in suites)
    passed = total - failed - error - skipped
    return total, passed, failed, error, skipped, duration


def build_report_summary(report):
    """从报告路径生成通知摘要。JUnit XML 可提取统计，其它路径只展示位置。"""
    report_path = Path(report)
    if report_path.is_file() and report_path.suffix.lower() == '.xml':
        total, passed, failed, error, skipped, duration = _junit_counts(report_path)
        return f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    报告位置：{report_path}
    """
    return f'自动化测试报告已生成，报告位置：{report_path}'


def generate_sign(secret):
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    str_to_sign = '{}\n{}'.format(timestamp, secret)
    str_to_sign_enc = str_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, str_to_sign_enc, digestmod='sha256').digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def send_dd_msg(content_str, at_all=True):
    """发送钉钉通知。"""
    if not DINGTALK_WEBHOOK or not DINGTALK_SECRET:
        raise RuntimeError('钉钉通知配置缺失：请设置 DINGTALK_WEBHOOK / DINGTALK_SECRET')
    timestamp, sign = generate_sign(DINGTALK_SECRET)
    url = f'{DINGTALK_WEBHOOK}&timestamp={timestamp}&sign={sign}'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        'msgtype': 'text',
        'text': {'content': content_str},
        'at': {'isAtAll': at_all},
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.text


class SendEmail:
    """构建并发送邮件。"""

    def __init__(self, host=EMAIL_HOST, user=EMAIL_USER, passwd=EMAIL_PASSWORD):
        self.__host = host
        self.__user = user
        self.__passwd = passwd

    def build_content(self, subject, email_content, addressee=None, atta_file=None):
        if not self.__host or not self.__user or not self.__passwd:
            raise RuntimeError('邮件通知配置缺失：请设置 EMAIL_HOST / EMAIL_USER / EMAIL_PASSWORD')
        recipients = addressee or EMAIL_ADDRESSEE
        if not recipients:
            raise RuntimeError('邮件收件人缺失：请设置 EMAIL_ADDRESSEE')
        addressee_list = recipients.split(';') if isinstance(recipients, str) else recipients

        sender = 'liaison officer' + '<' + self.__user + '>'
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = ';'.join(addressee_list)
        message.attach(MIMEText(email_content, _subtype='plain', _charset='utf-8'))

        if atta_file is not None:
            with open(atta_file, 'rb') as file:
                atta = MIMEApplication(file.read())
            atta['Content-Type'] = 'application/octet-stream'
            atta['Content-Disposition'] = 'attachment; filename="testresult.xml"'
            message.attach(atta)

        service = smtplib.SMTP_SSL(self.__host)
        try:
            service.login(self.__user, self.__passwd)
            service.sendmail(sender, addressee_list, message.as_string())
        finally:
            service.quit()
        logs.info('邮件发送成功!')


class BuildEmail(SendEmail):
    """兼容旧 BuildEmail 调用。"""

    def main(self, success, failed, error, not_running, atta_file=None, *args):
        success_num = len(success)
        fail_num = len(failed)
        error_num = len(error)
        notrun_num = len(not_running)
        total = success_num + fail_num + error_num + notrun_num
        execute_case = success_num + fail_num
        pass_result = '%.2f%%' % (success_num / execute_case * 100) if execute_case > 0 else '0%'
        fail_result = '%.2f%%' % (fail_num / execute_case * 100) if execute_case > 0 else '0%'
        err_result = '%.2f%%' % (error_num / execute_case * 100) if execute_case > 0 else '0%'
        content = '项目接口测试，共测试接口%s个，通过%s个，失败%s个，错误%s个，未执行%s个，通过率%s，失败率%s，错误率%s。' % (
            total, success_num, fail_num, error_num, notrun_num, pass_result, fail_result, err_result)
        self.build_content(EMAIL_SUBJECT, content, atta_file=atta_file)


def send_email_report(summary, report=None):
    SendEmail().build_content(EMAIL_SUBJECT, summary, atta_file=report if Path(report or '').is_file() else None)


def notify_report(report, channel='all'):
    """按显式命令发送报告通知。"""
    summary = build_report_summary(report)
    results = []
    if channel in ('all', 'dingtalk'):
        results.append(('dingtalk', send_dd_msg(summary)))
    if channel in ('all', 'email'):
        send_email_report(summary, report)
        results.append(('email', 'sent'))
    return results
