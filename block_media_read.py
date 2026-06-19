"""
PreToolUse hook: Block Read tool on multimedia files.

When the agent tries to Read an image/audio/video file, this hook
blocks the call (exit 2) and instructs the model to use the
mimo-media MCP tools instead.
"""
import sys, json

MEDIA_MAP = {
    ".png": ("image", "understand_image"),
    ".jpg": ("image", "understand_image"),
    ".jpeg": ("image", "understand_image"),
    ".gif": ("image", "understand_image"),
    ".bmp": ("image", "understand_image"),
    ".webp": ("image", "understand_image"),
    ".svg": ("image", "understand_image"),
    ".mp3": ("audio", "understand_audio"),
    ".wav": ("audio", "understand_audio"),
    ".m4a": ("audio", "understand_audio"),
    ".ogg": ("audio", "understand_audio"),
    ".flac": ("audio", "understand_audio"),
    ".aac": ("audio", "understand_audio"),
    ".mp4": ("video", "understand_video"),
    ".mov": ("video", "understand_video"),
    ".avi": ("video", "understand_video"),
    ".mkv": ("video", "understand_video"),
    ".webm": ("video", "understand_video"),
    ".flv": ("video", "understand_video"),
}

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = data.get("tool_input", {})
file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
if not file_path:
    sys.exit(0)

ext = ""
if "." in file_path:
    ext = "." + file_path.rsplit(".", 1)[-1].lower()

if ext in MEDIA_MAP:
    media_type, mcp_tool = MEDIA_MAP[ext]
    print(
        f"BLOCKED: The Read tool cannot process {media_type} files. "
        f"Use the MCP tool `mcp__mimo-media__{mcp_tool}` instead. "
        f"Example: call mcp__mimo-media__{mcp_tool} with "
        f'{{"prompt": "describe this {media_type}", "{media_type}_path": "{file_path}"}}',
        file=sys.stderr
    )
    sys.exit(2)

sys.exit(0)
