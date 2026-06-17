import allure
import pytest
import yaml
import os

from common.readyaml import get_testcase_yaml, ReadYamlData
from base.apiutil_business import RequestBase
from base.generateId import m_id, c_id
from conf.setting import FILE_PATH


@pytest.fixture(scope='module', autouse=True)
def clear_extract_before_scenario():
    """Preserve token, barCode, depotId from single-interface tests; clear all other extract data"""
    preserved = {}
    preserve_keys = ['token', 'barCode', 'depotId']
    if os.path.exists(FILE_PATH['EXTRACT']):
        with open(FILE_PATH['EXTRACT'], 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data:
                for key in preserve_keys:
                    if key in data:
                        preserved[key] = data[key]
    ReadYamlData().clear_yaml_data()
    for key, val in preserved.items():
        ReadYamlData().write_yaml_data({key: val})


@allure.feature(next(m_id) + 'ERP进销存-业务场景-采购入库核心链路')
@pytest.mark.business
@pytest.mark.smoke
class TestPurchaseScenario:

    @allure.story(next(c_id) + '新增入库单-查询-审核-付款')
    @pytest.mark.parametrize('case_info', get_testcase_yaml('./testcase/ERP/Business_Scenario/PurchaseScenario.yml'))
    def test_purchase_scenario(self, case_info):
        allure.dynamic.title(case_info['baseInfo']['api_name'])
        RequestBase().specification_yaml(case_info)


@allure.feature(next(m_id) + 'ERP进销存-业务场景-销售出库核心链路')
@pytest.mark.business
@pytest.mark.smoke
class TestSalesScenario:

    @allure.story(next(c_id) + '新增出库单-查询-审核-收款')
    @pytest.mark.parametrize('case_info', get_testcase_yaml('./testcase/ERP/Business_Scenario/SalesScenario.yml'))
    def test_sales_scenario(self, case_info):
        allure.dynamic.title(case_info['baseInfo']['api_name'])
        RequestBase().specification_yaml(case_info)
