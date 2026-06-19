# Claude Code Multimedia Hook

> Prevent Claude Code agents from directly reading image/audio/video files — route them through MCP multimedia recognition instead.

[English](#english) | [中文](#chinese)

---

## English

### The Problem

When using a **text-only model** (e.g., DeepSeek V4 Pro, MiMo V2.5 Pro) with Claude Code, the agent cannot process images, audio, or video. However, during long multi-step tasks, the agent tends to call the `Read` tool directly on multimedia files — which fails because the model can't understand binary data.

### The Solution: Two-Layer Defense

This repository provides a **PreToolUse Hook** that intercepts `Read` tool calls and blocks them for multimedia files, guiding the agent to use the correct MCP multimedia recognition tools instead.

Combined with CLAUDE.md instructions, this creates a **two-layer defense**:

| Layer | Type | What it does |
|-------|------|-------------|
| **1. CLAUDE.md** | Soft guidance | Tells the agent which MCP tools to use for multimedia |
| **2. PreToolUse Hook** | Hard interception | System-level block: prevents `Read` on media files, returns instructions |

### How It Works

```
Agent encounters "screenshot.png"
    │
    ├─ Layer 1: CLAUDE.md guidance
    │   "Use mcp__mimo-media__understand_image"
    │
    ├─ If Agent still tries Read("screenshot.png")
    │
    └─ Layer 2: PreToolUse Hook intercepts
        │
        ├── Detects .png extension
        ├── exit 2 (blocks the call)
        └── stderr: "BLOCKED: Use mcp__mimo-media__understand_image"
                │
                └── Agent sees feedback → switches to MCP tool
                    │
                    └── MCP returns text description → continues reasoning
```

### Prerequisites

1. **[mimo-media-recognition-mcp](https://github.com/congxxx/mimo-media-recognition-mcp)** installed and registered in Claude Code
2. Python 3.10+ (for the hook script)
3. Claude Code with a **text-only** model (the hook is unnecessary if your model is natively multimodal)

### File Overview

| File | Purpose |
|------|---------|
| `block_media_read.py` | PreToolUse hook script — blocks `Read` on media files |
| `CLAUDE.md.example` | Template rules to add to your `~/.claude/CLAUDE.md` |
| `settings.example.json` | Hook registration snippet for `~/.claude/settings.json` |

### Installation

**Step 1: Clone and copy**

```bash
git clone https://github.com/SongXue-J/claude-code-multimedia-hook.git
cp claude-code-multimedia-hook/block_media_read.py ~/.claude/hooks/block_media_read.py
```

**Step 2: Register the hook**

Add the following to your `~/.claude/settings.json` (merge with existing content):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/block_media_read.py",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

> **Note**: Adjust the `python` command if needed (e.g., `python3` on macOS/Linux, or the full path to your Python interpreter on Windows).

**Step 3: Update CLAUDE.md**

Append the content of `CLAUDE.md.example` to your `~/.claude/CLAUDE.md`.

**Step 4: Restart Claude Code**

The hook configuration is loaded at session start. Restart your Claude Code session for changes to take effect.

### Verification

```bash
# Test: hook blocks image reads
echo '{"tool_name":"Read","tool_input":{"file_path":"test.png"}}' | python ~/.claude/hooks/block_media_read.py
# Expected: stderr message, exit code 2

# Test: normal files pass through
echo '{"tool_name":"Read","tool_input":{"file_path":"README.md"}}' | python ~/.claude/hooks/block_media_read.py
# Expected: no output, exit code 0
```

### Supported File Types

| Category | Extensions | MCP Tool |
|----------|------------|----------|
| **Image** | .png .jpg .jpeg .gif .bmp .webp .svg | `understand_image` |
| **Audio** | .mp3 .wav .m4a .ogg .flac .aac | `understand_audio` |
| **Video** | .mp4 .mov .avi .mkv .webm .flv | `understand_video` |

### Known Limitations

- **`@file` references bypass hooks**: Due to [claude-code#9407](https://github.com/anthropics/claude-code/issues/9407), system-initiated tool calls (e.g., when a user types `@screenshot.png`) do not trigger PreToolUse hooks. The hook only intercepts explicit `Read` calls from the agent.
- **Only intercepts `Read`**: Other tools that can access file content (e.g., custom MCP tools) are not intercepted.
- **Requires MCP server**: This hook only routes to MCP tools — you must have `mimo-media-recognition-mcp` (or a compatible alternative) installed.

### Model-Agnostic

While this solution was developed for the MiMo MCP ecosystem, the hook script is **model-agnostic**. It works with any text-only model (DeepSeek, MiMo Pro, etc.) as long as you have a multimedia MCP server registered.

### Customization

To change the MCP tool prefix (e.g., if you use a different MCP server), edit the `MEDIA_MAP` dictionary in `block_media_read.py` and update the error message format.

### Acknowledgments

- **[congxxx/mimo-media-recognition-mcp](https://github.com/congxxx/mimo-media-recognition-mcp)** — The MCP server that bridges text-only models with MiMo's multimodal API
- **[congxxx's blog (cnblogs)](https://www.cnblogs.com/congxinxue/p/20086413)** — Original tutorial that inspired this solution
- **[Claude Code Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)** — Official hook API reference

### License

MIT © 2026 Song Xue

---

<a id="chinese"></a>

## 中文

### 问题

使用**纯文本模型**（如 DeepSeek V4 Pro、MiMo V2.5 Pro）接入 Claude Code 时，Agent 无法处理图片、音频和视频。但在长任务推理中，Agent 倾向于直接用 `Read` 工具读取多媒体文件——因为模型不理解二进制数据，导致报错和信息丢失。

### 解决方案：双层防御

本仓库提供一个 **PreToolUse Hook**，拦截对多媒体文件的 `Read` 调用，引导 Agent 改用正确的 MCP 多媒体识别工具。

结合 CLAUDE.md 指令，构成**双层防御**：

| 层级 | 类型 | 作用 |
|------|------|------|
| **1. CLAUDE.md** | 软引导 | 告诉 Agent 遇到多媒体文件应该用哪个 MCP 工具 |
| **2. PreToolUse Hook** | 硬拦截 | 系统级拦截：阻止 Read 调用多媒体文件，返回正确指令 |

### 工作原理

见上方英文版流程图。

### 前置条件

1. 已安装并注册 **[mimo-media-recognition-mcp](https://github.com/congxxx/mimo-media-recognition-mcp)**
2. Python 3.10+
3. Claude Code 使用的是**纯文本模型**（如果模型原生支持多模态，则不需要此 Hook）

### 安装步骤

**第一步：克隆并复制**

```bash
git clone https://github.com/SongXue-J/claude-code-multimedia-hook.git
cp claude-code-multimedia-hook/block_media_read.py ~/.claude/hooks/block_media_read.py
```

**第二步：注册 Hook**

在 `~/.claude/settings.json` 中添加（与已有内容合并）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/block_media_read.py",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

> **注意**：Windows 上可能需要将 `python` 替换为完整路径。

**第三步：更新 CLAUDE.md**

将 `CLAUDE.md.example` 的内容追加到 `~/.claude/CLAUDE.md` 末尾。

**第四步：重启 Claude Code**

Hook 配置在会话启动时加载，需重启 Claude Code 才能生效。

### 验证

```bash
# 测试：Hook 拦截图片读取
echo '{"tool_name":"Read","tool_input":{"file_path":"test.png"}}' | python ~/.claude/hooks/block_media_read.py
# 预期：stderr 输出提示信息，退出码 2

# 测试：普通文件正常放行
echo '{"tool_name":"Read","tool_input":{"file_path":"README.md"}}' | python ~/.claude/hooks/block_media_read.py
# 预期：无输出，退出码 0
```

### 已知限制

- **`@file` 语法绕过 Hook**：[claude-code#9407](https://github.com/anthropics/claude-code/issues/9407)，用户使用 `@screenshot.png` 引用文件时，系统发起的工具调用不会触发 PreToolUse Hook。Hook 只能拦截 Agent 主动发起的 `Read` 调用。
- **仅拦截 `Read`**：不拦截其他可能读取文件内容的工具。
- **依赖 MCP Server**：需要先安装并配置好多媒体识别的 MCP Server。

### 致谢

- **[congxxx/mimo-media-recognition-mcp](https://github.com/congxxx/mimo-media-recognition-mcp)** — 多媒体识别 MCP Server
- **[congxxx 博客](https://www.cnblogs.com/congxinxue/p/20086413)** — 原方案教程
- **[Claude Code Hooks 文档](https://docs.anthropic.com/en/docs/claude-code/hooks)** — 官方 Hook API 文档

### License

MIT © 2026 Song Xue
