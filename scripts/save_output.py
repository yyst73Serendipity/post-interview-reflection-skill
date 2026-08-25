#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保存最终Markdown文档到 Obsidian vault：/Users/yst/Documents/obsidianbase/
- 自动创建目录（不存在则创建）
- 文件名特殊字符转义（/ \\ : * ? " < > | → _）
- 重名不覆盖，自动追加 _v2 / _v3 / ...
"""
import os
import re
import sys
from datetime import datetime

DEFAULT_BASE_DIR = "/Users/yst/Documents/obsidianbase"

# 文件名非法字符（macOS + Windows 双平台安全）
ILLEGAL_CHARS = r'/\\:*?"<>|'


def _sanitize(name: str) -> str:
    """转义文件名非法字符，合并多余空格"""
    if not name:
        return "待定"
    for ch in ILLEGAL_CHARS:
        name = name.replace(ch, "_")
    # 连续空白/下划线 → 单个下划线
    name = re.sub(r"[\s_]+", "_", name)
    # 首尾下划线去掉
    name = name.strip("_")
    return name or "待定"


def _find_available_path(target_dir: str, filename_no_ext: str, ext: str = ".md") -> str:
    """如果文件已存在，自动加 _v2, _v3 ... 返回可用路径"""
    base = os.path.join(target_dir, filename_no_ext + ext)
    if not os.path.exists(base):
        return base
    # 已存在，找v号
    v = 2
    while True:
        candidate = os.path.join(target_dir, f"{filename_no_ext}_v{v}{ext}")
        if not os.path.exists(candidate):
            return candidate
        v += 1
        if v > 100:
            # 防死循环
            suffix = datetime.now().strftime("%H%M%S")
            return os.path.join(target_dir, f"{filename_no_ext}_{suffix}{ext}")


def save_markdown(
    markdown_content: str,
    company: str,
    position: str,
    interview_stage: str,
    interview_date: str,
    override_base_dir: str | None = None,
) -> str:
    """
    保存Markdown文件，返回保存成功的绝对路径。
    """
    base_dir = override_base_dir or DEFAULT_BASE_DIR
    # 1. 确保目录存在
    os.makedirs(base_dir, exist_ok=True)

    # 2. 组装文件名 + 转义
    safe_company = _sanitize(company)
    safe_position = _sanitize(position)
    safe_stage = _sanitize(interview_stage)
    safe_date = _sanitize(interview_date)
    filename_no_ext = f"{safe_company}_{safe_position}_{safe_stage}_{safe_date}"

    # 3. 找可用路径
    save_path = _find_available_path(base_dir, filename_no_ext, ".md")

    # 4. 写入UTF-8（无BOM，macOS习惯）
    with open(save_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(markdown_content)

    return os.path.abspath(save_path)


if __name__ == "__main__":
    # 自测：使用临时目录，不污染真实用户目录
    import tempfile
    import shutil

    tmp_dir = tempfile.mkdtemp(prefix="test_interview_output_")
    print(f"=== save_output 自测 ===")
    print(f"临时输出目录: {tmp_dir}")
    all_pass = True
    try:
        sample_md = """# 面试复盘：测试用

## 第一部分：完整QA实录
这是一个测试文件。
"""
        # Case 1: 基础保存
        p1 = save_markdown(sample_md, "字节跳动", "AI产品经理", "一面", "2026-08-20", override_base_dir=tmp_dir)
        assert os.path.exists(p1), f"文件不存在: {p1}"
        with open(p1, encoding="utf-8") as f:
            assert f.read() == sample_md, "内容不一致"
        assert "字节跳动_AI产品经理_一面_2026-08-20.md" in p1, f"文件名不对: {p1}"
        print(f"✅ Case1 基础保存 OK: {os.path.basename(p1)}")

        # Case 2: 重名不覆盖 → 自动加_v2
        p2 = save_markdown("另一份内容", "字节跳动", "AI产品经理", "一面", "2026-08-20", override_base_dir=tmp_dir)
        assert os.path.exists(p2) and p2 != p1
        assert "_v2.md" in p2, f"应该是v2: {p2}"
        print(f"✅ Case2 重名自动加v2 OK: {os.path.basename(p2)}")

        # Case 3: 特殊字符转义
        p3 = save_markdown("内容3", "字节/跳动:测试", "AI*产品?经理", "一面", "待定", override_base_dir=tmp_dir)
        fname3 = os.path.basename(p3)
        for ch in ILLEGAL_CHARS:
            assert ch not in fname3, f"文件名有非法字符: {fname3} 含 {ch!r}"
        assert "字节_跳动_测试" in fname3, f"转义后不对: {fname3}"
        print(f"✅ Case3 特殊字符转义 OK: {fname3}")

        # Case 4: 全空字段 → 待定占位
        p4 = save_markdown("内容4", "", "", "", "", override_base_dir=tmp_dir)
        fname4 = os.path.basename(p4)
        assert "待定_待定_待定_待定.md" in fname4 or fname4.count("待定") >= 3, f"空字段→待定失败: {fname4}"
        print(f"✅ Case4 空字段→待定 OK: {fname4}")

        # Case 5: 连续v2/v3
        p5 = save_markdown("x", "A", "B", "C", "D", override_base_dir=tmp_dir)
        p6 = save_markdown("x", "A", "B", "C", "D", override_base_dir=tmp_dir)
        p7 = save_markdown("x", "A", "B", "C", "D", override_base_dir=tmp_dir)
        assert "_v3.md" in p7, f"第三个应该是v3: {p7}"
        print(f"✅ Case5 v2/v3连续 OK: v1={os.path.basename(p5)}, v2={os.path.basename(p6)}, v3={os.path.basename(p7)}")

        print("\n文件列表:")
        for f in sorted(os.listdir(tmp_dir)):
            print(f"  - {f}")

    except AssertionError as e:
        all_pass = False
        print(f"❌ 断言失败: {e}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"\n临时目录已清理: {tmp_dir}")
        print("=== 自测结果:", "ALL PASS ✅" if all_pass else "有失败 ❌", "===")
    sys.exit(0 if all_pass else 1)
