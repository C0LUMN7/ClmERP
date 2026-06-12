import json
import os
from conf.setting import DIR_BASE
from common.dingRobot import send_dd_msg
from common.semail import BuildEmail


def parse_allure_results(allure_dir):
    counts = {'passed': 0, 'failed': 0, 'broken': 0, 'skipped': 0}
    if not os.path.isdir(allure_dir):
        return counts
    for f in os.listdir(allure_dir):
        if f.endswith('-result.json'):
            path = os.path.join(allure_dir, f)
            try:
                with open(path, encoding='utf-8') as fp:
                    data = json.load(fp)
                status = data.get('status', '')
                if status in counts:
                    counts[status] += 1
            except Exception:
                pass
    return counts


def build_summary(counts):
    total = sum(counts.values())
    passed = counts['passed']
    failed = counts['failed'] + counts['broken']
    skipped = counts['skipped']
    if total == 0:
        return '本次测试未执行任何用例。'
    pass_rate = f'{passed / total * 100:.1f}%' if total > 0 else '0%'
    lines = [
        '自动化测试结果通知，请着重关注失败接口：',
        f'测试用例总数：{total}',
        f'测试通过数：{passed}',
        f'测试失败数：{failed}',
        f'跳过执行数：{skipped}',
        f'通过率：{pass_rate}',
    ]
    return '\n'.join(lines)


def send_all(allure_dir):
    counts = parse_allure_results(allure_dir)
    summary = build_summary(counts)
    print(summary)
    send_dd_msg(summary)
    BuildEmail().main(
        success=[1] * counts['passed'],
        failed=[1] * (counts['failed'] + counts['broken']),
        error=[],
        not_running=[1] * counts['skipped'],
    )


if __name__ == '__main__':
    allure_dir = os.path.join(DIR_BASE, 'report', 'temp')
    send_all(allure_dir)
