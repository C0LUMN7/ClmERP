import allure
import pytest
from api.framework.yaml_loader import load_case_pairs
from api.framework.runner import run_case
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + '采购管理（单接口）')
@pytest.mark.single
class TestPurchase:

    @allure.story(next(c_id) + '新增采购入库单')
    @pytest.mark.run(order=4)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/purchase/buy_add.yaml"))
    def test_depot_head_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/purchase/buy_add.yaml")

    @allure.story(next(c_id) + '查询采购入库单')
    @pytest.mark.run(order=5)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/purchase/buy_get_detail.yaml"))
    def test_depot_head_get_detail(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/purchase/buy_get_detail.yaml")

    @allure.story(next(c_id) + '审核采购入库单')
    @pytest.mark.run(order=6)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/purchase/buy_set_status.yaml"))
    def test_depot_head_batch_set_status(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/purchase/buy_set_status.yaml")

    @allure.story(next(c_id) + '新增付款单（采购付款）')
    @pytest.mark.run(order=7)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/purchase/payment_add.yaml"))
    def test_payment_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/purchase/payment_add.yaml")
