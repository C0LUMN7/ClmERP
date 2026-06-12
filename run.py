import shutil
import pytest
import os
import webbrowser
from conf.setting import REPORT_TYPE, ALLURE_HOST, ALLURE_PORT

if __name__ == '__main__':

    if REPORT_TYPE == 'allure':
        pytest.main(
            ['-s', '-v', '--alluredir=./report/temp', './testcase/ERP/', '--clean-alluredir',
             '--junitxml=./report/results.xml'])

        shutil.copy('./conf/environment.xml', './report/temp')
        # 生成报告到固定目录
        os.system('allure generate ./report/temp -o ./report/allureReport --clean')
        # 使用配置的 host 和 port 打开报告
        os.system(f'allure open ./report/allureReport --host {ALLURE_HOST} --port {ALLURE_PORT}')