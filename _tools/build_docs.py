# -*- coding: utf-8 -*-
"""把 myportfolio_zhouym 里的 md 文档渲染成静态 HTML 页面。
只读源文件，输出到 works/docs/。改动源文档后重跑本脚本即可。
用法： python _tools/build_docs.py
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "..", "myportfolio_zhouym")
OUT = os.path.join(ROOT, "works", "docs")

DOCS = [
    # (源文件, 输出名, 分类键, 分类名, 一句话说明)
    ("【原型】智慧营业厅AI工作台/01-PRD-企业级补充版-v0.1.md", "lingshou-prd",
     "lingshou", "智慧营业厅 AI 工作台", "角色权限矩阵、状态机、客户端 30 分钟锁、AI 三段能力边界、15 条验收场景"),
    ("【原型】智慧营业厅AI工作台/02-异常兜底-合规-发布运维.md", "lingshou-risk",
     "lingshou", "智慧营业厅 AI 工作台", "21 类异常矩阵、五级降级链、个人信息处理映射、审计字段、告警与灰度回滚"),
    ("【原型】智慧营业厅AI工作台/03-评估指标与面试讲述稿.md", "lingshou-eval",
     "lingshou", "智慧营业厅 AI 工作台", "三层指标体系、210 题评估集、标注一致性要求、上线验收清单"),
    ("【原型】衡数ChatBI/衡数ChatBI-PRD.md", "chatbi-prd-v1",
     "chatbi", "衡数 ChatBI Studio", "产品定位、五个模块、指标口径、验收标准与风险清单（v1.0）"),
    ("【原型】衡数ChatBI/01-PRD-v0.2-企业级补充版.md", "chatbi-prd-v2",
     "chatbi", "衡数 ChatBI Studio", "七个角色权限、行级隔离由执行层强制、指标生命周期、语义层版本化、成本控制"),
    ("【原型】衡数ChatBI/02-评估方案与看板设计.md", "chatbi-eval",
     "chatbi", "衡数 ChatBI Studio", "200 题分层评估集、四级判定标准、三组消融实验、看板字段与采集口径"),
    ("【原型】衡数ChatBI/03-权限合规与发布运维.md", "chatbi-ops",
     "chatbi", "衡数 ChatBI Studio", "四道防线、输出约束十条、P0—P3 故障分级、影子比对、SLA 与发布流程"),
    ("业务场景skills/00-Skill作品集说明.md", "skills-overview",
     "skills", "业务场景 Skill 包", "四个 Skill 包的定位、两层路由设计、已实现与设计推演的边界"),
    ("业务场景skills/网络域投诉工单处理skill/看不见工单，场景分析以及日常处理方法.md", "workorder-notes",
     "skills", "业务场景 Skill 包", "七类工单查不到原因的原始场景笔记，含处置 SQL 与判断顺序"),
]

# 页面标题覆盖：源文件名里的字样不直接当标题用
TITLES = {
    "lingshou-prd": "智慧营业厅 AI 工作台 · PRD",
    "chatbi-prd-v2": "衡数 ChatBI Studio · PRD v0.2（权限与治理）",
}

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ITALIC = re.compile(r"(?<![\*\w])\*([^\*<]+)\*(?!\*)")


def inline(text):
    out = html.escape(text)
    out = LINK.sub(lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), out)
    out = INLINE_CODE.sub(lambda m: "<code>%s</code>" % m.group(1), out)
    out = BOLD.sub(lambda m: "<strong>%s</strong>" % m.group(1), out)
    out = ITALIC.sub(lambda m: "<em>%s</em>" % m.group(1), out)
    return out


def slug(text, used):
    s = re.sub(r"[^\w\u4e00-\u9fa5]+", "-", text).strip("-").lower()[:40] or "s"
    base, i = s, 1
    while s in used:
        i += 1
        s = "%s-%d" % (base, i)
    used.add(s)
    return s


def render(md):
    lines = md.split("\n")
    out, toc = [], []
    used = set()
    i, n = 0, len(lines)
    para = []

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para).strip()))
            para.clear()

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # 代码块
        if stripped.startswith("```"):
            flush_para()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(buf)))
            continue

        # 表格
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            flush_para()
            head = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ['<div class="tw"><table><thead><tr>']
            t += ["<th>%s</th>" % inline(c) for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue

        if stripped.startswith("#"):
            flush_para()
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            level = min(level, 4)
            if level == 1:
                # 标题已在页头渲染，正文首行不再重复
                if not out:
                    i += 1
                    continue
                out.append("<h1>%s</h1>" % inline(text))
            else:
                sid = slug(text, used)
                out.append('<h%d id="%s">%s</h%d>' % (level, sid, inline(text), level))
                if level == 2:
                    toc.append((sid, text))
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,})$", stripped):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            flush_para()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(buf)))
            continue

        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if m:
            flush_para()
            ordered = bool(re.match(r"^\d", m.group(2)))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n:
                mm = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", lines[i])
                if not mm or bool(re.match(r"^\d", mm.group(2))) != ordered:
                    break
                items.append("<li>%s</li>" % inline(mm.group(3).strip()))
                i += 1
            out.append("<%s>%s</%s>" % (tag, "".join(items), tag))
            continue

        if not stripped:
            flush_para()
            i += 1
            continue

        para.append(stripped)
        i += 1

    flush_para()
    return "\n".join(out), toc


TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · 周一鸣作品集</title>
<link rel="stylesheet" href="../../assets/doc.css">
</head>
<body>
<header class="top">
  <div class="top__in">
    <a class="back" href="../../index.html#docs">← 返回作品集</a>
    <span class="crumb">__GROUP__</span>
    <a class="dl" href="../../index.html#contact">联系我</a>
  </div>
</header>
<main>
  <div class="doc__head">
    <p class="doc__kicker">__GROUP__ · 文档</p>
    <h1 class="doc__title">__TITLE__</h1>
    <p class="doc__lede">__LEDE__</p>
    <p class="doc__meta">源文件 <code>__SRC__</code> · 约 __CHARS__ 字 · __DATE__</p>
  </div>
  <div class="doc__body">
__TOC__
    <article class="doc__article">
__BODY__
    </article>
  </div>
  <div class="doc__foot">
    <a href="../../index.html#docs">← 全部文档</a>
  </div>
</main>
</body>
</html>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for src, slugname, group_key, group, lede in DOCS:
        path = os.path.join(SRC, src)
        if not os.path.exists(path):
            print("缺失: " + src)
            continue
        md = open(path, encoding="utf-8").read()
        body, toc = render(md)
        title = TITLES.get(slugname)
        if not title:
            m = re.search(r"^#\s+(.+)$", md, re.M)
            title = m.group(1).strip() if m else slugname
        toc_html = ""
        if len(toc) >= 3:
            toc_html = '<nav class="toc"><p class="toc__t">本页目录</p><ol>' + "".join(
                '<li><a href="#%s">%s</a></li>' % (s, html.escape(t)) for s, t in toc) + "</ol></nav>"
        page = (TPL.replace("__TITLE__", html.escape(title))
                   .replace("__GROUP__", html.escape(group))
                   .replace("__LEDE__", html.escape(lede))
                   .replace("__SRC__", html.escape(src))
                   .replace("__CHARS__", "{:,}".format(len(md)))
                   .replace("__DATE__", "2026-10")
                   .replace("__TOC__", toc_html)
                   .replace("__BODY__", body))
        dst = os.path.join(OUT, slugname + ".html")
        open(dst, "w", encoding="utf-8").write(page)
        made.append((slugname + ".html", len(page)))
    for name, size in made:
        print("%-26s %7d B" % (name, size))
    print("共 %d 篇" % len(made))


if __name__ == "__main__":
    sys.exit(main())
