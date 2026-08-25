---
name: interview-reflection
description: |
  【面试复盘专家】AI产品经理专属面试复盘工具。用户上传「简历PDF + 岗位介绍 + 面试录音文字稿」3个资料并说一句类似"帮我复盘这次面试"后，全自动完成：文件解析 → QA信息提取 → 逐条打分分析 → 生成规范Markdown → 保存到 Obsidian vault (/Users/yst/Documents/obsidianbase/) 目录。
  核心能力：
  1. 智能区分发言人1/2角色
  2. 标注面试官态度信号（追问/打断/表扬等）
  3. 严格5档星级点评（★★★★★到★☆☆☆☆），附具体改进理由
  4. 理想回答必须引用简历真实数据+结尾邀请讨论
  5. 整体胜算评分+思维型/知识型缺陷分析+改进方案表格
  6. 卡片式排版（### Q{序号} 独立小节）+ HTML颜色标记（11色规范，Obsidian/VSCode 可渲染）
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
- 校验规则（必须全部满足）：
  1. 开头第一个非空字符必须是 `#`（Markdown一级标题）
  2. 必须同时包含 `## 第一部分` 和 `## 第三部分`（跳过第二部分的规则）
  3. **卡片式结构**：面试官QA和反问QA都不再用表格，改用 `### Q{序号}` 独立小节 + 字段列表
  4. **HTML颜色标记**：必须包含 `<span style="color:` 标签，且包含以下关键色值：
     - `#1F3864`（深蓝小标题）
     - `#00796B`（深青问题类型）
     - `#6A1B9A`（深紫考察点）
     - `#546E7A`（蓝灰理由正文）
     - `#5D4037`（深褐todo正文）
     - `#E70DCA`（品红框架内容）
     - `#C2185B`（玫红高亮）
     - `#D32F2F` / `#F57C00` / `#388E3C`（星级三色）
  5. **反问QA序号继承**：反问第一道题的序号 = 最后一个面试官提问的index + 1
  6. **标签格式**：所有【】标签必须用 `<b><span style="color:#1F3864">【xxx】</span></b>` 包裹
- 不满足则重试最多2次：`输出格式错误，必须是卡片式结构（### Q{序号}），必须包含HTML颜色标记（#1F3864/#00796B/#6A1B9A等），开头# 面试复盘...，且必须含有第一部分/第三部分章节`
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
