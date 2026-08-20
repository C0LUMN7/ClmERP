import allure
import pytest
from api.framework.yaml_loader import load_case_pairs
from api.framework.runner import run_case
from shared.test_data import m_id, c_id


@allure.feature(next(m_id) + '销售管理（单接口）')
@pytest.mark.single
class TestSales:

    @allure.story(next(c_id) + '新增销售出库单')
    @pytest.mark.run(order=8)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/sales/sale_add.yaml"))
    def test_sale_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/sales/sale_add.yaml")

    @allure.story(next(c_id) + '查询销售出库单')
    @pytest.mark.run(order=9)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/sales/sale_get_detail.yaml"))
    def test_sale_get_detail(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/sales/sale_get_detail.yaml")

    @allure.story(next(c_id) + '审核销售出库单')
    @pytest.mark.run(order=10)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/sales/sale_set_status.yaml"))
    def test_sale_set_status(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/sales/sale_set_status.yaml")

    @allure.story(next(c_id) + '新增收款单（销售收款）')
    @pytest.mark.run(order=11)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/sales/receipt_add.yaml"))
    def test_receipt_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/sales/receipt_add.yaml")
