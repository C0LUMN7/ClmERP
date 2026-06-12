import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil_business import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + 'ERP进销存-采购入库业务场景')
class TestERPPurchaseBusinessScenario:

    @allure.story(next(c_id) + '供应商-商品-仓库-采购入库-库存查询流程')
    @pytest.mark.parametrize('case_info', get_testcase_yaml('./testcase/ERP/Business_Scenario/BusinessScenario.yml'))
    def test_business_scenario(self, case_info):
        allure.dynamic.title(case_info['baseInfo']['api_name'])
        RequestBase().specification_yaml(case_info)
