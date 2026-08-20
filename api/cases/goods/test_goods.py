import allure
import pytest
from api.framework.yaml_loader import load_case_pairs
from api.framework.runner import run_case
from shared.test_data import m_id, c_id


@allure.feature(next(m_id) + 'ERP进销存-商品管理（单接口）')
@pytest.mark.single
class TestGoods:

    @allure.story(next(c_id) + '新增商品')
    @pytest.mark.smoke
    @pytest.mark.run(order=1)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/goods/goods_create.yaml"))
    def test_goods_create(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/goods/goods_create.yaml")

    @allure.story(next(c_id) + '商品查询')
    @pytest.mark.smoke
    @pytest.mark.run(order=2)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/goods/goods_read.yaml"))
    def test_goods_read(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/goods/goods_read.yaml")

    @allure.story(next(c_id) + '更新商品')
    @pytest.mark.run(order=3)
    @pytest.mark.parametrize('base_info,testcase', load_case_pairs("./api/cases/goods/goods_update.yaml"))
    def test_goods_update(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        run_case(base_info, testcase, yaml_file="./api/cases/goods/goods_update.yaml")
