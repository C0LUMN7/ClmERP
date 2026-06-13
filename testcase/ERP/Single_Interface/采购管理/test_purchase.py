import allure
import pytest
import yaml
import os

from common.readyaml import get_testcase_yaml, ReadYamlData
from base.apiutil import RequestBase
from base.generateId import m_id, c_id
from conf.setting import FILE_PATH


@pytest.fixture(scope='module', autouse=True)
def clear_extract_before_purchase():
    token_val = None
    if os.path.exists(FILE_PATH['EXTRACT']):
        with open(FILE_PATH['EXTRACT'], 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'token' in data:
                token_val = data['token']
    ReadYamlData().clear_yaml_data()
    if token_val:
        ReadYamlData().write_yaml_data({'token': token_val})


@allure.feature(next(m_id) + 'ERP进销存-采购管理（单接口）')
class TestPurchase:

    @allure.story(next(c_id) + '创建商品条码')
    @pytest.mark.run(order=1)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/material_add.yaml"))
    def test_material_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '新增采购入库单')
    @pytest.mark.run(order=2)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/depotHead_add.yaml"))
    def test_depot_head_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '根据编号查询采购入库单')
    @pytest.mark.run(order=3)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/depotHead_get_detail.yaml"))
    def test_depot_head_get_detail(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '审核/反审核采购入库单')
    @pytest.mark.run(order=4)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/depotHead_batch_set_status.yaml"))
    def test_depot_head_batch_set_status(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
