# ERP 全方面自动化测试框架合并改造方案

## 1. 文档目标

本方案用于将现有两个独立测试项目整合为一个面向 ERP 管理系统的综合自动化测试框架：

- 接口自动化项目：`/home/column/code/ClmERP`
- Playwright UI 自动化项目：`/home/column/code/playwright-ui`
- 新增能力：Locust 性能测试

合并后的项目统一覆盖：

1. API 单接口测试、业务场景测试、异常与边界测试。
2. Playwright Web UI 功能测试和端到端业务流程测试。
3. Locust 负载、压力、峰值和稳定性测试。
4. MySQL 数据库断言、测试数据准备与清理。
5. Allure 报告、Playwright 截图/视频/Trace、Locust 性能报告。
6. GitHub Actions 持续集成和手动性能测试流水线。

本次架构设计遵循以下原则：

- 按测试类型划分，打开仓库即可看到 API、UI、性能测试三个重点。
- 不为了形式上的“分层”制造大量空目录。
- 测试类型内部保持独立，配置、数据库、日志等真正通用的能力才共享。
- 合并执行入口、配置、依赖和报告体系，避免把两个项目简单拼接成两个子项目。
- 性能测试必须显式执行，不自动混入普通功能回归。
- 以秋招测开岗位作品为目标，优先保证真实、稳定、可运行、可解释，不以复刻企业级测试平台为目标。
- 当前版本只实现能够证明测开能力的最小闭环；不会直接提高演示效果或工程可信度的能力统一后置。

### 1.1 秋招版本的交付目标与范围边界

本项目当前目标是在尽可能短的时间内形成一个可用于简历、代码审阅和面试演示的 jshERP 自动化测试框架。完成标准不是目录或工具数量，而是以下能力能够真实运行并被清楚解释：

1. 敏感凭据与代码、YAML 分离。
2. API、UI、性能测试能够独立执行。
3. 现有真实 ERP YAML 可以通过统一 Runner 稳定运行，失败信息可定位。
4. 测试数据有唯一标识，只操作和清理本次创建的数据。
5. 至少完成一条采购和一条销售的 API/UI/数据库闭环。
6. Playwright 失败时能够提供截图和 Trace。
7. Locust 输出并发用户、响应时间、P95/P99、RPS/TPS、错误率、CPU/内存和结论。
8. 具备基础 CI、Allure/性能报告和可以让面试官快速理解项目的 README。

以下目标不属于当前秋招版本的交付门槛：完整自动部署 jshERP、企业级监控平台、分布式压测、全接口 Schema、完整安全测试平台、完整测试管理体系和大规模兼容性矩阵。这些能力统一记录在“后期改进优化方向”，不阻塞主线。

### 1.2 真实 ERP 数据与人工输入原则

当前接口项目 `testcase/ERP` 下的 YAML 不是演示数据，而是根据真实 ERP 接口文档、实际系统抓包和人工业务操作整理出的可用接口数据，包括请求路径、请求方法、请求头、业务参数、提取规则和断言。这些 YAML 应作为本次合并的**真实接口基线和优先数据来源**：

- 合并时直接迁移和复用，不要求用户重新提供已经存在的接口数据。
- 不得为了迁移方便擅自替换为虚构接口、示例字段或假业务数据。
- 目录调整或 Runner 重构时，应尽量保持 YAML 的业务含义、执行顺序和断言不变。
- 如果需要调整 YAML 格式，应先保证旧格式兼容或提供可验证的批量转换，并用真实测试环境回归。
- 只有当前 YAML 未覆盖、接口已经变化、UI 场景需要新增前置数据或性能场景需要特殊数据时，才要求用户补充资料。

UI 自动化与 API 自动化采用相同的“真实系统取材”原则，但两者的现状不同：现有 API YAML 已经从真实 jshERP 整理完成，可以直接作为基线；现有 Playwright UI 项目不是 ERP 页面，只能复用技术骨架，不能复用其业务用例。正式 UI 用例必须从用户部署在云服务器上的同一套 jshERP 测试实例中获取，由人工与 AI 配合整理：

- 人工在云端 jshERP 中选择并实际完成登录、商品、采购、销售等业务操作，确认角色权限、前置数据、操作步骤、页面结果和业务预期。
- 人工提供必要的页面信息，例如操作说明、截图/录屏、Playwright codegen、关键 DOM/稳定属性或允许 AI 访问测试页面；账号密码只配置在本地环境变量或 Secret 中。
- AI 结合实际页面信息、现有真实 API YAML、jshERP 接口文档和对应版本源码，将人工操作整理为结构化 UI 用例、Page Object、定位器、断言、数据准备和清理逻辑。
- AI 无法确认页面行为或业务预期时，必须列出需要人工补充的具体页面、步骤、账号、数据或预期结果，不能根据原非 ERP UI 项目虚构 ERP 页面和用例。
- UI 用例只有在云服务器上的真实 jshERP 页面执行并由人工确认结果后，才能标记为“真实场景完成”；仅生成 Page Object 或离线代码不能算完成。

每条正式 UI 用例至少应整理以下信息：用例名称、所属模块、测试角色、前置条件、测试数据、页面操作步骤、预期页面结果、API/数据库校验点和清理方式。第一批优先整理登录、采购和销售闭环所需页面，不追求一次性覆盖全部菜单。

后续使用 AI 修改代码时，必须区分两种完成状态：

1. **离线完成**：完成目录、代码、配置模板、用例收集和静态检查，但没有连接真实 ERP 环境。
2. **真实场景完成**：使用真实 ERP 地址、账号、接口、业务数据和数据库完成执行验证。

当真实验证所需资料不足时，AI 必须明确输出“需要人工提供”的资料清单并暂停对应的真实场景验收，不得自行猜测接口路径、字段、账号、业务 ID、页面定位器、数据库关系或性能阈值。离线代码完成不能表述为真实业务已经通过。

---

## 2. 当前接口自动化项目分析

### 2.1 建议保留的内容

| 当前内容 | 作用 | 合并处理 |
| --- | --- | --- |
| `testcase/ERP/Single_Interface` | 商品、仓库、采购、销售单接口测试 | 保留用例，迁入 `api/cases` 对应业务目录 |
| `testcase/ERP/Business_Scenario` | 采购、销售完整接口业务链路 | 保留，迁入 `api/cases/scenarios` |
| `testcase/ERP/Exception` | 鉴权、库存、重复操作、超额收款等异常场景 | 保留，迁入 `api/cases/negative` |
| YAML 数据驱动方式 | 请求、提取、断言与代码分离 | 保留并统一 YAML 场景格式 |
| JSONPath/正则提取 | 接口间参数传递 | 保留，后续减少对全局 `extract.yaml` 的依赖 |
| `common/assertions.py` | 响应与数据库断言 | 保留，迁入 API 框架层 |
| `common/connection.py` | MySQL 连接和查询 | 保留，改造成共享数据库组件 |
| 自动登录与 Token 重登 | 长时间回归稳定性 | 保留，移除硬编码账号密码 |
| 测试结束数据清理 | 防止 ERP 环境残留脏数据 | 保留，抽成可维护的清理逻辑 |
| Allure、JUnit、日志 | 测试结果展示和 CI 归档 | 保留，统一输出目录 |
| `.github/workflows/api-test.yml` | API 测试 CI 基础 | 保留思路，合并进统一 `quality-gate.yml` |

### 2.2 当前接口项目内部需要合并或优化的重复内容

#### `apiutil.py` 与 `apiutil_business.py` 重复

两个文件都实现了以下能力：

- 请求参数替换。
- HTTP 请求发送。
- Token 过期重新登录。
- 响应字段提取。
- Allure 附件。
- 响应和数据库断言。

二者只是输入形式不同：一个执行单条 YAML 用例，一个执行多步骤业务场景。合并后应统一为一个 `runner.py`：

- `run_case()` 执行一条接口用例。
- `run_scenario()` 按顺序调用多条接口步骤。

这样登录、提取、重试和断言逻辑只维护一份。

#### 通知统计逻辑重复

根目录 `conftest.py` 已通过 `pytest_terminal_summary` 生成摘要并发送通知，`common/send_notification.py` 又解析 Allure 结果发送通知。合并后只保留一套通知服务：

- pytest 执行结束时生成统一摘要。
- `shared/notification.py` 只负责发送邮件或钉钉消息。

#### 配置入口重复且存在硬编码

当前存在 `conf/setting.py`、`conf/operationConfig.py`、`config.ini`，同时登录重试代码中还硬编码了账号和密码，部分 YAML 也硬编码仓库、供应商、账户等 ID。

合并后应统一由 `config/settings.py` 读取：

- ERP API 地址。
- ERP UI 地址。
- MySQL 配置。
- 登录账号和密码。
- 默认仓库、客户、供应商和账户 ID。
- API/UI 超时。
- 通知配置。

敏感信息通过环境变量或本地未提交的配置文件提供。

### 2.3 不需要保留或不应原样迁移的内容

| 当前内容 | 处理建议 | 原因 |
| --- | --- | --- |
| `base/removefile.py` | 不作为独立核心模块迁移 | 只是简单产物清理，可并入统一运行入口或报告处理 |
| `base/generateId.py` | 评估后删除或简化 | Allure 展示不应依赖全局生成器决定顺序 |
| `base/__init__.py`、`common/__init__.py` 等空包文件 | 按新包结构重新创建 | 不需要机械复制旧结构 |
| 根目录 `extract.yaml` | 不提交，不作为跨测试类型共享状态 | 并发和失败重跑时容易相互污染 |
| `report/`、`logs/` 现有内容 | 不迁移历史产物 | 统一由新框架重新生成 |
| `__pycache__`、`.pytest_cache`、`.venv` | 不迁移 | 本地缓存和环境文件 |

---

## 3. 当前 Playwright UI 项目分析

### 3.1 建议保留的内容

UI 项目当前不是针对 ERP，但它已经形成了可复用的 Playwright 技术骨架。建议保留以下设计和实现思路：

| 当前内容 | 可复用能力 | 合并处理 |
| --- | --- | --- |
| 根 `conftest.py` | 浏览器启动参数、Context 参数、Allure 动态标题 | 精简后合并到 `ui/conftest.py` |
| `cases/conftest.py` | 已登录/未登录上下文、截图、视频附件 | 改造成 ERP 登录状态和独立 Context fixture |
| `cases/more_accounts/conftest.py` | 多账号、多 Context 场景 | 保留思路，用于采购员、销售员、管理员等角色 |
| `pages/` | Page Object 组织方式 | 保留模式，页面对象替换为 ERP 页面 |
| `mocks/mock_api.py` | 使用 `page.route()` Mock 后端响应 | 保留能力，ERP 场景初期整合为 `ui/mocks.py` |
| Trace、截图、视频 | UI 失败定位 | 保留，统一输出到 `reports/playwright` |
| Playwright 同步 API + pytest | 与现有 Python/pytest 技术栈一致 | 保留 |

### 3.2 UI 项目需要优化的地方

#### 不继续维护本地 Playwright 插件副本

`plugins/pytest_playwright.py` 是一份约 446 行的本地插件副本，并混入了 Allure 截图、视频等定制逻辑；`pytest.ini` 又通过 `-p no:playwright` 禁用外部插件，再加载本地插件。这会带来：

- Playwright 或 pytest 升级时需要人工同步插件源码。
- 与官方 `pytest-playwright` 产生行为差异。
- 截图、视频和 Context 处理代码在插件与 `cases/conftest.py` 中重复。

合并后直接依赖官方 `pytest-playwright`，仅在 `ui/conftest.py` 中保留 ERP 项目需要的少量定制 Hook。

#### 登录 Context 需要隔离

当前 `login_first` 在 session 级 Context 中登录并被多个测试共享，容易导致：

- 页面、Cookie 和 LocalStorage 状态相互污染。
- 一个测试修改状态后影响后续测试。
- 并行执行困难。

建议改为：

1. session 开始时登录一次并保存 `storage_state`。
2. 每条测试创建独立 BrowserContext。
3. 新 Context 加载已登录状态。
4. 测试结束关闭自己的 Context。

#### 去除硬编码

当前 UI 项目硬编码了：

- `http://47.116.12.183`
- `py/123456`
- `admin/123456`

合并后全部改由 `config/settings.py` 和环境变量提供。

### 3.3 不需要迁移的 UI 内容

| 当前内容 | 处理建议 | 原因 |
| --- | --- | --- |
| `allure_report/` | 不迁移 | 历史 HTML 报告 |
| `reports/` | 不迁移 | 历史 Allure 原始结果 |
| `test-results/` | 不迁移 | 历史截图、视频和 Trace |
| `plugins/pytest_playwright.py` | 不迁移 | 使用官方 `pytest-playwright` |
| `plugins/pytest_base_url_plugin.py` | 不迁移 | 官方/项目配置可提供 base URL |
| UI 项目的 `run.py` | 不迁移 | 与接口项目统一为一个根执行入口 |
| UI 项目的 `pytest.ini` | 不原样迁移 | 与根 pytest 配置合并，不能默认全局 `--headed` |
| UI 项目的 `requirements.txt` | 不独立保留 | 合并进根依赖清单 |
| 非 ERP 的历史页面与用例 | 不进入正式回归 | 只参考写法，在原仓库保留即可 |

现有 `add_project_page.py`、`project_list_page.py`、`add_module_page.py`、`list_env_page.py` 等页面对象，以及对应测试用例，不应简单改名后冒充 ERP 页面，而应根据 ERP 页面重新定位和封装。

---

## 4. 两个项目合并后的重复项与统一策略

| 重复或冲突点 | 接口项目现状 | UI 项目现状 | 合并策略 |
| --- | --- | --- | --- |
| 执行入口 | 根 `run.py` | 独立 `run.py` | 根目录只保留一个 `run.py` |
| pytest 配置 | API marker 和收集规则 | Playwright 全局 addopts | 合并为一个根 `pytest.ini`，UI 参数由运行命令传入 |
| conftest | 全局通知 + API fixture | Playwright fixture | 根、`api/`、`ui/` 三级作用域分开 |
| requirements | API 依赖 | UI 依赖 | 合并为一个 `requirements.txt` |
| Allure 结果 | `report/temp` | `reports` | 统一为 `reports/allure-results/api` 和 `ui` |
| Allure HTML | `report/allureReport` | `allure_report` | 统一为 `reports/allure-report` |
| 日志和 UI 产物 | `logs`、`report` | `test-results` | 统一收敛到 `reports/` |
| 服务地址 | `config.ini` API host | pytest `--base-url` | 配置中分别定义 API URL 和 UI URL |
| HTTP 调用 | requests 封装 | UI Mock 中 requests/route | 通用 ERP API Client 放 `shared/`，UI Mock 保留在 `ui/` |
| 动态数据 | `DebugTalk` | UUID 等散落在用例 | 统一为 `shared/test_data.py` |
| Allure 标题 | `generateId.py` + 装饰器 | docstring 动态标题 | 统一 feature/story/title 规范，不依赖全局编号生成器 |

---

## 5. 修改顺序与优先级

### 阶段门禁与共同验收规则

P0～P5 采用串行推进，不允许只因为代码已经生成或目录已经建立就直接进入下一阶段。每个阶段都必须满足以下条件：

1. 完成该阶段规定的代码和配置改造。
2. 按该阶段的跑通命令进行验证，保存日志、Allure、截图、Trace、性能报告或 CI 记录等证据。
3. AI 检查执行结果、失败原因、数据清理情况和遗留问题，并明确给出“通过”或“未通过”，不能把未验证的离线代码标记为完成。
4. 用户在真实云端 jshERP 中确认业务结果、页面状态、数据库影响和测试数据安全，并决定是否接受该阶段。
5. 只有用户与 AI 都确认阶段目标达成，才能进入下一阶段；只要存在阻断性失败、真实环境未验证或关键资料缺失，就停留在当前阶段继续修复。

共同验收不要求用户审核每一行代码，但必须能回答：执行了什么、结果是什么、是否符合真实 jshERP 业务、是否残留脏数据、是否具备进入下一阶段的条件。每个阶段结束时应留下简洁验收记录，包括执行命令、环境、结果、报告位置、遗留问题和最终结论。

### P0：建立合并骨架，保证两类测试可以独立运行

这是最高优先级，目标是完成仓库整合但不立即大规模重写业务。

1. 创建 `api/`、`ui/`、`performance/`、`shared/`、`config/`、`reports/`。
2. 将原 API 测试和 YAML 用例迁入 `api/cases/`。
3. 将 Playwright 的 fixture 技术骨架迁入 `ui/conftest.py`。
4. 根目录只保留一个 `run.py`、`pytest.ini` 和 `requirements.txt`。
5. 合并 `.gitignore`，忽略报告、截图、视频、Trace、Token、本地配置以及 `.runtime/auth/` 登录状态。
6. 将被测系统明确为开源项目 jshERP，在 README 或配置中记录当前云端测试实例所使用的版本、Tag 或 Commit；暂不开发自动识别和版本同步系统。
7. 提供最小多环境配置，至少区分当前 `cloud_test` 与可选的 `local`；API、UI、数据库地址和敏感凭据从配置或 Secret 读取，不写入用例。
8. 增加基础 `preflight` 环境预检，只检查当前执行真正依赖的前端/API 连通性、登录、测试账号、MySQL 连接和核心业务 ID；暂不建设完整运维巡检系统。
9. 验证以下命令互不干扰：

   ```bash
   pytest api --collect-only
   pytest ui --collect-only
   ```

建议的被测系统基线配置：

```yaml
system:
  name: jshERP
  repository: https://github.com/jishenghua/jshERP
  environment: cloud_test
  deployed_version: ${ERP_VERSION}
  # deployed_commit 为可选项，能够确认时再填写
```

验收标准：API 收集不启动浏览器；UI 收集不触发 API 自动登录或数据库清理；README 或配置能够说明当前被测 jshERP 版本；连接真实环境前能够发现最常见的地址、账号、数据库和核心数据配置问题。

**P0 跑通目标与阶段门禁：**

```bash
pytest api --collect-only
pytest ui --collect-only
```

- 两条命令都必须成功收集对应用例，不允许出现导入、fixture、插件或配置错误。
- API 收集不能启动浏览器，UI 收集不能触发 API 自动登录、数据库清理或性能任务。
- 基础 `preflight` 能对当前已配置项给出明确结果；缺失真实环境资料时允许标记为待配置，但不能伪造通过结果。
- AI 提供收集结果和冲突检查，用户确认目录、环境配置和被测 jshERP 信息符合实际。
- P0 未通过时不得进入 P1；必须先解决目录、依赖、pytest 配置和 fixture 隔离问题。

**本阶段可直接使用的现有资料：**

- 当前接口项目的全部 Python 代码和真实 YAML 用例。
- 当前 UI 项目的 Playwright fixture、Page Object、Mock 和报告处理思路。
- 两个项目现有的依赖、pytest 配置和运行入口。

**本阶段需要人工提供的资料：**

- 仅进行目录迁移、导入修复和 `--collect-only` 检查时，不需要新增 ERP 接口或业务数据。
- 如要求 P0 就连接真实环境做冒烟验证，需要提供或确认可访问的 ERP API 地址、ERP UI 地址、本地测试配置和测试账号；已有可用 `config.ini` 时只需确认其仍然有效，不必重复提供。
- 尽量确认云服务器当前部署的 jshERP 版本、Tag 或 Commit，以及是否修改过官方源码；暂时无法获得精确 Commit 时，可先在 README 记录部署来源和已知版本，不阻塞项目合并。
- 当前个人云服务器测试实例可以直接作为专用测试环境，不强制额外建立新租户；必须确认其中没有需要保护的正式业务数据。

**资料不足时的边界：**可以完成合并骨架、依赖整理和测试收集，但不能宣称 API 或 UI 已在真实 ERP 环境运行通过。

### P1：统一 API 框架核心

1. 合并 `apiutil.py` 与 `apiutil_business.py` 为 `api/framework/runner.py`。
2. 拆分 YAML 加载、模板解析、响应提取和断言职责。
3. 保持现有 YAML 用例可以继续运行，避免迁移时同时重写所有测试数据。
4. 将硬编码登录账号、密码和业务 ID 移到配置。
5. 把全局 `extract.yaml` 改为每次测试会话独立的运行上下文；短期内如果继续使用文件，也必须放进未跟踪的运行目录并在会话开始时清理。
6. 增加 `api/schemas/`，只选择 2～3 个有代表性的稳定接口展示 JSON Schema 契约校验，建议覆盖登录、商品/库存查询、采购或销售单详情；全接口 Schema 后置。
7. 明确 YAML 与 Python 的职责边界：YAML 只描述请求、变量、标准断言和清理声明；循环、复杂计算、签名加密、特殊业务校验和异常恢复由 Python 实现，避免 YAML 演变成难维护的脚本语言。
8. Runner 错误必须定位到 YAML 文件、用例名称、执行步骤、请求地址、失败断言、期望值、实际值和变量来源。
9. 校验接口时以云服务器实际请求/响应为第一依据；能够确认部署版本时再使用对应 Controller、Service、Mapper 和接口文档辅助分析，不为此额外建设源码同步能力。

验收标准：单接口、业务场景、异常测试均通过同一个 Runner 执行；关键稳定接口能够执行 Schema 校验；YAML 失败可以精确定位，复杂业务逻辑没有继续堆入 YAML。

**P1 跑通目标与阶段门禁：**

连接云端 jshERP 执行 API 冒烟验证，至少跑通：登录与 Token 提取、一个只读查询、一个写接口、一个数据库断言，以及一条现有采购或销售 API 场景。

```bash
python run.py api --suite smoke
```

- AI 检查 Runner、变量提取、响应断言、数据库断言、日志和失败定位是否有效。
- 用户确认请求确实作用于自己的云端 jshERP，接口结果和业务数据变化符合实际。
- P1 的目标是证明统一 Runner 能真实执行现有 YAML，不要求此时完成所有 YAML 的安全治理。
- 冒烟用例存在未解释失败、没有连接真实 jshERP 或没有形成可检查的执行证据时，不得进入 P1.5。

**本阶段可直接使用的现有资料：**

- `testcase/ERP` 下现有 YAML 全部视为真实可用接口基线，重构 Runner 时优先保持兼容。
- 现有登录、Token 提取、采购、销售、商品、仓库、异常场景和数据库断言可以直接迁移。
- 不应要求用户为了框架重构重新抓取这些已经存在的接口。

**本阶段仅在以下情况需要人工提供资料：**

- 真实 ERP 接口相较 YAML 已经变更：提供新的接口文档、抓包结果、请求/响应样例或字段说明。
- 登录、验证码、Token 规则发生变化：提供当前登录流程、测试账号和实际响应样例。
- YAML 中固定的仓库、客户、供应商、账户、商品分类等业务 ID 已失效：提供新的有效测试数据或可查询这些数据的接口。
- 新增现有 YAML 未覆盖的 ERP 模块：提供接口文档、真实抓包、必填字段、前置条件、预期响应和清理方式。
- 数据库断言或清理关系不明确：提供相关表结构、字段关系、业务状态含义或已验证 SQL。

**资料不足时的边界：**可以完成 Runner 合并、旧 YAML 兼容、静态检查和用例收集；遇到真实接口失败时必须报告缺少的具体接口或数据，不能用 Mock 响应代替真实 API 验收。

### P1.5：修复和治理现有 YAML 用例

该阶段安排在 API Runner 统一之后、ERP UI 开发之前。现有 YAML 均能通过语法解析，接口路径和请求数据来自真实 ERP，应继续作为业务基线；本阶段只修复敏感信息、误操作风险、环境耦合和可能导致误判的数据写法，不把真实数据替换成演示数据。

#### YAML 问题与修复清单

| 优先级 | 问题文件 | 当前问题 | 修复方式 | 是否需要人工资料 |
| --- | --- | --- | --- | --- |
| 最高 | `testcase/ERP/loginName.yaml` | 写有真实账号 `jsh` 和密码原值 `123456`；运行时 MD5 不能保护仓库中的明文 | 改为从环境变量或本地 Secret 读取；同时清理两份自动重登代码中的相同硬编码 | 代码改造不需要提供密码；真实验证前由用户在本地环境或 CI Secrets 中配置账号密码 |
| 最高 | `商品管理/goods_read.yaml` | 直接提取 `$.data.rows[0].id`，后续可能更新环境中原有商品 | 按本次创建的唯一商品名/条码精确查询并提取对应 ID，或直接从创建响应提取 ID | 如果现有列表接口过滤参数或创建响应结构不明确，需要提供真实请求/响应或抓包 |
| 最高 | `仓库管理/depot_read.yaml` | 直接提取 `$.data.rows[0].id`，后续更新和删除可能作用于真实仓库 | 创建唯一测试仓库并只提取该仓库 ID；更新、删除前校验测试前缀 | 如果仓库查询接口不支持按名称过滤，需要提供真实查询方式或创建响应样例 |
| 高 | 商品、采购、销售和异常 YAML | 写死 `categoryId=91`、`depotId=124`、`organId=196/204`、`accountId=86/105` 等环境 ID | 保留当前真实值作为当前环境配置，但从 YAML 移到配置或前置查询，并增加启动预检 | 当前环境继续运行可先不补数据；切换环境或 ID 失效时需要确认分类、仓库、供应商、客户和账户映射 |
| 高 | `depot_create.yaml`、`depot_update.yaml` | 仓库名固定为“自动化测试专属仓库1/2”，失败重跑时可能重名 | 名称增加运行 ID/时间戳；创建后保存精确 ID；补充失败后的定向清理 | 不需要新增接口资料，除非当前仓库删除/清理规则有特殊业务限制 |
| 高 | 多个库存和收付款数据库断言 | 使用 `LIKE '洗面奶_%'`、`LIKE 'EX_MATERIAL_%'`、`LIKE 'EX_SK_%'`，可能命中历史数据 | 优先按本次提取的商品 ID、单据 ID 或完整名称/单号精确查询 | 表关系已由现有 SQL 证明时可直接修；关系不明确时需要提供表结构或已验证 SQL |
| 中 | `PurchaseScenario.yml`、`SalesScenario.yml` | 同一会话都使用 `洗面奶_${fixed_timestamp()}`，可能产生同名商品并干扰断言 | 分别使用采购和销售专用前缀，如 `AUTOTEST_PURCHASE_`、`AUTOTEST_SALES_` | 不需要人工资料 |
| 中 | `Exception/sales_exception.yml` | 部分异常用例只断言 `code != 200`，服务器异常、Token 失效也可能误通过 | 增加真实业务错误码、错误信息、状态不变和无脏数据断言 | 需要真实 ERP 对库存不足、重复单号、重复审核的实际响应样例或用户确认预期行为 |
| 中 | 重复审核场景 | 第二次审核主要验证库存未重复扣减，没有明确接口应成功幂等还是返回业务错误 | 根据真实系统行为补充响应断言，同时保留库存断言 | 需要用户提供实际响应或允许在测试环境执行后采集 |

#### 不需要修复的 YAML 内容

- `X-Access-Token: ${get_extract_data(token)}` 是运行时变量引用，没有提交真实 Token，可以保留。
- 扫描未发现 API Key、Webhook、固定 Authorization、邮箱、手机号、身份证、银行卡或 ERP 主机地址等其他敏感数据。
- 商品价格、库存数量、采购/销售单结构和现有接口路径来源于真实 ERP，不因“硬编码”三个字就一律删除；只对敏感、跨环境或可能误操作的数据进行配置化。

#### 本阶段修改顺序

1. 先移除登录账号密码硬编码，并同步修改 `apiutil.py`、`apiutil_business.py` 的重登凭据来源。
2. 修复商品和仓库 `rows[0]` 提取，确保更新和删除只作用于本次创建的数据。
3. 为固定业务 ID 建立配置和启动预检，保留当前真实值的可用性。
4. 将固定仓库名和业务数据名改成带运行 ID 的唯一名称，并完善定向清理。
5. 将宽泛 `LIKE` 数据库断言改成当前运行的精确 ID、名称或单号。
6. 区分采购和销售场景的商品数据前缀。
7. 根据真实 ERP 响应补强异常用例和重复审核断言。
8. 为 API、UI、性能数据使用不同前缀，如 `AUTO_API_`、`AUTO_UI_`、`AUTO_PERF_`；所有清理动作必须校验数据前缀、本次运行 ID 和创建后保存的精确业务 ID。个人云服务器实例当前不强制再拆分专用租户。

**本阶段需要人工提供或确认的资料：**

- 账号密码不应写入文档或仓库；用户只需在本地配置、环境变量或 CI Secrets 中设置真实值，并确认变量名。
- 如商品/仓库创建响应或列表过滤能力无法从现有代码和接口响应确认，需要提供对应抓包、接口文档或响应样例。
- 确认 `91/124/196/204/86/105` 当前分别对应哪个商品分类、仓库、供应商、客户和账户；当前值有效时无需重新造数据。
- 提供库存不足、重复单号和重复审核的实际响应，或者授权在测试环境执行这些用例后采集。
- 数据库精确断言无法从现有 SQL 推导时，提供相关表结构和字段关系。
- 当前闭环需要什么角色就提供什么账号；秋招版本可以先使用管理员完成主链路，多角色权限覆盖列为后期优化，README 中如实说明当前范围。

**资料不足时的边界：**可以完成凭据外置、唯一数据命名、固定 ID 配置化和高风险 `rows[0]` 代码结构调整；没有真实接口响应时，异常用例只能标记为“等待真实错误码/消息确认”，不能自行编造断言。

验收标准：YAML 中不存在真实账号密码；任何更新或删除用例只能操作本次创建的测试数据；环境 ID 有明确配置和预检；数据库断言不会被历史同前缀数据误命中；异常用例能够区分预期业务拒绝与系统异常。

**P1.5 跑通目标与阶段门禁：**

按从低风险到高风险的顺序执行登录/查询、单接口、业务场景、异常用例和完整回归：

```bash
python run.py api --suite single
python run.py api --suite business
python run.py api --suite negative
python run.py api --suite all
python run.py api --suite all
```

- 完整回归连续执行两次，用于验证数据唯一化、环境独立性、失败恢复和清理逻辑，而不是只追求第一次偶然通过。
- AI 检查所有失败、误命中风险、测试数据前缀、精确 ID、数据库断言和清理结果。
- 用户在 jshERP 页面或数据库中抽查核心单据、库存变化和残留数据，确认没有修改需要保护的业务数据。
- 允许记录不阻塞主链路的已知限制，但登录、采购/销售核心 API、数据安全或清理存在问题时必须继续修复。
- P1.5 未经用户与 AI 共同确认通过，不得进入 P2。此门禁通过后，接口自动化才算完成本轮独立改造和真实跑通。

### P2：完成 ERP Playwright 基础能力

1. 增加官方 `pytest-playwright` 依赖，停止使用本地插件副本。
2. 建立 `ui/pages/base_page.py` 和 ERP `login_page.py`。
3. 实现基于 `storage_state` 的登录复用和每用例独立 Context。
4. 统一截图、视频、Trace 输出及 Allure 附件。
5. 先完成 ERP 登录冒烟测试。
6. 优先替换完成闭环所需的登录、商品、采购和销售页面对象；仓库维护和更多 ERP 页面在核心闭环稳定后按需增加。
7. 结合当前部署版本的 jshERP Vue 路由、页面组件和接口调用辅助页面建模，但定位器优先使用角色、标签、文本和稳定属性，不直接依赖易变化的 CSS 层级；必要时可在自有部署的前端增加 `data-testid`。
8. 将 `storage_state` 存放在独立的 `.runtime/auth/`，与截图、Trace、视频和 Allure 报告彻底分离；该目录必须被 Git 忽略、CI 结束后删除且禁止作为 Artifact 上传。

#### 登录状态和调试产物安全规则

- `storage_state` 可能包含 Cookie、Token、LocalStorage 和租户会话，只能作为本次运行的临时凭据使用。
- `.runtime/auth/` 不进入 `reports/`、Allure 附件或 CI Artifact，不在日志中输出文件内容，并在会话/Workflow 结束时清理。
- 截图、视频和 Trace 上传前应避免展示密码输入、Token、Cookie、完整 Authorization Header 或不必要的个人信息。
- CI 和本地日志统一脱敏账号、密码、Token、Cookie 与数据库连接串；调试需要查看敏感值时只能在受控本地环境处理。

#### UI 用例获取与落地流程

UI 改造不能把旧项目中的非 ERP 页面对象简单改名，而应按以下流程逐条从云端 jshERP 获取真实用例：

```text
人工选择 jshERP 真实业务场景并在云端实际操作
    → 记录角色、前置条件、步骤、页面结果和业务预期
    → 人工提供截图/录屏/codegen/DOM，或在安全条件下允许 AI 辅助探索
    → AI 整理结构化 UI 用例并实现 Page Object、定位器和断言
    → 复用真实 API YAML 准备数据，通过 API/数据库补充结果校验
    → 在同一云端 jshERP 环境运行
    → 人工与 AI 共同核对结果，修正定位器、等待条件和业务断言
    → 稳定通过后纳入正式 UI 回归
```

人工主要负责提供真实业务事实和最终确认；AI 主要负责将事实工程化为可维护代码。双方职责如下：

| 参与方 | 主要职责 |
| --- | --- |
| 人工 | 选择真实业务场景；在云端 jshERP 实际操作；提供角色、前置数据、步骤和预期；确认哪些数据允许新增、修改和删除；验收最终结果 |
| AI | 分析页面信息和现有 API 用例；整理 UI 用例；设计 Page Object 和稳定定位器；实现数据准备、断言、清理、截图和 Trace；明确报告缺失资料 |
| 人工 + AI | 共同执行和调试真实页面用例，确认 UI 展示、接口状态和数据库结果一致，并决定是否纳入正式回归 |

建议每条 UI 用例先形成简洁记录，再实现代码：

```yaml
case_name: 采购入库审核
module: 采购管理
role: 管理员或采购员
preconditions: 商品、供应商、仓库已存在
steps:
  - 进入采购入库列表
  - 新建采购入库单
  - 填写商品、数量、仓库并保存
  - 审核单据
expected:
  - 页面提示审核成功
  - 单据状态变为已审核
  - 库存按采购数量增加
cleanup: 按本次运行ID清理测试单据和关联数据
```

验收标准：ERP UI 登录及采购、销售闭环涉及的关键页面可以在 Chromium headless 下稳定运行，失败时可获得截图和 Trace；不要求当前覆盖全部 ERP 菜单和浏览器。

**P2 跑通目标与阶段门禁：**

```bash
python run.py ui --suite smoke
python run.py ui --suite all
```

- UI 用例必须来自云端 jshERP 的真实页面，至少跑通登录以及采购、销售闭环所需关键页面。
- AI 检查 Page Object、定位器、等待、Context 隔离、截图和 Trace，分析不稳定失败。
- AI 检查 `.runtime/auth/` 没有进入 Git、Allure 或 CI Artifact；用户确认报告和 Trace 中没有暴露登录凭据。
- 用户确认自动化操作步骤、页面提示、单据状态和业务预期与人工操作一致。
- 核心 UI 用例至少连续执行两次，排除依赖历史状态或偶然等待成功的情况。
- P2 未经用户与 AI 共同确认通过，不得进入 P3。此门禁通过后，UI 自动化才算完成本轮独立改造和真实跑通。

**本阶段必须由人工提供或确认的 ERP 资料：**

- ERP UI 测试环境地址及是否允许自动化操作。
- 可用的测试账号、密码、验证码处理方式，以及管理员、采购员、销售员等角色权限。
- ERP 登录成功后的判断条件，例如目标 URL、页面标题或稳定可见元素。
- 商品、仓库、采购、销售页面的菜单路径、关键操作步骤和预期结果。
- 新页面用例的业务规则；如果已有人工测试用例、操作说明、截图或录屏，应一并提供。
- AI 无法直接访问 ERP 页面时，需要提供关键页面 HTML/DOM、Playwright codegen 结果、稳定属性或实际定位器信息。

现有非 ERP UI 项目可以提供框架写法，但不能提供 ERP 页面定位器和业务预期。没有来自云端 jshERP 的实际操作和页面资料时，AI 只能完成 Playwright 骨架、通用 fixture、报告和空的 Page Object 结构，不能凭空实现或宣称 ERP UI 用例有效。

### P3：打通 API、UI 和数据库协同

1. 将通用 ERP API Client 放到 `shared/api_client.py`。
2. UI 用例通过 API 快速准备商品、库存、采购单和销售单数据。
3. UI 执行业务操作后，通过 API 或数据库验证最终状态。
4. 测试结束通过 API 或数据库清理数据。
5. 使用统一的数据前缀和唯一单号，保证数据可识别、可清理。

推荐的端到端模式：

```text
API 准备测试数据
    → Playwright 执行 ERP 页面操作
    → API/数据库校验业务结果
    → API/数据库清理测试数据
```

验收标准：至少完成一条采购和一条销售的跨层端到端链路。

**P3 跑通目标与阶段门禁：**

- 采购闭环必须完成：API 准备数据 → UI 操作/审核 → API 查询 → 数据库验证库存或单据状态 → 清理。
- 销售闭环必须完成：API 准备商品和库存 → UI 操作/审核 → API 查询 → 数据库验证库存或单据状态 → 清理。
- AI 检查跨层数据传递、断言、报告和清理证据；用户确认页面结果、单据状态、库存变化符合真实 jshERP 业务。
- 两条闭环均应能够重复执行，不依赖人工修改中间状态。
- 任一闭环未跑通、业务结果未经用户确认或清理不安全时，不得进入 P4。

**本阶段可直接复用的现有资料：**

- 现有 YAML 中的商品创建、采购入库、销售出库、查询、审核、付款和收款接口，可优先作为 UI 测试的数据准备与结果校验能力。
- 已有数据库断言和清理 SQL 可作为跨层校验的起点。

**本阶段需要人工提供或确认的资料：**

- UI 操作与 API、数据库状态之间的对应关系，例如“页面审核成功”对应哪个接口、单据状态值和库存变化。
- 各业务链路真实前置条件：仓库、商品、库存、供应商、客户、账户和角色权限。
- 现有 YAML 未覆盖但 UI 场景需要的数据准备、查询或清理接口。
- 采购和销售端到端用例的预期结果，包括单据状态、库存变化、应收应付和收付款关系。
- 哪些数据允许自动删除、软删除或只能保留，避免清理真实基础数据。

**资料不足时的边界：**可以搭建 API Client、数据库 fixture 和跨层测试模板，但不能自行推断业务状态或删除规则；必须列出缺失的接口、数据、表关系或预期结果，等待人工补充后再完成真实闭环。

### P4：加入 Locust 性能测试

1. 新增 `locust` 依赖和 `performance/locustfile.py`。
2. 先实现只读接口：商品查询、库存查询、单据查询。
3. 再实现低比例写操作：采购入库、销售出库等业务链路。
4. 为当前选定场景准备够用的账号和业务数据池，并使用独立数据前缀；暂不建设通用大规模数据平台。
5. 增加阶梯加压、峰值和稳定性负载模型。
6. 通过宝塔监控、SSH 或受控脚本采集云服务器 CPU、内存；暂不要求搭建 Prometheus/Grafana。
7. 输出 HTML/CSV 报告及资源监控数据到 `reports/locust/`。
8. 性能测试只允许显式运行，CI 中采用手动触发或定时触发。

#### 每种性能场景的强制指标

商品查询、库存查询、采购业务、销售业务、阶梯加压、峰值和稳定性测试等每一种性能场景，都必须至少记录和分析以下指标：

| 指标 | 关注内容 | 统计要求 |
| --- | --- | --- |
| 并发用户数 | 当前场景同时在线或执行任务的虚拟用户数量 | 记录目标并发数、实际峰值并发数、用户生成速率和稳定运行时间 |
| 响应时间 | 请求或完整业务事务的处理耗时 | 至少记录平均响应时间、最小值、最大值和中位数 |
| P95/P99 | 95% 和 99% 请求能够完成的响应时间边界 | 必须分别记录 P95 与 P99，不允许只用平均响应时间判断性能 |
| RPS/TPS | 系统吞吐能力 | 查询类场景关注 RPS；采购、销售等完整业务链路同时关注请求 RPS 和成功事务 TPS |
| 错误率 | 超时、HTTP 错误、业务失败和数据异常占比 | 记录总体错误率，并按错误类型统计数量和比例 |
| CPU/内存 | 被测 ERP 服务和数据库的资源消耗 | 记录平均值、峰值、测试前基线和测试结束后的资源恢复情况 |

其中：

- **RPS** 表示每秒处理的 HTTP 请求数量。
- **TPS** 表示每秒成功完成的完整业务事务数量。例如一次“销售出库事务”可能包含登录、创建单据、查询和审核等多个请求，不能直接用单个接口 RPS 代替事务 TPS。
- **CPU/内存** 默认指被测 ERP 应用服务器和数据库服务器，不只是 Locust 压测机。必要时同时记录压测机资源，防止负载发生器先成为瓶颈。
- 秋招版本的 CPU/内存可以通过宝塔监控、SSH 或受控系统采集脚本获取，并与 Locust 测试时间段对齐；Prometheus、Grafana 和 Node Exporter 属于后期工程化增强。

每个性能场景执行前必须定义指标阈值，执行后给出“通过/失败”结论。场景报告建议使用以下表格：

| 场景 | 并发用户 | 平均响应时间 | P95 | P99 | RPS | TPS | 错误率 | CPU 峰值 | 内存峰值 | 结论 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 商品查询 | 待配置 | 待采集 | 待采集 | 待采集 | 待采集 | 不适用 | 待采集 | 待采集 | 待采集 | 待评估 |
| 采购业务 | 待配置 | 待采集 | 待采集 | 待采集 | 待采集 | 待采集 | 待采集 | 待采集 | 待采集 | 待评估 |
| 销售业务 | 待配置 | 待采集 | 待采集 | 待采集 | 待采集 | 待采集 | 待采集 | 待采集 | 待采集 | 待评估 |

不能在缺少业务容量目标的情况下预先写死统一数值。后续应根据 ERP 测试环境配置、生产基线和业务 SLA，在场景配置中明确各自阈值。例如查询场景和采购事务的响应时间、吞吐量要求通常不同。

验收标准：能够通过命令指定并发用户数、生成速率和运行时间；每一种性能场景都必须输出并发用户数、响应时间、P95、P99、RPS/TPS、错误率、CPU 和内存数据，并根据该场景预设阈值给出结论。

**P4 跑通目标与阶段门禁：**

先用单用户验证请求和业务逻辑，再执行获批的小并发和正式场景，禁止直接开始高并发：

```bash
python run.py performance --users 1 --spawn-rate 1 --run-time 1m
python run.py performance --users 10 --spawn-rate 2 --run-time 5m
```

- 每个实际纳入本轮的性能场景都必须输出并发用户、响应时间、P95/P99、RPS/TPS、错误率、CPU/内存和通过/失败结论。
- AI 检查 Locust 请求是否正确、业务失败是否计入错误、TPS 统计是否合理，以及报告和资源数据是否时间对齐。
- 用户确认压测授权、并发规模、服务器状态、业务数据影响和指标结论；测试后确认没有不可接受的脏数据或服务异常。
- 单用户调试未通过、指标采集不完整、错误率原因不明确或用户未批准测试结果时，不得进入 P5。

**本阶段可直接复用的现有资料：**

- 现有真实 YAML 接口可作为 Locust 场景选型和请求参数的重要来源。
- 商品、库存、单据查询适合作为第一批只读性能场景；采购和销售 YAML 可作为低比例业务事务场景参考。

**本阶段必须由人工提供或批准的资料：**

- 明确非生产的性能测试环境地址和压测授权；当前个人云端 jshERP 实例在没有重要业务数据且做好备份、限流和停止方案时可以使用，禁止对生产环境执行。
- 环境拓扑和容量信息，例如 ERP 应用节点、数据库节点、CPU 核数、内存和部署方式。
- 云服务器基本规格，包括 CPU 核数、内存、带宽，以及 jshERP 后端、MySQL、Redis 是否共享服务器；Java 堆参数无法获取时可作为补充信息，不阻塞首轮测试。
- CPU/内存的可行采集方式和访问权限，优先复用现有宝塔监控或受控脚本。
- 目标并发用户数、用户生成速率、持续时间和预期业务比例。
- 每个场景的响应时间、P95、P99、RPS/TPS、错误率、CPU 和内存阈值；没有正式 SLA 时，至少提供基线测试目标和可接受范围。
- 性能测试专用账号池、商品/库存数据池，以及允许执行的写接口和清理规则。
- 是否允许采购、销售、审核、付款、收款等有副作用的性能场景。

**资料不足时的边界：**可以完成 Locust 代码骨架、场景模板和离线语法检查，但不得实际发起压力测试，也不能给出容量结论。AI 必须明确提示需要压测授权、环境、数据池、监控权限和指标阈值。

### P5：统一运行、报告和 CI

1. `run.py` 支持 API、UI、回归和性能四类命令。
2. API 和 UI 的 Allure 原始结果分目录保存，最终合并生成统一 HTML 报告。
3. 性能报告独立保存，不强行转换成 Allure 用例。
4. CI 收敛为 `quality-gate.yml` 和 `performance-tests.yml` 两条 Workflow：日常功能质量检查集中展示，性能测试独立授权和触发。
5. 当前 CI 直接连接宝塔部署的云端 jshERP，不在秋招版本中自动构建或部署被测系统；Docker 临时环境列入后期优化。
6. 完善面向面试官的 README、环境配置模板和运行说明，展示真实业务闭环、报告样例、性能结果、当前范围及后期方向。

#### `quality-gate.yml`：PR 和功能回归质量门禁

建议 Job 关系如下：

```text
lint-and-collect
    ├── api-smoke
    └── ui-smoke
          ├── publish-report（始终执行）
          └── e2e-smoke（主分支或手动触发）
```

各 Job 的职责：

| Job | 主要任务 | 是否连接真实 jshERP |
| --- | --- | --- |
| `lint-and-collect` | Ruff、API/UI `collect-only`、导入与 fixture 检查 | 否 |
| `api-smoke` | `preflight`、登录/Token、只读查询及少量可安全清理的写接口 | 是 |
| `ui-smoke` | 安装 Chromium、登录、关键页面冒烟、截图和 Trace | 是 |
| `e2e-smoke` | API 造数、UI 操作、API/数据库校验和清理 | 是，仅主分支或手动 |
| `publish-report` | 下载 API/UI Artifact，合并 Allure Results 并上传统一 HTML | 否，使用 `if: always()` |

触发策略：

| 触发方式 | 默认执行范围 |
| --- | --- |
| Pull Request | Lint、用例收集、API/UI 安全冒烟 |
| Push 到 `main` | Lint、API/UI 冒烟，可增加采购/销售 E2E 冒烟 |
| `workflow_dispatch` | 通过参数选择 `smoke`、`api-full`、`ui-full` 或 `e2e` |
| 定时任务 | 秋招版本不强制；需要夜间回归时再增加 |

API 与 UI 冒烟在 `lint-and-collect` 通过后可以并行，不需要因为放在同一 Workflow 就让 UI 等待全部 API 回归。完整 API、UI 和 E2E 通过手动范围参数执行，避免每个 PR 都产生大量 ERP 数据。

#### Branch Protection 与 Required Checks

Workflow 显示失败并不自动等于禁止合并。P5 必须在 GitHub 主分支 Ruleset/Branch Protection 中将以下检查设为 Required：

```text
lint-and-collect
api-smoke
ui-smoke
```

验收时故意制造一个安全断言失败，确认 PR 无法合并；修复并重新执行后，只有 Required Checks 全部通过才允许合并。`e2e-smoke` 是否作为 Required Check 根据数据库访问和稳定性决定，秋招版本默认作为主分支或手动验收，不阻塞每个普通 PR。

#### 共享云环境的并发与中断清理

- API/UI 安全冒烟使用运行 ID 和唯一数据前缀后可以并行。
- 完整回归、E2E 和性能任务分别使用环境级 `concurrency`，同一云端环境同一时间只允许一个高副作用任务；使用 `cancel-in-progress: false`，避免强制取消后留下半完成单据。
- 测试数据清理和 Artifact 上传使用 `if: always()`；测试框架同时提供 `python run.py cleanup --run-id <RUN_ID>`，用于 Workflow 超时、Runner 崩溃或人工取消后的定向补偿清理。
- 清理命令必须校验环境、自动化数据前缀、运行 ID 和精确业务 ID，不允许模糊删除共享环境数据。

建议的并发组：

```text
jsh-erp-cloud-full-regression
jsh-erp-cloud-e2e
jsh-erp-performance
```

#### 当前 CI 的数据库访问默认方案

当前秋招版本采用以下默认边界：

1. GitHub 托管 Runner 的 PR 门禁只通过 HTTP 访问云端 jshERP，执行 API/UI 冒烟，不为数据库断言直接开放公网 MySQL。
2. API/UI/数据库完整闭环先在本地真实环境验收；如后续配置自托管 Runner，只允许主分支或经过 Environment 审批的手动任务使用。
3. 自托管 Runner 不执行不受信任 Fork PR 的代码，数据库和 SSH Secret 也不提供给此类任务。
4. 后期 Docker 环境完成后，CI 在临时容器内部网络访问 MySQL，替代公网数据库连接。

#### `performance-tests.yml`：独立性能测试流水线

性能流水线只允许 `workflow_dispatch` 手动触发，至少提供以下输入：

```text
environment
scenario
users
spawn_rate
run_time
```

执行流程：

```text
validate-input
    → preflight
    → 单用户请求验证
    → Locust 正式场景
    → CPU/内存采集
    → 阈值判断
    → 上传 HTML/CSV 和资源报告
```

必须限制最大并发、最大运行时间和 Workflow 超时；使用并发锁保证同一测试环境同一时间只运行一个性能任务；禁止默认指向生产环境。单用户预检失败时不得继续升压。

#### 测试失败、报告和 Secrets 规则

- 测试命令不得使用 `pytest ... || true` 隐藏失败；pytest 或性能阈值失败必须让对应 Job 和 Workflow 显示失败，从而具备真实质量门禁作用。
- 报告上传步骤使用 `if: always()`，保证成功和失败时都能获得 Allure、日志、截图、Trace、Locust HTML/CSV 和资源指标。
- `api-smoke` 与 `ui-smoke` 分别上传 `api-allure-results` 和 `ui-allure-results`；`publish-report` 下载两个 Artifact、合并 Allure Results、生成统一 HTML 并再次上传。性能报告保持独立，不伪装成功能用例。
- Artifact 建议保留 7～14 天，README 展示 Workflow 状态徽章、成功运行截图和报告样例。
- 云端地址、账号、密码、Token 和数据库凭据只能通过 GitHub Secrets/Environment 注入，不能写入 Workflow、YAML 或日志。
- `.runtime/auth/` 和任何 `storage_state` 文件禁止上传；报告、Trace、截图和日志在归档前必须完成敏感信息检查或脱敏。
- 不建议为了 GitHub 托管 Runner 的数据库断言直接把 MySQL 暴露到公网。PR 冒烟优先使用 HTTP API/UI；数据库闭环可先在本地或受保护的自托管 Runner 执行，后期由 Docker 内部网络解决。
- Fork PR 没有可信 Secrets 时只执行 Lint 和用例收集，不得把真实环境凭据提供给不受信任代码。

当前流水线模拟的实际工作流程：

```text
开发者提交代码
    → 创建 Pull Request
    → Lint + API/UI 用例收集
    → API/UI 快速冒烟
    → 失败则阻止合并并上传证据
    → 成功后评审并合并
    → 主分支或发布前手动执行完整回归/E2E
    → 需要性能验证时单独审批并触发 Locust
```

**本阶段需要人工提供或确认的资料：**

- GitHub Actions Runner 是否能访问云端 jshERP 的 API 和 UI；数据库、SSH 和监控能力是否只允许本地或自托管 Runner 访问。
- API/UI Secrets：地址、账号和必要配置；Secret 值不写入仓库或文档。
- `quality-gate` 的 PR、主分支和手动范围，以及是否把 `e2e-smoke` 设为主分支任务。
- 是否有权限为 `main` 配置 Ruleset/Branch Protection，并将 `lint-and-collect`、`api-smoke`、`ui-smoke` 设置为 Required Checks。
- 完整回归/E2E 是否只在本地执行，或后续提供受保护的自托管 Runner；未确认前默认不向 GitHub 托管 Runner 暴露 MySQL。
- 性能测试允许的场景、最大并发、最长时间、环境审批和监控权限。
- Artifact 保留时间、README 徽章和报告展示方式。

**资料不足时的边界：**可以生成 CI 工作流模板、配置项和 README 命令，但无法验证 Runner 网络连通性、Secret 正确性和真实流水线结果，必须将这些项目标记为“等待人工配置/验证”。

**P5 跑通目标与最终验收门禁：**

- 本地统一入口能够分别执行 API、UI、回归和性能测试，性能测试不会被普通回归误触发。
- 创建一次真实 PR，`lint-and-collect`、`api-smoke` 和 `ui-smoke` 按设计执行；如果 Runner 无法访问云端 jshERP，必须在 README 如实说明并保留本地/自托管 Runner 的真实验收证据。
- 故意制造一次安全的测试断言失败，确认 Workflow 显示红色、Required Check 阻止合并，同时 `publish-report` 和其他证据上传步骤仍然执行，证明流水线不是“永远绿色”的展示模板。
- 手动触发并验证至少一次完整 API/UI 或 E2E 回归，以及一次获批的小规模性能测试。
- API/UI 独立 Allure 结果和合并 HTML、Playwright 截图/Trace、Locust 报告和日志能够按约定位置生成或归档，且不包含 `storage_state` 或可用凭据。
- AI 检查命令、配置模板、CI、报告路径和 README 是否与实际实现一致，删除或修正未实现的能力描述。
- 用户按照 README 从配置到执行完成一次最终演练，并确认项目能够用于代码展示和面试讲解。
- P5 只有在用户与 AI 共同确认后才能标记整个秋招版本完成；未跑通的 CI、命令或报告不能用“后期优化”掩盖，必须明确修复或从当前能力中移除。

### P0～P5 人工资料与阶段门禁总览

| 阶段 | 默认可离线完成 | 进入真实 ERP 验收前需要人工提供或确认 | 进入下一阶段前必须通过 |
| --- | --- | --- | --- |
| P0 合并骨架 | 目录迁移、依赖合并、用例收集、基础环境配置和预检 | 云端 API/UI 地址、有效配置和测试账号；jshERP 已知版本写入 README 即可 | API/UI `collect-only` 均成功且互不触发；用户与 AI 确认骨架通过 |
| P1 API 核心 | 使用现有真实 YAML 完成 Runner 重构、2～3 个 Schema 示例和错误定位 | 仅对已变化或新增接口提供文档、抓包、有效业务 ID、表关系和清理规则 | 云端 jshERP 的 API 冒烟真实通过；用户与 AI 确认 Runner 可用 |
| P1.5 YAML 治理 | 凭据外置、唯一数据命名、固定 ID 配置化、精确查询和断言结构调整 | 当前闭环所需账号、商品/仓库接口响应、业务 ID 映射、异常实际响应和无法推导的数据库关系 | API 全量回归连续两次通过，数据安全清理完成；用户与 AI 验收后进入 P2 |
| P2 ERP UI | Playwright fixture、报告、UI 用例模板和 Page Object 骨架 | 从云端 jshERP 实际操作获得的角色账号、前置条件、操作路径、页面结果、业务预期，以及截图/录屏/codegen/DOM 或安全的页面访问条件；由人工和 AI 共同整理、运行和确认 | ERP UI 核心回归连续两次通过，截图/Trace 可用；用户与 AI 验收后进入 P3 |
| P3 跨层闭环 | API Client、数据库 fixture、场景模板 | API/UI/DB 映射、业务前置、状态变化、缺失接口和安全清理边界 | 采购、销售两条 API/UI/DB 闭环可重复通过并安全清理；用户与 AI 验收后进入 P4 |
| P4 性能测试 | Locust 场景、报告和基础资源采集代码 | 压测授权、云服务器规格、数据池、宝塔/脚本监控方式、并发模型和性能阈值 | 单用户、小并发和正式场景通过，强制指标齐全；用户与 AI 验收后进入 P5 |
| P5 CI/报告 | 两条 Workflow、报告和配置模板 | Runner 网络、Secrets、质量门禁/性能触发策略和报告保留规则 | 真实 PR 门禁、手动回归和小规模性能流水线均有执行证据；用户按 README 完成演练，AI 核对实现与文档，双方确认秋招版本完成 |

---

## 6. 合并后的最终目录

```text
ClmERP/
├── api/                              # API 自动化
│   ├── conftest.py                   # API 登录、Token、数据清理
│   ├── framework/
│   │   ├── runner.py                 # 单接口和业务场景统一执行器
│   │   ├── yaml_loader.py            # YAML 加载、变量保存
│   │   ├── template.py               # ${function()} 动态表达式
│   │   └── assertions.py             # 响应及数据库断言
│   ├── cases/
│   │   ├── goods/                    # 商品接口测试及 YAML
│   │   ├── warehouse/                # 仓库接口测试及 YAML
│   │   ├── purchase/                 # 采购接口测试及 YAML
│   │   ├── sales/                    # 销售接口测试及 YAML
│   │   ├── scenarios/                # 采购、销售完整接口链路
│   │   └── negative/                 # 异常与边界测试
│   ├── schemas/                       # 关键稳定接口的 JSON Schema
│   │   ├── auth/
│   │   ├── inventory/
│   │   └── documents/
│   └── login.yaml
│
├── ui/                               # Playwright UI 自动化
│   ├── conftest.py                   # Browser、Context、Page、登录状态管理
│   ├── pages/
│   │   ├── base_page.py
│   │   ├── login_page.py
│   │   ├── goods_page.py
│   │   ├── warehouse_page.py
│   │   ├── purchase_page.py
│   │   └── sales_page.py
│   ├── cases/
│   │   ├── test_login.py
│   │   ├── test_goods.py
│   │   ├── test_warehouse.py
│   │   ├── test_purchase.py
│   │   ├── test_sales.py
│   │   └── test_business_flows.py
│   ├── data/                         # UI 专用账号和数据
│   └── mocks.py                      # ERP UI 接口 Mock
│
├── performance/                      # Locust 性能测试
│   ├── locustfile.py                 # Locust 入口和用户模型
│   ├── scenarios.py                  # 商品、库存、采购、销售任务
│   ├── load_shapes.py                # 阶梯、峰值、稳定性模型
│   ├── monitoring.py                 # ERP/数据库 CPU、内存指标采集
│   └── data/                         # 性能账号和数据池
│
├── shared/                           # API/UI/性能共享能力
│   ├── api_client.py                 # ERP HTTP 客户端
│   ├── database.py                   # MySQL 连接
│   ├── test_data.py                  # 单号、时间戳、随机数据
│   ├── logger.py                     # 统一日志
│   └── notification.py               # 邮件、钉钉通知
│
├── config/
│   ├── settings.py                   # 统一配置读取
│   ├── environments.yaml.example     # cloud_test/local 环境和 jshERP 版本基线模板
│   ├── config.ini.example            # 本地配置模板
│   └── environment.xml               # Allure 环境信息
│
├── reports/                          # 所有运行产物，Git 忽略
│   ├── allure-results/
│   │   ├── api/
│   │   └── ui/
│   ├── allure-report/
│   ├── playwright/                   # 仅截图、视频和 Trace，不存登录状态
│   ├── locust/                       # Locust HTML/CSV、资源指标和场景结论
│   └── logs/
│
├── .runtime/                         # 运行期敏感临时文件，Git 忽略且不上传
│   └── auth/                         # Playwright storage_state，运行后删除
│
├── .github/workflows/
│   ├── quality-gate.yml              # Lint、API/UI 冒烟和按需 E2E
│   └── performance-tests.yml         # 仅手动触发的 Locust 性能测试
├── conftest.py                       # 全局报告、通知 Hook
├── run.py                            # 统一运行入口
├── pytest.ini                        # 公共规则和 marker
├── requirements.txt                  # 一份依赖清单
├── .gitignore
└── README.md
```

一级核心目录只有：

```text
api
ui
performance
shared
config
reports
```

既能一眼看到重点，又保留必要的职责边界。

---

## 7. 统一执行方式建议

根 `run.py` 建议支持以下命令：

```bash
# API 测试
python run.py api --suite smoke
python run.py api --suite single
python run.py api --suite business
python run.py api --suite negative
python run.py api --suite all

# UI 测试
python run.py ui --suite smoke
python run.py ui --suite all
python run.py ui --browser chromium --headed

# API + UI 功能回归，不包含性能测试
python run.py regression --suite smoke
python run.py regression --suite all

# Locust 必须显式执行
python run.py performance --users 50 --spawn-rate 5 --run-time 5m

# 流水线异常中断后的定向清理
python run.py cleanup --run-id <RUN_ID>
```

`regression` 不应包含 Locust。性能测试可能产生大量请求、业务数据和环境压力，必须单独授权和触发。

### Suite、目录与 pytest marker 映射

`run.py` 的参数必须有明确、稳定的选择范围，不能仅依赖文件名模糊匹配：

| 命令 | 选择范围 |
| --- | --- |
| `api --suite smoke` | 登录、Token、只读查询和少量可安全清理的写接口 |
| `api --suite single` | 商品、仓库、采购、销售等单接口增删改查 |
| `api --suite business` | 采购、销售 API 多步骤业务场景 |
| `api --suite negative` | 鉴权、库存不足、重复操作和超额收付款等异常场景 |
| `api --suite all` | 当前全部 API 用例，不包含 UI 和性能测试 |
| `ui --suite smoke` | 登录、导航和采购/销售闭环所需关键页面 |
| `ui --suite all` | 当前全部真实 jshERP UI 用例 |
| `regression --suite smoke` | API/UI 安全冒烟，不包含性能测试和高副作用场景 |
| `regression --suite all` | API/UI 功能回归和已纳入的 E2E，不包含 Locust |
| `cleanup --run-id` | 只清理指定运行 ID 且符合自动化前缀的数据 |

`pytest.ini` 至少登记：

```ini
markers =
    smoke: 安全且快速的冒烟用例
    business: ERP 多步骤业务场景
    negative: 异常和边界场景
    e2e: API、UI、数据库跨层闭环
    destructive: 会新增、修改、审核或删除业务数据
```

Locust 继续使用独立入口，不强行包装成 pytest marker。`destructive` 用例在 PR 中默认排除，只允许主分支或手动审批流程执行。

---

## 8. 合并后完成的主要改进

### 8.1 从两个独立项目变成一个统一测试框架

合并前 API 和 UI 分别维护依赖、配置、执行入口和报告。合并后统一：

- 一个代码仓库。
- 一份环境配置。
- 一份依赖清单。
- 一个执行入口。
- 一套 pytest marker。
- 一套 Allure 报告体系。
- 一套 CI/CD 入口。

### 8.2 API 执行器消除重复

单接口和业务场景使用同一个 Runner，Token 重登、参数替换、提取、断言和报告逻辑只维护一份。

### 8.3 UI 测试从共享状态改为隔离状态

通过登录状态复用和每用例独立 Context，降低 UI 用例互相污染，提高失败重跑和并行执行能力。

### 8.4 API、UI、数据库形成闭环

API 不再只是单独验证接口，UI 也不再依靠缓慢、脆弱的页面操作准备所有数据。三者协作实现：

- API 快速创建前置数据。
- UI 验证真实用户操作。
- 数据库验证最终业务状态。
- API/数据库完成测试数据清理。

### 8.5 测试产物统一管理

历史项目存在 `report`、`reports`、`allure_report`、`test-results`、`logs` 多套目录。合并后全部归档到 `reports/`，源码目录保持干净。

### 8.6 使用官方 Playwright 插件

停止维护本地插件副本，降低 pytest 和 Playwright 升级成本，同时保留项目真正需要的截图、视频、Trace 和 Allure 集成。

### 8.7 性能测试与功能测试隔离

Locust 共享配置和测试数据规范，但拥有独立的用户模型、负载模型、报告和 CI 触发方式，避免误把压力流量带入普通回归。

每个性能场景统一关注并发用户数、响应时间、P95/P99、RPS/TPS、错误率以及 ERP/数据库 CPU 和内存，避免只展示 Locust 请求数量而无法判断系统是否满足容量目标。

---

## 9. 项目最终亮点评价

完成上述改造后，这个项目的亮点不只是“同时用了 requests、Playwright 和 Locust”，而是三种测试能力围绕同一个 ERP 业务体系形成了完整闭环。

### 核心亮点

1. **API + UI + 性能一体化**
   一个仓库覆盖接口正确性、真实页面交互和系统承载能力。

2. **ERP 真实业务链路覆盖**
   围绕商品、库存、采购和销售等真实 jshERP 业务展开，并重点跑通采购、销售闭环，而不是只有简单登录和查询示例。

3. **YAML 数据驱动与场景编排**
   请求数据、变量提取和断言独立维护，支持多接口上下游参数传递。

4. **API、UI、数据库三层校验**
   页面显示正确不代表数据正确；框架可进一步验证库存、单据状态和收付款数据是否真实落库。

5. **Playwright 调试能力完整**
   失败时提供截图、视频和 Trace，能够还原浏览器操作、网络请求和页面状态。

6. **稳定的测试数据治理**
   使用唯一前缀和数据工厂生成数据，并在会话结束后定向清理，降低测试环境污染。

7. **可扩展的浏览器上下文设计**
   当前主链路使用必要账号完成，Context 隔离为后续采购员、销售员等多角色权限测试保留扩展能力，但不把完整权限矩阵作为本轮交付要求。

8. **可控的性能测试体系**
   支持不同用户模型、任务权重、阶梯加压、峰值测试和长时间稳定性测试，并使用并发用户数、响应时间、P95/P99、RPS/TPS、错误率、CPU 和内存对每个场景进行量化验收。

9. **统一报告与持续集成**
   API/UI 使用统一 Allure 报告，性能测试输出专用报告，CI 分类型执行和归档。

### 综合评价

如果上述秋招核心能力落地，该项目将从“两个自动化脚本集合”升级为一个有明确业务对象、测试分层、数据闭环、调试能力和基础持续集成的 ERP 自动化测试框架。它不追求模拟大型公司的完整测试平台，而是重点证明应届测开候选人具备接口自动化、UI 自动化、性能测试、数据库校验、测试数据治理和工程化落地能力。

需要注意的是，真正的亮点应以稳定可运行的业务链路为基础。目录完整、工具数量多本身不是亮点；可重复执行、失败可定位、数据可清理、结果可信才是框架价值。

---

## 10. README 编写建议

README 应面向第一次看到项目的人回答以下问题：

1. 这是什么项目？
2. 能测试什么？
3. 为什么这样设计？
4. 如何安装和配置？
5. 如何分别运行 API、UI 和性能测试？
6. 报告在哪里？
7. CI 如何触发？
8. 执行测试会不会产生业务数据？
9. 哪些用例使用现有真实 ERP 数据，新增模块需要人工提供哪些资料？

### 推荐 README 目录

```markdown
# ERP 全方面自动化测试框架

## 项目简介
## 核心能力
## 技术栈
## 架构设计
## 项目目录
## 测试范围
### API 自动化
### Playwright UI 自动化
### Locust 性能测试
## 性能指标与 SLA
## 环境准备
## 配置说明
## 快速开始
## 执行测试
## 测试报告
## 真实数据来源与人工依赖
## 测试数据与环境安全
## CI/CD
## 常见问题
## 后续规划
```

### README 开头示例

```markdown
# ERP 全方面自动化测试框架

基于 pytest、requests、Playwright、Locust、MySQL 和 Allure 构建的 ERP
综合自动化测试框架，覆盖接口功能测试、Web UI 自动化、端到端业务链路、
数据库一致性校验以及负载与压力测试。

框架围绕商品、仓库、采购、销售和收付款等 ERP 核心业务展开，支持 API
准备数据、UI 执行业务操作、数据库验证结果、测试结束自动清理的完整测试闭环。
```

### README 核心能力建议写法

```markdown
## 核心能力

- YAML 数据驱动的 API 自动化及多步骤业务场景编排
- Token 自动管理、动态参数替换和 JSONPath 数据提取
- Playwright Page Object、登录状态复用和独立 BrowserContext，并为后续多角色权限测试保留扩展能力
- UI 失败截图、视频和 Trace 自动留存
- MySQL 数据库断言和测试数据自动清理
- Locust 用户模型、任务权重及多种负载曲线
- 每个性能场景统计并发用户数、响应时间、P95/P99、RPS/TPS、错误率、CPU 和内存
- API 与 UI 统一 Allure 报告，Locust 独立性能报告
- GitHub Actions 分类执行和测试产物归档
```

### README 中必须明确的安全提示

```markdown
> 本项目包含新增商品、采购入库、销售出库、审核、付款、收款和性能压测等
> 有副作用的测试。禁止直接对生产环境执行。Locust 性能测试必须使用独立测试
> 环境并显式触发。
```

README 不应堆积大量源码实现细节。核心执行流程、目录、命令和安全约束写在 README；具体迁移和架构决策保留在本文档中。

README 的“真实数据来源与人工依赖”应明确说明：现有 API YAML 来源于真实接口文档、抓包和系统操作并可继续使用；正式 UI 用例来自用户部署在云服务器上的 jshERP 真实页面，由人工实际操作并确认业务预期，AI 辅助整理用例、Page Object、定位器、断言和清理逻辑；新增 API、跨层业务规则和性能 SLA 仍需要由项目维护者提供或确认。这样后续使用 AI 扩展项目时，可以清楚地区分离线代码生成与真实环境验收。

---

## 11. 后期改进优化方向

以下事项具有长期价值，但不会阻塞当前 API、Playwright UI、数据库闭环和 Locust 性能测试的合并主线。当前阶段只保留扩展边界，不提前增加大量目录或基础设施；应在 P0～P5 主线稳定后，根据实际使用频率、团队规模和维护精力逐项实施。

| 后期方向 | 当前暂不立即实施的原因 | 建议启动条件 |
| --- | --- | --- |
| jshERP 版本自动识别、Commit 同步和兼容矩阵 | 当前在 README 记录已知部署版本即可，自动同步对秋招演示收益有限 | 频繁升级或同时维护多个 jshERP 版本时 |
| 自动化专用租户和完整多角色权限矩阵 | 当前是个人云服务器测试实例，先通过数据前缀和精确 ID 保证安全；主链路可先使用必要账号 | 环境开始多人共用，或准备重点展示租户隔离和权限测试时 |
| 全接口 JSON Schema 覆盖 | 当前用 2～3 个代表性接口证明契约校验能力即可 | 接口稳定且需要持续发现大范围契约变化时 |
| jshERP 一键部署或 Docker Compose 测试环境 | 已有宝塔部署的云端 jshERP 可用于真实验证，现在重做部署链路会扩大范围 | 需要在新机器快速复现、CI 隔离运行或频繁切换 jshERP 版本时 |
| CI 自动构建并销毁完整 jshERP 环境 | 前后端、MySQL、Redis、Nginx 和基础数据初始化成本较高，当前可直接连接专用云端测试环境 | 云端共享环境开始影响并行稳定性，或要求每次流水线使用全新环境时 |
| 数据库快照、全量恢复和完整基础数据种子 | 当前优先通过 API 创建本轮数据并定向清理，完整恢复不应阻塞核心链路 | 用例规模扩大、历史脏数据频繁导致失败，或需要灾难恢复演练时 |
| Prometheus、Grafana、Node Exporter 完整监控平台 | P4 可以先通过宝塔、SSH 或受控脚本采集 CPU/内存，不必为首轮压测先搭建平台 | 需要长期趋势、跨版本性能对比、告警或多节点监控时 |
| 分布式 Locust 和大规模容量测试 | 第一阶段先验证场景、数据池、阈值和单机压测安全性 | 单台压测机成为瓶颈或目标并发超过其负载能力时 |
| 手工测试用例库和缺陷模板 | 属于测试管理资产，不影响框架执行 | 自动化范围稳定、开始多人协作或需要正式测试交付时 |
| 需求—模块—接口—用例覆盖矩阵 | 早期接口和 UI 场景仍在调整，过早维护容易增加重复工作 | 需要统计覆盖率、发布准入或对外展示质量范围时 |
| YAML 可视化编辑、自动补全和高级调试器 | P1 先通过 Schema、职责边界和精确错误信息解决主要维护问题 | YAML 用例数量明显增长，人工编写和排错成本成为主要瓶颈时 |
| 完整安全自动化模块 | 当前优先完成凭据外置、日志脱敏和环境隔离，安全专项会显著扩大项目范围 | API/UI/性能主线稳定，并有明确安全测试范围和授权时 |
| 完整的新成员开发指南和贡献规范 | P5 先提供安装、配置、运行、报告和安全说明即可 | 项目进入多人维护、开源展示或需要标准化代码评审时 |
| 更广泛的浏览器、移动端和兼容性矩阵 | 首阶段以 Chromium 跑通 jshERP 核心流程更重要 | 核心 UI 用例稳定，并出现明确的浏览器兼容需求时 |

### 11.1 后期 Docker 被测环境改造目标

后期引入 Docker 的主要目的不是单纯把 pytest、Playwright 或 Locust 放进容器，而是自动启动一套版本固定、数据干净、可以销毁的 jshERP 被测环境，为 CI 提供可复现的 API/UI/E2E 测试基础。

当前与后期的环境模式：

```text
当前秋招版本：
GitHub Actions / 本地测试框架
    → 连接宝塔部署的云端 jshERP

后期 Docker 版本：
CI 获取指定版本 jshERP
    → Docker Compose 启动完整被测环境
    → 初始化数据库和基础资料
    → 执行 API/UI/E2E
    → 上传报告和容器日志
    → 销毁容器与测试数据
```

Docker Compose 建议包含：

```text
docker/
├── compose.yml
├── backend.Dockerfile               # Maven 构建并运行 jshERP 后端
├── frontend.Dockerfile              # 构建 Vue，使用 Nginx 提供页面
├── nginx.conf                       # 前端静态资源和 API 代理
└── initdb/                          # jshERP 初始化 SQL 与最小测试基础数据

services:
├── jsh-erp-backend
├── jsh-erp-frontend
├── mysql
├── redis
└── nginx（如果不合并在前端镜像中）
```

jshERP 源码仍与自动化框架保持独立：本地或 CI 明确获取指定 Tag/Commit 作为构建上下文，不把完整 jshERP 源码长期复制到测试仓库，也不默认拉取随时变化的最新 `master`。

#### Docker 第一版必须实现的能力

1. 固定 jshERP Tag 或 Commit，并将版本写入镜像标签和测试报告。
2. 后端完成 Maven 构建、JAR 运行、MySQL/Redis 配置和健康检查。
3. 前端完成 Vue 构建、Nginx 静态托管和后端 API 代理。
4. MySQL 自动创建数据库、导入 jshERP 初始化 SQL，并准备测试登录账号、角色、商品分类、仓库、供应商、客户和结算账户等最小基础数据。
5. Redis 仅在内部网络提供服务，具备健康检查，不暴露不必要端口。
6. 环境启动后依次检查 MySQL、Redis、后端、前端和登录接口，全部就绪后才执行测试。
7. 业务单据继续由自动化运行时动态创建，使用运行 ID 定向清理；初始化脚本只维护稳定基础资料。
8. Secrets 通过 `.env` 模板、CI Secret 或运行时变量注入，不能写入 Dockerfile、Compose、镜像层或仓库。
9. 测试成功和失败时都收集容器日志；CI 最终使用 `docker compose down -v` 销毁容器和测试数据卷。
10. 自动化测试框架第一版仍可运行在宿主机或 CI Runner，只需访问 Docker 网络暴露的 jshERP 地址；不强制同时容器化 pytest、Playwright 和 Locust。

#### Docker 接入 CI 后的流程

```text
lint-and-collect
    → 获取指定版本 jshERP
    → docker-build
    → docker-up
    → health-check / preflight
    → API/UI 冒烟
    → 采购/销售 E2E
    → 上传测试报告和容器日志
    → docker-down -v（始终执行）
```

不要求每个普通 PR 都重新构建完整 jshERP。建议按成本分层：

| 触发方式 | Docker 策略 |
| --- | --- |
| 自动化仓库普通 PR | Lint、用例收集和现有云端环境的安全冒烟 |
| jshERP 版本升级验证 | 构建指定版本 Docker 环境并执行完整回归 |
| 主分支手动触发 | 在临时 Docker 环境执行 API/UI/E2E |
| 性能测试 | 使用资源规格固定且明确授权的独立环境，不默认用普通临时 CI 容器得出容量结论 |

#### Docker 后期验收标准

Docker 改进只有满足以下条件才算完成：

1. 在一台仅具备 Git、Docker 和 Docker Compose 的干净机器上可以按文档启动环境。
2. `docker compose up -d --build` 后 MySQL、Redis、前端和后端健康检查全部通过。
3. 可以使用初始化账号登录 jshERP，API/UI 冒烟以及采购、销售闭环能够运行。
4. 环境可以销毁后重新创建，第二次运行不依赖第一次遗留的数据和容器状态。
5. 测试失败时仍能获得容器日志、Allure、截图和 Trace，并且清理步骤始终执行。
6. 仓库、Workflow、镜像历史和日志中不存在真实密码、Token 或生产配置。
7. 测试报告可以明确对应 jshERP 版本、镜像版本和本次 CI Run。
8. 用户与 AI 在干净环境共同完成一次“启动—测试—报告—销毁—重建”验收后，才能把 Docker 环境写入 README 当前能力。

#### Docker 第一版明确不做的内容

- Kubernetes、Docker Swarm 和多节点部署。
- 自动扩缩容、蓝绿发布、灰度发布和生产部署。
- 完整镜像治理、制品审批和漏洞管理平台。
- 强制把所有自动化测试工具容器化。
- 使用资源不固定的临时 CI 容器给出正式生产容量结论。

后期优化应遵循以下原则：

1. 不为了“看起来完整”提前建设暂时无人使用的平台。
2. 优先解决已经通过运行数据证明存在的问题，例如环境污染、压测机瓶颈或多人协作冲突。
3. jshERP 源码与自动化框架保持独立仓库，通过版本/Commit 配置建立关联，不把完整被测系统源码复制进测试仓库。
4. 后期新增能力优先放进现有 `api/`、`ui/`、`performance/`、`shared/`、`config/` 和 `docs/`，确有独立职责时才增加新的一级目录。

README 中应设置“后期优化方向”章节，但必须明确这些内容尚未实现，不能写入“当前核心能力”。建议只展示最有代表性的方向：

```markdown
## 后期优化方向

- 增加 jshERP Docker Compose 一键测试环境和 CI 环境自动初始化
- 扩展专用租户、多角色权限和浏览器兼容性覆盖
- 将 JSON Schema 契约校验逐步扩展到更多稳定接口
- 接入 Prometheus/Grafana，形成跨版本性能趋势和告警
- 增加安全专项、覆盖矩阵和更完整的测试管理文档
```

面试时应把后期方向作为技术取舍来解释：当前优先完成真实闭环和稳定运行，后续再根据团队规模、环境数量和测试需求增加工业化能力。

---

## 12. 最终实施结论

本次合并不采用“把两个项目原封不动放进两个子目录”的方式，而是：

1. 以现有 ERP 接口项目作为主仓库和业务基础。
2. 迁移 Playwright 项目的浏览器管理、Page Object、Mock 和调试能力。
3. 根据 ERP 页面逐步替换非 ERP 页面对象和测试用例。
4. 合并重复的执行入口、配置、fixture、依赖和报告目录。
5. 新建独立但不分散的 Locust 性能测试模块。
6. 通过 `shared/` 共享 API Client、数据库、数据生成、日志和通知。
7. 最终形成 `api / ui / performance / shared / config / reports` 六个清晰的一级模块。

当前秋招版本只把凭据外置、基础多环境配置、基础预检、测试数据唯一化与安全清理、统一 Runner 与清晰错误定位、2～3 个关键接口 Schema、采购/销售真实闭环、Playwright 调试产物、完整性能指标、两条真实可执行的 CI Workflow 和 README 作为交付门槛。其中 `quality-gate.yml` 集中展示 Lint、API/UI 冒烟和按需 E2E，`performance-tests.yml` 负责独立授权的 Locust 性能测试。

jshERP 版本自动管理、专用租户、完整多角色权限矩阵、全接口 Schema、Docker Compose 自动部署被测环境、完整监控平台、测试管理资产、安全专项和高级工程体验统一列入“后期改进优化方向”，不阻塞秋招版本交付。后期 Docker 的验收重点是能够在干净机器完成“启动 jshERP—初始化数据—执行 API/UI/E2E—上传报告—销毁并重建”，而不是单纯增加 Dockerfile。

该方案在保证职责合理的前提下控制了目录数量，适合当前项目规模，也为后续扩展更多 ERP 模块、多角色权限测试、并行执行和持续集成保留了空间。
