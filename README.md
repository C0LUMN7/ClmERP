# ERP 接口自动化测试框架

基于 jshERP 进销存系统的接口自动化测试框架，用于接口回归、业务链路验证和数据一致性校验。通过一键回归和 GitHub Actions 持续集成，提升测试效率。

## 被测系统

| 项               | 值                                    |
| ---------------- | ------------------------------------- |
| system.name      | jshERP                                |
| repository       | https://github.com/jishenghua/jshERP  |
| environment      | cloud_test（另有可选 local）            |
| deployed_version | 待确认（云端测试实例部署版本，确认后通过环境变量 `ERP_VERSION` 写入） |
| deployed_commit  | 待确认（可选，能够确认时再填写）          |

被测系统版本信息同时记录在 `config/settings.py` 与 `config/environments.yaml.example` 中；无法确认精确版本/Commit 时如实标记待确认，不伪造。

## 项目亮点

- **YAML 数据驱动** — 测试数据与脚本分离，新增接口用例只需编写 YAML 文件，无需修改框架代码
- **JSONPath 提取与接口参数传递** — 通过 `extract.yaml` 实现接口间数据依赖，一个接口的响应字段可自动提取并传递给后续接口，串联完整业务链路
- **Token 自动管理** — session 级 fixture 自动完成登录鉴权，Token 过期时自动检测并重新登录，保证长时间测试稳定性
- **多类型断言 + MySQL 数据库断言** — 支持 contains、eq、ne、rv、db、db_eq 六种断言，不只验证状态码，还校验数据落库一致性
- **全面的场景覆盖** — 覆盖单接口 CRUD、采购/销售完整业务链路、Token 鉴权异常、库存溢出、重复提交、重复审核、超额收款等异常与边界场景
- **基于 pytest marker 的一键回归** — 通过 `run.py api --suite` 选择 smoke / single / business / exception / all，统一处理报告生成
- **GitHub Actions 持续集成** — 手动触发真实接口测试并归档报告；push 触发仅做语法检查和用例收集，不污染测试环境

## 技术栈

| 技术/工具           | 作用                    |
| ------------------- | ----------------------- |
| Python              | 编程语言                |
| pytest              | 测试执行与用例管理      |
| requests            | HTTP 接口请求           |
| YAML                | 测试数据驱动            |
| JSONPath            | 响应字段提取            |
| MySQL / PyMySQL     | 数据库断言              |
| Allure              | 可视化测试报告          |
| GitHub Actions      | CI 自动化执行与报告归档 |

## 项目结构

```
column-erp-testing/
├── api/                      # API 自动化（P0 合并骨架）
│   ├── conftest.py           # API 登录、Token、数据清理 fixture
│   ├── login.yaml            # 登录用例（真实 YAML 基线）
│   └── cases/
│       ├── goods/            # 商品管理单接口测试及 YAML
│       ├── warehouse/        # 仓库管理单接口测试及 YAML
│       ├── purchase/         # 采购管理单接口测试及 YAML
│       ├── sales/            # 销售管理单接口测试及 YAML
│       ├── scenarios/        # 采购、销售完整接口链路
│       └── negative/         # 异常与边界测试
├── ui/                       # Playwright UI 自动化（P0 技术骨架）
│   ├── conftest.py           # 浏览器/Context fixture 骨架（P2 启用）
│   └── cases/                # P0 仅收集骨架用例，正式 ERP UI 用例待 P2
├── performance/              # Locust 性能测试（P0 骨架目录，P4 实现）
├── shared/                   # API/UI/性能共享能力（P0 骨架目录）
├── config/                   # 统一配置（P0 新增）
│   ├── settings.py           # 多环境配置读取与 preflight 预检
│   └── environments.yaml.example
├── reports/                  # 统一运行产物（Git 忽略）
├── base/                     # 核心框架层（现有）：请求调度、参数替换、断言、自动重登
├── common/                   # 公共组件层（现有）：断言引擎、数据库连接、动态数据生成、通知
├── conf/                     # 配置层（现有）：config.ini、环境信息、全局常量
├── testcase/ERP/             # 原接口项目用例（保留，已复制迁移至 api/cases/）
├── .github/workflows/        # GitHub Actions 工作流定义
├── run.py                    # 统一执行入口（api / ui / preflight）
├── pytest.ini                # pytest 配置与 marker 定义
└── requirements.txt          # 合并后的依赖清单
```

## 核心流程

1. 读取 `conf/config.ini` 获取环境与数据库配置
2. session 级 fixture 自动登录，识别验证码，提取 Token 并写入 `extract.yaml`
3. 加载 YAML 测试用例
4. 替换动态参数，如 `${timestamp()}`、`${get_extract_data(token)}`
5. 发送 HTTP 请求
6. 使用 JSONPath 提取响应字段并写入 `extract.yaml`
7. 执行响应断言和数据库断言
8. 生成 Allure 报告、JUnit XML 和日志
9. 本地通过 `allure open` 查看报告；CI 中上传 artifacts

## 用例分组与一键回归

| suite     | marker    | 说明            |
| --------- | --------- | --------------- |
| smoke     | smoke     | 冒烟测试，快速验证核心链路 |
| single    | single    | 单接口测试       |
| business  | business  | 采购/销售业务链路测试 |
| exception | exception | 异常与边界场景测试 |
| all       | 无         | 全量回归         |

```bash
# 使用 run.py（推荐，统一处理报告生成与 CI 适配）
python run.py api --suite smoke
python run.py api --suite single
python run.py api --suite business
python run.py api --suite exception
python run.py api --suite all
python run.py ui --suite all

# 环境预检（对已配置项给出明确结果，缺失项标记待配置）
python run.py preflight

# 或直接使用 pytest 原生命令（P0 阶段门禁）
pytest api --collect-only
pytest ui --collect-only
pytest -m smoke api
```

## 测试场景覆盖

### 单接口测试

覆盖商品管理、仓库管理、采购管理、销售管理等模块的接口 CRUD 验证。

### 业务链路测试

- **采购链路**：创建商品 → 采购入库 → 查询 → 审核 → 付款
- **销售链路**：创建商品 → 销售出库 → 查询 → 审核 → 收款

### 异常与边界场景测试

| 场景                  | 校验重点                                   |
| -------------------- | ---------------------------------------- |
| Token 为空           | 无 Token 时不能正常访问核心接口              |
| Token 错误           | 非法 Token 不能获取业务数据                  |
| 销售出库数量大于库存     | 库存不能变成负数，不能错误扣减                 |
| 重复提交销售单号       | 相同单号不能重复生成有效单据                   |
| 重复审核销售单         | 库存不能重复扣减，单据状态保持一致              |
| 超额收款边界场景       | 系统允许超额收款，校验收款金额、欠款状态、明细关联的数据一致性 |

## 数据库断言

- `db`：验证 SQL 查询结果是否存在
- `db_eq`：验证 SQL 查询结果是否等于预期值

用于校验单据状态、库存变化、收付款金额、收款明细关联、异常请求是否产生脏数据等场景。

## GitHub Actions

当前工作流文件位于 `.github/workflows/api-test.yml`：

- **手动触发（`workflow_dispatch`）**：可选择 smoke / single / business / exception / all 套件，真实请求 ERP 测试环境并归档报告
- **push 触发**：只执行 `py_compile` 语法检查和 `pytest --collect-only` 用例收集，不请求真实接口，避免脏数据
- 使用 GitHub Secrets 动态生成 `conf/config.ini`
- 上传 artifacts：JUnit XML 结果文件、Allure 原始结果、Allure HTML 报告、日志

需要配置的 Secrets：

| Secret             | 说明            |
| ------------------ | --------------- |
| ERP_HOST           | ERP 服务地址     |
| MYSQL_HOST         | MySQL 地址       |
| MYSQL_PORT         | MySQL 端口       |
| MYSQL_USERNAME     | MySQL 用户名     |
| MYSQL_PASSWORD     | MySQL 密码       |
| MYSQL_DATABASE     | 数据库名          |
| DINGTALK_WEBHOOK   | 钉钉 Webhook（可选） |
| DINGTALK_SECRET    | 钉钉加签密钥（可选） |
| EMAIL_HOST         | 邮件 SMTP（可选）  |
| EMAIL_PORT         | 邮件端口（可选）   |
| EMAIL_USER         | 邮箱账号（可选）   |
| EMAIL_PASSWD       | 邮箱授权码（可选）  |
| EMAIL_ADDRESSEE    | 收件人（可选）     |

## 快速开始

```bash
git clone https://github.com/C0LUMN7/column-erp-testing.git
cd column-erp-testing
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp conf/config.ini.example conf/config.ini
```

编辑 `conf/config.ini`，填写测试环境地址、数据库连接和通知配置。

执行冒烟测试：

```bash
python run.py api --suite smoke
```

## 查看 Allure 报告

```bash
allure open ./reports/allure-report
```

或使用 Python HTTP 服务：

```bash
python -m http.server 8080 -d ./reports/allure-report
```

浏览器访问 `http://localhost:8080`。

> 不要直接双击 `index.html` 打开，浏览器安全策略会阻止 JS 加载，导致页面一直 Loading。

## 注意事项

- 不要在生产环境执行新增、修改、审核、付款、收款等有副作用的用例
- GitHub Actions 真实接口测试建议手动触发，push 只做轻量检查，避免污染测试环境
- `conf/config.ini`、`extract.yaml`、报告和日志不应提交到 Git
- 数据库断言需要确保 MySQL 能被测试执行环境访问
- 推荐优先使用 `python run.py api --suite <suite>`，它会自动处理 Allure 报告生成、环境信息注入和 CI 适配

## 后续优化

- 引入测试数据工厂，进一步提升数据准备和清理能力
- 增加更多参数异常、权限异常和并发场景
- 后续可将 GitHub Actions 切换为 self-hosted runner 或 Jenkins，避免数据库暴露公网
