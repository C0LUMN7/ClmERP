import allure
import pytest
from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + '销售管理（单接口）')
@pytest.mark.single
class TestSales:

    @allure.story(next(c_id) + '新增销售出库单')
    @pytest.mark.run(order=8)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./api/cases/sales/sale_add.yaml", flat=True))
    def test_sale_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '查询销售出库单')
    @pytest.mark.run(order=9)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./api/cases/sales/sale_get_detail.yaml"))
    def test_sale_get_detail(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '审核销售出库单')
    @pytest.mark.run(order=10)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./api/cases/sales/sale_set_status.yaml"))
    def test_sale_set_status(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '新增收款单（销售收款）')
    @pytest.mark.run(order=11)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./api/cases/sales/receipt_add.yaml"))
    def test_receipt_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)