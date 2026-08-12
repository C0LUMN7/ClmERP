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


def _short_run_id(run_id):
    value = int(run_id)
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = ''
    while value:
        value, remainder = divmod(value, 36)
        result = chars[remainder] + result
    return result or '0'


def _cleanup_sql(cursor, conn, label, sql):
    try:
        cursor.execute(sql)
        affected = cursor.rowcount
        conn.commit()
        logs.info('后置清理%s完成，影响行数: %s', label, affected)
        return True
    except Exception as e:
        conn.rollback()
        logs.warning('后置清理%s异常: %s', label, e)
        return False


def _cleanup_run_data():
    run_id = DebugTalk._fixed_ts
    if not run_id:
        logs.info('本次会话未生成运行ID，跳过后置数据清理')
        return

    depot_run_id = _short_run_id(run_id)
    conn = ConnectMysql()
    if not conn.conn or not conn.cursor:
        logs.warning('后置数据清理跳过：MySQL 未连接')
        return

    try:
        cursor = conn.cursor
        head_ids = (f"SELECT id FROM jsh_depot_head WHERE number LIKE 'AUTO_API_%' "
                    f"AND number LIKE '%{run_id}%' AND delete_flag = '0'")
        account_ids = (f"SELECT id FROM jsh_account_head WHERE bill_no LIKE 'AUTO_API_%' "
                       f"AND bill_no LIKE '%{run_id}%' AND delete_flag = '0'")
        material_ids = (f"SELECT id FROM jsh_material WHERE name LIKE 'AUTO_API_%' "
                        f"AND name LIKE '%{run_id}%' AND delete_flag = '0'")
        statements = [
            ('收付款明细-按业务单据', f"DELETE FROM jsh_account_item WHERE bill_id IN ({head_ids})"),
            ('收付款明细-按收付款单', f"DELETE FROM jsh_account_item WHERE header_id IN ({account_ids})"),
            ('出入库明细', f"DELETE FROM jsh_depot_item WHERE header_id IN ({head_ids})"),
            ('收付款单', f"DELETE FROM jsh_account_head WHERE bill_no LIKE 'AUTO_API_%' "
                     f"AND bill_no LIKE '%{run_id}%' AND delete_flag = '0'"),
            ('出入库单', f"DELETE FROM jsh_depot_head WHERE number LIKE 'AUTO_API_%' "
                    f"AND number LIKE '%{run_id}%' AND delete_flag = '0'"),
            ('库存', f"DELETE FROM jsh_material_current_stock WHERE material_id IN ({material_ids})"),
            ('商品扩展', f"DELETE FROM jsh_material_extend WHERE material_id IN ({material_ids})"),
            ('商品', f"DELETE FROM jsh_material WHERE name LIKE 'AUTO_API_%' "
                   f"AND name LIKE '%{run_id}%' AND delete_flag = '0'"),
            ('新增仓库', f"DELETE FROM jsh_depot WHERE name LIKE 'AUTO_API_D_%' "
                    f"AND name LIKE '%{depot_run_id}%' AND delete_flag = '0'"),
            ('更新仓库', f"DELETE FROM jsh_depot WHERE name LIKE 'AUTO_API_U_%' "
                    f"AND name LIKE '%{depot_run_id}%' AND delete_flag = '0'"),
        ]
        failed = 0
        for label, sql in statements:
            if not _cleanup_sql(cursor, conn.conn, label, sql):
                failed += 1
        if failed:
            logs.warning('后置定向清理完成但存在异常项，运行ID: %s，异常项数量: %s', run_id, failed)
        else:
            logs.info('后置定向清理完成（AUTO_API_ 前缀 + 本次运行 ID: %s）', run_id)
    finally:
        conn.close()


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
    后置定向清理：只清理本次会话创建且带 AUTO_API_ 前缀与本次运行 ID 的测试数据。

    单据按单号前缀 + 运行 ID 匹配，商品/仓库按名称前缀 + 运行 ID 匹配，
    不模糊删除共享环境中的历史数据；本次创建数据的精确业务 ID 优先在用例内
    通过创建响应/数据库精确查询获取，这里只作为失败重跑后的兜底清理。
    """
    yield
    _cleanup_run_data()
