import allure
import pytest
from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + 'ERP进销存-仓库管理（单接口）')
@pytest.mark.single
class TestWarehouse:

    @allure.story(next(c_id) + '新增仓库')
    @pytest.mark.run(order=12)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./api/cases/warehouse/depot_create.yaml"))
    def test_depot_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '查看仓库列表')
    @pytest.mark.smoke
    @pytest.mark.run(order=13)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./api/cases/warehouse/depot_read.yaml"))
    def test_depot_list(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '更新仓库')
    @pytest.mark.run(order=14)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./api/cases/warehouse/depot_update.yaml"))
    def test_depot_update(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '删除仓库')
    @pytest.mark.run(order=15)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./api/cases/warehouse/depot_delete.yaml"))
    def test_depot_delete(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
