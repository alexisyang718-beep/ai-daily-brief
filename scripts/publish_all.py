#!/usr/bin/env python3
"""
一键发布脚本：GitHub + 邮件 + 公众号

用法:
    # 发布今天的日报（自动检测最新）
    python publish_all.py
    
    # 发布指定日报
    python publish_all.py brief/2026-03-18.html
    
    # 只执行部分步骤
    python publish_all.py --skip-github    # 跳过 GitHub
    python publish_all.py --skip-email     # 跳过邮件
    python publish_all.py --skip-wechat    # 跳过公众号
    
    # 邮件只发给测试邮箱
    python publish_all.py --test-email alexisyang@tencent.com
    
    # 邮件只发给新增的一批人
    python publish_all.py --new-only

流程:
    1. Git: add -> commit -> push
    2. 邮件: 发送给收件人列表
    3. 公众号: 同步到微信草稿箱
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
BRIEF_DIR = PROJECT_DIR / "brief"
RAPHAEL_DIR = PROJECT_DIR.parent / "raphael-publish"


def run(cmd, cwd=None, check=True):
    """执行 shell 命令"""
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        print(f"❌ 命令失败: {' '.join(cmd)}")
        sys.exit(1)
    return result


def find_latest_brief():
    """自动检测 brief/ 下最新的日报 HTML（排除 -wechat.html）"""
    html_files = sorted(
        [f for f in BRIEF_DIR.glob("*.html") if not f.name.endswith("-wechat.html")],
        reverse=True
    )
    if not html_files:
        raise FileNotFoundError(f"brief/ 目录下没有找到日报 HTML 文件")
    return html_files[0]


def step_github(brief_file: Path, skip: bool = False):
    """步骤1: 推送到 GitHub"""
    if skip:
        print("\n⏭️  跳过 GitHub 推送")
        return
    
    print("\n" + "="*50)
    print("📤 步骤 1/3: 推送到 GitHub")
    print("="*50)
    
    # 检查是否有变更
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_DIR,
        capture_output=True, text=True
    )
    
    if not result.stdout.strip():
        print("⚠️  没有待提交的变更")
        return
    
    # git add
    run(["git", "add", "-A"], cwd=PROJECT_DIR)
    
    # git commit
    date_str = brief_file.stem  # e.g., "2026-03-18"
    run(["git", "commit", "-m", f"📰 Daily brief {date_str}"], cwd=PROJECT_DIR)
    
    # git push
    run(["git", "push", "origin", "main"], cwd=PROJECT_DIR)
    
    print(f"✅ GitHub 推送完成: https://alexisyang718-beep.github.io/ai-archive/brief/{brief_file.name}")


def step_email(brief_file: Path, test_email: str = None, new_only: bool = False, skip: bool = False):
    """步骤2: 发送邮件"""
    if skip:
        print("\n⏭️  跳过邮件发送")
        return
    
    print("\n" + "="*50)
    print("📧 步骤 2/3: 发送邮件")
    print("="*50)
    
    cmd = [sys.executable, "scripts/send_email.py"]
    
    if test_email:
        cmd.extend(["--to", test_email])
        print(f"🧪 测试模式: 只发送给 {test_email}")
    elif new_only:
        cmd.append("--new-only")
        print("🆕 只发送给新增的收件人")
    else:
        print("📨 发送给全部收件人")
    
    cmd.append(str(brief_file))
    
    run(cmd, cwd=PROJECT_DIR)


def step_wechat(brief_file: Path, skip: bool = False):
    """步骤3: 同步到公众号"""
    if skip:
        print("\n⏭️  跳过公众号同步")
        return
    
    print("\n" + "="*50)
    print("💬 步骤 3/3: 同步到公众号草稿箱")
    print("="*50)
    
    if not RAPHAEL_DIR.exists():
        print(f"❌ Raphael 目录不存在: {RAPHAEL_DIR}")
        print("请确认 raphael-publish 项目路径正确")
        sys.exit(1)
    
    # 设置 PATH 包含 node
    env = os.environ.copy()
    node_path = Path.home() / ".nvm" / "versions" / "node" / "v20.20.0" / "bin"
    if str(node_path) not in env.get("PATH", ""):
        env["PATH"] = f"{node_path}:{env.get('PATH', '')}"
    
    cmd = ["node", "publish-daily.mjs", str(brief_file), "nyt"]
    
    print(f"🚀 执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=RAPHAEL_DIR, env=env, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        print("❌ 公众号同步失败")
        sys.exit(1)
    
    print("✅ 公众号草稿箱同步完成")


def main():
    parser = argparse.ArgumentParser(description='一键发布科技资讯日报')
    parser.add_argument('file', nargs='?', help='日报 HTML 文件路径（默认自动检测最新）')
    parser.add_argument('--skip-github', action='store_true', help='跳过 GitHub 推送')
    parser.add_argument('--skip-email', action='store_true', help='跳过邮件发送')
    parser.add_argument('--skip-wechat', action='store_true', help='跳过公众号同步')
    parser.add_argument('--test-email', help='测试邮箱（只发给指定邮箱）')
    parser.add_argument('--new-only', action='store_true', help='邮件只发给新增的收件人')
    
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
    
    print(f"\n📰 发布日报: {brief_file.name}")
    print(f"   路径: {brief_file}")
    
    # 执行三个步骤
    step_github(brief_file, skip=args.skip_github)
    step_email(brief_file, test_email=args.test_email, new_only=args.new_only, skip=args.skip_email)
    step_wechat(brief_file, skip=args.skip_wechat)
    
    print("\n" + "="*50)
    print("🎉 全部完成！")
    print("="*50)
    print(f"\n📱 在线版: https://alexisyang718-beep.github.io/ai-archive/brief/{brief_file.name}")
    print("💬 公众号: 请登录后台查看草稿")


if __name__ == "__main__":
    main()
