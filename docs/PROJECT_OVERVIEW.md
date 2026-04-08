# Cyber-Ideal-State 项目说明

## 项目概述

**Cyber-Ideal-State（赛博理想国）** 是一个基于 OpenClaw 的多 Agent 数字生命管理框架。

项目灵感来源于：
- **柏拉图《理想国》** - 三等级会话制（统治者-护卫者-劳动者）
- **ex-skill & colleague-skill** - 数据采集和人格分析

---

## 完整项目结构

```
Cyber-Ideal-State/
├── README.md                        # 📄 项目文档
├── LICENSE                          # ⚖️ MIT 许可证
├── requirements.txt                 # 📦 Python 依赖
├── package.json                     # 📦 前端依赖元数据
├── install.sh                       # 🔧 一键安装脚本
├── start.sh                         # 🚀 一键启动脚本
├── uninstall.sh                     # 🗑️ 卸载清理脚本
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
│   ├── wechat_collector.py          # 微信采集（SQLite）
│   ├── qq_collector.py              # QQ 采集（TXT/MHT）
│   ├── feishu_collector.py          # 飞书采集（API）
│   ├── email_collector.py           # 邮件采集（EML/MBOX）
│   └── photo_collector.py           # 照片采集（EXIF）
│
├── analyzers/                       # 🔍 数据分析器层
│   ├── base.py                      # 分析器抽象基类
│   ├── persona_analyzer.py          # 人格分析器
│   ├── memory_analyzer.py           # 记忆分析器
│   └── relationship_analyzer.py     # 关系分析器
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
│   │   │       ├── ChatPanel.tsx         # 聊天面板
│   │   │       ├── SessionPanel.tsx      # 会话面板（旧版兼容）
│   │   │       └── DecisionEngine.tsx    # 决策模式说明页
│   │   ├── index.html
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   ├── postcss.config.js
│   │   ├── tsconfig.json
│   │   └── package.json
│   └── backend/                     # Python 后端
│       └── server.py                # FastAPI 服务器
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
│   └── sync_openclaw.py             # 同步 OpenClaw 配置
│
├── logs/                            # 📋 日志目录
└── docs/                            # 📚 文档
    ├── PROJECT_OVERVIEW.md           # 项目总览
    ├── INSTALLATION.md               # 安装指南
    └── ROADMAP.md                    # 路线图
```

---

## 核心功能说明

### 1. 数据采集器

支持的采集器：

| 采集器 | 功能 | 文件 | 输入格式 |
|--------|------|------|----------|
| 微信 | 解析微信聊天记录 | `wechat_collector.py` | SQLite（兼容 WeChatMsg/PyWxDump/留痕） |
| QQ | 解析 QQ 聊天记录 | `qq_collector.py` | TXT/MHT |
| 飞书 | 通过 API 采集飞书消息和文档 | `feishu_collector.py` | API（需 app_id/app_secret） |
| 邮件 | 解析邮件导出文件 | `email_collector.py` | EML/MBOX |
| 照片 | 提取照片 EXIF 元信息 | `photo_collector.py` | JPEG/PNG |

### 2. Agent 生成引擎

**核心流程：**

```
输入数据
    ↓
采集（Collectors）
    ↓
分析（Analyzers）
    ↓
生成 OpenClaw Agent（SOUL.md + 角色配置）
    ↓
同步到 OpenClaw（scripts/sync_openclaw.py）
```

**分析能力：**

| 分析器 | 提取内容 | 依赖 |
|--------|----------|------|
| PersonaAnalyzer | MBTI、性格标签、说话风格、情感模式、活跃时间 | LLM（可选） |
| MemoryAnalyzer | 共同经历、内部梗、时间线、频繁互动日 | LLM（可选） |
| RelationshipAnalyzer | 互动频率、发起模式、响应时间、话题分布 | LLM（可选） |

> 无 LLM 时，分析器会执行基础规则分析（消息长度、时间分布、表情使用等）。

### 3. 三等级会话制

**柏拉图式的理想国架构：**

| 等级 | 职责 | 模板 | 典型角色 |
|------|------|------|----------|
| 统治者（Philosopher King） | 战略思考、价值判断、终极决策 | `philosopher_agent.md` | 导师、智者、长期顾问 |
| 护卫者（Guardian） | 执行、保护、协调、风险评估 | `guardian_agent.md` | 可靠同事、执行力强的朋友 |
| 劳动者（Worker） | 创作、生成、服务、提供方案 | `worker_agent.md` | 创作型同事、活力同学 |

**权限矩阵**（`config/permissions.yaml`）：
- 统治者：可与护卫者、劳动者对话，有投票权
- 护卫者：可与统治者、劳动者对话，有投票权
- 劳动者：可与所有等级对话，无投票权

### 4. 会话引擎

**支持 5 种发言模式：**

| 模式 | 描述 | 实现方式 |
|------|------|----------|
| 自由讨论 | 所有角色自由发言 | 每个参与者独立回复 |
| 轮流发言 | 按顺序轮流回应 | 根据消息计数轮转 |
| 辩论 | 多轮辩论，总结观点 | 指定轮数，后续轮参考前轮回复 |
| 投票 | 对问题投票决定 | 收集 YES/NO/ABSTAIN，加权计算 |
| 共识 | 多轮协商，必要时回退到投票 | 最多指定轮数，全员同意则通过 |

### 5. Web UI

**技术栈：**
- 前端：React 18 + TypeScript + Tailwind CSS + Vite
- 后端：Python + FastAPI + Uvicorn
- 通信：Axios HTTP 客户端

**功能模块：**

| 模块 | 组件 | 功能 |
|------|------|------|
| 仪表盘 | `Dashboard.tsx` | 系统概览、角色统计、会话统计、理想国状态检测、新手指南 |
| 角色管理 | `RoleManager.tsx` + `CreateRoleModal.tsx` | 角色列表/筛选/创建/删除，数据源配置，等级选择 |
| 会话管理 | `SessionManager.tsx` + `CreateSessionModal.tsx` | 会话列表/创建/删除，角色选择，发言模式配置 |
| 聊天面板 | `ChatPanel.tsx` | 多角色对话、投票结果展示、消息导出、自动滚动 |

### 6. API 接口

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/stats` | GET | 系统统计（角色/会话/等级分布） |
| `/api/roles` | GET/POST | 角色列表 / 创建角色 |
| `/api/roles/{id}` | GET/PUT/DELETE | 角色详情 / 更新 / 删除 |
| `/api/roles/{id}/regenerate` | POST | 重新生成 Agent |
| `/api/sessions` | GET/POST | 会话列表 / 创建会话 |
| `/api/sessions/{id}` | GET/DELETE | 会话详情 / 删除 |
| `/api/sessions/{id}/messages` | POST | 发送消息到会话 |
| `/ui` | GET | 前端 UI |

---

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/KKKenChow/Cyber-Ideal-State.git
cd Cyber-Ideal-State

# 运行安装脚本
chmod +x install.sh && ./install.sh
```

### 启动

```bash
# 一键启动
chmod +x start.sh && ./start.sh
```

访问管理界面：http://localhost:8080/ui

---

## 技术架构图

```
┌───────────────────────────────────┐
│     Web Browser (React SPA)       │
│  Dashboard / Roles / Sessions     │
│         + ChatPanel               │
└───────────────┬───────────────────┘
                │ HTTP (Axios)
┌───────────────▼───────────────────┐
│       FastAPI Server (:8080)      │
│  ┌─────────────────────────────┐  │
│  │     Static File Serving     │  │
│  │     (/ui → dist/index.html) │  │
│  └─────────────────────────────┘  │
│  ┌─────────────────────────────┐  │
│  │         REST API            │  │
│  │  /api/roles  /api/sessions  │  │
│  │  /api/stats  /api/health    │  │
│  └────────────┬────────────────┘  │
└───────────────┼───────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐  ┌───▼───┐  ┌───▼──────────┐
│ Core  │  │Collect │  │  Analyzers   │
│Engine │  │  ors   │  │              │
│       │  │        │  │ - Persona    │
│Models │  │WeChat  │  │ - Memory     │
│Role   │  │QQ      │  │ - Relation   │
│Session│  │Feishu  │  │              │
│Decide │  │Email   │  │              │
│       │  │Photo   │  │              │
└───┬───┘  └────────┘  └──────────────┘
    │
┌───▼─────────────────────────────────┐
│           OpenClaw                   │
│                                      │
│  - Agent Runtime (openclaw agent)    │
│  - Gateway                          │
│  - Workspace (~/.openclaw/)         │
│  - Config (openclaw.json)           │
└──────────────────────────────────────┘
```

---

## 数据流

```
用户创建角色
    ↓
选择数据源（微信/QQ/飞书/邮件/照片/手动描述）
    ↓
Collector 采集数据 → 缓存到 data/cache/
    ↓
Analyzer 分析数据 → 提取 Persona + Memory
    ↓
AgentGenerator 生成 SOUL.md + 角色配置
    ↓
保存到 data/roles/{id}.yaml
    ↓
生成到 ~/.openclaw/workspace/agents/{id}/
    ↓
sync_openclaw.py 同步到 openclaw.json
    ↓
用户创建会话 → 选择角色 → 选择发言模式
    ↓
SessionEngine 驱动对话 → 通过 OpenClaw CLI 调用 Agent
    ↓
保存到 data/sessions/{id}.json
```

---

## License

MIT License - 详见 [LICENSE](../LICENSE)

---

**愿我们都可以驾驭理性、意志、欲望**

🏛️ 赛博理想国
