import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil_business import RequestBase
from base.generateId import m_id, c_id


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
