# zhipu-vision-mcp

MCP Server for vision understanding, powered by [ZhipuAI](https://open.bigmodel.cn/) GLM-4.6V / GLM-5V-Turbo multimodal models.

Provides 8 vision tools for AI coding assistants (Claude Code, Cursor, Windsurf, etc.) to analyze images, videos, charts, UI screenshots, error screenshots, and technical diagrams.

## Features

| Tool | Description |
|------|-------------|
| `analyze_image` | General-purpose image analysis (supports URL & local path) |
| `analyze_video` | Video content analysis (MP4/MOV/M4V, max 8MB) |
| `analyze_data_visualization` | Chart/dashboard analysis — extract trends, anomalies, metrics |
| `diagnose_error_screenshot` | Error screenshot diagnosis — identify error type & fix suggestions |
| `extract_text_from_screenshot` | OCR text extraction from screenshots |
| `ui_to_artifact` | UI screenshot → code / design spec / AI prompt / description |
| `ui_diff_check` | Compare design mockup vs implementation screenshot |
| `understand_technical_diagram` | Parse architecture diagrams, flowcharts, UML, ER diagrams |

## Prerequisites

- Python 3.10+
- [ZhipuAI API Key](https://open.bigmodel.cn/) (set as environment variable)

## Installation

### Option 1: uvx (recommended)

```bash
uvx zhipu-vision-mcp
```

### Option 2: pip

```bash
pip install zhipu-vision-mcp
zhipu-vision-mcp
```

### Option 3: Clone & run

```bash
git clone https://github.com/JiaoBingJie/zhipu-vision-mcp.git
cd zhipu-vision-mcp
pip install -e .
zhipu-vision-mcp
```

## Configuration

Set your ZhipuAI API key as an environment variable:

```bash
export ZHIPUAI_API_KEY="your-api-key-here"
```

### Claude Code

Add to your `.claude/settings.json` or global `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "zhipu-vision": {
      "command": "uvx",
      "args": ["zhipu-vision-mcp"],
      "env": {
        "ZHIPUAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Or if installed via pip:

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

### Cursor

Add to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "zhipu-vision": {
      "command": "uvx",
      "args": ["zhipu-vision-mcp"],
      "env": {
        "ZHIPUAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Windsurf / VS Code (Continue)

Add to your `~/.continue/config.json` or project `.continue/config.json`:

```json
{
  "mcpServers": {
    "zhipu-vision": {
      "command": "uvx",
      "args": ["zhipu-vision-mcp"],
      "env": {
        "ZHIPUAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Models

| Tool | Default Model | Notes |
|------|--------------|-------|
| `analyze_image` | `glm-4.6v` | Configurable via `model` parameter |
| `analyze_video` | `glm-4.6v` | Configurable via `model` parameter |
| `analyze_data_visualization` | `glm-4.6v` | Fixed |
| `diagnose_error_screenshot` | `glm-4.6v` | Fixed |
| `extract_text_from_screenshot` | `glm-4.6v` | Fixed |
| `ui_to_artifact` | `glm-5v-turbo` | Uses faster model for code generation |
| `ui_diff_check` | `glm-4.6v` | Fixed |
| `understand_technical_diagram` | `glm-4.6v` | Fixed |

## Development

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run server directly
python -m zhipu_vision_mcp.server
```

## License

MIT
