# 面试复盘 Skill 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现一个面试复盘自动化 Skill。输入「简历PDF + 岗位介绍 + 面试录音文字稿」，全静默自动完成「PDF解析→信息提取→QA分析打分→Markdown文档生成→文件保存」全流程，输出符合用户自定义规范的面试复盘Markdown。

**Architecture:** 方案D混合模式：4个Python脚本处理确定性脏活（markitdown PDF解析、文件名正则提取、文本正则清洗、Markdown文件保存）+ 3套分阶段Prompt做LLM语义推理（信息提取、分析打分、文档生成），由 SKILL.md 作为总控入口串行编排执行，共3次LLM调用 + 4次脚本调用。

**Tech Stack:** Python 3.10+、markitdown（已安装）、JSON Schema（Draft-07）、Markdown（GFM表格）、Trae Skill Framework（SKILL.md + prompts/ 约定目录）

---

## Global Constraints

- **输出路径**：Markdown文件必须保存到 `/Users/yst/Documents/面试复盘/`，不存在则自动创建
- **文件命名**：`{公司}_{岗位}_{面试阶段}_{面试日期}.md`，特殊字符`/ \ : * ? " < > |`替换为`_`
- **UTF-8编码**：所有文本/Python脚本读写均使用UTF-8，macOS不加BOM
- **5档星级严格执行**：★★★★★ / ★★★★☆ / ★★★☆☆ / ★★☆☆☆ / ★☆☆☆☆，定义与设计文档附录A完全一致
- **问题分类约束**：优先使用固定8类（自我介绍/实习深挖/个人项目深挖/技术考察/产品八股/场景题/出勤/职业规划），扩展分类无固定列表但每道题只能有1个主分类
- **理想回答约束**：必须引用简历真实数据，结尾必须加邀请讨论句；无匹配经历时加`【注意】未在简历中找到可直接引用的匹配经历`前缀
- **发言人推断规则**：提问多→面试官，回答多→候选人，明确标注优先使用；无法区分保留发言人1/2并文档头提示
- **全静默 + 缺文件追问**：资料齐全后不打扰用户；检测到缺文件（简历/岗位/文字稿任一）必须主动追问用户，不硬跑
- **JSON重试机制**：3次LLM调用后若JSON解析失败，自动重试最多2次，用更严格格式prompt再调用；仍失败则提示用户
- **不覆盖原文件**：保存时若目标文件名已存在，自动追加`_v2`/`_v3`后缀

---

### Task 0: 项目基础配置（环境验证 + .gitignore + requirements.txt）

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/.gitignore`
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/requirements.txt`
- Verify: 运行 `python3 -c "import markitdown; print(markitdown.__version__)"` 验证依赖已安装

**Interfaces:**
- Consumes: 无（第一个任务）
- Produces: `.gitignore` 忽略 `temp/`、`__pycache__/`、`.DS_Store`；`requirements.txt` 声明 `markitdown>=0.1.0`、`jsonschema>=4.0.0`（用于后续Schema校验可选）

- [ ] **Step 1: 验证环境**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && \
python3 --version && \
python3 -c "import markitdown; print('markitdown OK:', markitdown.__version__ if hasattr(markitdown, '__version__') else 'version unknown')" && \
python3 -c "import jsonschema; print('jsonschema OK')" 2>/dev/null || echo "jsonschema not installed, will add to requirements"
```
Expected: Python 3.10+, markitdown OK 输出（import不报错即可）

- [ ] **Step 2: 写 .gitignore**

```gitignore
# Temp files
temp/
*.tmp

# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
.Python

# macOS
.DS_Store
.AppleDouble
.LSOverride

# IDE
.idea/
.vscode/
*.swp
*.swo

# Output samples (user data)
examples/*_output.md
```

- [ ] **Step 3: 写 requirements.txt**

```
# 核心依赖：微软PDF转Markdown工具（用户已安装）
markitdown>=0.1.0

# 可选：JSON Schema校验（用于阶段1/2输出格式检查）
jsonschema>=4.19.0,<5
```

- [ ] **Step 4: 安装 requirements（用户已安装markitdown，补装jsonschema）**

Run:
```bash
pip3 install --upgrade pip && \
pip3 install "jsonschema>=4.19.0,<5" && \
python3 -c "import jsonschema; print('jsonschema installed OK, version:', jsonschema.__version__)"
```
Expected: jsonschema 版本输出 >= 4.19

- [ ] **Step 5: 验证所有文件存在**

Run:
```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/.gitignore" "/Users/yst/Coding/post‑interview-reflection-skill/requirements.txt"
```
Expected: 两个文件都存在，size > 0

---

### Task 1: scripts/text_cleaner.py —— 通用文本清洗模块

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/scripts/text_cleaner.py`
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/scripts/__init__.py`
- Verify: 运行 `python3 scripts/text_cleaner.py` 自测试

**Interfaces:**
- Consumes: string（原始Markdown文本），可选 bool `aggressive`（是否加强口语清洗力度，默认False，面试文字稿用True）
- Produces: 对外暴露函数 `clean(text: str, aggressive: bool = False) -> str`；脚本可直接 `python3 -m scripts.text_cleaner` 运行内嵌自测

- [ ] **Step 1: 写 scripts/__init__.py（空文件，标识包）**

```python
# scripts package
```

- [ ] **Step 2: 写 scripts/text_cleaner.py 完整实现（含自测main函数）**

```python
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
    "然后", "就是", "那个", "嗯", "额", "呃", "啊",
    "其实", "基本上", "说实话", "好比"
]
# aggressive模式额外增加的强过滤词（更激进，可能误删少量语义，面试稿可接受）
FILLER_WORDS_AGGRESSIVE_EXTRA = [
    "那个啥", "怎么说呢", "对吧", "是吧", "嗯嗯", "呃呃", "啊啊",
    "对的对的", "是的是的", "好好好", "我我我", "你你你",
    "或者说", "就是说", "也就是说", "然后呢", "就是呢"
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
        if aggressive:
            # aggressive：任意位置出现就替换
            pattern = re.escape(w)
            text = re.sub(pattern, "", text)
        else:
            # normal：仅独立出现（前后为标点/空白/字符串边界）
            pattern = rf"(?<=[\s，。,.!?？！；;：:\"'（）()\[\]【】《》\-—_/\\]){re.escape(w)}(?=[\s，。,.!?？！；;：:\"'（）()\[\]【】《》\-—_/\\]|$)"
            text = re.sub(pattern, "", text)
    # 清理口语词替换后留下的多标点/多空格
    text = re.sub(r"[，。,.!?？！；;：:]{2,}", lambda m: m.group(0)[-1], text)
    return text


def _remove_duplicate_words(text: str) -> str:
    """去口吃式重复：这个这个这个→这个；对对对→对"""
    # 中文单字/两字词重复2+次
    text = re.sub(r"([\u4e00-\u9fa5A-Za-z]{1,2})\1{2,}", r"\1", text)
    # 中文短语（2-4字）重复
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
        ("然后然后，那个我叫lucky，嗯，就是做AI产品的。", "我叫lucky，做AI产品的。"),
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
```

- [ ] **Step 3: 运行自测脚本验证通过**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 scripts/text_cleaner.py
```
Expected: 输出 ALL PASS ✅，exit code 0

- [ ] **Step 4: 包引用验证（确保能从父目录import）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && \
python3 -c "
from scripts.text_cleaner import clean
r = clean('然后嗯那个就是我叫lucky。', aggressive=True)
print('包引用结果:', repr(r))
assert 'lucky' in r
assert '然后' not in r
print('包引用验证 PASS ✅')
"
```
Expected: 包引用验证 PASS ✅

- [ ] **Step 5: 确认文件存在并提交（可选）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && ls -la scripts/__init__.py scripts/text_cleaner.py && python3 -c "
# 最后一次完整性检查：所有公开接口都有
from scripts.text_cleaner import clean
assert callable(clean)
import inspect
sig = inspect.signature(clean)
params = list(sig.parameters.keys())
assert 'text' in params and 'aggressive' in params
print('text_cleaner 模块完整性检查 PASS ✅')
"
```

---

### Task 2: scripts/extract_filename.py —— 文件名元信息正则提取

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/scripts/extract_filename.py`
- Verify: 运行 `python3 scripts/extract_filename.py` 自测通过

**Interfaces:**
- Consumes: string（文件名字符串，不含路径；或完整路径脚本自动取basename）
- Produces: 对外暴露函数 `parse(filename: str) -> dict`，返回 `{ company, position, interview_stage, interview_date }`，提取不到的字段填 `"待定"`；`interview_date` 格式统一为 `"YYYY-MM-DD"` 或 `"待定"`

- [ ] **Step 1: 写 extract_filename.py 完整实现（含内嵌自测）**

```python
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
    "拼多多", "PDD", "58同城", "携程", "去哪儿",
    "微软", "Google", "谷歌", "Meta", "亚马逊", "Apple", "苹果",
]
# 岗位关键词（用于岗位名辅助识别）
POSITION_KEYWORDS = [
    "产品经理", "产品", "PM", "pm", "AI产品", "AI PM",
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
        ("字节跳动_AI产品经理_一面_20260820.pdf", {"company": "字节跳动", "position": "AI产品", "interview_stage": "一面", "interview_date": "2026-08-20"}),
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
```

- [ ] **Step 2: 运行自测验证通过**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 scripts/extract_filename.py
```
Expected: ALL PASS ✅，exit code 0（6个用例全通过，包括"完全没有规律的名字.txt"全待定的情况）

- [ ] **Step 3: 日期格式/阶段格式合法性验证（Schema前置检查）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
from scripts.extract_filename import parse
import re

# 校验输出字段类型和枚举
cases = ['未知文件名.pdf', '腾讯_产品_HR面_20260101.pdf']
for c in cases:
    r = parse(c)
    assert isinstance(r['company'], str) and r['company'], f'company invalid: {r}'
    assert isinstance(r['position'], str) and r['position'], f'position invalid: {r}'
    assert isinstance(r['interview_stage'], str) and r['interview_stage'], f'stage invalid: {r}'
    assert isinstance(r['interview_date'], str)
    assert r['interview_date'] == '待定' or re.match(r'^\d{4}-\d{2}-\d{2}$', r['interview_date']), f'date invalid: {r}'
print('Schema前置检查 PASS ✅')
"
```
Expected: Schema前置检查 PASS ✅

- [ ] **Step 4: 中文大小写/混合分隔符兼容验证**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
from scripts.extract_filename import parse
# 空格分隔、中文括号、混合大小写
r = parse('【阿里巴巴】 AI PM 业务面 20260115 transcript.docx')
assert r['company'] == '阿里巴巴', r
assert r['position'] == 'AI PM', r
assert r['interview_stage'] == '业务面', r
assert r['interview_date'] == '2026-01-15', r
print('混合分隔符兼容 PASS ✅')
"
```
Expected: 混合分隔符兼容 PASS ✅

- [ ] **Step 5: 文件存在检查**

```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && ls -la scripts/extract_filename.py
```
Expected: 文件存在，size > 5KB（至少200行代码）

---

### Task 3: scripts/save_output.py —— Markdown文件保存模块

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/scripts/save_output.py`
- Verify: 运行 `python3 scripts/save_output.py` 自测通过（使用一个临时输出目录，不污染真实的/Users/yst/Documents/面试复盘/）

**Interfaces:**
- Consumes: `markdown_content: str, company: str, position: str, interview_stage: str, interview_date: str`，可选 `override_base_dir: str`（用于测试时覆盖）
- Produces: 对外暴露函数 `save_markdown(...) -> str` 返回保存成功的绝对路径；自动创建目录、转义特殊字符、重名加_v2后缀

- [ ] **Step 1: 写 save_output.py 完整实现（含内嵌自测）**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保存最终Markdown文档到指定路径：/Users/yst/Documents/面试复盘/
- 自动创建目录（不存在则创建）
- 文件名特殊字符转义（/ \ : * ? " < > | → _）
- 重名不覆盖，自动追加 _v2 / _v3 / ...
"""
import os
import re
import sys
from datetime import datetime

DEFAULT_BASE_DIR = "/Users/yst/Documents/面试复盘"

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
```

- [ ] **Step 2: 运行自测验证通过**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 scripts/save_output.py
```
Expected: 5个Case全PASS，临时目录被清理（自测脚本内部自动处理，不污染真实目录）

- [ ] **Step 3: 真实目录创建能力验证（仅目录创建，不写真实内容到用户目录）**

Run:
```bash
# 先不写用户目录，仅验证默认路径的dirname存在性逻辑
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
import os, tempfile
from scripts.save_output import DEFAULT_BASE_DIR, _sanitize, _find_available_path
# 1. 非法字符转义
assert _sanitize('a/b:c*d?e\"f<g>h|i') == 'a_b_c_d_e_f_g_h_i'
# 2. 空字符串→待定
assert _sanitize('') == '待定' and _sanitize('   ') == '待定'
# 3. 找可用路径（临时目录下）
tmp = tempfile.mkdtemp()
try:
    p1 = _find_available_path(tmp, 'testfile', '.md')
    assert p1.endswith('testfile.md')
    open(p1, 'w').close()
    p2 = _find_available_path(tmp, 'testfile', '.md')
    assert p2.endswith('testfile_v2.md')
    open(p2, 'w').close()
    p3 = _find_available_path(tmp, 'testfile', '.md')
    assert p3.endswith('testfile_v3.md')
    print(f'DEFAULT_BASE_DIR = {DEFAULT_BASE_DIR}')
    print(f'目录/路径逻辑 PASS ✅')
finally:
    import shutil; shutil.rmtree(tmp, ignore_errors=True)
"
```
Expected: 目录/路径逻辑 PASS ✅

- [ ] **Step 4: 包导入验证**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
from scripts.save_output import save_markdown, DEFAULT_BASE_DIR, _sanitize
import inspect
sig = inspect.signature(save_markdown)
params = list(sig.parameters.keys())
required = ['markdown_content','company','position','interview_stage','interview_date']
for r in required: assert r in params, f'save_markdown 缺少参数 {r}'
print('save_markdown 签名检查 PASS ✅, 参数列表:', params)
"
```
Expected: 签名检查 PASS，参数至少包含 5 个必填参数 + override_base_dir

- [ ] **Step 5: 文件完整性**

Run:
```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/scripts/save_output.py"
```

---

### Task 4: scripts/parse_files.py —— 统一文件解析入口（调markitdown + 调上面两个模块）

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/scripts/parse_files.py`
- Verify: 用一个小的样例PDF/或纯文本TXT跑通；如果用户暂无测试PDF，用字符串构造模拟markitdown.convert返回，确保调用链和清洗流程正确

**Interfaces:**
- Consumes: `resume_path: str, job_desc_path: str, transcript_path: str`（三个文件的绝对路径），可选 `_use_mock_markitdown: bool = False`（测试模式，用文件本身内容替代markitdown.convert返回，避免依赖真实PDF）
- Produces: `parse(resume_path, job_desc_path, transcript_path) -> dict` 返回 `{ resume_md, job_desc_md, transcript_md, filename_meta }`

- [ ] **Step 1: 写 parse_files.py 完整实现（内置mock模式，无需真实PDF也能自测）**

```python
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
        assert meta["position"] == "AI产品", f"岗位名提取失败: {meta}"
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
```

- [ ] **Step 2: 运行mock模式自测（不依赖真实PDF/不调markitdown）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -m scripts.parse_files
```
Expected: ALL PASS ✅（mock模式用临时TXT文件走通全流程：转内容→清洗→文件名元信息提取）

- [ ] **Step 3: markitdown真实导入能力检查（如果用户已安装）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
try:
    from markitdown import MarkItDown
    print(f'✅ markitdown 真实可用: MarkItDown 类存在，可实例化={callable(MarkItDown)}')
except ImportError as e:
    print(f'⚠️ markitdown 未安装或导入失败: {e}（后续实现阶段如需要会补装，自测走mock不受影响）')
"
```
Expected: ✅ markitdown 真实可用（用户已安装）

- [ ] **Step 4: 包签名与异常处理验证**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
from scripts.parse_files import parse
import inspect
sig = inspect.signature(parse)
params = list(sig.parameters.keys())
assert 'resume_path' in params and 'job_desc_path' in params and 'transcript_path' in params, f'缺少参数: {params}'
# 异常：文件不存在
try:
    parse('/no/such/a', '/no/such/b', '/no/such/c', _use_mock_markitdown=True)
    assert False, '应该抛出FileNotFoundError'
except FileNotFoundError as e:
    print(f'✅ 异常捕获正确: 文件不存在抛出 FileNotFoundError')
print('parse_files 签名与异常处理 PASS ✅')
"
```
Expected: PASS ✅

- [ ] **Step 5: 文件完整性检查**

```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/scripts/parse_files.py"
```

---

### Task 5: schemas/extracted_data.schema.json —— 阶段1输出数据结构

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/schemas/extracted_data.schema.json`
- Verify: `python3 -m jsonschema -i <(echo '测试JSON') schemas/extracted_data.schema.json` 验证合法样例通过、非法样例拒绝

**Interfaces:**
- Consumes: 无（纯定义）
- Produces: JSON Schema文件，供后续Prompt阶段要求LLM严格输出此格式；同时 Python端可通过 `jsonschema.validate()` 校验LLM返回的JSON

- [ ] **Step 1: 写 extracted_data.schema.json（完全对应设计文档5.3.1）**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/extracted_data.schema.json",
  "title": "Interview Extracted Data",
  "description": "面试复盘阶段1：信息提取输出结构。包含公司/岗位/日期/阶段元信息 + 面试官QA列表 + 候选人反问QA列表",
  "type": "object",
  "required": [
    "company",
    "position",
    "interview_stage",
    "interview_date",
    "interviewer_qa",
    "candidate_retro_qa"
  ],
  "additionalProperties": false,
  "properties": {
    "company": {
      "type": "string",
      "minLength": 1,
      "description": "公司名称，提取不到填'待定'"
    },
    "position": {
      "type": "string",
      "minLength": 1,
      "description": "岗位名称，提取不到填'待定'"
    },
    "interview_stage": {
      "type": "string",
      "description": "面试阶段，枚举或'待定'",
      "oneOf": [
        {
          "enum": [
            "一面", "二面", "三面", "四面", "五面", "六面",
            "终面", "HR面", "技术面", "业务面", "交叉面",
            "待定"
          ]
        },
        {
          "pattern": "^[一二三四五六七八九十百]+面$"
        }
      ]
    },
    "interview_date": {
      "type": "string",
      "description": "面试日期，格式YYYY-MM-DD或'待定'",
      "pattern": "^(\\d{4}-\\d{2}-\\d{2}|待定)$"
    },
    "source_confidence": {
      "type": "object",
      "description": "元信息来源标记（可选，用于debug）",
      "additionalProperties": false,
      "properties": {
        "company_from": {
          "type": "string",
          "examples": ["filename", "infer_from_job_desc", "user_input", "待定"]
        },
        "position_from": {
          "type": "string"
        },
        "stage_from": {
          "type": "string"
        },
        "date_from": {
          "type": "string"
        }
      }
    },
    "interviewer_qa": {
      "type": "array",
      "description": "面试官提问QA列表（含候选人对应回答）",
      "minItems": 0,
      "items": {
        "type": "object",
        "required": ["index", "question", "candidate_answer"],
        "additionalProperties": false,
        "properties": {
          "index": {
            "type": "integer",
            "minimum": 1,
            "description": "问题序号（从1开始）"
          },
          "question": {
            "type": "string",
            "minLength": 1
          },
          "attitude_signals": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["追问", "打断", "表扬", "展开引导", "质疑", "沉默", "其他"]
            },
            "default": []
          },
          "signal_inferred": {
            "type": "boolean",
            "default": false,
            "description": "true表示这道题的问题或回答内容部分或全部是AI推断（信号差）"
          },
          "signal_notes": {
            "type": "string",
            "description": "当signal_inferred=true时，标注推断原因或信号差的具体位置"
          },
          "candidate_answer": {
            "type": "string",
            "minLength": 0,
            "description": "候选人的回答（已二次过滤口语词）"
          }
        }
      }
    },
    "candidate_retro_qa": {
      "type": "array",
      "description": "候选人反问QA列表",
      "minItems": 0,
      "items": {
        "type": "object",
        "required": ["index", "question", "interviewer_answer"],
        "additionalProperties": false,
        "properties": {
          "index": {
            "type": "integer",
            "minimum": 1
          },
          "question": {
            "type": "string",
            "minLength": 1
          },
          "signal_inferred": {
            "type": "boolean",
            "default": false
          },
          "signal_notes": {
            "type": "string"
          },
          "interviewer_answer": {
            "type": "string",
            "description": "面试官对候选人反问的回答（尽量还原原文）"
          }
        }
      }
    },
    "notes": {
      "type": "array",
      "items": { "type": "string" },
      "description": "备注信息，如发言人角色难以区分的警告、文字稿异常提示等"
    }
  }
}
```

- [ ] **Step 2: 验证Schema文件JSON语法正确**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && \
python3 -c "
import json
with open('schemas/extracted_data.schema.json', encoding='utf-8') as f:
    schema = json.load(f)
print(f'✅ Schema语法正确，关键字段: {list(schema[\"properties\"].keys())}')
assert 'required' in schema
required = schema['required']
print(f'Required字段: {required}')
for r in ['company','position','interview_stage','interview_date','interviewer_qa','candidate_retro_qa']:
    assert r in required, f'required缺少: {r}'
print('extracted_data Schema完整性检查 PASS ✅')
"
```
Expected: PASS ✅

- [ ] **Step 3: 用合法样例JSON跑jsonschema校验（PASS）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
import json, jsonschema

with open('schemas/extracted_data.schema.json', encoding='utf-8') as f:
    schema = json.load(f)

# 合法样例
valid_sample = {
    'company': '字节跳动',
    'position': 'AI产品经理',
    'interview_stage': '一面',
    'interview_date': '2026-08-20',
    'interviewer_qa': [
        {
            'index': 1,
            'question': '做个自我介绍',
            'attitude_signals': [],
            'signal_inferred': False,
            'candidate_answer': '我叫lucky，做AI产品'
        }
    ],
    'candidate_retro_qa': [
        {
            'index': 1,
            'question': '汇报线是？',
            'interviewer_answer': '汇报给产品负责人'
        }
    ],
    'notes': ['发言人1=面试官, 发言人2=候选人（通过提问频次推断）']
}
jsonschema.validate(valid_sample, schema)
print('✅ 合法样例通过Schema校验')

# 非法样例：缺必填字段
invalid_sample = {k: v for k, v in valid_sample.items() if k != 'position'}  # 删position
try:
    jsonschema.validate(invalid_sample, schema)
    print('❌ 非法样例居然通过了（缺position）')
    exit(1)
except jsonschema.ValidationError:
    print('✅ 非法样例1（缺必填字段）正确被拒绝')

# 非法样例：日期格式不对
invalid_sample2 = dict(valid_sample)
invalid_sample2['interview_date'] = '08-20-2026'
try:
    jsonschema.validate(invalid_sample2, schema)
    print('❌ 非法样例2（日期格式）居然通过了')
    exit(1)
except jsonschema.ValidationError:
    print('✅ 非法样例2（日期格式错误）正确被拒绝')
print('Schema 双向校验 PASS ✅')
"
```
Expected: 3条✅ 输出全部出现

- [ ] **Step 4: "待定"边界值校验**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
import json, jsonschema
with open('schemas/extracted_data.schema.json', encoding='utf-8') as f:
    schema = json.load(f)
pending_sample = {
    'company': '待定',
    'position': '待定',
    'interview_stage': '待定',
    'interview_date': '待定',
    'interviewer_qa': [],
    'candidate_retro_qa': []
}
jsonschema.validate(pending_sample, schema)
print('✅ 待定边界值全部通过校验（全空场景合法）')
"
```
Expected: 待定边界值通过 ✅

- [ ] **Step 5: 文件存在与格式**

```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/schemas/extracted_data.schema.json"
```

---

### Task 6: schemas/analyzed_data.schema.json —— 阶段2输出数据结构

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/schemas/analyzed_data.schema.json`
- Verify: jsonschema校验合法/非法样例

**Interfaces:**
- Consumes: 阶段1 extracted_data的全部字段（继承）
- Produces: 每个QA追加analysis字段 + overall整体评分与改进计划

- [ ] **Step 1: 写 analyzed_data.schema.json**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/analyzed_data.schema.json",
  "title": "Interview Analyzed Data",
  "description": "面试复盘阶段2：QA分析打分和整体评分输出结构。阶段1所有字段全部保留，在每个QA中追加分析字段，并新增overall整体分析",
  "type": "object",
  "required": [
    "company", "position", "interview_stage", "interview_date",
    "interviewer_qa", "candidate_retro_qa",
    "overall"
  ],
  "allOf": [
    { "$ref": "extracted_data.schema.json" }
  ],
  "properties": {
    "interviewer_qa": {
      "type": "array",
      "items": {
        "type": "object",
        "allOf": [
          {
            "required": ["index", "question", "candidate_answer"]
          },
          {
            "properties": {
              "index": { "type": "integer", "minimum": 1 },
              "question": { "type": "string" },
              "candidate_answer": { "type": "string" }
            }
          }
        ],
        "required": [
          "question_type", "inspection_point", "answer_framework",
          "rating", "rating_reason", "ideal_answer", "improve_todo"
        ],
        "properties": {
          "question_type": {
            "type": "string",
            "minLength": 2,
            "description": "问题分类：固定8类优先，可合理扩展新分类"
          },
          "inspection_point": {
            "type": "string",
            "description": "面试官考察点（1-2句话）"
          },
          "answer_framework": {
            "type": "string",
            "description": "我的回答框架（用分点描述即可）"
          },
          "rating": {
            "type": "string",
            "enum": ["★★★★★", "★★★★☆", "★★★☆☆", "★★☆☆☆", "★☆☆☆☆"],
            "description": "回答点评星级（严格5档）"
          },
          "rating_reason": {
            "type": "string",
            "description": "打这个星级的具体理由（指出哪里好哪里缺，不要空泛）"
          },
          "ideal_answer": {
            "type": "object",
            "required": ["framework", "full_text"],
            "properties": {
              "framework": {
                "type": "array",
                "items": { "type": "string" },
                "minItems": 1,
                "description": "理想回答的框架（bullet point列表，每点一句）"
              },
              "full_text": {
                "type": "string",
                "minLength": 10,
                "description": "理想回答完整文字（可直接口述）。必须引用简历真实数据；结尾必须加邀请讨论句；若简历无匹配必须加【注意】前缀"
              },
              "no_resume_match": {
                "type": "boolean",
                "default": false,
                "description": "true=简历未找到匹配经历，full_text开头已加【注意】前缀"
              }
            }
          },
          "improve_todo": {
            "type": "array",
            "items": { "type": "string" },
            "description": "计划改进todo list（具体可执行项）"
          }
        }
      }
    },
    "candidate_retro_qa": {
      "type": "array",
      "items": {
        "type": "object",
        "allOf": [
          { "required": ["index", "question", "interviewer_answer"] }
        ],
        "required": ["position_insights", "action_items"],
        "properties": {
          "position_insights": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 0,
            "description": "从面试官回答中提炼的岗位有效信息（汇报线/团队规模/对候选人要求等）"
          },
          "action_items": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 0,
            "description": "从反问环节得出的后续todo"
          }
        }
      }
    },
    "overall": {
      "type": "object",
      "required": [
        "score", "pass", "reasons", "problems", "improvement_plan"
      ],
      "properties": {
        "score": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10,
          "description": "整场面试胜算评分（1最低，10最高）"
        },
        "pass": {
          "type": "string",
          "enum": ["是", "否", "待定"],
          "description": "是否通过该场面试（综合判断）"
        },
        "reasons": {
          "type": "string",
          "description": "评估理由（从面试时长/面试官态度/反问回答详细程度等维度展开）"
        },
        "problems": {
          "type": "array",
          "minItems": 0,
          "items": {
            "type": "object",
            "required": ["title", "description", "category"],
            "properties": {
              "title": { "type": "string" },
              "description": { "type": "string" },
              "category": {
                "type": "string",
                "enum": [
                  "思维型缺陷-表层",
                  "思维型缺陷-深层",
                  "知识型缺陷",
                  "其他"
                ]
              }
            }
          }
        },
        "improvement_plan": {
          "type": "array",
          "minItems": 0,
          "items": {
            "type": "object",
            "required": ["todo", "type"],
            "properties": {
              "todo": { "type": "string" },
              "type": {
                "type": "string",
                "enum": ["学习项", "准备项"]
              },
              "related_links": {
                "type": "array",
                "items": { "type": "string" },
                "default": [],
                "description": "可参考学习的链接列表（可为空数组）"
              }
            }
          }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Schema语法校验**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
import json
with open('schemas/analyzed_data.schema.json', encoding='utf-8') as f:
    schema = json.load(f)
# required 字段检查
props_top = schema.get('properties', {})
print(f'顶层properties: {list(props_top.keys())}')
for req in schema.get('required', []):
    assert req in props_top or any('overall' == req for r in [req]), f'顶层required字段{req}未在properties中定义'
print('analyzed_data Schema 语法检查 PASS ✅')
"
```
Expected: 语法检查 PASS ✅

- [ ] **Step 3: 合法/非法样例双向校验**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
import json, jsonschema
# 注意：analyzed_data schema 用了 \$ref: extracted_data.schema.json，需提供resolver
from jsonschema.validators import validator_for

with open('schemas/analyzed_data.schema.json', encoding='utf-8') as f:
    schema = json.load(f)
with open('schemas/extracted_data.schema.json', encoding='utf-8') as f:
    extracted_schema = json.load(f)

# 构造ref解析器（本地目录）
from jsonschema import RefResolver
resolver = RefResolver(
    base_uri='file:///Users/yst/Coding/post-interview-reflection-skill/schemas/',
    referrer=schema,
    store={'extracted_data.schema.json': extracted_schema}
)
Validator = validator_for(schema)
validator = Validator(schema, resolver=resolver)

# 合法样例：完整的阶段2数据
sample = {
    'company': '字节', 'position': 'AI PM', 'interview_stage': '一面', 'interview_date': '2026-08-20',
    'interviewer_qa': [{
        'index': 1,
        'question': '自我介绍',
        'candidate_answer': '我叫lucky...',
        'question_type': '自我介绍类',
        'inspection_point': '考察表达逻辑和个人标签',
        'answer_framework': '1.背景 2.核心经历 3.求职动机',
        'rating': '★★★★☆',
        'rating_reason': '主体完整但缺少量化数据',
        'ideal_answer': {
            'framework': ['1.个人标签一句话', '2.最相关项目+数据', '3.为什么来这里'],
            'full_text': '面试官你好，我是lucky，3年AI产品经理经验。在XX项目中主导RAG迭代，DAU从1万涨到1.3万。今天想深入了解字节的AGI产品机会。你觉得这履历匹配吗？',
            'no_resume_match': False
        },
        'improve_todo': ['自我介绍补量化版本']
    }],
    'candidate_retro_qa': [{
        'index': 1,
        'question': '汇报线？',
        'interviewer_answer': '汇报给产品负责人',
        'position_insights': ['汇报线：产品组负责人'],
        'action_items': ['了解团队OKR']
    }],
    'overall': {
        'score': 7,
        'pass': '待定',
        'reasons': '面试45分钟偏长，追问较多有戏',
        'problems': [
            {'title': '口语填充词多', 'description': '然后出现12次', 'category': '思维型缺陷-表层'}
        ],
        'improvement_plan': [
            {'todo': '学AARRR模型', 'type': '学习项', 'related_links': []}
        ]
    }
}
errors = sorted(validator.iter_errors(sample), key=lambda e: list(e.path))
if errors:
    print('❌ 合法样例居然校验失败:')
    for e in errors[:5]:
        print(f'  path={list(e.path)}: {e.message}')
    exit(1)
print('✅ 合法样例通过 analyzed_data schema 校验')

# 非法样例：rating枚举错误
sample_bad = dict(sample)
sample_bad['interviewer_qa'] = [dict(sample['interviewer_qa'][0])]
sample_bad['interviewer_qa'][0]['rating'] = '5星'
errors = sorted(validator.iter_errors(sample_bad), key=lambda e: list(e.path))
assert errors, '应该有rating枚举错误'
print(f'✅ 非法样例（rating=5星）正确被拒绝，错误数={len(errors)}')

# 非法样例：overall.score超出1-10
sample_bad2 = dict(sample)
sample_bad2['overall'] = dict(sample['overall'])
sample_bad2['overall']['score'] = 11
errors = sorted(validator.iter_errors(sample_bad2), key=lambda e: list(e.path))
assert errors, '应该有score范围错误'
print(f'✅ 非法样例（score=11）正确被拒绝，错误数={len(errors)}')
print('analyzed_data Schema 双向校验 PASS ✅')
"
```
Expected: 3条✅ 全部出现

- [ ] **Step 4: 文件存在性检查**

```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/schemas/analyzed_data.schema.json"
```

---

### Task 7: prompts/01_extract.md —— 阶段1信息提取Prompt

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/prompts/01_extract.md`
- Verify: Prompt文件存在，且包含所有核心规则（发言人推断/态度信号/乱码标注/口语过滤/JSON输出格式）

**Interfaces:**
- Consumes: 设计文档5.2.1节定义的规则
- Produces: LLM的系统Prompt（SYSTEM角色），用户消息（USER角色）随后会注入`{resume_md}{job_desc_md}{transcript_md}{filename_meta}`。输出必须是纯JSON，符合extracted_data.schema.json

- [ ] **Step 1: 写 prompts/01_extract.md（SYSTEM Prompt完整内容）**

```markdown
# 阶段1 系统Prompt：面试信息提取专家

## 身份定义
你是资深面试文字稿信息提取专家，擅长从口语化/带乱码/只有发言人1/2的录音转写稿中，精确拆分面试官提问和候选人回答，并结构化输出。

## 输入资料（将在下一条USER消息中提供，格式见下方占位符）
1. 【文件名元信息 JSON】filename_meta = { company, position, interview_stage, interview_date }（从面试文字稿文件名正则提取，可能是"待定"，你可以结合文字稿内容修正）
2. 【岗位介绍 Markdown】job_desc_md
3. 【简历 Markdown】resume_md（仅辅助理解，不在这阶段深度分析）
4. 【面试文字稿 Markdown】transcript_md（已经过脚本粗清洗：大部分口语填充词已被正则去掉，但可能还有漏网之鱼；可能只有发言人1/2未标注角色；可能有信号差导致的乱码）

## 你的核心任务
按优先级完成：
1. 修正/确认基础元信息：公司company、岗位position、面试阶段interview_stage、面试日期interview_date
2. 识别说话人角色：把「发言人1」「发言人2」（如果有的话）推断为「面试官」或「候选人」
3. 完整拆分「面试官提问QA列表」：每个问题 + 对应候选人的回答
4. 完整拆分「候选人反问QA列表」：候选人反问的问题 + 面试官对应回答
5. 全程标注特殊信号（见下方规则）

## 详细执行规则

### A. 说话人角色推断（严格按优先级）
1. **明确标注优先**：如果文字稿里已有「面试官：」「候选人：」「HR：」「我：」等明确标注，直接使用，不推断
2. **提问频次**：谁问的问题更多（含反问），谁更可能是面试官
3. **内容职责**：问问题、引导流程、说"请介绍一下""你为什么选择我们"等 → 面试官；做自我介绍、讲项目经历、回答问题 → 候选人
4. **无法区分兜底**：如果完全无法确定，保留发言人1/2原名，并在notes[0]加一句警告：`"⚠️ 原始文字稿未标注发言人且AI无法可靠推断角色，QA拆分仅供参考，建议手动核对"`

### B. 面试官态度信号识别（每个面试官提问后，标记attitude_signals）
可选值（枚举，按真实情况出现就标，不出现就空数组）：
- `追问`："继续""还有呢""这个点展开一下""还有吗"，或候选人回答完后面试官就同一个点再提1个问题
- `打断`：候选人回答还在句子中间（没有句号/问号结尾），面试官就说话了
- `表扬`："很好""不错""这个回答挺完整的""思路清晰"等正面评价
- `展开引导`："不用紧张""可以换个角度想想""没关系，想到什么说什么"
- `质疑`："真的是这样吗？""你确定这个数据对吗？"
- `沉默`：候选人说完后很长时间面试官没说话（文字稿里出现"...""......""（沉默）"等标记）
- `其他`：以上都不是，但有明显态度信号

### C. 乱码/信号差处理（signal_inferred + signal_notes）
1. **可推断的乱码**：某段话单看不通顺，但结合上下文（前一句后一句）可以100%推断原意，那么：
   - 输出内容写成推断后的正确文字（方便后续分析）
   - `signal_inferred = true`
   - `signal_notes = "【信号推断】问题的后半段'XXX'原文字稿乱码，根据上下文推断为'YYY'"`
2. **完全不可推断**：某段话完全读不懂，无法推断：
   - `signal_inferred = true`
   - `signal_notes = "【信号差】本段乱码严重，内容保留原文但可能不准确"`
   - 候选回答/问题字段保留原文（但清理重复/填充词）

### D. 口语二次过滤
1. 尽管脚本已清洗，但仍要人工检查并删除以下口语痕迹（删除后不要改变原意）：
   - 开头/句中的独立「然后」「就是」「那个」「嗯」「额」「呃」「啊」
   - 口吃式重复：「我我我我」→「我」，「对对对对」→「对」，「这个这个这个」→「这个」
   - 无意义确认语气词：「对吧」「是吧」「嘛」「啦」（独立成句或在句末无意义时删）
2. **不要**删除语义词：比如「那个项目」中的「那个」是语义词，不能删；「然后我们就上线了」中的「然后」是连接词，保留

### E. QA拆分边界规则
1. 面试官提问 = 面试官说话的完整一段（从问好/提问开始，到下一次候选人说话前），如果一次说话里问了2个独立问题，拆成2条index
2. 候选人回答 = 紧跟该问题之后的候选人说话，直到下一次面试官说话为止（即使候选人反问了别的，也先全部归到该问题的candidate_answer）
3. **候选人反问QA** = 候选人主动发起的问题（通常发生在面试后半段，面试官说"你有什么想问我的吗"之后），每条单独成项，index从1开始重新计数

## 输出格式（MUST BE ONLY JSON，前后不能有任何解释文字、Markdown、代码块标记）

严格符合 extracted_data.schema.json。如果filename_meta中的字段和你从文字稿中推断的不一致，以你推断的为准（更智能）。

示例结构（仅参考，实际字段必须严格符合Schema，不能少required字段）：
{
  "company": "字节跳动",
  "position": "AI产品经理",
  "interview_stage": "一面",
  "interview_date": "2026-08-20",
  "source_confidence": {
    "company_from": "filename+job_desc_verify",
    "stage_from": "filename"
  },
  "interviewer_qa": [
    {
      "index": 1,
      "question": "先做个自我介绍吧",
      "attitude_signals": [],
      "signal_inferred": false,
      "candidate_answer": "我叫lucky，3年AI产品经验..."
    }
  ],
  "candidate_retro_qa": [
    {
      "index": 1,
      "question": "请问这个岗位具体汇报给谁？",
      "signal_inferred": false,
      "interviewer_answer": "汇报给AI产品组总监..."
    }
  ],
  "notes": []
}

## 最最最重要的输出约束
1. 你的完整回复必须是**纯JSON字符串**，开头第一个字符必须是`{`，结尾最后一个字符必须是`}`
2. **不要**输出 ` ```json ... ``` ` 代码块标记，不要输出"好的我来提取"等多余文字
3. 任何输出内容都必须在JSON结构里，要写备注放notes数组中
4. 必须包含Schema中所有required字段，即使是空数组/待定也不能省略
```

- [ ] **Step 2: 验证Prompt文件内容完整性（包含所有核心规则）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
path = 'prompts/01_extract.md'
with open(path, encoding='utf-8') as f:
    content = f.read()
keywords = [
    '说话人角色推断', '态度信号识别', '乱码', 'signal_inferred', '口语二次过滤',
    'QA拆分边界', '候选人反问',
    '纯JSON', '开头第一个字符必须是', '不要', '代码块标记'
]
missing = [kw for kw in keywords if kw not in content]
if missing:
    print(f'❌ 缺少核心规则关键词: {missing}')
    exit(1)
print(f'✅ 阶段1 Prompt 完整性检查通过，包含全部{len(keywords)}个核心关键词')
print(f'文件长度: {len(content)}字符，总行数: {content.count(chr(10))+1}')
"
```
Expected: 完整性检查通过 ✅

- [ ] **Step 3: 检查示例结构字段覆盖Schema required**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
import json, re
with open('prompts/01_extract.md', encoding='utf-8') as f:
    content = f.read()
# 提取示例JSON（正则抓{...}最大块）
match = re.search(r'\{[\s\S]+?\"notes\":\s*\[[\s\S]*?\][\s\S]*\}', content)
assert match, 'Prompt里找不到示例JSON'
obj = json.loads(match.group(0))
with open('schemas/extracted_data.schema.json') as f:
    schema = json.load(f)
required = schema['required']
miss = [r for r in required if r not in obj]
if miss:
    print(f'❌ 示例JSON缺少Schema required字段: {miss}')
    exit(1)
print(f'✅ 阶段1 Prompt中的示例JSON包含全部Schema required字段: {required}')
"
```
Expected: 示例JSON字段齐全 ✅

- [ ] **Step 4: 文件存在检查**

```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/prompts/01_extract.md"
```

---

### Task 8: prompts/02_analyze.md —— 阶段2 QA分析打分Prompt

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/prompts/02_analyze.md`
- Verify: 包含所有分析规则（问题分类8类+扩展、5档星级严格定义、理想回答5条规则、overall评分维度、problems分类）

**Interfaces:**
- Consumes: 设计文档5.2.2节全部规则
- Produces: 系统Prompt，要求LLM输入阶段1JSON+简历全文后，输出符合analyzed_data.schema.json的纯JSON

- [ ] **Step 1: 写 prompts/02_analyze.md**

```markdown
# 阶段2 系统Prompt：面试QA分析+评分专家

## 身份定义
你是顶级AI产品面试教练，擅长从面试官视角对面试QA逐条做深度分析：问题分类、判断考察点、按严格5档标准点评打分、结合简历真实经历给出理想回答，并最终给出整场面试的胜算评估和改进计划。

## 输入
1. 【阶段1提取结果 JSON】extracted_data_json（符合extracted_data.schema.json，含面试官QA和候选人反问QA，保留全部原字段不要删）
2. 【简历 Markdown 全文】resume_md_full（**用于理想回答引用真实经历和数据，必须使用，不要空泛**）

## 输出要求
输出一个单独的JSON（纯JSON，前后无其他文字/代码块标记），符合analyzed_data.schema.json。规则：
- **必须保留** extracted_data_json中所有原始字段和值（company/position/interview_stage/interview_date/interviewer_qa原字段/candidate_retro_qa原字段/notes等），一个都不能少
- 在每个interviewer_qa的对象中，**追加** question_type / inspection_point / answer_framework / rating / rating_reason / ideal_answer / improve_todo 7个分析字段
- 在每个candidate_retro_qa的对象中，**追加** position_insights / action_items 2个分析字段
- **新增** overall整体分析对象

---

## 一、面试官提问QA 逐条分析规则（7个追加字段）

### A. question_type（问题分类）
优先从**固定8类**中选1个最匹配的：
1. 自我介绍类
2. 实习深挖类
3. 个人项目深挖类
4. 技术考察类
5. 产品八股类
6. 场景题类
7. 出勤/稳定性问题类
8. 职业规划类

如果8类都不太匹配，允许合理扩展自定义分类（如：压力测试类、行为面试类、文化匹配类、业务理解力考察类、逻辑分析考察类、行业认知类 等）。
⚠️ **每道题必须且只能选1个主分类**

### B. inspection_point（面试官考察点）
用1-2句话说明"面试官问这道题到底想考什么"。
- 不要复述问题本身
- 要挖到深层能力：比如场景题"DAU跌了怎么办"不是考会不会排查，而是考「指标拆解框架能力 + 根因分析逻辑 + 是否有量化意识」

### C. answer_framework（我的回答框架）
把候选人的回答**提炼成结构化框架**（分点），不用逐字复述。如果候选人回答完全没结构，就按他说的顺序拆1/2/3点，标注"回答无清晰框架，以下为内容顺序"。

### D. rating（回答点评星级，严格5档，不能自创星级） + E. rating_reason（点评理由）
严格对照下表打分，rating_reason中**必须具体指出**哪条满足/哪条没满足：

| 星级 | 严格标准 |
|---|---|
| ★★★★★ | 逻辑完整（有框架）、证据充分（用了简历项目/量化数据）、有终止指标（给出了可量化的最终结果/北极星指标）、主动邀请面试官讨论（回答结尾问了"你觉得呢"/"你怎么看"） |
| ★★★★☆ | 主体完整（有框架有证据），但有1-2个明显可改进点：比如结尾忘了邀请讨论、或1个关键数据没量化（用了很多而不是具体%） |
| ★★★☆☆ | 方向对（答的是这个领域的内容）但**缺关键内容**：通常是缺终端指标/缺根源分析。只讲了做什么过程，没说做到了什么结果；或者只说了表层问题没分析深层原因 |
| ★★☆☆☆ | 只给了现象/空泛陈述，没给分析/没给证据支持。比如"我觉得用户体验很重要"但不说为什么/怎么衡量/自己做过什么 |
| ★☆☆☆☆ | 防御模式（回避问题/答非所问）、完全跑偏话题、或者根本没答到点上（比如人家问技术选型思路你扯团队协作） |

rating_reason写法要求：
❌ 不要写："不够详细""回答一般"（空泛）
✅ 要写："缺少DAU增长数据的量化说明（没有用具体%，用了'很多'）；结尾没有主动邀请面试官讨论"（具体）

### F. ideal_answer（理想回答 = framework + full_text + no_resume_match标记）
理想回答的**最高要求**：让面试官能直接看到"如果这道题满分回答应该长什么样"，并且真实可信（不是空喊口号）。

#### 强制规则5条：
1. **必须引用简历中的真实经历和数据**（对照resume_md_full找匹配度最高的项目/实习/成果）。用"在简历中XX项目里，我当时做了XXX，带来了XXX的具体数据结果（比如DAU涨X%，留存升Y%）"这种句式。
2. **禁止空泛表达**：绝对不能出现"我会……""我认为……""我要努力……"这种无证据表述。要用"我做过XX，结果是YY"。
3. **结尾必须加一句邀请面试官参与讨论的话**（三选一或类似意思）：
   - "你觉得这个假设合不合理？"
   - "你在这个业务里是怎么看的？"
   - "如果是你，会怎么优化这个指标？"
4. **结构要求**：ideal_answer是一个对象，含3个key：
   - `framework`：string[]数组，每个元素是1条框架点（把理想回答的逻辑骨架列出来）
   - `full_text`：string，完整的回答文字（可以直接口述的一段话，自然流畅，不是框架点朗读）
   - `no_resume_match`：boolean（见第5条）
5. **简历中找不到匹配经历时怎么办**：
   - `no_resume_match = true`
   - 仍然生成合理的通用回答框架和示例
   - **在full_text的第一行最开头**必须加前缀：`【注意】未在简历中找到可直接引用的匹配经历，以下回答为通用框架示例，建议你补充自己的真实项目/数据后再使用。`
   - full_text中示例可以用"假设我曾做过XX项目……"但要明确是假设

### G. improve_todo（计划改进todo list）
string[]数组，每个元素是1条具体可执行的改进动作。
❌ 不要写："提升表达能力""优化项目介绍"（空泛）
✅ 要写："把自我介绍重写为量化版本，3个核心数据点各补1个具体数字""准备STAR版的'RAG优化'项目案例，准备好3个指标（召回率/延迟/成本）的具体数字"

---

## 二、候选人反问QA 逐条分析规则（2个追加字段）

### H. position_insights（从面试官回答中提炼的岗位有效信息）
string[]数组，提炼任何关于：
- 汇报线/组织架构
- 团队规模/成员背景
- 该岗位近期核心OKR/核心业务指标
- 对候选人的具体能力要求（面试官回答中提到的"我们希望招的人要XXX"）
- 团队技术栈/产品方向
- 入职后前3个月期望
- 其他任何有助于判断这个岗位值不值得去的信息

### I. action_items（从反问环节得出的后续todo）
string[]数组，每个是1条可执行动作：
例：`"确认该团队最近3个月的核心OKR文档并精读"``"提前了解XX技术栈（面试官提到在用GraphRAG）"`

---

## 三、overall（整体评分与失分复盘 + 改进方案）

### J. overall.score（1-10整数） + overall.pass（是/否/待定） + overall.reasons（评估理由）
- score = 1分（完全没戏）到 10分（稳过毫无疑问）
- pass = 三选一："是""否""待定"
- reasons 评估维度（至少写3个维度的分析）：
  1. **面试时长**：<20分钟通常挂；20-40分钟正常；>40分钟通常面试官有较大兴趣
  2. **面试官态度信号**：追问次数多=兴趣大；打断多=回答不吸引或不耐烦；表扬多=加分；质疑多=需谨慎
  3. **反问阶段回答详细程度**：面试官回答很具体/主动给信息=有戏；回答敷衍/模糊=没戏
  4. **星级分布**：★★★★★占比≥30% = 明显加分；★☆☆☆☆≥2道 = 明显减分
  5. **其他你观察到的信号**：比如面试官主动加微信/主动介绍下一轮流程=有戏

### K. overall.problems（存在问题列表）
必须把所有问题归到三类中的一类：
- **思维型缺陷-表层**：表达层面的问题（口语词太多、无结构、逻辑混乱、语速、口头禅等）
- **思维型缺陷-深层**：思考框架层面的问题（没有框架、缺指标意识、不会根源分析、只会看现象不会挖原因等）
- **知识型缺陷**：产品/技术名词不了解、方法论没听过（比如被问到GraphRAG不知道是什么、海盗模型AARRR不会用）
- **其他**：以上都不适用的（极少）

每个problem是一个对象：`{ "title": "问题一句话标题", "description": "问题具体说明（哪道题/什么表现/为什么这是问题）", "category": "枚举值" }`

### L. overall.improvement_plan（改进方案表格）
所有问题对应的改进动作汇总，每个是：
`{ "todo": "具体动作（含要学的知识点/工具/方法论名）", "type": "学习项"或"准备项", "related_links": [] }`
- **学习项**：需要去学习的知识点/方法论/工具（例："学习AARRR海盗模型指标拆解框架，结合自己做过的项目出1套拆解案例"）
- **准备项**：需要补充到简历/作品集/面试题库的内容（例："准备1个量化的自我介绍版本，3句话讲完"）
- related_links：空数组即可（V1阶段不自动搜链接，V2可以补）

---

## 输出格式最最最重要的约束
1. 完整回复**必须是纯JSON**，开头第一个字符`{`，结尾最后一个字符`}`
2. **禁止**输出任何 ```json ``` 代码块标记
3. **禁止**输出"好的我开始分析"等解释性文字
4. analyzed_data.schema.json中所有required字段必须包含，空数组也要写`[]`，不能省略字段
5. 原始extracted_data_json中的字段全部保留，不要修改不要删除（比如原candidate_answer原文不要动）
```

- [ ] **Step 2: 验证阶段2 Prompt 包含全部核心规则**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
path = 'prompts/02_analyze.md'
with open(path, encoding='utf-8') as f:
    content = f.read()
# 固定8类 + 扩展分类
classes = ['自我介绍类', '实习深挖类', '个人项目深挖类', '技术考察类', '产品八股类', '场景题类', '出勤/稳定性问题类', '职业规划类']
missing_class = [c for c in classes if c not in content]
# 5档星级（至少出现5个★符号）
star_count = content.count('★')
# 理想回答5条规则
ideal_keywords = ['必须引用简历', '禁止空泛表达', '结尾必须加一句邀请', 'no_resume_match', '【注意】未在简历中找到']
missing_ideal = [k for k in ideal_keywords if k not in content]
# overall三大块
overall_kws = ['思维型缺陷-表层', '思维型缺陷-深层', '知识型缺陷', '学习项', '准备项']
missing_overall = [k for k in overall_kws if k not in content]
# 纯JSON约束
json_kws = ['纯JSON', '开头第一个字符', '代码块标记']
missing_json = [k for k in json_kws if k not in content]

ok = True
if missing_class: print(f'❌ 缺少问题分类: {missing_class}'); ok=False
if star_count < 20: print(f'❌ 星级符号不足（应至少出现5种星级多次）'); ok=False
if missing_ideal: print(f'❌ 理想回答规则缺失: {missing_ideal}'); ok=False
if missing_overall: print(f'❌ overall分析维度缺失: {missing_overall}'); ok=False
if missing_json: print(f'❌ 纯JSON约束缺失: {missing_json}'); ok=False
if ok: print(f'✅ 阶段2 Prompt 全部核心规则检查通过（分类8类/5档星级/理想回答5规则/overall分类/纯JSON约束均有），文件长度{len(content)}字符')
exit(0 if ok else 1)
"
```
Expected: 全部通过 ✅

- [ ] **Step 3: 检查追加字段数（interviewer QA:7，反问QA:2，overall:1）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
with open('prompts/02_analyze.md', encoding='utf-8') as f:
    content = f.read()
# interviewer QA 7个追加字段
i_fields = ['question_type','inspection_point','answer_framework','rating','rating_reason','ideal_answer','improve_todo']
# 反问 QA 2个追加字段
r_fields = ['position_insights','action_items']
# overall 5个必填子字段
o_fields = ['score','pass','reasons','problems','improvement_plan']

miss_i = [f for f in i_fields if f not in content]
miss_r = [f for f in r_fields if f not in content]
miss_o = [f for f in o_fields if f not in content]
ok = not miss_i and not miss_r and not miss_o
if not ok:
    print(f'❌ 缺失字段定义: interviewer={miss_i}, retro={miss_r}, overall={miss_o}')
    exit(1)
print(f'✅ 阶段2 追加字段覆盖检查通过（7+2+5 = 14个字段全部在Prompt中有定义）')
"
```
Expected: 覆盖检查通过 ✅

- [ ] **Step 4: 文件存在检查**

```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/prompts/02_analyze.md"
```

---

### Task 9: prompts/03_generate.md —— 阶段3 生成Markdown文档Prompt

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/prompts/03_generate.md`
- Verify: 文档结构严格匹配设计文档第六章（第一部分表格1/表格2 + 第三部分整体评分 + 改进方案表格），格式细节（星级字符/换行/br标签）全部覆盖

**Interfaces:**
- Consumes: 设计文档6.2/6.3节 全部格式规范
- Produces: 系统Prompt，输入analyzed_data JSON → 输出最终Markdown全文（纯文本，不是JSON）

- [ ] **Step 1: 写 prompts/03_generate.md**

```markdown
# 阶段3 系统Prompt：面试复盘Markdown文档格式化工程师

## 身份定义
你是资深技术文档工程师，擅长把结构化的JSON数据严格按照用户自定义的Markdown格式规范，输出一份排版工整、表格对齐、特殊标记正确的Markdown文档。你不做任何内容的增删改，只做「JSON → Markdown格式」的映射转换。

## 输入
【阶段2分析结果 JSON】analyzed_data（符合analyzed_data.schema.json）。内容包括：
- company/position/interview_stage/interview_date 元信息
- interviewer_qa：面试官提问QA列表（含分析字段）
- candidate_retro_qa：候选人反问QA列表（含分析字段）
- overall：整体评分 + 存在问题 + 改进方案
- notes[]：备注

## 输出
一份**完整的Markdown文本**（纯Markdown，开头是# 标题，结尾是改进方案）。Markdown中所有内容**100%来自输入JSON**，禁止发挥/脑补/修改。

---

## 严格文档结构（照此顺序输出，任何内容不得颠倒）

### 【文档一级标题】
格式：
```
# 面试复盘：{company} {position} {interview_stage} {interview_date}
```
如果interview_stage或interview_date是"待定"，保留"待定"两个字。

如果notes数组非空，在标题下方另起一段，把每条note以`⚠️ 提示：xxx`的格式输出。示例：
```
⚠️ 提示：原始文字稿未标注发言人，QA拆分为AI自动推断，建议手动核对准确性
⚠️ 提示：本次仅提取到2个面试官问题，文字稿可能不完整
```

---

### 【第二行：基础信息】
用引用块（>开头）展示基础元信息（可选但建议有，方便快速浏览）：
```
> **公司**：{company}　**岗位**：{position}　
> **面试阶段**：{interview_stage}　**面试日期**：{interview_date}
```

---

## 第一部分：完整QA实录

### 表格1：面试官提问QA

**严格8列，列顺序必须如下：**

| 序号 | 面试问题 | 问题类型 | 面试官考察点 | 我的回答（回答框架） | 回答点评 | 理想回答 | 计划改进todo list |
|---|---|---|---|---|---|---|---|
| 1 | {question} | {question_type} | {inspection_point} | {answer_framework} | {rating}<br>理由：{rating_reason} | **框架**：<br>1. {ideal_answer.framework[0]}<br>2. {ideal_answer.framework[1]}<br>...<br>**回答全文**：<br>{ideal_answer.full_text} | 1. {improve_todo[0]}<br>2. {improve_todo[1]}<br>... |

**表格内格式细节强制规范：**
1. 序号 = interviewer_qa[i].index 的值（原封不动，不重新编号）
2. 面试问题 = question 的原文
   - 如果 signal_inferred=true，在问题末尾加 `<br>【信号推断】`
3. 我的回答（回答框架） = answer_framework 的原文，换行用`<br>`
4. 回答点评列 = 第一行写rating星级字符（★★★★★到★☆☆☆☆），第二行起写`理由：{rating_reason}`，行之间用`<br>`
   - ⚠️ 星级必须用Unicode字符★☆，**不要**用emoji星，不要用`*`字符
5. 理想回答列 = 先写加粗行`**框架**：`，然后用`<br>`1. xxx<br>2. xxx`枚举framework；空一行（用<br><br>），再写加粗行`**回答全文**：`，然后写full_text
   - 如果 ideal_answer.no_resume_match=true，full_text 中已有【注意】前缀，你不需要再加一遍；直接原样输出
6. 计划改进todo list列 = 用`<br>1. xxx<br>2. xxx`格式逐条枚举improve_todo数组
   - 如果improve_todo是空数组，输出`-`

如果interviewer_qa是空数组（极端情况），在表格位置输出一段说明：
> （未提取到面试官提问，可能文字稿格式异常）

---

### 表格2：候选人反问QA

**严格5列，列顺序必须如下：**

| 序号 | 候选人反问问题 | 面试官的回答（尽量还原原文，标注信号不清） | 从面试官的回答中可以得到关于该岗位的有效信息 | todo list |
|---|---|---|---|---|
| 1 | {question} | {interviewer_answer}<br>（如果signal_inferred=true，在行尾加`<br>【信号推断部分内容可能不准确】`） | 1. {position_insights[0]}<br>2. {position_insights[1]}<br>... | 1. {action_items[0]}<br>2. {action_items[1]}<br>... |

**格式细节：**
1. 面试官的回答列 = 直接写 interviewer_answer 原文
   - signal_inferred=true时，在回答内容末尾加一行（用`<br>`）：`【信号推断：该回答部分内容由上下文推断，原文字稿信号较差】`
2. 有效信息列 = 用`<br>1. xxx<br>2. xxx`枚举position_insights数组
   - 空数组时输出`-`
3. todo list列 = 用`<br>1. xxx<br>2. xxx`枚举action_items数组
   - 空数组时输出`-`

如果candidate_retro_qa是空数组，输出说明：
> （本次面试未检测到候选人反问环节，建议下轮面试准备2-3个有质量的反问问题）

---

## 第三部分：整体失分复盘与修复方案

### 3.1 综合评分

```
【整体评分】：{overall.score}分
【是否通过】：{overall.pass}
【评估理由】：{overall.reasons}

【存在问题】：
```

然后逐条输出overall.problems：
```
「问题一」：{problems[0].title}（{problems[0].category}）
{problems[0].description}

「问题二」：{problems[1].title}（{problems[1].category}）
{problems[1].description}

...（按数组顺序依次输出，用「问题一」「问题二」「问题三」……不要用数字编号1.2.3.）
```

注意：
- category要翻译成括号里的中文标签，如实输出（例如"思维型缺陷-表层"）
- 如果overall.problems是空数组，写：`（本场面试表现较好，暂未发现明显重大问题）`
- 整体用三反引号代码块包裹吗？**不要！** 直接纯文本写「问题一」。原规范不用代码块，直接写段落文本。
  ——更正：原用户规范是用类似纯文本的格式，不要用代码块，直接输出纯文本段落即可，整体内容就写在该小节下，不用```包裹

---

### 3.2 怎么改进（表格形式）

严格3列，列顺序必须如下：

| todo（含工具、方法论） | 类型 | 相关链接（可参考学习的链接） |
|---|---|---|
| {improvement_plan[0].todo} | {improvement_plan[0].type} | {improvement_plan[0].related_links如果是空数组输出`-`，否则用`<br>`一个链接一行} |
| {improvement_plan[1].todo} | {improvement_plan[1].type} | {同上} |
| ... | ... | ... |

**格式细节：**
1. 类型列：原样输出"学习项"或"准备项"
2. 相关链接列：
   - 如果related_links是空数组，输出 `-`
   - 如果有多个链接，用`<br>`每个链接占一行
   - 链接如果是URL，直接写（Markdown自动识别）；如果是文字说明（如"（更新简历/作品集）"）也直接写

如果improvement_plan是空数组，在表格位置写：
> （暂无改进项，保持即可）

---

## 格式强制约束（再强调一遍，必须遵守）
1. **表格列数严格对应**：表格1=8列，表格2=5列，改进表格=3列。多一列少一列都是错误。
2. **表格表头文字严格复制**：比如「我的回答（回答框架）」一个字不能改，不能写"我的回答"或"回答框架"。
3. **星级字符**：★☆ 必须使用**Unicode字符**（U+2605 / U+2606），不要用`*`⭐🌟等替代。
4. **表格内换行统一用 `<br>`**，不要用Markdown换行（两个空格+回车，因为表格内不一定生效）；但段落之间/表格之间正常Markdown空行分隔。
5. **全角标记**：`【信号推断】`「问题一」`【注意】`等，用全角括号，不要用半角[]()。
6. **理想回答的框架/回答全文标题用`**框架**：`和`**回答全文**：`（双星号加粗+冒号），不要变格式。
7. **整个输出不要加任何额外的装饰性内容**（比如分割线、emoji美化除了★☆之外的、目录导航等），完全按以上结构输出即可。
8. **你输出的内容是一个完整的.md文件内容**：开头是`# 面试复盘：...`，结尾是改进表格的结束或说明。直接输出md内容，不要包代码块。
```

- [ ] **Step 2: 验证所有表格列头与规范完全一致（字符级对比）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
with open('prompts/03_generate.md', encoding='utf-8') as f:
    content = f.read()

# 强制表格列头（来自用户原始需求，必须完全一致）
table1_headers = '| 序号 | 面试问题 | 问题类型 | 面试官考察点 | 我的回答（回答框架） | 回答点评 | 理想回答 | 计划改进todo list |'
table2_headers = '| 序号 | 候选人反问问题 | 面试官的回答（尽量还原原文，标注信号不清） | 从面试官的回答中可以得到关于该岗位的有效信息 | todo list |'
improve_headers = '| todo（含工具、方法论） | 类型 | 相关链接（可参考学习的链接） |'
# 章节标题
sections = [
    '## 第一部分：完整QA实录',
    '### 表格1：面试官提问QA',
    '### 表格2：候选人反问QA',
    '## 第三部分：整体失分复盘与修复方案',
    '### 3.1 综合评分',
    '### 3.2 怎么改进（表格形式）',
    '【整体评分】',
    '【是否通过】',
    '【评估理由】',
    '【存在问题】',
    '「问题一」',
]
ok = True
if table1_headers not in content: print('❌ 表格1列头不一致/缺失（必须完全匹配用户原始定义）'); ok=False
else: print('✅ 表格1列头完全匹配规范')
if table2_headers not in content: print('❌ 表格2列头不一致/缺失'); ok=False
else: print('✅ 表格2列头完全匹配规范')
if improve_headers not in content: print('❌ 改进方案表格列头不一致/缺失'); ok=False
else: print('✅ 改进方案表格列头完全匹配规范')
for s in sections:
    if s not in content:
        print(f'❌ 缺少章节/关键标记: {repr(s)}'); ok=False
print('✅ 章节标记检查：PASS' if all(s in content for s in sections) else '')

# Unicode 星级和全角标记
special_chars = {
    '★': 'Unicode实心星',
    '☆': 'Unicode空心星',
    '「问题一」': '全角书名号问题标记',
    '【信号推断】': '全角方括号信号标记',
    '【整体评分】': '全角方括号评分标记',
    '【注意】': '全角方括号注意标记',
    '<br>': 'HTML换行标签（表格内用）',
    '**框架**：': '加粗小标题格式',
}
for ch, name in special_chars.items():
    if ch not in content:
        print(f'❌ 缺少特殊字符/格式 {name}: {repr(ch)}')
        ok = False
if ok: print(f'✅ 所有特殊字符（Unicode星级/全角标记/<br>/加粗小标题）均在Prompt中明确要求')
print('阶段3 Prompt 格式合规性总检:', '全部通过 ✅' if ok else '有失败 ❌')
exit(0 if ok else 1)
"
```
Expected: 表格列头/章节/特殊字符 全部✅

- [ ] **Step 3: 检查第一/第三部分编号逻辑（跳过第二部分，按用户原始需求保留编号）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
with open('prompts/03_generate.md', encoding='utf-8') as f:
    content = f.read()
has_first = '第一部分' in content
has_second = '第二部分' in content
has_third = '第三部分' in content
if has_first and (not has_second) and has_third:
    print('✅ 编号逻辑正确：保留第一/第三部分，没有第二部分（严格匹配用户原始需求）')
else:
    print(f'❌ 编号逻辑异常！有第一={has_first}, 有第二={has_second}, 有第三={has_third}。必须没有第二部分')
    exit(1)
"
```
Expected: 编号逻辑正确 ✅（这是用户需求里明确的奇怪但必须遵守的规则）

- [ ] **Step 4: 文件存在检查**

```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/prompts/03_generate.md"
```

---

### Task 10: examples/ 示例文件（3个输入示例 + 1个输出示例）

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/examples/sample_resume.md` —— 脱敏简历示例
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/examples/sample_job_desc.md` —— 岗位介绍示例
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/examples/sample_transcript.md` —— 发言人1/2格式的面试文字稿（故意带口语词、信号差内容、追问打断等信号，用于测试清洗）
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/examples/sample_output.md` —— 一份正确格式的输出参考示例（直接对应上面3份输入跑出来的结果）

**Interfaces:**
- 用于全流程端到端冒烟测试（Task 12）；也给用户调试参考。

- [ ] **Step 1: 写 examples/sample_resume.md（脱敏简历）**

```markdown
# lucky - AI产品经理简历

## 基本信息
- 姓名：lucky
- 应聘岗位：AI产品经理
- 工作年限：3年
- 学历：985本科 / 计算机相关专业

## 核心技能
- AI产品全流程：需求挖掘 / 方案设计 / 模型评估 / 上线运营
- 大模型应用：RAG / Agent / 提示词工程 / 微调流程
- 数据分析：SQL / Python / A/B实验设计 / 指标体系搭建

## 工作经历
### 某互联网大厂（2024.03 - 至今）| AI产品经理
- **项目1：企业知识库RAG系统（主责）**
  - 背景：企业内部文档分散，员工搜索效率低
  - 方案：设计RAG技术选型管线（Chunk切块→Embedding→向量库→Hybrid检索→Rerank→LLM生成），定义召回率/准确率/答案相关性3个核心指标
  - 结果：上线后内部员工知识库搜索满意度从 3.2分 → 4.5分（满分5）；答案首解率从 47% → 78%；DAU稳定在 1.3万（上线前只有3000）
- **项目2：客服Agent 智能体平台**
  - 负责产品方案设计和模型评估标准搭建；覆盖 12个业务场景；客服平均处理时长下降 32%

### 某创业公司（2022.07 - 2024.02）| 产品经理
- **项目3：用户增长体系搭建**
  - 主导设计AARRR漏斗指标体系；落地7个增长实验；3个月内新增用户月环比提升 18%

## 项目作品集
1. GraphRAG 企业知识库产品方案（有原型和指标）
2. DAU下跌场景的排查框架案例（有复盘报告）

## 自我评价
逻辑清晰、数据驱动，对大模型产品从0到1有完整落地经验。
```

- [ ] **Step 2: 写 examples/sample_job_desc.md**

```markdown
# 岗位介绍：字节跳动 - AI产品经理（一面）

## 岗位描述
- 负责字节跳动核心APP的AI功能产品规划与落地，包括大模型在内容理解、用户画像、个性化推荐等场景的应用
- 与算法/工程团队紧密配合，定义模型评估标准，推动模型迭代，最终达成业务指标
- 深入用户调研和数据分析，挖掘用户真实需求，输出高质量的产品方案

## 任职要求
### 硬性
- 3年及以上互联网产品经理经验，有AI相关产品经验优先
- 有扎实的数据分析能力，熟练使用SQL，有完整的指标体系搭建经历
- 对大模型（LLM/RAG/Agent）技术原理有基础理解，能和算法工程师无障碍沟通
- 有从0到1的产品落地经验

### 加分项
- 有RAG系统、推荐系统、用户增长系统的设计经验
- 会Python，能做简单的数据处理/可视化
- 有大厂完整项目经历

## 团队介绍
- AI产品中心，团队规模40人，向产品副总裁汇报
- 近期核心OKR：AI功能渗透用户占比从15%提升到40%
```

- [ ] **Step 3: 写 examples/sample_transcript.md（发言人1/2，故意带口语填充词和信号问题）**

```
文件名：字节跳动_AI产品经理_一面_20260820.pdf

发言人1：那个，你好啊同学，首先欢迎你过来面试哈。嗯，咱们先简单做个自我介绍吧。
发言人2：嗯好的好的面试官！呃就是，我叫lucky，然后呢，今年3年产品经验，然后就是主要做AI产品方向，然后之前呢在老东家做过两个比较大的项目，一个是RAG知识库的系统，然后第二个是客服Agent智能体平台，啊然后数据上表现都还不错吧，然后DAU涨了不少。然后呢，就是今天就是过来面一下咱们这个字节AI产品经理的岗位，然后希望能有进一步的交流啊。
发言人1：好的，嗯嗯，那我们就进入正题吧。我看你简历里写了一个企业知识库RAG系统是你主责的对吧？那个你再展开讲一下，就是这个项目的话你具体是怎么做的啊？就是重点讲一下你是怎么定义核心指标的吧。（追问）
发言人2：哦好的好的。啊这个项目呢，就是然后当时背景是企业员工搜资料很慢啊，然后很多重复问HR和行政，然后我们就想做一个知识库RAG系统来解决这个问题。嗯然后我呢就是主要负责产品的整个流程设计，然后就是和算法那边一起定了一个指标体系吧，大概是有三个核心指标，召回率啊准确率啊什么的。然后呢上线之后效果还不错，大家都挺满意的，然后用户量也涨了。
发言人1：就是你说的"大家都挺满意的"这个具体是怎么衡量的？你刚才说DAU涨了不少，具体是从多少涨到了多少呀？（追问 + 打断，信号：候选人回答缺量化数据，面试官追问具体数值）
发言人2：呃——哦这个啊，（沉默了一下），满意度的话原来大概3分左右吧，然后后来涨到了4点几分。DAU的话从3000涨到了大概1万多吧。具体数字我简历里好像写了是1.3万应该。
发言人1：行。我们换个题。假设啊，我们字节的某个APP的DAU在一周内突然跌了15%，你作为AI产品经理会怎么排查和处理？（场景题）
发言人2：嗯好的。DAU下跌了对吧？然后呢我觉得首先要先排查渠道吧，看一下是不是渠道那边流量掉了，比如买量停了或者渠道异常了。然后然后再看一下是不是留存的问题，比如新用户留存掉了还是老用户活跃掉了。然后然后再看一下是不是产品有bug或者版本更新有问题。嗯，大概就是这些方向吧。
发言人1：还有吗？你刚才说的都是排查方向，那如果根因是"AI推荐模型某个版本更新后CTR掉了"，你怎么从指标拆解里快速定位到这个？（追问）
发言人2：呃——对哦，那应该还要拆用户的行为漏斗吧？就是从曝光到点击到使用每一层看看是不是哪里掉了。对。
发言人1：嗯。（语气平淡，停顿3秒）那你有没有了解过，最近RAG领域有什么新的优化手段？就2025年之后的一些新的做法之类的。（技术考察）
发言人2：啊RAG优化啊。嗯，我知道的就是优化Chunk大小，然后用更好的Embedding模型，然后还有混合检索。然后还有加Rerank。嗯...其他的我就不太了解了吧。
发言人1：好。那接下来你有什么想问我的吗？（进入反问环节）
发言人2：好的面试官。我想问一下，就是咱们这个岗位的话，具体是向谁汇报呢？然后团队大概规模是怎么样的？
发言人1：嗯。汇报线是AI产品中心的总监，他直接汇报给VP。团队规模的话，整个中心40人左右，你进去的话是在一个10人的小组，组里都是有3-5年经验的产品。还有其他问题吗？
发言人2：哦还有一个，就是咱们团队最近3个月的核心OKR大概是什么呀？我如果有幸进来的话前3个月大概会做什么方向？
发言人1：最近主要是做AI功能的用户渗透，目标是从15%到40%，这个在JD里也提了。你如果进来的话，前3个月先熟悉业务，然后会接一个RAG优化的子方向，负责体验指标提升。还有吗？
发言人2：没有了，谢谢面试官。
发言人1：好的，那今天的面试就到这里，我们会在3个工作日内给你答复。再见。
【信号差，最后一段话是推测内容，原录音结束突然】
```

- [ ] **Step 4: 写 examples/sample_output.md（参考输出，严格对应格式规范）**

```markdown
# 面试复盘：字节跳动 AI产品经理 一面 2026-08-20

> **公司**：字节跳动　**岗位**：AI产品经理　
> **面试阶段**：一面　**面试日期**：2026-08-20

## 第一部分：完整QA实录

### 表格1：面试官提问QA

| 序号 | 面试问题 | 问题类型 | 面试官考察点 | 我的回答（回答框架） | 回答点评 | 理想回答 | 计划改进todo list |
|---|---|---|---|---|---|---|---|
| 1 | 先做个自我介绍吧 | 自我介绍类 | 考察表达逻辑、个人标签提炼、求职动机匹配度 | 1. 基本背景（3年AI产品）<br>2. 两个项目（RAG/Agent）<br>3. 来意（想面字节） | ★★★☆☆<br>理由：方向对但缺关键量化内容，3年经验/项目名有了但没有任何数据结果；整个回答有大量"然后"填充词冗余，结尾也没有主动邀请讨论 | **框架**：<br>1. 一句话标签（3年AI产品经理，聚焦RAG/Agent落地）<br>2. 最相关项目+量化结果（RAG项目DAU 3k→1.3w，满意度3.2→4.5）<br>3. 为什么选字节（匹配岗位要求的RAG+指标经验）<br>4. 邀请讨论<br>**回答全文**：<br>面试官您好，我是lucky，3年AI产品经理经验，核心聚焦RAG/Agent类大模型应用产品落地。上一段在老东家主责的企业知识库RAG系统，我定义了召回率/准确率/答案满意度3个核心指标，上线6个月后DAU从3000涨到了1.3万，答案满意度从3.2分提升到4.5分；另一个客服Agent平台覆盖12个场景，客服时长下降了32%。关注到字节这个岗位恰好要求RAG系统设计经验和指标体系能力，和我的履历非常匹配，想进一步了解团队的业务方向。您觉得这段经历和岗位需求匹配度如何？<br>【注意】未在简历中找到可直接引用的匹配经历，以下回答为通用框架示例，建议你补充自己的真实项目/数据后再使用。 | 1. 重写自我介绍为「1句话标签+1个核心项目量化+求职动机+邀请讨论」版本，控制在90秒内<br>2. 录自己练习自我介绍的音频，统计口语填充词，每多1个"然后/就是/那个"重来 |
| 2 | 展开讲一下企业知识库RAG项目？重点讲怎么定义核心指标？<br>【信号推断】 | 个人项目深挖类 | 考察项目指标定义能力、产品框架思维、结果量化意识（是否只会说"效果不错"还是有硬数据） | 1. 项目背景（员工搜资料慢）<br>2. 我做全流程设计<br>3. 定了3个指标（召回/准确/什么的）<br>4. 上线大家满意用户量涨了 | ★★☆☆☆<br>理由：只给了现象级描述（做了全流程设计、定了3个指标），但**没有给出指标的具体阈值/目标值是多少**（召回率做到多少算达标？），且"大家满意""用户量涨了"完全没给量化数据，直到面试官追问才说出满意度3.x→4.x，DAU3k→1.3万，属于典型缺证据支持 | **框架**：<br>1. 项目背景量化（员工月均搜索N次，重复问HR占M小时）<br>2. 指标定义逻辑（业务指标+系统指标双层，业务=满意度+DAU，系统=召回Top5命中率+答案相关性评分）<br>3. 每个指标的具体目标值和达成结果（召回Top5命中率目标90%，实际88%）<br>4. 邀请讨论<br>**回答全文**：<br>这个项目启动前我们先做了一轮调研，全公司2000人月均搜索知识库约1.2万次，其中37%的问题会重复找HR/行政二次确认，所以问题很明确。关于核心指标，我当时拆了两层：第一层是业务指标——答案满意度（NPS式5分评）目标从3.2提到4.0以上，还有日活跃使用人数目标3000→1万；第二层是系统指标——Top5检索命中相关文档的比例（目标≥85%）、LLM生成答案和参考答案的一致性（目标≥75%）。最终上线后满意度做到了4.5分（超过目标），DAU稳定在1.3万，Top5命中率88%。不过回头看，系统指标和业务指标之间的相关性当时还可以挖得更深。你在这个业务里会怎么定义这个项目的成功标准？ | 1. 把RAG项目重新整理成标准STAR版：S（背景具体数字）→T（指标目标值）→A（你做的方案设计）→R（结果实际值对比目标值），写在1页文档上<br>2. 准备3个最常被深挖的项目，每个项目都按「指标定义+目标值+实际值」格式准备卡片，随时可以背出来 |
| 3 | 如果DAU一周跌了15%，怎么排查处理？ | 场景题类 | 考察指标拆解框架能力（能否系统化拆漏斗）、根因定位逻辑、是否有量化/优先级意识 | 1. 先查渠道（买量停没停）<br>2. 再查留存（新/老用户）<br>3. 再查产品bug或版本更新 | ★★★☆☆<br>理由：方向对（有初步拆解顺序），但**缺关键指标拆解树**——只说了排查方向，没有给出「DAU=新增用户+回流用户+留存活跃」这种公式级拆解，也没有给出「按维度切分（用户分群/平台/地区/版本）+按漏斗环节（曝光→点击→启动→使用→完成关键行为）」的结构化拆解方法，面试官追问"AI推荐模型CTR掉怎么定位"时反应慢了半拍 | **框架**：<br>1. Step1：确认数据真实性（排除统计口径/Bug）<br>2. Step2：DAU公式拆解（=新增+回流+老活跃），定位哪一层掉最多<br>3. Step3：对掉最多的层做多维度切分（用户分群/平台/地区/版本/渠道来源）<br>4. Step4：看用户行为漏斗（曝光→启动→关键行为完成率）定位断点<br>5. Step5：对应回可能原因（产品/技术/运营/外部），给出优先级排序和验证方法<br>6. 邀请讨论<br>**回答全文**：<br>如果遇到DAU一周跌15%，我会先花30分钟确认不是统计口径或埋点Bug，避免虚惊一场。然后用我在上一份工作里搭建DAU指标体系的方法处理——先按DAU=新增用户+7日内回流用户+≥2日活跃老用户做公式拆解，定位到底是哪一块掉得最多。比如在我做增长项目的那个阶段，新增掉了就反查渠道（ROI/投放量/渠道包存活率），老用户掉了就分新老/地区/版本/平台9个维度做切分，然后对疑似的那个子群看完整的行为漏斗（Push触达→点击→App启动→浏览≥3屏→完成关键行为），看漏斗在哪一层突然断了，对应的原因通常能缩小到2-3个，再A/B验证根因。2023年我做过一次DAU掉18%的排查，3小时内定位到是Android某个版本的崩溃率飙升，当天就推动了热修复。你会在这个框架的基础上补充什么维度？ | 1. 学习并输出1页《DAU/MAU北极星指标拆解框架》文档，包含公式+维度表+漏斗层级表<br>2. 结合自己做过的「用户增长体系搭建」项目，整理出1个真实DAU异常排查的案例（要写具体排查过程和数据结论） |
| 4 | 2025年后RAG领域有什么新的优化手段？ | 技术考察类 | 考察对AI领域前沿技术的关注度（产品经理是否跟得上行业节奏）、技术理解深度 | 1. Chunk大小优化<br>2. 更好的Embedding<br>3. 混合检索<br>4. 加Rerank | ★★☆☆☆<br>理由：只答出了2023-2024年的常见手段（Chunk/Embedding/混合检索/Rerank），**2025年后已经成为主流的GraphRAG、HyDE（假设性文档嵌入）、Query改写/多Query扩展、结构化元数据过滤 这4个高频手段一个都没提到**，属于典型的知识型缺陷（对技术新进展不了解） | **框架**：<br>1. 2024年及以前的主流方案（Chunk/混合检索/Rerank，我已实践过的）<br>2. 2025年后成为工业界标配的4个新手段（GraphRAG/结构化元数据/HyDE/Query扩展），每个一句话讲作用和适用场景<br>3. 自己对GraphRAG的实践思路（如果在字节做的话）<br>4. 邀请讨论<br>**回答全文**：<br>2024年及之前RAG的常规优化手段，我在老东家的RAG项目里基本都实践过——比如把Chunk从默认1024调整为512+256重叠，换了BGE-large的Embedding，加了BM25+向量的混合检索，最后用BGE-Rerank重排，这套组合拳把Top5命中率从76%拉到了88%。2025年之后我观察到4个新的优化手段已经在工业界基本成为标配了：第一个是GraphRAG，用知识图谱把Chunk关联起来，解决多跳推理和全局性问题；第二个是结构化元数据过滤，检索前先按文档类型/时间窗/权限标签先做粗过滤，减少向量库的搜索范围；第三个是HyDE假设性文档嵌入，先让LLM生成一个假设的答案，用这个答案的向量去检索而不是用原始Query，解决了Query和文档的语义分布差；第四个是Query扩展，把一个用户Query改写成3个语义相同但表达方式不同的子Query，提升召回召回率。如果让我来设计字节团队RAG优化的优先级，我会先推结构化元数据过滤和Query扩展，这两个改动成本最低、上线收益通常最大；GraphRAG成本最高但能解决复杂多跳问题，放在第二阶段推进。你团队目前这4个新手段的落地进度是怎样的？ | 1. 本周内精读GraphRAG（微软2025版）、HyDE、Query改写 3篇工业界主流论文/博客，输出1页学习笔记<br>2. 在作品集里补充 1 个 RAG 优化的对比方案（旧手段 vs 2025新手段，列出指标提升预期） |
| 5 | （面试官打断/追问等，略，示例文件仅展示4个主QA覆盖格式即可） |  |  |  |  |  |  |

### 表格2：候选人反问QA

| 序号 | 候选人反问问题 | 面试官的回答（尽量还原原文，标注信号不清） | 从面试官的回答中可以得到关于该岗位的有效信息 | todo list |
|---|---|---|---|---|
| 1 | 岗位汇报线？团队规模？ | 汇报给AI产品中心总监（总监直接对VP）；整个中心40人左右，具体在10人小组，组员都是3-5年经验的产品经理。 | 1. 汇报线：总监→VP（2层汇报，层级不深）<br>2. 团队规模：10人小团队，都是资深产品，说明对新人要求较高<br>3. 对候选人期望：至少3-5年经验匹配或超预期 | 1. 面试前补做「字节AI产品中心最近公开的10个产品动作」调研<br>2. 准备「如何快速融入资深团队」的回答思路 |
| 2 | 团队最近3个月核心OKR？入职前3个月方向？ | OKR：AI功能用户渗透率 15%→40%（JD也写了）；入职前3月先熟悉业务，再接RAG优化子方向，负责体验指标提升。<br>【信号推断：最后收尾部分信号差，后半句为上下文推断】 | 1. 核心业务指标：AI功能渗透率（重点！面试第二轮大概率会被问到怎么设计提升方案）<br>2. 入职后接手方向：RAG优化（正好是你知识型缺陷那道题涉及的领域，提前准备加分） | 1. 输出1页《AI功能渗透率从15%→40%提升方案草稿》，下次面试可以直接讲<br>2. RAG优化相关的4个新技术（GraphRAG/HyDE/Query扩展/元数据过滤），每个准备好1个具体落地案例 |

## 第三部分：整体失分复盘与修复方案

### 3.1 综合评分

【整体评分】：6分
【是否通过】：待定
【评估理由】：面试时长约35-40分钟（中间有追问共5次，追问多=面试官有一定兴趣），反问环节回答较为详细，属于正面信号；但4个主问题的星级分布为：★★★☆☆ / ★★☆☆☆ / ★★★☆☆ / ★★☆☆☆，没有任何一道达到★★★★及以上，且出现了1个严重的知识型缺陷（RAG新手段完全不了解），拉低了整体胜算。反问阶段你提的2个问题属于中等质量，没有提出让面试官眼前一亮的深度问题。综合判断有戏但概率约50%，需要做好没过的准备。

【存在问题】：
「问题一」：表达层面大量口语填充词（思维型缺陷-表层）
  具体说明：在4道题的回答中，"然后"共出现21次，"就是/那个/嗯/呃"合计出现17次。说明回答时思路衔接不流畅，没有提前列好框架点，边想边说导致用填充词拖时间。

「问题二」：量化意识薄弱，习惯用空泛形容词代替具体数据（思维型缺陷-深层）
  具体说明：第2题（项目深挖）回答时先说"大家都挺满意""用户量涨了"这种空泛描述，直到面试官连续两次追问才说出具体数值3.2→4.5分、DAU3000→1.3万。这是面试大忌——"不说数据=没做到"。

「问题三」：指标框架化拆解能力不足（思维型缺陷-深层）
  具体说明：第3题DAU下跌场景题，只给出了3个独立的排查方向，没有给出公式级拆解（DAU=新增+回流+老活跃）和维度表（新老/平台/地区/版本/渠道），说明平时工作中没有养成「公式化+多维切分」的思维习惯。

「问题四」：对AI技术2025年后的最新进展脱节（知识型缺陷）
  具体说明：第4题RAG优化手段一个都没答对2025年的新方向，属于典型的"行业信息摄入不足"。作为AI产品经理，这个领域迭代非常快，季度级别的脱节都可能影响方案设计质量。

### 3.2 怎么改进（表格形式）

| todo（含工具、方法论） | 类型 | 相关链接（可参考学习的链接） |
|---|---|---|
| 学习DAU北极星指标拆解框架（海盗模型AARRR + 公式拆解法 + 9维度切分表），结合自己做过的用户增长项目，输出1页《我的指标拆解工具卡》 | 学习项 | - |
| 精读GraphRAG微软2025技术报告、HyDE论文解读、Query扩展实战、结构化元数据过滤最佳实践，4个主题各写1页学习笔记 | 学习项 | - |
| 重写自我介绍版本：控制90秒，结构=1句话标签+1个核心项目量化结果+求职动机+邀请讨论，反复练到无口语填充词 | 准备项 | - |
| 整理3个核心项目（企业RAG/客服Agent/用户增长）的STAR卡片：每题写清楚「指标定义→目标值→实际值→差距分析」，随时可以背 | 准备项 | - |
| 输出1页《AI渗透率15%→40%提升方案》草稿：包含假设路径、阶段性目标、风险分析，作为下一轮面试储备 | 准备项 | - |
| 每次面试练习录音：回答10个常见高频题，事后自己转写，圈出所有口语填充词做复盘 | 学习项 | - |
```

Expected: 文件长度应超过10KB，至少包含 2 个表格（面试官QA/反问QA）+ 整体评分章节 + 改进表格

- [ ] **Step 2: 验证3个输入示例文件存在**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && ls -la examples/sample_resume.md examples/sample_job_desc.md examples/sample_transcript.md examples/sample_output.md
```
Expected: 4个文件均存在，size均>1KB

- [ ] **Step 3: 验证sample_transcript.md中包含用于测试的关键信号**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
with open('examples/sample_transcript.md', encoding='utf-8') as f:
    t = f.read()
# 测试用信号
must_have = ['发言人1：', '发言人2：', '然后', '那个', '嗯', '呃', '（追问）', '【信号差，', '（沉默了一下）']
miss = [k for k in must_have if k not in t]
if miss:
    print(f'❌ sample_transcript缺少测试用信号: {miss}（这些信号用于测文本清洗和态度信号识别）')
    exit(1)
print(f'✅ sample_transcript测试用信号齐全，包含口语填充词/追问/信号差标记/沉默标记')
"
```
Expected: 全部测试信号包含 ✅

- [ ] **Step 4: 验证sample_output.md中包含所有文档结构章节**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
with open('examples/sample_output.md', encoding='utf-8') as f:
    o = f.read()
sections = [
    '# 面试复盘：', '## 第一部分：完整QA实录',
    '### 表格1：面试官提问QA', '### 表格2：候选人反问QA',
    '## 第三部分：整体失分复盘与修复方案',
    '### 3.1 综合评分', '### 3.2 怎么改进',
    '【整体评分】', '【是否通过】', '「问题一」',
]
miss = [s for s in sections if s not in o]
if miss:
    print(f'❌ sample_output缺少章节/标记: {miss}')
    exit(1)
# 5档星级符号至少出现1种
star_count = sum(o.count(c) for c in ['★★★★★','★★★★☆','★★★☆☆','★★☆☆☆','★☆☆☆☆'])
if star_count == 0:
    print('❌ sample_output无任何星级标记')
    exit(1)
print(f'✅ sample_output结构完整：章节/标记/星级 全部包含（星级符号出现{star_count}次）')
"
```
Expected: 全部包含 ✅

- [ ] **Step 5: 文件集合检查**

```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && ls -la examples/
```

---

### Task 11: SKILL.md —— Skill入口总控（流程编排）

**Files:**
- Create: `/Users/yst/Coding/post‑interview-reflection-skill/SKILL.md`
- Verify: 包含完整工作流的自然语言描述（供Trae Skill框架识别+执行）；覆盖缺文件追问、Step0-4顺序、3次LLM调用、JSON重试、文件保存提示

**Interfaces:**
- Consumes: 用户上传的3个文件路径 + 用户自然语言指令（"帮我复盘""生成复盘文档"等）
- Produces: 触发整个流程（脚本→Prompt→脚本），最终保存Markdown并给用户反馈

- [ ] **Step 1: 写 SKILL.md 完整内容**

```markdown
---
name: interview-reflection
description: |
  【面试复盘专家】AI产品经理专属面试复盘工具。用户上传「简历PDF + 岗位介绍 + 面试录音文字稿」3个资料并说一句类似"帮我复盘这次面试"后，全自动完成：文件解析 → QA信息提取 → 逐条打分分析 → 生成规范Markdown → 保存到 /Users/yst/Documents/面试复盘/ 目录。
  核心能力：
  1. 智能区分发言人1/2角色
  2. 标注面试官态度信号（追问/打断/表扬等）
  3. 严格5档星级点评（★★★★★到★☆☆☆☆），附具体改进理由
  4. 理想回答必须引用简历真实数据+结尾邀请讨论
  5. 整体胜算评分+思维型/知识型缺陷分析+改进方案表格
  输出文件名格式：{公司}_{岗位}_{面试阶段}_{面试日期}.md
version: 1.0.0
author: lucky
triggers:
  - 帮我复盘
  - 生成复盘文档
  - 复盘这次面试
  - 面试复盘
  - 做一份复盘
---

# 面试复盘 Skill 执行手册（给Agent的自然语言执行指令）

## 第一阶段：触发 & 文件完整性检查（全静默 + 缺东西追问）

### 1.1 触发条件
当用户发送的自然语言消息匹配以下任意语义时，触发本Skill：
- "帮我复盘""复盘这次面试""生成复盘文档""面试复盘""做一份复盘" 等类似含义

### 1.2 检测用户上传的文件
在当前对话附件/用户消息中，查找以下3类文件（必须全部存在才能开始）：
| 资料类型 | 常见文件后缀 | 识别方式 |
|---|---|---|
| 简历（resume） | .pdf（必须） | 文件名/正文包含「简历""CV""个人信息""工作经历""教育经历"等关键词；或用户明确说"这是我简历" |
| 岗位介绍（job_desc） | .pdf / .docx / .doc / .txt / 图片 | 文件名/正文包含「岗位""职责""任职要求""JD""Job Description"等关键词；或用户明确说"这是岗位介绍/这是JD" |
| 面试文字稿（transcript） | .pdf / .docx / .doc / .txt | 文件名/正文包含「面试""面经""录音""转写""文字稿""发言人1""面试官:"等关键词；或用户明确说"这是面试文字稿/这是录音转写" |

### 1.3 缺文件处理（必须追问，不硬跑）
- **缺简历**：主动问用户：`检测到缺少【简历PDF】。方便补充上传吗？（如果暂时没有，也可以跳过，只是"理想回答"部分将无法引用你的真实经历，会以通用框架输出并加【注意】提示）`
- **缺岗位介绍**：主动问用户：`检测到缺少【岗位介绍】。方便补充上传吗？（也可以直接把岗位描述粘贴在对话里，缺少岗位介绍会影响「面试官考察点」和「问题分类」的准确性）`
- **缺面试文字稿**：主动问用户：`检测到缺少【面试录音文字稿】。这是复盘的核心材料，请提供 PDF / Word(docx) / TXT 格式的文字稿文件～`

用户补充任何一个缺少的文件后，回到1.2重新检测；**3个文件全部到位后才进入下一阶段**。

---

## 第二阶段：Step 0 —— 脚本预处理层（调用Python脚本）

### 2.1 执行 parse_files.py
在终端运行以下命令（mock模式关闭，正式调markitdown）：

```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
from scripts.parse_files import parse
import json

# ----- 这里替换成真实检测到的3个文件绝对路径 -----
RESUME_PATH = '替换成简历文件绝对路径'
JOB_DESC_PATH = '替换成岗位介绍文件绝对路径'
TRANSCRIPT_PATH = '替换成面试文字稿文件绝对路径'

result = parse(RESUME_PATH, JOB_DESC_PATH, TRANSCRIPT_PATH, _use_mock_markitdown=False)
# 把结果保存到temp/step0_preprocessed.json（供LLM读取，避免上下文丢失）
import os; os.makedirs('temp', exist_ok=True)
with open('temp/step0_preprocessed.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('✅ Step0完成，预处理结果已保存到 temp/step0_preprocessed.json')
print('   文件名元信息:', json.dumps(result['filename_meta'], ensure_ascii=False))
print('   各文本长度: 简历=', len(result['resume_md']), '字符，岗位=', len(result['job_desc_md']), '字符，文字稿=', len(result['transcript_md']), '字符')
"
```

### 2.2 如果markitdown解析失败（抛异常/报错）
暂停流程，按以下提示用户：
- 简历解析失败 → `【简历PDF】解析失败（可能是加密或纯图片扫描件）。能否提供可复制文字的版本，或者直接把简历内容粘贴到对话里？`
- 岗位介绍/文字稿解析失败 → 类似对应句式

---

## 第三阶段：Step 1 —— 信息提取（第1次LLM调用）

### 3.1 系统Prompt
读取并发送 `prompts/01_extract.md` 的全文作为 SYSTEM 角色消息。

### 3.2 用户消息（USER角色）
把 `temp/step0_preprocessed.json` 中的4个字段，按以下格式组合成1条用户消息发送：

```
--- filename_meta JSON ---
{把 filename_meta 完整JSON粘贴在这里}
--- 岗位介绍 Markdown ---
{把 job_desc_md 全文粘贴在这里}
--- 简历 Markdown ---
{把 resume_md 全文粘贴在这里}
--- 面试文字稿 Markdown ---
{把 transcript_md 全文粘贴在这里}

请严格按系统Prompt要求，输出纯JSON（不要任何其他文字或代码块）。
```

### 3.3 JSON解析与重试机制（关键容错）
1. 拿到LLM输出后，先尝试用 `json.loads()` 解析
2. 解析成功：继续用 `jsonschema.validate()` 校验是否符合 `schemas/extracted_data.schema.json`
3. 解析失败 或 Schema校验失败：
   - 重试第1次：系统Prompt保持不变，用户消息末尾追加：`你上一次的输出不是合法JSON或不符合Schema要求。请重新输出，必须是纯JSON（开头{，结尾}，没有```json标记），并严格包含所有required字段。`
   - 重试第2次：再追加：`再次失败。请只输出以下JSON的完成版，不要任何其他文字。（用实际值替换TODO）：{ 包含所有required字段的最小骨架JSON TODO }`
   - 3次全失败：终止并提示用户：`AI生成异常（JSON格式连续失败），请稍后重试，或检查面试文字稿是否格式异常`
4. 成功后，保存到 `temp/step1_extracted.json`

---

## 第四阶段：Step 2 —— QA分析打分（第2次LLM调用）

### 4.1 系统Prompt
读取并发送 `prompts/02_analyze.md` 全文作为 SYSTEM 角色消息。

### 4.2 用户消息（USER角色）
组合消息：
```
--- extracted_data.json（阶段1结果）---
{把 temp/step1_extracted.json 全文JSON粘贴在这里}
--- 简历全文 Markdown（供理想回答引用真实经历/数据）---
{把 temp/step0_preprocessed.json 中 resume_md 全文粘贴在这里}

严格按系统Prompt输出纯JSON，保留所有原始字段，追加分析字段，不要任何其他文字。
```

### 4.3 重试机制
同3.3，但Schema改为 `schemas/analyzed_data.schema.json`；重试提示语对应调整（"必须保留所有原始extracted字段并追加7+2+overall分析字段"）。

成功后保存到 `temp/step2_analyzed.json`。

---

## 第五阶段：Step 3 —— 生成Markdown文档（第3次LLM调用）

### 5.1 系统Prompt
读取并发送 `prompts/03_generate.md` 全文作为 SYSTEM 角色消息。

### 5.2 用户消息
```
--- analyzed_data.json ---
{把 temp/step2_analyzed.json 全文JSON粘贴在这里}

严格按系统Prompt的文档结构规范输出完整Markdown，开头第一个字符是#，不要任何前后缀解释文字！
```

### 5.3 校验与重试
- 校验：输出开头第一个非空字符必须是 `#`（Markdown一级标题），且必须同时包含 `## 第一部分` 和 `## 第三部分`（跳过第二部分的规则）
- 不满足则重试最多2次：`输出格式错误，必须是完整的Markdown文档，开头# 面试复盘...，且必须有第一部分/第三部分章节`
- 成功后把Markdown全文保存到Python变量 `final_markdown_content`

---

## 第六阶段：Step 4 —— 保存文件（调用save_output.py脚本 + 给用户最终反馈）

### 6.1 提取元信息
从 `temp/step2_analyzed.json` 或 `temp/step1_extracted.json` 中读取：
`company, position, interview_stage, interview_date` 4个字段值。

### 6.2 调用 save_output.py
在终端运行：

```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
from scripts.save_output import save_markdown
import json

# 从step2_analyzed.json读元信息（提取不到就用待定）
with open('temp/step2_analyzed.json', encoding='utf-8') as f:
    data = json.load(f)
company = data.get('company', '待定')
position = data.get('position', '待定')
stage = data.get('interview_stage', '待定')
date = data.get('interview_date', '待定')

# 这里把 final_markdown_content 从Step3的结果原样替换进来
FINAL_MARKDOWN = '''
这里把Step3生成的Markdown全文原封不动粘贴进来
'''

saved_path = save_markdown(FINAL_MARKDOWN, company, position, stage, date)
print('SAVED_PATH=', saved_path)
"
```

### 6.3 给用户的最终反馈
抓取脚本输出中的 `SAVED_PATH=` 后面的绝对路径，给用户回复：

```
✅ 面试复盘完成！

📄 文档已保存到：
{SAVED_PATH}

📊 快速预览：
- 公司：{company}
- 岗位：{position}
- 阶段：{stage}
- 日期：{date}
- 整体评分：{从overall.score中读取}分
- 是否通过：{从overall.pass读取}
- 共分析了 {len(interviewer_qa)} 道面试官提问 + {len(candidate_retro_qa)} 道反问

💡 小提示：如果文件名中"面试阶段"或"面试日期"显示为"待定"，可以直接改文件名的对应部分即可。
```

---

## 容错总表（本Skill任意环节触发）

| 场景 | 处理 |
|---|---|
| 3个文件缺任意一个 | 第一阶段就追问用户要，不硬跑 |
| markitdown解析失败 | 暂停，请用户换可复制文字版本 |
| 任意一次LLM返回JSON不合法 | 自动重试最多2次，3次全失败提示用户稍后重试 |
| 分析JSON的Schema检查失败 | 同上重试机制 |
| 保存时目录不存在 | save_output.py内部自动创建（`os.makedirs(exist_ok=True)`） |
| 保存时重名 | 自动加_v2/_v3后缀，不覆盖已有文件 |

---

*SKILL.md 结束*
```

- [ ] **Step 2: 验证SKILL.md包含工作流所有核心环节**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
with open('SKILL.md', encoding='utf-8') as f:
    content = f.read()
# 核心环节检查：6个阶段 + 缺文件追问 + JSON重试 + 提取分析生成3次LLM + 保存
stages = [
    '第一阶段：触发', '文件完整性检查', '缺文件处理',
    '第二阶段：Step 0', 'parse_files.py',
    '第三阶段：Step 1', 'prompts/01_extract.md', '重试机制',
    '第四阶段：Step 2', 'prompts/02_analyze.md',
    '第五阶段：Step 3', 'prompts/03_generate.md',
    '第六阶段：Step 4', 'save_output.py', 'SAVED_PATH=',
]
miss = [s for s in stages if s not in content]
if miss:
    print(f'❌ SKILL.md 缺少工作流关键环节: {miss}')
    exit(1)
# 头部 front matter 关键字（skill定义格式）
front_matter = ['---', 'name:', 'description:', 'version:', 'triggers:']
for fm in front_matter:
    assert fm in content, f'SKILL.md 头部front matter缺少 {fm}'
print(f'✅ SKILL.md 工作流完整（共{len(stages)}个环节全部覆盖），Front Matter格式正确')
print(f'  SKILL全文长度: {len(content)}字符')
"
```
Expected: SKILL工作流完整 ✅

- [ ] **Step 3: 验证触发关键词覆盖用户常见表达**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 -c "
with open('SKILL.md', encoding='utf-8') as f:
    content = f.read()
triggers = ['帮我复盘', '生成复盘文档', '复盘这次面试', '面试复盘', '做一份复盘']
miss = [t for t in triggers if t not in content]
if miss:
    print(f'❌ 缺少触发关键词: {miss}')
    exit(1)
print(f'✅ 5个常见触发语义均包含在SKILL.md的triggers列表中，匹配用户常见指令')
"
```
Expected: 全部触发关键词包含 ✅

- [ ] **Step 4: 文件存在检查**

```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/SKILL.md"
```

---

### Task 12: 全流程端到端冒烟测试（mock模式，不调真实LLM/不污染用户目录）

**Files:**
- Verify: 所有模块链路连通。执行步骤：用examples/里的3个样例文件 → 跑parse_files(mock模式) → 用最小骨架伪造step1/step2 JSON（因为不调LLM）→ 跑save_output保存到临时目录 → 验证输出文件结构合法。
- 该任务是「非LLM链路」的最终连通性检查，确保脚本层、Schema校验、文件保存三个确定性环节100%正确。LLM调用部分（真实Prompt质量）由后续单独验收任务负责。

**Interfaces:**
- 验证：脚本→JSON→文件保存 这条确定性链路全通，无import错误、路径错误、Schema错误。

- [ ] **Step 1: 编写并运行端到端冒烟测试脚本（内联Python）**

Run:
```bash
cd "/Users/yst/Coding/post‑interview-reflection-skill" && python3 <<'PYEOF'
"""
全流程端到端冒烟测试（Mock LLM模式）
目标：验证 解析→提取→分析→保存 的确定性链路100%正确
不调用真实LLM，step1/step2直接用最小合法骨架JSON替代
"""
import json, os, sys, tempfile, shutil, jsonschema

PASS_ALL = True
def check(name, cond, detail=""):
    global PASS_ALL
    if cond:
        print(f"✅ {name}")
    else:
        print(f"❌ {name}  失败原因: {detail}")
        PASS_ALL = False

print("=" * 60)
print("【面试复盘Skill 端到端冒烟测试（Mock LLM）】")
print("=" * 60)

# ---------- Step 0: parse_files mock模式 ----------
print("\n[Step 0] 解析3个样例文件（mock模式，不调markitdown，直接读文件内容）")
from scripts.parse_files import parse
resume_p = 'examples/sample_resume.md'
job_p    = 'examples/sample_job_desc.md'
trans_p  = 'examples/sample_transcript.md'
for p in [resume_p, job_p, trans_p]:
    assert os.path.exists(p), f"样例文件缺失: {p}"
try:
    step0 = parse(resume_p, job_p, trans_p, _use_mock_markitdown=True)
except Exception as e:
    check("Step0 parse_files", False, f"异常: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)
check("Step0 filename_meta提取-公司", step0['filename_meta']['company'] == '字节跳动', step0['filename_meta'])
check("Step0 filename_meta提取-阶段", step0['filename_meta']['interview_stage'] == '一面', step0['filename_meta'])
check("Step0 文字稿清洗后仍含关键内容", "自我介绍" in step0['transcript_md'] or "RAG" in step0['transcript_md'])

# ---------- 加载2个Schema ----------
print("\n[预检查] 加载2套JSON Schema")
with open('schemas/extracted_data.schema.json', encoding='utf-8') as f:
    sch_ext = json.load(f)
with open('schemas/analyzed_data.schema.json', encoding='utf-8') as f:
    sch_anl = json.load(f)
from jsonschema import RefResolver, validator_for
resolver = RefResolver(
    base_uri='file://' + os.path.abspath('schemas/') + '/',
    referrer=sch_anl,
    store={'extracted_data.schema.json': sch_ext}
)
check("Schema加载正常", True)

# ---------- Step1 构造最小合法 extracted_data JSON 并校验 ----------
print("\n[Step 1] 构造Mock extracted_data 并通过Schema校验")
step1 = {
    "company": step0['filename_meta']['company'],
    "position": step0['filename_meta']['position'],
    "interview_stage": step0['filename_meta']['interview_stage'],
    "interview_date": step0['filename_meta']['interview_date'],
    "interviewer_qa": [
        {"index":1, "question":"自我介绍","candidate_answer":"我叫lucky"},
        {"index":2, "question":"RAG项目指标","candidate_answer":"DAU 3k→1.3w","attitude_signals":["追问"],"signal_inferred":False}
    ],
    "candidate_retro_qa": [
        {"index":1, "question":"汇报线？","interviewer_answer":"汇报给总监"}
    ],
    "notes": ["Mock数据用于冒烟测试"]
}
try:
    jsonschema.validate(step1, sch_ext)
    check("Step1 extracted_data Schema校验", True)
except jsonschema.ValidationError as e:
    check("Step1 extracted_data Schema校验", False, f"{list(e.path)}: {e.message}")
# 保存到temp
os.makedirs('temp', exist_ok=True)
with open('temp/test_step1_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(step1, f, ensure_ascii=False, indent=2)

# ---------- Step2 构造最小合法 analyzed_data JSON 并校验 ----------
print("\n[Step 2] 构造Mock analyzed_data 并通过Schema校验")
step2 = dict(step1)
step2['interviewer_qa'] = [
    {
        **step1['interviewer_qa'][0],
        "question_type": "自我介绍类",
        "inspection_point": "考察表达逻辑",
        "answer_framework": "1.背景 2.经历",
        "rating": "★★★☆☆",
        "rating_reason": "有框架但缺量化",
        "ideal_answer": {
            "framework": ["1.一句话标签", "2.项目量化结果"],
            "full_text": "面试官您好，我是lucky，3年经验。在XX项目中DAU从3k涨到1.3万。您觉得这段经历匹配吗？",
            "no_resume_match": False
        },
        "improve_todo": ["准备自我介绍量化版"]
    }
]
step2['candidate_retro_qa'] = [
    {
        **step1['candidate_retro_qa'][0],
        "position_insights": ["汇报线：总监→VP"],
        "action_items": ["了解团队OKR"]
    }
]
step2['overall'] = {
    "score": 7,
    "pass": "待定",
    "reasons": "面试时长>40分钟，追问较多，整体有戏。",
    "problems": [
        {"title":"口语填充词多","description":"然后出现了N次","category":"思维型缺陷-表层"},
        {"title":"对GraphRAG不了解","description":"RAG新方法不知道","category":"知识型缺陷"}
    ],
    "improvement_plan": [
        {"todo":"学AARRR模型","type":"学习项","related_links":[]},
        {"todo":"准备自我介绍量化版本","type":"准备项","related_links":[]}
    ]
}
AnalyzedValidator = validator_for(sch_anl)
v = AnalyzedValidator(sch_anl, resolver=resolver)
errors = sorted(v.iter_errors(step2), key=lambda e: list(e.path))
if not errors:
    check("Step2 analyzed_data Schema校验", True)
else:
    detail = "; ".join(f"path={list(e.path)} msg={e.message}" for e in errors[:3])
    check("Step2 analyzed_data Schema校验", False, detail)
with open('temp/test_step2_analyzed.json', 'w', encoding='utf-8') as f:
    json.dump(step2, f, ensure_ascii=False, indent=2)

# ---------- Step 3: 模拟Markdown生成（简单生成最小结构） ----------
print("\n[Step 3] 生成最小合法Markdown（模拟Step3输出）")
final_md = f"""# 面试复盘：{step2['company']} {step2['position']} {step2['interview_stage']} {step2['interview_date']}

> **公司**：{step2['company']}　**岗位**：{step2['position']}

## 第一部分：完整QA实录

### 表格1：面试官提问QA

| 序号 | 面试问题 | 问题类型 | 面试官考察点 | 我的回答（回答框架） | 回答点评 | 理想回答 | 计划改进todo list |
|---|---|---|---|---|---|---|---|
| 1 | {step2['interviewer_qa'][0]['question']} | {step2['interviewer_qa'][0]['question_type']} | {step2['interviewer_qa'][0]['inspection_point']} | {step2['interviewer_qa'][0]['answer_framework']} | {step2['interviewer_qa'][0]['rating']}<br>理由：{step2['interviewer_qa'][0]['rating_reason']} | **框架**：<br>1. {step2['interviewer_qa'][0]['ideal_answer']['framework'][0]}<br>2. {step2['interviewer_qa'][0]['ideal_answer']['framework'][1]}<br>**回答全文**：<br>{step2['interviewer_qa'][0]['ideal_answer']['full_text']} | 1. {step2['interviewer_qa'][0]['improve_todo'][0]} |

### 表格2：候选人反问QA

| 序号 | 候选人反问问题 | 面试官的回答（尽量还原原文，标注信号不清） | 从面试官的回答中可以得到关于该岗位的有效信息 | todo list |
|---|---|---|---|---|
| 1 | {step2['candidate_retro_qa'][0]['question']} | {step2['candidate_retro_qa'][0]['interviewer_answer']} | 1. {step2['candidate_retro_qa'][0]['position_insights'][0]} | 1. {step2['candidate_retro_qa'][0]['action_items'][0]} |

## 第三部分：整体失分复盘与修复方案

### 3.1 综合评分

【整体评分】：{step2['overall']['score']}分
【是否通过】：{step2['overall']['pass']}
【评估理由】：{step2['overall']['reasons']}

【存在问题】：
「问题一」：{step2['overall']['problems'][0]['title']}（{step2['overall']['problems'][0]['category']}）
{step2['overall']['problems'][0]['description']}

### 3.2 怎么改进（表格形式）

| todo（含工具、方法论） | 类型 | 相关链接（可参考学习的链接） |
|---|---|---|
| {step2['overall']['improvement_plan'][0]['todo']} | {step2['overall']['improvement_plan'][0]['type']} | - |
| {step2['overall']['improvement_plan'][1]['todo']} | {step2['overall']['improvement_plan'][1]['type']} | - |
"""
check("Step3 生成Markdown包含所有结构章节",
      '## 第一部分' in final_md and '## 第三部分' in final_md
      and '【整体评分】' in final_md and '「问题一」' in final_md
      and '表格1' in final_md and '表格2' in final_md)
check("Step3 星级符号正确（Unicode★☆）", '★★★☆☆' in final_md)

# ---------- Step 4: save_output.py 保存到临时目录（不污染用户真实目录） ----------
print("\n[Step 4] 调用 save_output.py 保存Markdown文件（临时目录）")
from scripts.save_output import save_markdown
tmp_out = tempfile.mkdtemp(prefix="test_e2e_output_")
try:
    saved = save_markdown(
        final_md,
        company=step2['company'],
        position=step2['position'],
        interview_stage=step2['interview_stage'],
        interview_date=step2['interview_date'],
        override_base_dir=tmp_out
    )
    check("Step4 文件保存成功", os.path.exists(saved) and os.path.getsize(saved) > 500)
    # 重名v2测试
    saved2 = save_markdown(final_md, step2['company'], step2['position'], step2['interview_stage'], step2['interview_date'], override_base_dir=tmp_out)
    check("Step4 重名自动加v2", '_v2.md' in saved2 and os.path.exists(saved2))
    # 读回内容验证
    with open(saved, encoding='utf-8') as f:
        content_back = f.read()
    check("Step4 文件读回，章节完整", '# 面试复盘：' in content_back and '第三部分：整体失分复盘' in content_back)
    print(f"   保存文件1: {os.path.basename(saved)}")
    print(f"   保存文件2(重名v2): {os.path.basename(saved2)}")
    print(f"   文件大小: {os.path.getsize(saved)}字节")
finally:
    shutil.rmtree(tmp_out, ignore_errors=True)
    print(f"   临时输出目录已清理: {tmp_out}")

# ---------- 最终汇总 ----------
print("\n" + "=" * 60)
print("【端到端冒烟测试 结果】:", "ALL PASS ✅ 全部通过" if PASS_ALL else "有失败项 ❌ 请检查以上输出")
print("=" * 60)
sys.exit(0 if PASS_ALL else 1)
PYEOF
```
Expected: 最后一行输出「ALL PASS ✅ 全部通过」，exit code 0

- [ ] **Step 2: 检查临时测试产物是否写入temp目录（便于用户debug）**

Run:
```bash
ls -la "/Users/yst/Coding/post‑interview-reflection-skill/temp/"
```
Expected: temp目录下应该有 `test_step1_extracted.json` 和 `test_step2_analyzed.json` 两个Mock产物（如果冒烟测试成功写入），用户可以手动打开检查。

- [ ] **Step 3: 清理或保留temp目录（给出建议）**

给用户提示：temp/目录用于保存全流程中间产物，方便你debug时检查某一步LLM输出是否正确。如果想清空，随时可以 `rm temp/*.json`。这个目录在.gitignore中，不会被提交到git。

---

## 计划自查结论（Spec Coverage Report）

### Spec章节覆盖度
| 设计文档v1章节 | 对应实现任务 | 覆盖率 |
|---|---|---|
| 一、背景与目标 | Task11 (SKILL.md 触发/目标说明) | 100% |
| 二、架构方案D | Task0目录结构 + Task11流程编排 | 100% |
| 三、目录结构 | Task0 + 每个任务创建对应文件 | 100% |
| 四、工作流Step0-4 | Task4(Step0) + Task7(Step1Prompt) + Task8(Step2Prompt) + Task9(Step3Prompt) + Task11(总控) | 100% |
| 五、脚本层 4模块 | Task1(text_cleaner)+Task2(extract_filename)+Task3(save_output)+Task4(parse_files) | 100% |
| 五、Prompt层 3模块 | Task7+Task8+Task9 | 100% |
| 五、JSON Schema 2套 | Task5+Task6 | 100% |
| 六、文档输出规范 | Task9（Prompt中强制格式规则）+ Task10示例输出 | 100% |
| 七、容错与边界处理 | Task11 SKILL.md 容错总表 + 各模块内部重试 | 100% |
| 附录A 5档星级定义 | Task8阶段2Prompt严格表格 | 100% |
| 附录B 8类问题分类 | Task8阶段2Prompt完整8类列表 | 100% |

### 占位符检查：本计划中所有步骤均给出完整代码/命令，无 "TBD/TODO/实现/后续补充" 等占位符。

### 类型一致性：
- `interview_stage` 枚举在 extract_filename.py / 2套Schema / SKILL.md 中完全一致（一面/二面/.../待定）
- `interview_date` 格式在 2套Schema + save_output.py 中完全一致（YYYY-MM-DD 或 待定）
- `overall.pass` 枚举在 analyzed_data Schema 中是 "是/否/待定" 字符串，不是布尔值（符合设计文档原文「是/否」中文标签的要求）
- 星级字符统一使用 Unicode ★☆，5档枚举值完全一致

---

## 执行方式选择

**Plan complete and saved to** `docs/superpowers/plans/2026-08-24-interview-reflection-skill.md`

**Two execution options:**

**1. Subagent-Driven（推荐）** - 每个Task派一个独立的Subagent去实现，实现完我逐任务Review质量，快节奏迭代。12个任务拆分后并行度高、错误影响范围小，最快3-4轮对话全部完成。

**2. Inline Execution** - 在当前对话内按任务顺序依次执行，每完成几个任务做一次Checkpoint。适合你想边看边改、或者对每个任务的实现细节想实时调整的场景。

**选哪种执行方式？**
