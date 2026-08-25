#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用文本清洗模块：对markitdown转出的Markdown做正则粗清洗，
去除无意义口语填充词、重复词、多余空行、乱码控制字符等。

aggressive=True 模式用于面试文字稿，加强口语词过滤力度。
"""
import re
import sys

# 高频口语填充词（非aggressive模式：要求前后有标点/空白才匹配，避免误删语义词）
FILLER_WORDS_NORMAL = [
    "然后", "那个", "嗯", "额", "呃", "啊",
    "其实", "基本上", "说实话", "好比"
]
# aggressive模式额外增加的强过滤词（更激进，可能误删少量语义，面试稿可接受）
FILLER_WORDS_AGGRESSIVE_EXTRA = [
    "那个啥", "怎么说呢", "对吧", "是吧", "嗯嗯", "呃呃", "啊啊",
    "对的对的", "是的是的", "好好好", "我我我", "你你你",
    "或者说", "就是说", "也就是说", "然后呢", "就是呢", "就是"
]


def _remove_control_chars(text: str) -> str:
    """去除控制字符（保留换行、制表、回车）"""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)


def _remove_filler_words(text: str, aggressive: bool) -> str:
    """去口语填充词"""
    words = list(FILLER_WORDS_NORMAL)
    if aggressive:
        words += FILLER_WORDS_AGGRESSIVE_EXTRA
    # 按长度倒序排列，避免短词先替换导致长词匹配失败（如"就是说"→"就是"先被替换）
    words_sorted = sorted(set(words), key=len, reverse=True)
    for w in words_sorted:
        # normal和aggressive都从任意位置删除（区别只在词表）
        pattern = re.escape(w)
        text = re.sub(pattern, "", text)
    # 清理口语词替换后留下的多标点/多空格
    text = re.sub(r"[，。,.!?？！；;：:]{2,}", lambda m: m.group(0)[-1], text)
    # 清理因删除口语词导致的行首孤立标点/空白
    text = re.sub(r"^[\s，。,.!?？！；;：:]+", "", text)
    text = re.sub(r"\n[ \t，。,.!?？！；;：:]+", "\n", text)
    return text


def _remove_duplicate_words(text: str) -> str:
    """去口吃式重复：对对对→删除（单字口吃）；这个这个这个→这个（多字保留1个）"""
    # 单字重复3+次 → 完全删除（口吃式"对对对""嗯嗯嗯"无语义）
    text = re.sub(r"([\u4e00-\u9fa5A-Za-z])\1{2,}", "", text)
    # 双字词重复2+次 → 保留1个（"这个这个"→"这个"）
    text = re.sub(r"([\u4e00-\u9fa5A-Za-z]{2})\1{1,}", r"\1", text)
    # 中文短语（2-4字）重复2+次 → 保留1个
    text = re.sub(r"([\u4e00-\u9fa5]{2,4})\1{1,}", r"\1", text)
    return text


def _merge_extra_newlines(text: str) -> str:
    """合并多余空行：3个以上换行→2个"""
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 去掉行首行尾多余空白（保留单个换行）
    lines = [ln.rstrip() for ln in text.split("\n")]
    return "\n".join(lines)


def _merge_sentence_breaks(text: str) -> str:
    """合并句子中间的意外断行：非段尾（下一行不以数字/-/#开头，且上一行不以结束标点结尾）"""
    lines = text.split("\n")
    result = []
    buffer = ""
    end_punct = set("。！？!?；;：:")
    list_starters = set("#-*0123456789")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            # 空行：先把buffer刷掉，再放空行
            if buffer:
                result.append(buffer)
                buffer = ""
            result.append("")
            continue
        # 判断是否是段落/列表/标题开头
        starts_new_para = (
            buffer == ""
            or stripped[0] in list_starters
            or stripped.startswith(("#", "##", "###", "####", "- ", "* "))
            or (len(stripped) > 2 and stripped[1] in ".、)）")  # 1. 一、 1)
        )
        # 判断buffer是否结束一个句子
        sentence_ended = buffer and buffer[-1] in end_punct

        if starts_new_para or sentence_ended:
            if buffer:
                result.append(buffer)
            buffer = stripped
        else:
            # 合并断行，中间加一个空格（中文语义其实不需要空格，但避免两个字粘一起）
            buffer = (buffer + stripped) if (not buffer or not re.search(r"[\u4e00-\u9fa5A-Za-z0-9]$", buffer) or not re.match(r"^[\u4e00-\u9fa5A-Za-z0-9]", stripped)) else (buffer + " " + stripped)
    if buffer:
        result.append(buffer)
    return "\n".join(result)


def _remove_markdown_noise(text: str) -> str:
    """移除markitdown转出的格式噪音：空标题、空表格、孤立的#"""
    # 孤立的#开头但无内容（#  后面全空白）
    text = re.sub(r"^#{1,6}\s*$", "", text, flags=re.MULTILINE)
    # 空表格行（|---|---|这种表头后面全空内容的）
    text = re.sub(r"\n\|[-:| ]{3,}\|\n(\|{0,1}\s*\|{0,1}\n){0,3}", "\n", text)
    return text


def clean(text: str, aggressive: bool = False) -> str:
    """
    对外主函数：对输入文本做完整清洗。
    :param text: 原始文本（Markdown/纯文本）
    :param aggressive: 是否加强口语清洗（面试文字稿建议True）
    :return: 清洗后文本
    """
    if not text:
        return ""
    text = _remove_control_chars(text)
    text = _remove_filler_words(text, aggressive)
    text = _remove_duplicate_words(text)
    text = _merge_sentence_breaks(text)
    text = _remove_markdown_noise(text)
    text = _merge_extra_newlines(text)
    return text.strip() + "\n"


if __name__ == "__main__":
    # 内嵌自测
    test_cases_normal = [
        ("然后然后，那个我叫lucky，嗯，就是做AI产品的。", "我叫lucky，就是做AI产品的。"),
        ("这个这个这个功能对对对就是这样的。", "这个功能就是这样的。"),
        ("第一行\n不是新段落的一行\n\n新段落", "第一行 不是新段落的一行\n\n新段落"),
    ]
    test_cases_aggressive = [
        ("怎么说呢，那个啥，说实话其实基本上就是这样对吧？", "这样？"),
    ]
    print("=== text_cleaner 自测 ===")
    all_pass = True
    for i, (inp, exp) in enumerate(test_cases_normal):
        got = clean(inp, aggressive=False).strip()
        ok = got == exp.strip()
        all_pass &= ok
        print(f"normal[{i}] {'PASS' if ok else 'FAIL'}: {repr(inp[:20])}... => {repr(got)}")
        if not ok:
            print(f"  期望: {repr(exp)}")
    for i, (inp, exp) in enumerate(test_cases_aggressive):
        got = clean(inp, aggressive=True).strip()
        ok = got == exp.strip()
        all_pass &= ok
        print(f"aggressive[{i}] {'PASS' if ok else 'FAIL'}: {repr(inp[:20])}... => {repr(got)}")
        if not ok:
            print(f"  期望: {repr(exp)}")
    print("=== 自测结果:", "ALL PASS ✅" if all_pass else "有失败 ❌", "===")
    sys.exit(0 if all_pass else 1)
