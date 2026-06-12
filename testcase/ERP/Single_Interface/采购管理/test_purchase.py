import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + 'ERP进销存-采购管理（单接口）')
class TestPurchase:

    @allure.story(next(c_id) + "新增供应商/客户")
    @pytest.mark.run(order=1)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/supplier_add.yaml"))
    def test_supplier_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "供应商列表查询")
    @pytest.mark.run(order=2)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/supplier_list.yaml"))
    def test_supplier_list(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
