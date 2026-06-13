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
    """Preserve token from login, clear all other extract data before business scenario runs"""
    token_val = None
    if os.path.exists(FILE_PATH['EXTRACT']):
        with open(FILE_PATH['EXTRACT'], 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'token' in data:
                token_val = data['token']
    ReadYamlData().clear_yaml_data()
    if token_val:
        ReadYamlData().write_yaml_data({'token': token_val})


@allure.feature(next(m_id) + 'ERP进销存-采购入库业务场景')
class TestERPPurchaseBusinessScenario:

    @allure.story(next(c_id) + '供应商-商品-仓库-采购入库-库存查询流程')
    @pytest.mark.parametrize('case_info', get_testcase_yaml('./testcase/ERP/Business_Scenario/BusinessScenario.yml'))
    def test_business_scenario(self, case_info):
        allure.dynamic.title(case_info['baseInfo']['api_name'])
        RequestBase().specification_yaml(case_info)
