import allure
import pytest

from api.framework.runner import run_scenario_file
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + 'ERP进销存-业务场景-采购入库核心链路')
@pytest.mark.business
@pytest.mark.smoke
class TestPurchaseScenario:

    @allure.story(next(c_id) + '新增入库单-查询-审核-付款')
    def test_purchase_scenario(self):
        allure.dynamic.title('采购入库核心链路（创建商品-入库-查询-审核-付款）')
        run_scenario_file('./api/cases/scenarios/PurchaseScenario.yml')


@allure.feature(next(m_id) + 'ERP进销存-业务场景-销售出库核心链路')
@pytest.mark.business
@pytest.mark.smoke
class TestSalesScenario:

    @allure.story(next(c_id) + '新增出库单-查询-审核-收款')
    def test_sales_scenario(self):
        allure.dynamic.title('销售出库核心链路（创建商品-出库-查询-审核-收款）')
        run_scenario_file('./api/cases/scenarios/SalesScenario.yml')
