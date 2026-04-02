#!/usr/bin/env python3
"""
一键发布脚本

默认行为（同步三步）：
    python publish_all.py brief/2026-04-01.html
    → GitHub push + 发测试邮件给 alexisyang@tencent.com + 同步公众号草稿箱

群发（单独步骤，确认测试邮件OK后执行）：
    python publish_all.py brief/2026-04-01.html --send-all

跳过某些步骤：
    python publish_all.py brief/2026-04-01.html --skip-github
    python publish_all.py brief/2026-04-01.html --skip-wechat
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
BRIEF_DIR = PROJECT_DIR / "brief"
SCRIPTS_DIR = PROJECT_DIR / "scripts"
TEST_EMAIL = "alexisyang@tencent.com"

# node 路径
NODE_PATH = Path.home() / ".nvm" / "versions" / "node" / "v20.20.0" / "bin"


def run(cmd, cwd=None, check=True):
    print(f"\n$ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        print(f"❌ 命令失败: {' '.join(str(c) for c in cmd)}")
        sys.exit(1)
    return result


def find_latest_brief():
    html_files = sorted(
        [f for f in BRIEF_DIR.glob("*.html") if not f.name.endswith("-wechat.html")],
        reverse=True
    )
    if not html_files:
        raise FileNotFoundError("brief/ 目录下没有找到日报 HTML 文件")
    return html_files[0]


def step_github(brief_file: Path, skip: bool = False):
    if skip:
        print("\n⏭️  跳过 GitHub 推送")
        return
    print("\n" + "="*50)
    print("📤 GitHub 推送")
    print("="*50)
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_DIR, capture_output=True, text=True
    )
    if not result.stdout.strip():
        print("⚠️  没有待提交的变更，跳过")
        return
    run(["git", "add", "-A"], cwd=PROJECT_DIR)
    run(["git", "commit", "-m", f"📰 Daily brief {brief_file.stem}"], cwd=PROJECT_DIR)
    run(["git", "push", "origin", "main"], cwd=PROJECT_DIR)
    print(f"✅ 在线地址: https://alexisyang718-beep.github.io/ai-archive/brief/{brief_file.name}")


def step_test_email(brief_file: Path, skip: bool = False):
    if skip:
        print("\n⏭️  跳过测试邮件")
        return
    print("\n" + "="*50)
    print(f"📧 发送测试邮件 → {TEST_EMAIL}")
    print("="*50)
    run([sys.executable, SCRIPTS_DIR / "send_email.py",
         str(brief_file), "--to", TEST_EMAIL, "-y"],
        cwd=PROJECT_DIR)
    print(f"✅ 测试邮件已发送至 {TEST_EMAIL}")


def step_wechat(brief_file: Path, skip: bool = False):
    if skip:
        print("\n⏭️  跳过公众号同步")
        return
    print("\n" + "="*50)
    print("💬 同步公众号草稿箱")
    print("="*50)
    env = os.environ.copy()
    if str(NODE_PATH) not in env.get("PATH", ""):
        env["PATH"] = f"{NODE_PATH}:{env.get('PATH', '')}"
    result = subprocess.run(
        ["node", SCRIPTS_DIR / "publish-daily.mjs", str(brief_file), "nyt"],
        cwd=PROJECT_DIR, env=env, capture_output=True, text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print("❌ 公众号同步失败")
        sys.exit(1)
    print("✅ 公众号草稿箱同步完成，请登录后台查看")


def step_send_all(brief_file: Path):
    print("\n" + "="*50)
    print("📨 群发邮件（全部收件人）")
    print("="*50)
    run([sys.executable, SCRIPTS_DIR / "send_email.py", str(brief_file)],
        cwd=PROJECT_DIR)
    print("✅ 群发完成")


def main():
    parser = argparse.ArgumentParser(description="科技资讯日报发布脚本")
    parser.add_argument("file", nargs="?", help="日报 HTML 路径（默认自动检测最新）")
    parser.add_argument("--skip-github", action="store_true", help="跳过 GitHub 推送")
    parser.add_argument("--skip-email",  action="store_true", help="跳过测试邮件")
    parser.add_argument("--skip-wechat", action="store_true", help="跳过公众号同步")
    parser.add_argument("--send-all",    action="store_true", help="群发邮件给全部收件人（单独执行）")
    args = parser.parse_args()

    # 确定日报文件
    if args.file:
        brief_file = Path(args.file)
        if not brief_file.is_absolute():
            brief_file = PROJECT_DIR / brief_file
    else:
        brief_file = find_latest_brief()

    if not brief_file.exists():
        print(f"❌ 文件不存在: {brief_file}")
        sys.exit(1)

    print(f"\n📰 日报文件: {brief_file.name}")

    if args.send_all:
        # 只群发，不跑其他步骤
        step_send_all(brief_file)
    else:
        # 默认：同步三步
        step_github(brief_file,     skip=args.skip_github)
        step_test_email(brief_file, skip=args.skip_email)
        step_wechat(brief_file,     skip=args.skip_wechat)
        print("\n" + "="*50)
        print("✅ 同步完成！确认测试邮件OK后，执行群发：")
        print(f"   python scripts/publish_all.py {brief_file.name} --send-all")
        print("="*50)


if __name__ == "__main__":
    main()
