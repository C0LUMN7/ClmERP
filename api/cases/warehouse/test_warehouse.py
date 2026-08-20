import allure
import pytest
from api.framework.yaml_loader import load_case_pairs
from api.framework.runner import run_case
from shared.test_data import m_id, c_id


@allure.feature(next(m_id) + 'ERP进销存-仓库管理（单接口）')
@pytest.mark.single
class TestWarehouse:

    @allure.story(next(c_id) + '新增仓库')
    @pytest.mark.run(order=12)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/warehouse/depot_create.yaml"))
    def test_depot_add(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/warehouse/depot_create.yaml")

    @allure.story(next(c_id) + '查看仓库列表')
    @pytest.mark.smoke
    @pytest.mark.run(order=13)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/warehouse/depot_read.yaml"))
    def test_depot_list(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/warehouse/depot_read.yaml")

    @allure.story(next(c_id) + '更新仓库')
    @pytest.mark.run(order=14)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/warehouse/depot_update.yaml"))
    def test_depot_update(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/warehouse/depot_update.yaml")

    @allure.story(next(c_id) + '删除仓库')
    @pytest.mark.run(order=15)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/warehouse/depot_delete.yaml"))
    def test_depot_delete(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/warehouse/depot_delete.yaml")
