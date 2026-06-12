import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + 'ERP进销存-销售管理（单接口）')
class TestSales:

    @allure.story(next(c_id) + "采购销售统计")
    @pytest.mark.run(order=1)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/销售管理/sale_statistics.yaml"))
    def test_sale_statistics(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
