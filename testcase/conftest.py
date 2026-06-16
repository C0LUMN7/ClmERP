import time
import pytest
import allure
from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from common.recordlog import logs
from common.debugtalk import DebugTalk
from common.connection import ConnectMysql

"""
-fixture scope: function, class, module, session
-autouse: true -> auto-execute without explicit reference
"""


@pytest.fixture(autouse=True)
def start_test_and_end():
    logs.info('-------------接口测试开始--------------')
    yield
    logs.info('-------------接口测试结束--------------')


@pytest.fixture(scope='session', autouse=True)
@allure.story("登录")
def system_login():
    max_retries = 5
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                DebugTalk._captcha_data = None
                time.sleep(1)
            api_info = get_testcase_yaml('./testcase/ERP/loginName.yaml')
            RequestBase().specification_yaml(api_info[0][0], api_info[0][1])
            return
        except Exception as e:
            logs.error(f'登录接口异常 (第{attempt+1}次/共{max_retries}次): {e}')
            if attempt == max_retries - 1:
                logs.error(f'登录重试{max_retries}次均失败，退出测试')
                exit()


@pytest.fixture(scope='session', autouse=True)
def datadb_init():
    """
    后置处理器，比如测试之后的数据清理
    数据库可以预先预置一批本次测试的数据，在测试完成之后将这批数据清理，就不会对系统造成影响，也不会产生脏数据
    :return:
    """
    yield
    conn = ConnectMysql()
    try:
        cursor = conn.cursor
        bill_prefixes = ("PO_", "SO_", "FK_", "SK_", "BS_")
        for p in bill_prefixes:
            cursor.execute(f"DELETE FROM jsh_account_item WHERE bill_id IN (SELECT id FROM jsh_depot_head WHERE number LIKE '{p}%' AND delete_flag = '0')")
            cursor.execute(f"DELETE FROM jsh_account_item WHERE header_id IN (SELECT id FROM jsh_account_head WHERE bill_no LIKE '{p}%' AND delete_flag = '0')")
            cursor.execute(f"DELETE FROM jsh_depot_item WHERE header_id IN (SELECT id FROM jsh_depot_head WHERE number LIKE '{p}%' AND delete_flag = '0')")
            cursor.execute(f"DELETE FROM jsh_account_head WHERE bill_no LIKE '{p}%' AND delete_flag = '0'")
            cursor.execute(f"DELETE FROM jsh_depot_head WHERE number LIKE '{p}%' AND delete_flag = '0'")
        material_prefixes = ("电动牙刷_", "洗面奶_")
        for p in material_prefixes:
            cursor.execute(f"DELETE FROM jsh_material_current_stock WHERE material_id IN (SELECT id FROM jsh_material WHERE name LIKE '{p}%' AND delete_flag = '0')")
            cursor.execute(f"DELETE FROM jsh_material_extend WHERE material_id IN (SELECT id FROM jsh_material WHERE name LIKE '{p}%' AND delete_flag = '0')")
            cursor.execute(f"DELETE FROM jsh_material WHERE name LIKE '{p}%' AND delete_flag = '0'")
        conn.conn.commit()
        logs.info("后置数据清理完成")
    except Exception as e:
        logs.warning(f"后置数据清理异常: {e}")
    finally:
        conn.close()
