# ERP 自动化测试框架

本项目面向开源进销存系统 jshERP，整合 API 自动化、Playwright UI 自动化、跨层 E2E 冒烟和 Locust 只读性能基线。当前文档描述的是仓库已有能力和执行边界；未在 GitHub Actions 中真实跑通的内容不会标记为已通过。

## 被测系统

| 项 | 值 |
| --- | --- |
| system.name | jshERP |
| repository | https://github.com/jishenghua/jshERP |
| environment | cloud_test（可通过 `ERP_ENV` 切换） |
| deployed_version | 管伊佳ERP V3.6 或通过 `ERP_VERSION` 覆盖 |
| deployed_commit | 待确认，能够确认时再补充 |

## 当前能力

- API 自动化：复用真实 jshERP YAML 基线，覆盖商品、仓库、采购、销售、异常边界和采购/销售接口链路。
- UI 自动化：使用官方 `pytest-playwright`，包含登录、采购转入库、销售转出库等 ERP 页面冒烟用例；失败产物输出到统一 Playwright 目录。
- E2E 冒烟：采购和销售跨层闭环，串联 UI 操作、API 查询和数据库校验；需要真实 ERP、账号和数据库配置。
- Locust 只读性能基线：仅包含登录、商品列表、库存列表和单据列表等只读请求，不执行采购、销售、审核、付款、收款等写入类性能场景。
- 统一入口：根目录 `run.py` 负责 API、UI、E2E、环境预检和性能入口。
- 报告产物：API/UI/E2E 使用分目录 Allure 原始结果，UI/E2E 使用 Playwright 截图、视频和 Trace，性能输出 Locust HTML、CSV 和日志。

## 技术栈

| 技术/工具 | 作用 |
| --- | --- |
| Python / pytest | 测试执行、fixture 和 marker 管理 |
| requests / YAML / JSONPath | API 请求、数据驱动和响应字段提取 |
| Playwright | Web UI 自动化、截图、视频和 Trace |
| MySQL / PyMySQL | 数据库断言和测试数据复核 |
| Allure | API、UI、E2E 可视化报告 |
| Locust | 只读性能基线与 HTML/CSV 输出 |
| GitHub Actions | 质量门禁与手动性能流水线 |

## 项目结构

```text
ClmERP/
├── .github/workflows/        # GitHub Actions workflow
├── api/                      # API 自动化用例、YAML、Schema 和统一执行器
├── ui/                       # Playwright UI 用例、fixture、页面对象
├── e2e/                      # API + UI + 数据库跨层冒烟
├── performance/              # Locust 只读性能测试
├── shared/                   # API/UI/E2E 复用的客户端和数据库辅助方法
├── config/                   # 统一配置读取与配置模板
├── reports/                  # 统一运行产物（Git 忽略）
├── run.py                    # 统一执行入口
├── pytest.ini                # pytest 配置与 marker
└── requirements.txt          # 依赖清单
```

## 统一入口

```bash
# 环境预检
python run.py preflight

# API
python run.py api --suite smoke
python run.py api --suite single
python run.py api --suite business
python run.py api --suite negative
python run.py api --suite all
python run.py api --collect-only

# UI
python run.py ui --suite smoke
python run.py ui --suite all
python run.py ui --browser chromium --headed
python run.py ui --collect-only

# E2E
python run.py e2e --suite smoke
python run.py e2e --suite all
python run.py e2e --collect-only

# 只读性能基线
python run.py performance --scenario readonly --users 1 --spawn-rate 1 --run-time 1m

# 显式发送通知
python run.py notify --report reports/api_results.xml --channel email
python run.py notify --report reports/api_results.xml --channel dingtalk
python run.py notify --report reports/api_results.xml --channel all
```

`performance` 必须显式执行，不会混入 API/UI/E2E 普通回归。当前性能入口只允许 `readonly` 场景，最大用户数 `10`，最长运行时间 `5m`。

`notify` 也必须显式执行，API/UI/E2E 默认执行完成后不会自动发送通知。通知依赖本地 `config/local.ini` 或环境变量中的钉钉、邮箱配置。

## 配置说明

本地优先使用环境变量或 `config/local.ini`；模板见 `config/local.ini.example` 和 `config/environments.yaml.example`。敏感信息不要写入代码、YAML、报告或提交记录。

常用环境变量：

| 变量 | 说明 |
| --- | --- |
| `ERP_ENV` | 环境名，默认 `cloud_test` |
| `ERP_VERSION` | 云端测试实例版本说明 |
| `ERP_API_URL` | jshERP 后端 API 根地址 |
| `ERP_UI_URL` | jshERP 前端根地址 |
| `ERP_USERNAME` | 测试账号 |
| `ERP_PASSWORD` | 测试密码 |
| `MYSQL_HOST` | MySQL 地址，E2E 和数据库断言需要 |
| `MYSQL_PORT` | MySQL 端口 |
| `MYSQL_USERNAME` | MySQL 用户名 |
| `MYSQL_PASSWORD` | MySQL 密码 |
| `MYSQL_DATABASE` | MySQL 数据库名 |
| `ERP_CATEGORY_ID` | 商品分类 ID |
| `ERP_DEPOT_ID` | 默认仓库 ID |
| `ERP_SUPPLIER_ORGAN_ID` | 供应商 ID |
| `ERP_CUSTOMER_ORGAN_ID` | 客户 ID |
| `ERP_SETTLE_ACCOUNT_ID` | 单据结算账户 ID |
| `ERP_FINANCE_ACCOUNT_ID` | 收付款财务账户 ID |
| `ERP_UI_LOGIN_SUCCESS_KIND` | UI 登录成功判断方式：`url` / `title` / `text` |
| `ERP_UI_LOGIN_SUCCESS_VALUE` | UI 登录成功判断值 |

## 报告路径

| 产物 | 路径 |
| --- | --- |
| API Allure 原始结果 | `reports/allure-results/api/` |
| UI Allure 原始结果 | `reports/allure-results/ui/` |
| E2E Allure 原始结果 | `reports/allure-results/e2e/` |
| Allure HTML 报告 | `reports/allure-report/<类型>-<时间戳>/` |
| Playwright 截图、视频、Trace | `reports/playwright/` |
| Locust HTML、CSV、日志 | `reports/locust/` |
| JUnit XML | `reports/api_results.xml`、`reports/ui_results.xml`、`reports/e2e_results.xml` |

`.runtime/auth/` 只用于 Playwright 登录态，不属于报告目录，不应上传为 artifact。

## GitHub Actions

当前仓库包含三个 workflow 文件：

| 文件 | 用途 |
| --- | --- |
| `.github/workflows/api-test.yml` | 旧 API workflow，保留兼容 |
| `.github/workflows/quality-gate.yml` | API/UI/E2E 质量门禁 |
| `.github/workflows/performance-tests.yml` | 手动只读性能流水线 |

质量门禁策略：

- PR 到 `master` 默认运行 `lint-and-collect`、`api-smoke`、`ui-smoke`。
- PR 的 `api-smoke` 只做 API smoke 收集和 API 连通性检查，不执行数据库断言或数据库闭环。
- `master` push 或 `workflow_dispatch` 可运行 `e2e-smoke`。
- 建议 Required Checks 设置为 `lint-and-collect`、`api-smoke`、`ui-smoke`。
- 不建议把 `e2e-smoke` 和 `performance-tests` 设为普通 PR Required Checks。
- artifact 上传使用 `if: always()` 保留失败证据；测试步骤失败时 job 仍然失败，不使用 `continue-on-error` 掩盖结果。

手动性能流水线策略：

- 只能通过 `workflow_dispatch` 手动触发。
- 输入包含 `environment`、`scenario`、`users`、`spawn_rate`、`run_time`。
- `scenario` 只能是 `readonly`。
- `users` 最大 `10`，`run_time` 最长 `5m`。
- 正式执行前先跑 `1` 用户、`1m`、`readonly` 预检。
- 预检失败不得继续升压。
- 不执行写入类性能场景，不使用 `MYSQL_*` 做数据库闭环。
- 使用并发锁 `jsh-erp-performance`，同一时间只允许一个性能任务运行。

## GitHub Secrets

建议配置的 Secrets：

| Secret | 用途 |
| --- | --- |
| `ERP_API_URL` | 新质量门禁和性能流水线使用的 API 地址 |
| `ERP_UI_URL` | 新质量门禁使用的 UI 地址 |
| `ERP_USERNAME` | API/UI/E2E/性能测试账号 |
| `ERP_PASSWORD` | API/UI/E2E/性能测试密码 |
| `ERP_HOST` | 旧 API workflow 兼容字段；新 workflow 优先使用 `ERP_API_URL` / `ERP_UI_URL` |
| `MYSQL_HOST` | E2E 或非 PR 数据库断言需要 |
| `MYSQL_PORT` | E2E 或非 PR 数据库断言需要 |
| `MYSQL_USERNAME` | E2E 或非 PR 数据库断言需要 |
| `MYSQL_PASSWORD` | E2E 或非 PR 数据库断言需要 |
| `MYSQL_DATABASE` | E2E 或非 PR 数据库断言需要 |

暂不配置且不阻塞当前质量门禁的通知类 Secrets：

- `DINGTALK_WEBHOOK`
- `DINGTALK_SECRET`
- `EMAIL_*`

## 快速开始

```bash
git clone https://github.com/C0LUMN7/ClmERP.git
cd ClmERP
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/local.ini.example config/local.ini
```

填写 `config/local.ini` 或导出环境变量后，可先执行：

```bash
python run.py preflight
python run.py api --collect-only
python run.py ui --collect-only
python run.py e2e --collect-only
```

连接真实测试环境后，再按需要运行 API、UI、E2E 或只读性能命令。

## 注意事项

- 不要在生产环境执行会新增、修改、审核、付款、收款或影响库存的用例。
- PR 质量门禁不跑数据库闭环，不依赖 `MYSQL_*` Secrets。
- E2E 冒烟、完整数据库断言和只读性能基线依赖真实 ERP、测试数据库和稳定业务数据，当前作为本地真实环境手动验收执行。
- Locust 当前只用于只读性能基线，不能据此直接给出生产容量结论。
- 报告、日志、`.runtime/auth/`、本地配置和登录态文件不应提交或上传为敏感 artifact。

## 后续增强项

- 可后续补充更多稳定 UI 定位器和 ERP 页面用例。
- 可后续接入受控自托管 Runner，将完整 API/UI/E2E 业务闭环和只读性能基线纳入受控 CI 环境，减少数据库公网暴露。
- 可后续补充资源监控、阈值判定和性能趋势对比。
- 可后续增加更多安全清理策略和异常中断补偿流程。
