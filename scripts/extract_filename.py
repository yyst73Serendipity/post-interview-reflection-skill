#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从面试文字稿的文件名中用正则提取：公司 / 岗位 / 面试阶段 / 日期。
提取不到的字段统一填 "待定"。
"""
import os
import re
import sys

# 面试阶段关键词（按匹配优先级：长的先匹配，避免"面"先吞掉）
STAGE_TERMS = [
    "HR面", "技术面", "业务面", "交叉面", "终面",
    "一面", "二面", "三面", "四面", "五面", "六面",
    "第一轮", "第二轮", "第三轮",
    "初试", "复试",
]
# 常见大厂关键词（用于公司名辅助识别）
COMPANY_KEYWORDS = [
    "字节跳动", "今日头条", "抖音", "TikTok", "tiktok",
    "阿里巴巴", "阿里", "淘宝", "天猫", "支付宝", "蚂蚁",
    "腾讯", "微信", "QQ", "WeChat",
    "百度", "美团", "京东", "拼多多", "快手", "B站", "哔哩哔哩",
    "小米", "华为", "网易", "滴滴", "蚂蚁集团", "小红书",
    "PDD", "58同城", "携程", "去哪儿",
    "微软", "Google", "谷歌", "Meta", "亚马逊", "Apple", "苹果",
]
# 岗位关键词（用于岗位名辅助识别）
POSITION_KEYWORDS = [
    "AI产品经理", "产品经理", "产品", "PM", "pm", "AI产品", "AI PM",
    "产培生", "产品培训生", "产品运营", "运营",
    "前端", "后端", "研发", "算法", "测试", "客户端", "iOS", "Android",
    "数据分析师", "数据分析", "DS", "数据",
    "设计", "UI", "UX", "交互",
]

STAGE_VALID_VALUES = [
    "一面", "二面", "三面", "四面", "终面",
    "HR面", "技术面", "业务面", "交叉面",
]


def _basename(f: str) -> str:
    """从可能的完整路径中提取文件名（不带扩展名）"""
    base = os.path.basename(f)
    # 去掉扩展名（最多处理 .tar.gz 这种多级的，这里简单处理最后一个.）
    if "." in base:
        base_no_ext = base.rsplit(".", 1)[0]
    else:
        base_no_ext = base
    return base_no_ext


def parse(filename: str) -> dict:
    """
    :param filename: 文件名（可含路径，自动取basename）
    :return: dict with keys: company, position, interview_stage, interview_date
    """
    raw = _basename(filename)
    result = {
        "company": "待定",
        "position": "待定",
        "interview_stage": "待定",
        "interview_date": "待定",
    }

    # 1) 日期提取（优先级最高，不容易误匹配）
    # 格式 YYYY-MM-DD / YYYY/MM/DD
    m = re.search(r"(20\d{2})[-/_年](\d{1,2})[-/_月](\d{1,2})", raw)
    if m:
        y, mo, d = m.group(1), m.group(2).zfill(2), m.group(3).zfill(2)
        result["interview_date"] = f"{y}-{mo}-{d}"
    else:
        # 格式 YYYYMMDD（8位数字）
        m = re.search(r"(20\d{2})(\d{2})(\d{2})", raw)
        if m:
            y, mo, d = m.group(1), m.group(2), m.group(3)
            if 1 <= int(mo) <= 12 and 1 <= int(d) <= 31:
                result["interview_date"] = f"{y}-{mo}-{d}"

    # 2) 面试阶段提取
    for term in sorted(STAGE_TERMS, key=len, reverse=True):
        if term in raw:
            # 规范输出：第一轮→一面，初试→一面，HR面→HR面 等
            if term == "第一轮" or term == "初试":
                result["interview_stage"] = "一面"
            elif term == "第二轮" or term == "复试":
                result["interview_stage"] = "二面"
            elif term == "第三轮":
                result["interview_stage"] = "三面"
            elif term in STAGE_VALID_VALUES:
                result["interview_stage"] = term
            else:
                # 四面/五面等 → 直接取原term
                result["interview_stage"] = term
            break

    # 3) 尝试按常见分隔符切分（_ - 空格 · 等）
    # 先把日期阶段等已匹配的内容去掉，减少干扰
    clean_for_split = raw
    if m:
        clean_for_split = clean_for_split.replace(m.group(0), "")
    if result["interview_stage"] != "待定":
        # 只替换第一次出现（避免替换公司里恰好也有这个词）
        clean_for_split = clean_for_split.replace(result["interview_stage"], "", 1)
    clean_for_split = re.sub(r"面试记录|面经|面試|錄音|录音|文字稿|转写稿|transcript", "", clean_for_split, flags=re.IGNORECASE)
    # 按分隔符切
    tokens = [t for t in re.split(r"[_\-\s·\|/\\【】\[\]（）()]+", clean_for_split) if t]

    # 公司识别：优先关键词匹配；否则token[0]
    company_kw = None
    for kw in sorted(COMPANY_KEYWORDS, key=len, reverse=True):
        if kw.lower() in raw.lower():
            company_kw = kw
            break
    if company_kw:
        result["company"] = company_kw
    elif tokens:
        result["company"] = tokens[0]

    # 岗位识别：优先关键词匹配；否则token[1]（如果token数>=2）
    pos_kw = None
    for kw in sorted(POSITION_KEYWORDS, key=len, reverse=True):
        if kw.lower() in raw.lower():
            pos_kw = kw
            break
    if pos_kw:
        result["position"] = pos_kw
    elif len(tokens) >= 2:
        result["position"] = tokens[1]

    # 边界值清洗：空字符串→待定
    for k in list(result.keys()):
        if not result[k]:
            result[k] = "待定"

    # 日期格式再兜底（必须是YYYY-MM-DD或待定）
    if result["interview_date"] != "待定" and not re.match(r"^\d{4}-\d{2}-\d{2}$", result["interview_date"]):
        result["interview_date"] = "待定"
    # 阶段必须是枚举或待定
    if result["interview_stage"] != "待定" and result["interview_stage"] not in STAGE_VALID_VALUES:
        # 四面/五面/六面 也保留（合法）
        if not re.match(r"^[一二三四五六七八九十]面$", result["interview_stage"]):
            result["interview_stage"] = "待定"

    return result


if __name__ == "__main__":
    test_cases = [
        # (输入文件名, 期望结果的部分字段)
        ("字节跳动_AI产品经理_一面_20260820.pdf", {"company": "字节跳动", "position": "AI产品经理", "interview_stage": "一面", "interview_date": "2026-08-20"}),
        ("腾讯_产培生_二面_2026-08-21.docx", {"company": "腾讯", "position": "产培生", "interview_stage": "二面", "interview_date": "2026-08-21"}),
        ("阿里-AI PM-HR面-20260822.pdf", {"company": "阿里", "interview_stage": "HR面", "interview_date": "2026-08-22"}),
        ("美团面试记录0823一面.pdf", {"company": "美团", "interview_stage": "一面"}),
        ("完全没有规律的名字.txt", {}),  # 应该全是待定，不报错
        ("/绝对/路径/前缀/字节跳动_产品经理_三面_20260101.docx", {"company": "字节跳动", "position": "产品经理", "interview_stage": "三面", "interview_date": "2026-01-01"}),
    ]
    print("=== extract_filename 自测 ===")
    all_pass = True
    for fn, expect in test_cases:
        got = parse(fn)
        print(f"输入: {fn}")
        print(f"  => 输出: {got}")
        for k, v in expect.items():
            if got[k] != v:
                all_pass = False
                print(f"  ❌ 字段[{k}] 不匹配: 期望={v!r}, 实际={got[k]!r}")
            else:
                print(f"  ✅ 字段[{k}] = {got[k]!r}")
        print()
    print("=== 自测结果:", "ALL PASS ✅" if all_pass else "有失败 ❌", "===")
    sys.exit(0 if all_pass else 1)
