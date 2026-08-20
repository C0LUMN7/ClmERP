# performance（性能测试）

Locust 性能测试目录。

当前包含只读性能测试入口：

- `locustfile.py`：只读 Locust 用户模型，包含登录、商品查询、库存查询和单据查询。
- `reports/locust/`：后续 Locust HTML、CSV 和资源监控记录输出目录。

执行入口必须显式使用：

```bash
python run.py performance --users 1 --spawn-rate 1 --run-time 1m --scenario readonly
```

只读接口来源：

- `/user/login`：来自现有 `api/login.yaml`、`shared/api_client.py` 和 `shared/debugtalk.py`。
- `/material/list`：来自现有 `api/cases/goods/goods_read.yaml`。
- `/material/getListWithStock`：来自 jshERP 商品库存页面 `MaterialStock.vue` 的只读列表接口。
- `/depotHead/list`：来自 jshERP 单据列表页面的只读列表接口；现有 API 用例也已使用同一
  `depotHead` 模块的详情、审核接口。

本阶段不执行写入类性能压测，不给出生产容量结论；当前仅保留只读性能测试基线，
不包含采购、销售、审核、反审核、删除、付款、收款等写入类性能场景，也不包含
`AUTO_PERF_` 测试数据创建或清理逻辑。
