# Cyber-Ideal-State 安装指南

本文档提供了详细的安装和配置说明。

---

## 环境要求

### 必需

- **Python** 3.9 或更高版本
- **Node.js** 18 或更高版本（用于前端 UI 构建）
- **OpenClaw** 已安装并配置

### 可选

- **Redis** 5.0+（用于事件总线，默认未启用）
- **jq**（用于卸载脚本自动清理 OpenClaw 配置）

---

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/KKKenChow/Cyber-Ideal-State.git
cd Cyber-Ideal-State
```

### 2. 安装 Python 依赖

```bash
pip3 install -r requirements.txt
```

如果遇到权限问题，可以使用用户级安装：

```bash
pip3 install --user -r requirements.txt
```

### 3. 安装 Node.js 依赖

```bash
cd ui/frontend
npm install
cd ../..
```

> **注意**：前端已经预构建好了（`ui/frontend/dist/` 已包含），如果你不需要修改前端，可以跳过此步。

### 4. 创建数据目录

```bash
mkdir -p data/roles
mkdir -p data/sessions
mkdir -p data/decisions
mkdir -p data/cache
```

> 安装脚本会自动创建这些目录。

### 5. 配置 OpenClaw

确保 OpenClaw 已安装并配置：

```bash
# 检查 OpenClaw 状态
openclaw status
```

### 6. 运行安装脚本（推荐）

```bash
chmod +x install.sh
./install.sh
```

安装脚本会自动：
- 创建数据目录结构
- 生成默认配置文件（`config/config.yaml`、`config/permissions.yaml`）
- 同步 OpenClaw 配置（运行 `scripts/sync_openclaw.py`）
- 构建前端（如果 Node.js 可用）

---

## 配置

### 主配置文件

编辑 `config/config.yaml`：

```yaml
# OpenClaw 集成
openclaw:
  workspace: ~/.openclaw/workspace
  agents_config: ~/.openclaw/openclaw.json

# Web 服务器
server:
  host: "127.0.0.1"
  port: 8080
  debug: true

# Agent 默认配置
agent:
  default_model: "gpt-4"
  default_temperature: 0.7
  default_max_tokens: 2000
  default_timeout: 300

# Redis（可选，默认未启用）
redis:
  enabled: false
  host: "127.0.0.1"
  port: 6379
  db: 0

# 日志
logging:
  level: "INFO"
  file: "logs/cyber-ideal-state.log"
```

### 权限配置

编辑 `config/permissions.yaml`：

```yaml
# 三等级权限矩阵
philosopher:
  can_chat_with:
    - guardian
    - worker
  can_mention:
    - all
  can_vote: true

guardian:
  can_chat_with:
    - philosopher
    - worker
  can_mention:
    - philosopher
    - guardian
    - worker
  can_vote: true

worker:
  can_chat_with:
    - philosopher
    - guardian
    - worker
  can_mention:
    - all
  can_vote: false
```

### API Key 配置

系统会自动从 OpenClaw 配置中读取 API Key，查找路径优先级：

1. `~/.openclaw/agents/main/agent/models.json`（第一个模型的 apiKey）
2. `~/.openclaw/openclaw.json`（models.providers.*.apiKey）
3. Agent 级别配置（apiKey / api_key）

如果未找到 API Key，基础功能仍可使用，但无法生成数字 Agent。

---

## 启动系统

### 一键启动（推荐）

```bash
chmod +x start.sh
./start.sh
```

### 开发模式

```bash
# 启动后端（同时托管前端静态文件）
python3 ui/backend/server.py

# 如果需要修改前端，在另一个终端启动开发服务器
cd ui/frontend
npm run dev
```

### 访问地址

- **管理界面**：http://localhost:8080/ui
- **API 根路径**：http://localhost:8080
- **健康检查**：http://localhost:8080/api/health

---

## 验证安装

### 检查 API

```bash
curl http://localhost:8080/api/health
```

期望输出：

```json
{
  "status": "healthy",
  "managers": {
    "role_manager": "active",
    "session_manager": "active",
    "session_engine": "active",
    "agent_generator": "active"
  }
}
```

### 检查系统状态

```bash
curl http://localhost:8080/api/stats
```

### 验证数据采集器

```bash
# 测试微信采集器
python3 -c "from collectors.wechat_collector import WeChatCollector; print('OK')"

# 测试飞书采集器
python3 -c "from collectors.feishu_collector import FeishuCollector; print('OK')"

# 测试邮件采集器
python3 -c "from collectors.email_collector import EmailCollector; print('OK')"
```

---

## 故障排除

### Python 依赖安装失败

```bash
# 升级 pip
pip3 install --upgrade pip

# 使用国内镜像
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### OpenClaw 同步失败

```bash
# 检查 OpenClaw 状态
openclaw status

# 手动运行同步脚本
python3 scripts/sync_openclaw.py

# 手动重启 Gateway
openclaw gateway restart
```

### 前端构建失败

确保 Node.js 和 npm 已安装：

```bash
node --version   # 需要 18+
npm --version
```

如果版本不符合要求，从 https://nodejs.org 下载安装。

> 前端已预构建，通常不需要手动构建。只在修改前端代码后才需要重新 `npm run build`。

### API Key 未找到

系统会提示 "No API key found in OpenClaw configuration"。

解决方式：
1. 确保 OpenClaw 已正确配置 API Key
2. 检查 `~/.openclaw/openclaw.json` 中是否包含 API Key
3. 缺少 API Key 不影响基础功能，但无法生成数字 Agent

---

## 卸载

```bash
chmod +x uninstall.sh
./uninstall.sh
```

会自动：
- 从 `~/.openclaw/openclaw.json` 移除所有本项目创建的 Agent（需要 jq）
- 删除本地所有项目数据（角色/会话/缓存）

如需完全删除项目：

```bash
cd .. && rm -rf Cyber-Ideal-State
```

---

## 下一步

安装完成后，请参考：

- [使用指南](../README.md#📖-使用指南)
- [项目架构](../README.md#🏗️-项目架构)
