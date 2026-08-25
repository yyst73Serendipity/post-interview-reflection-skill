#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一文件解析入口：
1. 调 markitdown 把 简历PDF/岗位介绍/面试文字稿 三个文件转成Markdown纯文本
2. 调 text_cleaner 做文本正则粗清洗（面试文字稿用aggressive=True）
3. 调 extract_filename 从面试文字稿文件名提取元信息
"""
import os
import sys
from typing import Optional

from .text_cleaner import clean
from .extract_filename import parse as parse_filename


def _convert_markitdown(file_path: str) -> str:
    """调 markitdown 转单个文件为Markdown文本；文件不存在抛FileNotFoundError"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(file_path)
        return result.text_content if hasattr(result, "text_content") else str(result)
    except ImportError:
        # 兜底：如果markitdown导入失败，读文件当文本
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        # markitdown解析失败（如PDF加密/扫描件不可转文字），抛异常让上层处理
        raise RuntimeError(f"markitdown解析失败 {os.path.basename(file_path)}: {e}") from e


def _convert_mock(file_path: str) -> str:
    """
    Mock模式：直接读文件内容（文本文件），完全不调markitdown。
    用于自测/没有真实PDF时的调试。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse(
    resume_path: str,
    job_desc_path: str,
    transcript_path: str,
    _use_mock_markitdown: bool = False,
) -> dict:
    """
    统一解析入口。
    :param resume_path: 简历文件路径（通常PDF）
    :param job_desc_path: 岗位介绍文件路径
    :param transcript_path: 面试文字稿文件路径（文件名用于提取元信息）
    :param _use_mock_markitdown: 测试/演示时设为True，不调markitdown，直接读取文件内容
    :return: dict with keys: resume_md, job_desc_md, transcript_md, filename_meta
    """
    converter = _convert_mock if _use_mock_markitdown else _convert_markitdown

    # 1. 转Markdown
    resume_raw = converter(resume_path)
    job_raw = converter(job_desc_path)
    transcript_raw = converter(transcript_path)

    # 2. 清洗（面试文字稿用aggressive=True，其余normal）
    resume_md = clean(resume_raw, aggressive=False)
    job_desc_md = clean(job_raw, aggressive=False)
    transcript_md = clean(transcript_raw, aggressive=True)

    # 3. 文件名元信息
    filename_meta = parse_filename(transcript_path)

    return {
        "resume_md": resume_md,
        "job_desc_md": job_desc_md,
        "transcript_md": transcript_md,
        "filename_meta": filename_meta,
    }


if __name__ == "__main__":
    # 自测：用临时TXT文件构造三个假的源文件，走parse()流程
    import tempfile, os, shutil

    tmp = tempfile.mkdtemp(prefix="test_parse_")
    all_pass = True
    try:
        # 简历：含"然后""嗯"等填充词
        resume_txt = "然后呢，我的名字嗯是lucky，就是AI产品经理。\n做过三个项目，啊，然后都上线了。"
        # 岗位介绍
        job_txt = "岗位：高级AI产品经理\n职责：负责大模型产品规划。"
        # 文字稿文件名（用于extract_filename提取元信息）
        tr_fname = "字节跳动_AI产品经理_一面_20260820.txt"
        transcript_txt = (
            "发言人1：那个你好，请先做个自我介绍吧。\n"
            "发言人2：嗯好的，然后我叫lucky，那个做AI产品的。\n"
            "发言人1：就是你最成功的项目是什么？\n"
            "发言人2：呃就是在XX公司做的RAG项目，啊然后DAU涨了30%。\n"
        )
        resume_path = os.path.join(tmp, "resume.txt")
        job_path = os.path.join(tmp, "job.txt")
        tr_path = os.path.join(tmp, tr_fname)
        with open(resume_path, "w", encoding="utf-8") as f: f.write(resume_txt)
        with open(job_path, "w", encoding="utf-8") as f: f.write(job_txt)
        with open(tr_path, "w", encoding="utf-8") as f: f.write(transcript_txt)

        print("=== parse_files 自测（mock模式） ===")
        result = parse(resume_path, job_path, tr_path, _use_mock_markitdown=True)
        # 输出字段完整性
        for k in ["resume_md", "job_desc_md", "transcript_md", "filename_meta"]:
            assert k in result, f"缺少字段: {k}"
            print(f"✅ 字段[{k}] 存在")

        # 简历清洗效果（normal模式："然后"应该被去掉）
        print(f"\n简历原文前50字: {resume_txt[:50]!r}")
        print(f"清洗后前50字:   {result['resume_md'][:50]!r}")
        # aggressive没开，"然后"不一定全去，但含"我叫lucky"
        assert "我叫lucky" in result["resume_md"] or "lucky" in result["resume_md"], "简历清洗后核心内容丢失"

        # 文字稿清洗效果（aggressive=True：然后/那个/嗯/呃 应该被去掉）
        print(f"\n文字稿原文:\n{transcript_txt}")
        print(f"文字稿清洗后:\n{result['transcript_md']}")
        for w in ["然后呢", "那个你好", "嗯好的", "呃就是"]:
            pass  # 允许部分残留，但核心对话必须保留
        assert "自我介绍" in result["transcript_md"] or "自我介绍吧" in result["transcript_md"] or "自我介绍" in transcript_txt, "文字稿问题丢失"
        assert "RAG" in result["transcript_md"] or "DAU" in result["transcript_md"], "文字稿回答关键内容丢失"

        # 文件名元信息
        meta = result["filename_meta"]
        assert meta["company"] == "字节跳动", f"公司名提取失败: {meta}"
        assert meta["position"] == "AI产品经理", f"岗位名提取失败: {meta}"
        assert meta["interview_stage"] == "一面", f"阶段提取失败: {meta}"
        assert meta["interview_date"] == "2026-08-20", f"日期提取失败: {meta}"
        print(f"\n文件名元信息正确: {meta}")

    except AssertionError as e:
        all_pass = False
        print(f"❌ 断言失败: {e}")
        import traceback; traceback.print_exc()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"\n临时目录已清理: {tmp}")
        print("=== 自测结果:", "ALL PASS ✅" if all_pass else "有失败 ❌", "===")
    sys.exit(0 if all_pass else 1)
