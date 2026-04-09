# 🏛️ Cyber-Ideal-State - 赛博理想国

**基于 OpenClaw 的多数字生命（AI Agents）智能协作框架**

> "在虚拟世界里创造你的理想国，哲学也不会是尽头"

---

## ✨ 项目愿景

打造一个**赛博理想国**，让你的人际关系、职场记忆、情感纽带在 AI 时代得到永生，并通过柏拉图《理想国》的三等级协作模式实现智能化的多 Agent 对话与决策。

**核心理念：**
- 🤖 **数字生命蒸馏** - 从聊天记录、文档、照片中提取人格和能力，生成独立的数字 Agent
- 👑 **三等级会话制** - 借鉴柏拉图《理想国》，实现"统治者-护卫者-劳动者"的智能协作
- 🔗 **自由组合会话** - 像群聊一样，自由选择任何角色组合进行对话
- 🎨 **全功能 Web UI** - 所有操作都在浏览器中完成，无需命令行

---

## 🎯 核心功能

### 1. 数字生命生成

支持从多种数据源生成独立的数字生命（AI Agent）。本项目**不提供聊天记录导出工具**，你需要先通过其他开源工具导出聊天记录，再导入到本项目。

| 数据源 | 推荐导出工具 | 支持格式 | 提取内容 | 完成度 |
|--------|--------------|----------|----------|--------|
| 微信聊天记录 | [WeChatMsg](https://github.com/LC044/WeChatMsg) / [PyWxDump](https://github.com/xaoyaoo/PyWxDump) / [留痕](https://github.com/ljc001100/liuhhen) | SQLite | 关系记忆、说话风格、情感模式、共同经历 | ✅ 可用 |
| QQ 聊天记录 | [qq-export](https://github.com/duanls/qq-export) / 手动导出 | TXT | 学生时代记忆、性格特征、聊天历史 | ✅ TXT 可用，MHT 规划中 |
| 飞书文档/聊天 | 飞书官方 API | JSON | 工作能力、技术规范、协作风格 | 🔄 认证可用，消息采集规划中 |
| 邮件 | 任何邮箱客户端 | .eml/.mbox | 正式沟通风格、决策历史 | ✅ 可用 |
| 照片 | 直接导入 | JPEG/PNG（保留 EXIF） | 时间线、地点信息、共同经历记忆 | ✅ 可用 |
| 手动描述 | 直接在 UI 填写 | 纯文本 | 主观标签、性格描述、补充记忆 | ✅ 可用 |

**数据源说明：**
- **本项目只处理你导出后的文件/数据**

**生成产物：**
```
每个数字 Agent 包含：
├─ Persona（人格）
│  ├─ Hard Rules（硬规则）
│  ├─ Identity（身份认同）
│  ├─ Speaking Style（说话风格）
│  ├─ Emotional Pattern（情感模式）
│  └─ Relationship Behavior（关系行为）
└─ Memory（记忆）
   ├─ Shared Experiences（共同经历）
   ├─ Decision History（决策历史）
   ├─ Inside Jokes（内部梗）
   └─ Timeline（时间线）
```

### 2. 三等级会话制（理想国哲学）

**柏拉图式的协作架构：**

```
┌─────────────────────────────────────────┐
│  统治者（Philosopher King）               │
│  定位：战略决策者                          │
│  职责：最终拍板、价值判断、终极决策           │
│  代表：导师、智者、长期顾问、你自己           │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  护卫者（Guardian）                       │
│  定位：执行监督者                          │
│  职责：风险评估、辩论讨论、落地执行协调        │
│  代表：可靠同事、执行力强的朋友、家人守护者    │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  劳动者（Worker）                         │
│  定位：方案提供者                          │
│  职责：产出思路、生成方案、具体执行           │
│  代表：创作型同事、技术工人、活力同学         │
└─────────────────────────────────────────┘
```

**使用场景（单等级会话）：**
- 🏛️ **统治者** - 人生重大决策（职业选择、投资策略、情感困扰）
- 🛡️ **护卫者** - 执行具体任务（技术方案、项目管理、问题解决）
- 🔧 **劳动者** - 创意生成（头脑风暴、内容创作、艺术表达）

### 3. 自由组合会话

**像群聊一样的灵活会话机制：**

- 📝 **创建会话** - 选择任意角色组合（1个或多个）
- 🔗 **角色权限体系** - 基于等级的投票权重和互动权限（`permissions.yaml`）
- 💬 **多角色对话** - 多个 Agent 同时参与对话
- 🎯 **自定义决策模式** - 投票、辩论、共识或自由讨论

**示例场景：**

```
场景 1：个人对话
┌─────────────────────────────┐
│ 用户: 我应该转行做 AI 吗？   │
│ 初恋A: 根据你的性格...      │
└─────────────────────────────┘

场景 2：小组讨论
┌─────────────────────────────┐
│ 用户: 这个技术方案怎么样？   │
│ 技术导师: 从架构角度看...   │
│ 同事B: 实际上我们试过...    │
│ 朋友C: 听起来很有意思...    │
└─────────────────────────────┘

场景 3：三等级协作
┌─────────────────────────────┐
│ 用户: 如何平衡工作和生活？ │
│ [统治者] 导师A: 长远考虑... │
│ [护卫者] 导师B: 具体建议... │
│ [劳动者] 朋友C: 生活小技巧...│
└─────────────────────────────┘
```

### 4. 多种发言模式

**支持 5 种会话模式：**

| 模式 | 描述 | 适用场景 |
|------|------|----------|
| 🗣️ 自由讨论 | 所有角色自由发言 | 需要多方意见，无严格顺序 |
| 🔄 轮流发言 | 按顺序轮流回应 | 需要有序讨论，避免混乱 |
| 🎭 辩论 | 多轮辩论，总结观点 | 复杂问题需要深入讨论 |
| 🗳️ 投票 | 对问题投票决定 | 需要明确的决策 |
| 🤝 共识 | 多轮协商达成一致 | 希望达成一致意见 |

### 5. 理想国三等级协作

**当会话同时包含统治者、护卫者、劳动者时：**

- ✅ 系统自动识别为理想国模式
- ✅ 显示"理想国三等级协作模式"标记
- ✅ 基于等级的差异化投票权重自动生效
- 🔄 协作规则增强（规划中）

---

## 🚀 快速开始

### 环境要求

- **OpenClaw** 已安装并配置
- **Python** 3.9+
- **Node.js** 18+（用于前端 UI）

### 一键安装

```bash
# 克隆仓库
git clone https://github.com/KKKenChow/Cyber-Ideal-State.git
cd Cyber-Ideal-State

# 运行安装脚本
chmod +x install.sh && ./install.sh
```

安装脚本自动完成：
- ✅ 创建多 Agent Workspace
- ✅ 初始化数据目录结构
- ✅ 生成默认配置文件（从 `config/config.yaml.example` 复制）
- ✅ 构建前端 UI（如果 Node.js 可用）
- ✅ 尝试同步 Agent 配置到 OpenClaw（如果 openclaw Python API 可用）

> **注意**: 需要先安装好 OpenClaw，安装脚本会自动尝试同步配置。如果你遇到 Python 依赖问题，可以手动运行 scripts/sync_openclaw.py 完成同步。

### 启动系统

```bash
# 一键启动
chmod +x start.sh && ./start.sh
```

### 访问管理界面

打开浏览器访问：http://127.0.0.1:8080/ui

> **注意**: 前端已经预构建好了，不需要你再执行 npm install 和 npm run build，开箱即用！

---

## 📖 使用指南

### 第一步：创建你的第一个数字角色

1. **打开浏览器** 访问 http://localhost:8080
2. **点击左侧菜单** 的"角色管理"
3. **点击右上角** "创建角色"按钮
4. **填写角色信息**：
   - **角色名称**：例如"技术导师"、"初恋"、"妈妈"
   - **角色类型**：初恋、同事、家人、朋友
   - **等级**：统治者、护卫者、劳动者
   - **描述**：简要描述这个角色
5. **选择数据来源**：
   - 从下拉菜单选择数据源类型（微信、QQ、飞书、邮件、照片、手动描述等）
   - 输入文件路径或 API 凭证
   - 点击"添加"按钮
   - 可以添加多个数据源
6. **填写手动描述**（可选）：
   - 用你自己的话描述这个人的性格、习惯、你们的关系
7. **点击"创建角色"** 按钮

**系统会自动：**
- 📥 从指定数据源采集数据
- 🔍 分析并提取人格特征和记忆
- 🤖 生成独立的 OpenClaw Agent
- 🔗 注册到 OpenClaw 系统
- ✅ 在角色列表中显示

### 第二步：创建会话并开始对话

#### 创建单角色会话（个人对话）

1. **点击左侧菜单** 的"会话管理"
2. **点击"创建会话"** 按钮
3. **配置会话**：
   - **会话名称**：例如"与导师的对话"
   - **选择角色**：从列表中选择一个角色
   - **会话模式**：选择该角色的等级（自动匹配）
   - **决策模式**：选择对话方式（自由讨论/投票/辩论等）
4. **点击"创建会话"**
5. **在会话面板中输入消息** 开始对话

#### 创建多角色会话（群聊模式）

1. **点击"创建会话"** 按钮
2. **选择多个角色**：按住 Ctrl/Cmd 点击多个角色
3. **配置会话**：
   - **会话名称**：例如"技术讨论小组"
   - **决策模式**：
     - `自由讨论` - 所有角色自由发言
     - `轮流发言` - 按顺序轮流发言
     - `投票决定` - 对每个问题投票
     - `辩论` - 让角色互相辩论
4. **点击"创建会话"**
5. **在会话面板中输入消息**，多个角色会同时参与

#### 创建三等级协作会话

1. **创建三个不同等级的角色**：
   - 统治者：导师、智者
   - 护卫者：可靠同事、执行力强的朋友
   - 劳动者：创作型同事、活力同学
2. **创建会话** 时选择这三个角色
3. **系统会自动**：
   - 识别为理想国模式
   - 显示"理想国三等级协作模式"标记
   - 自动配置协作规则

---

## 🏗️ 项目架构

```
Cyber-Ideal-State/
├── README.md                        # 项目文档
├── LICENSE                          # MIT License
├── requirements.txt                 # Python 依赖
├── package.json                     # 前端依赖元数据
├── install.sh                       # 一键安装脚本
├── start.sh                         # 一键启动脚本
├── uninstall.sh                     # 卸载清理脚本
│
├── core/                            # 🧠 核心引擎层
│   ├── models.py                    # 数据模型（Role/Session/Decision/Persona/Memory）
│   ├── agent_generator.py           # Agent 生成引擎（采集→分析→生成→注册）
│   ├── role_manager.py              # 角色管理器（CRUD、筛选、导入导出）
│   ├── session_manager.py           # 会话管理器（CRUD、消息管理）
│   ├── session_engine.py            # 会话引擎（5种发言模式驱动）
│   └── decision_engine.py           # 决策引擎（投票/辩论/共识）
│
├── collectors/                      # 📥 数据采集器层
│   ├── base.py                      # 采集器基类 + 工具函数
│   ├── wechat_collector.py          # 微信采集（SQLite，兼容 WeChatMsg/PyWxDump/留痕）
│   ├── qq_collector.py              # QQ 采集（TXT/MHT）
│   ├── feishu_collector.py          # 飞书采集（API）
│   ├── email_collector.py           # 邮件采集（EML/MBOX）
│   └── photo_collector.py           # 照片采集（EXIF 元信息）
│
├── analyzers/                       # 🔍 数据分析器层
│   ├── base.py                      # 分析器抽象基类
│   ├── persona_analyzer.py          # 人格分析器（MBTI/标签/说话风格/情感模式）
│   ├── memory_analyzer.py           # 记忆分析器（共同经历/内部梗/时间线）
│   └── relationship_analyzer.py     # 关系分析器（频率/发起/响应/话题/洞察）
│
├── templates/                       # 📝 Agent SOUL.md 模板
│   ├── philosopher_agent.md         # 统治者模板
│   ├── guardian_agent.md            # 护卫者模板
│   └── worker_agent.md              # 劳动者模板
│
├── ui/                              # 🎨 Web UI
│   ├── frontend/                    # React + TypeScript 前端
│   │   ├── src/
│   │   │   ├── main.tsx             # 入口（HashRouter）
│   │   │   ├── App.tsx              # 主应用（侧边栏 + 路由）
│   │   │   ├── index.css            # 全局样式（玻璃态/动画/设计系统）
│   │   │   ├── lib/
│   │   │   │   └── api.ts           # Axios API 客户端
│   │   │   └── components/
│   │   │       ├── Dashboard.tsx         # 仪表盘
│   │   │       ├── RoleManager.tsx       # 角色管理
│   │   │       ├── CreateRoleModal.tsx   # 创建角色弹窗
│   │   │       ├── SessionManager.tsx    # 会话管理
│   │   │       ├── CreateSessionModal.tsx # 创建会话弹窗
│   │   │       ├── ChatPanel.tsx         # 聊天面板（支持投票/辩论/共识结果渲染）
│   │   │       └── DecisionEngine.tsx    # 决策模式说明页
│   │   ├── index.html
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   ├── postcss.config.js
│   │   ├── tsconfig.json
│   │   └── package.json
│   └── backend/                     # Python 后端
│       └── server.py                # FastAPI 服务器（API + 静态托管）
│
├── data/                            # 💾 数据目录（gitignored）
│   ├── roles/                       # 角色配置（YAML）
│   ├── sessions/                    # 会话记录（JSON）
│   ├── decisions/                   # 决策记录
│   └── cache/                       # 采集数据缓存
│
├── config/                          # ⚙️ 配置文件
│   ├── config.yaml.example          # 配置模板（复制为 config.yaml 使用）
│   └── permissions.yaml             # 三等级权限矩阵
│
├── scripts/                         # 🔧 工具脚本
│   └── sync_openclaw.py             # 同步 Agent 到 OpenClaw + API Key 检测
│
├── logs/                            # 📋 日志目录
│
└── docs/                            # 📚 文档
    ├── PROJECT_OVERVIEW.md           # 项目总览
    ├── INSTALLATION.md               # 安装指南
    └── ROADMAP.md                    # 路线图
```

### 核心引擎协作关系

```
用户消息
   │
   ▼
SessionEngine.send_message()
   │
   ├── speaking_mode == "free"      → _free_discussion()    → 各角色独立回复
   ├── speaking_mode == "turn_based" → _turn_based()         → 按序轮流回复
   ├── speaking_mode == "debate"     → _debate_mode()        ─┐
   ├── speaking_mode == "vote"       → _vote_mode()          ─┤ 委托给 DecisionEngine
   └── speaking_mode == "consensus"  → _consensus_mode()     ─┘
                                              │
                                              ▼
                                    DecisionEngine
                                    ├── vote()      → 加权投票，返回 YES/NO/TIE
                                    ├── debate()    → 多轮辩论 + AI 总结
                                    └── consensus() → 多轮协商，失败降级为投票
                                              │
                                              ▼
                                    保存决策到 data/decisions/
                                    关联 session_id，可追溯
```

### 投票权重说明

投票权重由 `config/permissions.yaml` 中的等级权限自动决定：

| 等级 | 投票权重 | 说明 |
|------|----------|------|
| 统治者（philosopher） | 2.0 | 战略决策者，权重最高 |
| 护卫者（guardian） | 1.0 | 执行监督者，标准权重 |
| 劳动者（worker） | 0.0 | 方案提供者，可讨论但无投票权 |

> **注意**: 劳动者在投票模式下权重为 0（根据 `permissions.yaml` 中 `can_vote: false`），但仍可参与讨论和辩论。当所有参与者权重为 0 时，系统会降级为简单多数计数。
>
> **平权降级**: 当会话中参与者等级单一（如全是护卫者）或缺少等级多样性时，系统自动切换为**平权投票模式**（所有人权重=1.0），确保投票公平。例如：
> - 全是劳动者 → 所有人权重 1.0（否则全员 0 权重无法投票）
> - 全是护卫者 → 所有人权重 1.0（否则 1.0 vs 1.0 无差异）
> - 统治者+护卫者 → 保留等级权重（2.0 vs 1.0）

### 会话状态管理

会话有两种状态：
- **活跃**（active）— 可以正常发送消息
- **已结束**（inactive）— 会话归档，保留历史记录

在会话管理页面，你可以：
- 点击 ⏸ 按钮结束会话
- 点击 ▶ 按钮重新激活已结束的会话

---

## 📡 API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| **角色** | | |
| GET | `/api/roles` | 列出角色（支持 `tier`/`type`/`active` 过滤） |
| GET | `/api/roles/{id}` | 获取角色详情 |
| POST | `/api/roles` | 创建角色（含数据采集、分析、生成） |
| PUT | `/api/roles/{id}` | 更新角色 |
| DELETE | `/api/roles/{id}` | 删除角色（同步清理 OpenClaw 注册） |
| POST | `/api/roles/{id}/regenerate` | 重新生成角色 Agent |
| **会话** | | |
| GET | `/api/sessions` | 列出会话（支持 `role_id`/`mode`/`active` 过滤） |
| GET | `/api/sessions/{id}` | 获取会话详情（含消息历史） |
| POST | `/api/sessions` | 创建会话 |
| POST | `/api/sessions/{id}/messages` | 发送消息（触发发言模式） |
| PUT | `/api/sessions/{id}/active` | 切换会话活跃状态 |
| DELETE | `/api/sessions/{id}` | 删除会话 |
| DELETE | `/api/sessions/{id}/messages` | 清空会话消息（保留系统消息） |
| **决策** | | |
| GET | `/api/decisions` | 列出决策记录（支持 `session_id` 过滤） |
| GET | `/api/decisions/{id}` | 获取决策详情 |
| **统计** | | |
| GET | `/api/stats` | 系统统计（角色/会话/决策数量） |
| GET | `/api/health` | 健康检查 |

---

## 📂 数据存储说明

| 存储位置 | 内容 | 说明 |
|----------|------|------|
| `data/roles/` | 用户创建的数字角色 | 每个角色一个 yaml 文件，包含人格分析、记忆提取、配置 |
| `data/sessions/` | 对话会话 | 每个会话一个 json 文件，存储完整对话历史和参与者 |
| `data/decisions/` | 决策记录 | 投票/辩论/共识决策存储 |
| `data/cache/` | 采集数据缓存 | 采集到的原始聊天数据缓存 |
| `~/.openclaw/workspace/agents/` | OpenClaw Agent 工作区 | 生成的 Agent 工作目录，包含 SOUL.md 符合 OpenClaw 规范 |
| `./config/` | 项目配置 | 配置模板（config.yaml.example），不含用户隐私 |

### 隐私权说明

- 所有你创建的数字角色、对话数据、决策记录都保存在**本地**，不会上传到任何云端
- 创建角色时，项目会从你的聊天记录中**蒸馏提取**人格和记忆，生成 SOUL.md 存入 `~/.openclaw/workspace/agents/`。原始聊天记录**不会被复制**到 OpenClaw 目录
- 角色元信息（ID、名称、工作区路径）会同步到 `~/.openclaw/openclaw.json`，不含隐私内容
- OpenClaw 的 Agent 在对话中会自行积累记忆（`memory/` 目录和 `MEMORY.md`），这些也**仅存于本地**
- 投票/辩论/共识的决策过程记录保存在 `data/decisions/`，仅包含投票结果和理由，不包含原始聊天数据
- `config/permissions.yaml` 中的权限配置不包含个人信息，仅为功能规则定义
- 卸载时运行 `./uninstall.sh` 会删除所有本项目创建的数据

### 卸载

```bash
./uninstall.sh
```

会自动：

- 从你的 `~/.openclaw/openclaw.json` 移除所有本项目创建的 Agent
- 删除本地所有项目数据（角色/会话/缓存）

---

## 🔧 配置说明

### 权限配置（permissions.yaml）

`config/permissions.yaml` 定义了三等级的权限矩阵，影响投票权重和功能限制：

```yaml
philosopher:          # 统治者
  can_vote: true      # 可投票
  can_decide: true    # 可做最终决策
  can_debate: true    # 可辩论
  can_propose: true   # 可提方案

guardian:             # 护卫者
  can_vote: true
  can_decide: false
  can_debate: true
  can_propose: true

worker:               # 劳动者
  can_vote: false     # 不可投票（投票权重为 0）
  can_decide: false
  can_debate: true    # 仍可参与讨论和辩论
  can_propose: true
```

修改此文件后重启服务即可生效，投票权重会自动重新计算。

### 角色配置示例

```yaml
id: first-love-001
name: 初恋
type: first-love  # first-love | colleague | family | friend
tier: philosopher  # philosopher | guardian | worker
created_at: 2024-04-07T10:00:00Z

persona:
  mbti: ENFP
  zodiac: 双子座
  tags:
    - 话痨
    - 浪漫主义

memory:
  shared_experiences:
    - 第一次约会去了那家难吃的意面店
  inside_jokes:
    - 你总说我是你的小太阳

agent_config:
  model: gpt-4
  temperature: 0.8

sources:
  - type: wechat
    path: /data/wechat_export_001.db
```

---

## 💡 使用场景

### 场景 1：职业咨询

创建"技术导师"（统治者）和"猎头朋友"（护卫者），使用辩论模式讨论职业选择。

### 场景 2：技术方案讨论

创建"架构师同事"和"测试同事"，使用投票模式评估技术方案。

### 场景 3：情感支持

创建"初恋"角色（统治者），使用对话模式进行情感交流。

---

## 🤝 贡献指南

欢迎贡献！无论是 Bug 报告、功能建议、代码贡献还是文档改进。

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 贡献方向

- 🎨 UI/UX 改进
- 🤖 新数据源支持（Telegram、WhatsApp、Slack 等）
- 📦 新分析器
- 🔗 第三方集成
- 📱 移动端适配
- 🌐 国际化（i18n）
- 📝 文档改进

---

## 🙏 致谢

- **[OpenClaw](https://github.com/openclaw/openclaw)** - AI Agent 运行时框架
- **柏拉图《理想国》** - 三等级协作哲学思想

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

---

## 💬 联系方式

- **作者**: KKKenChow
- **GitHub**: https://github.com/KKKenChow/Cyber-Ideal-State
- **Issue**: https://github.com/KKKenChow/Cyber-Ideal-State/issues

---

**愿我们都可以驾驭理性、意志、欲望**

🏛️ 欢迎来到赛博理想国
