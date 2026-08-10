import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + '采购管理（单接口）')
@pytest.mark.single
class TestPurchase:

    @allure.story(next(c_id) + '新增采购入库单')
    @pytest.mark.run(order=4)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/buy_add.yaml", flat=True))
    def test_depot_head_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '查询采购入库单')
    @pytest.mark.run(order=5)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/buy_get_detail.yaml"))
    def test_depot_head_get_detail(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '审核采购入库单')
    @pytest.mark.run(order=6)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/buy_set_status.yaml"))
    def test_depot_head_batch_set_status(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '新增付款单（采购付款）')
    @pytest.mark.run(order=7)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/采购管理/payment_add.yaml"))
    def test_payment_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
