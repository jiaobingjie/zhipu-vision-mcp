# zhipu-vision-mcp

基于 [智谱AI](https://open.bigmodel.cn/) GLM-4.6V / GLM-5V-Turbo 多模态模型的视觉理解 MCP Server。

为 AI 编程助手（Claude Code、Cursor、Windsurf 等）提供 8 个视觉分析工具，支持图像、视频、图表、UI 截图、错误截图和技术图表的理解。

## 功能

| 工具 | 说明 |
|------|------|
| `analyze_image` | 通用图像分析（支持 URL 和本地路径） |
| `analyze_video` | 视频内容分析（MP4/MOV/M4V，最大 8MB） |
| `analyze_data_visualization` | 图表/仪表盘分析 — 提取趋势、异常、指标 |
| `diagnose_error_screenshot` | 错误截图诊断 — 识别错误类型并给出修复建议 |
| `extract_text_from_screenshot` | 截图 OCR 文字提取 |
| `ui_to_artifact` | UI 截图 → 代码 / 设计规范 / AI 提示词 / 自然语言描述 |
| `ui_diff_check` | 设计稿与实现截图对比 |
| `understand_technical_diagram` | 解析架构图、流程图、UML、ER 图等技术图表 |

## 前置条件

- Python 3.10+
- [智谱AI API Key](https://open.bigmodel.cn/)（设置为环境变量）

## 安装与使用

### 第 1 步：安装

```bash
git clone https://github.com/JiaoBingJie/zhipu-vision-mcp.git
cd zhipu-vision-mcp
pip install -e .
```

安装完成后，`zhipu-vision-mcp` 命令将注册到系统 PATH 中，可在任意目录运行。

### 第 2 步：获取 API Key

前往 [智谱AI开放平台](https://open.bigmodel.cn/) 注册并获取 API Key。

### 第 3 步：配置 AI 编程助手

在对应的配置文件中添加 MCP 服务器配置。配置中的 `env.ZHIPUAI_API_KEY` 会在启动 MCP Server 时注入为环境变量，无需手动 export。

#### Claude Code

添加到 `~/.claude/settings.json`（全局）或项目 `.claude/settings.json`：

```json
{
  "mcpServers": {
    "zhipu-vision": {
      "command": "zhipu-vision-mcp",
      "env": {
        "ZHIPUAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Cursor

添加到 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "zhipu-vision": {
      "command": "zhipu-vision-mcp",
      "env": {
        "ZHIPUAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Windsurf / VS Code (Continue)

添加到 `~/.continue/config.json` 或项目 `.continue/config.json`：

```json
{
  "mcpServers": {
    "zhipu-vision": {
      "command": "zhipu-vision-mcp",
      "env": {
        "ZHIPUAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 模型

| 工具 | 默认模型 | 备注 |
|------|----------|------|
| `analyze_image` | `glm-4.6v` | 可通过 `model` 参数配置 |
| `analyze_video` | `glm-4.6v` | 可通过 `model` 参数配置 |
| `analyze_data_visualization` | `glm-4.6v` | 固定，关闭深度思考 |
| `diagnose_error_screenshot` | `glm-4.6v` | 固定 |
| `extract_text_from_screenshot` | `glm-4.6v` | 固定 |
| `ui_to_artifact` | `glm-5v-turbo` | 使用更快的模型，关闭深度思考 |
| `ui_diff_check` | `glm-4.6v` | 固定 |
| `understand_technical_diagram` | `glm-4.6v` | 固定 |

## 开发

```bash
# 开发模式安装（包含测试和 lint 工具）
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check src/

# 直接运行 server
python -m zhipu_vision_mcp.server
```

## 许可证

MIT
