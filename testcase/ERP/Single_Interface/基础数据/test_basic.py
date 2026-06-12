import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + 'ERP进销存-基础数据（单接口）')
class TestBasicData:

    @allure.story(next(c_id) + "用户列表查询")
    @pytest.mark.run(order=1)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/ERP/Single_Interface/基础数据/user_list.yaml"))
    def test_user_list(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
