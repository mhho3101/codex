---
name: mcp
description: 模型上下文协议（Model Context Protocol, MCP）——概念、MCP 服务器配置、客户端接入、工具/资源暴露与故障排查。涉及 MCP、上下文协议、连接外部工具/数据源时使用本技能。
---

# MCP（Model Context Protocol）技能

MCP 是 Anthropic 提出的开放协议，让 AI 应用通过标准化方式连接外部工具、数据源和服务。本技能指导配置与使用 MCP。

## 核心概念

- **MCP Server（服务器）**：暴露能力的一方。三种传输方式：
  - `stdio`：子进程本地启动（最常见，本地工具）
  - `sse` / `http`：远程 HTTP 服务
- **MCP Client（客户端）**：AI 应用（如 DSH/Claude 类工具），连接服务器
- **三类原语**：
  - `tools`（工具）：模型可调用的函数，执行动作
  - `resources`（资源）：可读取的数据/文件（read-only）
  - `prompts`（提示模板）：可复用的指令模板
- **发现与协商**：客户端启动时通过 `initialize` 握手，获取服务器能力列表

## 典型用途

- 连接数据库查询数据（如 postgres MCP server）
- 连接浏览器/网页抓取（如 playwright/puppeteer MCP）
- 连接文件系统、Git、开发工具
- 连接视频/图像处理工具链
- 企业内部 API 封装为 MCP server

## 配置 MCP Server（通用 JSON 形式）

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-xxx"],
      "env": { "API_KEY": "..." }
    }
  }
}
```

- `command` + `args`：stdio 启动方式
- `env`：传给服务器进程的环境变量（密钥等）
- 远程服务器：`{ "url": "https://example.com/mcp" }`（sse/http）

## 在 DSH 中使用

DSH 支持 MCP 客户端能力（`@deepseek-ai/dsh-mcp-client`）。使用方法：
1. 确认当前环境的 MCP 配置入口（`dsh` CLI 或配置文件）
2. 按上面 JSON 格式注册服务器
3. 连接后，服务器暴露的 tools 会出现在可用工具中
4. 若环境不支持直接配置，可用 `npx @modelcontextprotocol/inspector <command> <args>` 调试服务器

## 编写自己的 MCP Server

最小 TypeScript/Node 服务器（stdio）：

```js
// server.js
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({ name: "demo", version: "1.0.0" });

server.tool("echo", { text: "string" }, async ({ text }) => ({
  content: [{ type: "text", text: `echo: ${text}` }]
}));

await server.connect(new StdioServerTransport());
```

Python 版用 `mcp` 包：`@mcp.tool()` 装饰器声明工具。

## 故障排查

| 症状 | 排查 |
|---|---|
| 连接失败 | 检查 command 是否可执行（`npx` 需 Node）、路径正确性 |
| 握手超时 | stdio 服务器需持续监听 stdin/stdout，不能直接退出 |
| 工具不出现 | 检查服务器是否崩溃（看 stderr 日志）；`initialize` 是否返回 tools 列表 |
| 权限/密钥错误 | 确认 `env` 注入正确，密钥未过期 |
| Windows 路径问题 | 用完整路径调用 node/npx；避免中文路径 |

## 安全注意事项

- MCP 服务器可执行任意命令：**只连接可信来源的服务器**
- 密钥走 `env` 注入，不要写进对话/代码库
- 公开 MCP server（远程 URL）要审查其暴露的 tools 权限
- 生产环境使用前先隔离测试

## 常用现成 MCP Server（npm 包，供参考）

- `@modelcontextprotocol/server-filesystem` — 文件系统
- `@modelcontextprotocol/server-git` — Git 操作
- `@modelcontextprotocol/server-postgres` — PostgreSQL 查询
- `@playwright/mcp` — 浏览器自动化
- `@modelcontextprotocol/server-puppeteer` — 无头浏览器
- 社区：`github.com/modelcontextprotocol/servers` 官方仓库列表

按需注册；不确定某个服务器是否适合时，先查其文档与安全性。
