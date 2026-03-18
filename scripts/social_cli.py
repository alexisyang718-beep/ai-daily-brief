#!/usr/bin/env python3
"""
社交媒体 CLI 工具统一调用入口
自动设置 PATH，支持 Twitter / Weibo

用法:
    python social_cli.py twitter feed -t following -n 100 --json
    python social_cli.py weibo search "AI" -n 50
    python social_cli.py twitter search "OpenAI" --json -o results.json
"""
import os
import sys
import subprocess
from pathlib import Path

# 自动添加 uv 工具路径
UV_BIN_PATH = Path.home() / ".local" / "bin"
if str(UV_BIN_PATH) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{UV_BIN_PATH}:{os.environ.get('PATH', '')}"

VALID_TOOLS = ["twitter", "weibo"]


def run_tool(tool: str, args: list):
    """执行 CLI 工具"""
    if tool not in VALID_TOOLS:
        print(f"❌ 未知工具: {tool}")
        print(f"支持的工具: {', '.join(VALID_TOOLS)}")
        sys.exit(1)
    
    # 检查工具是否存在
    result = subprocess.run(["which", tool], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 未找到 {tool} 命令")
        print(f"请确认已安装: uv tool install twitter-cli / kabi-weibo-cli")
        sys.exit(1)
    
    # 执行命令
    cmd = [tool] + args
    print(f"🚀 执行: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def main():
    if len(sys.argv) < 2:
        print("用法: python social_cli.py <twitter|weibo> [args...]")
        print("")
        print("示例:")
        print("  python social_cli.py twitter feed -t following -n 100 --json")
        print("  python social_cli.py twitter search \"OpenAI\" --json -o results.json")
        print("  python social_cli.py weibo search \"AI\" -n 50")
        sys.exit(1)
    
    tool = sys.argv[1]
    args = sys.argv[2:]
    run_tool(tool, args)


if __name__ == "__main__":
    main()
