python
import os
import re
import json
import datetime
import pathlib
import requests

API_KEY = os.environ["GROQ_API_KEY"]
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

today = datetime.date.today()
now = datetime.datetime.now()
date_str = today.strftime("%Y-%m-%d")
time_str = now.strftime("%H%M%S")

prompt = f"""
你是金融理财博客作者。请写一篇面向普通人的理财教育文章。
要求：
1. 第一行是标题，不要加“标题：”两个字。
2. 空一行，然后写正文。
3. 正文用 Markdown，800-1200 字。
4. 内容必须客观、教育性，不承诺收益，不构成投资建议。
5. 主题围绕：存钱方法、基金定投、预算管理、副业收入、保险基础、理财误区等。
6. 语言通俗，像和朋友聊天。
"""

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "你是一个严谨的金融理财内容作者。"},
        {"role": "user", "content": prompt},
    ],
    "temperature": 0.7,
    "max_tokens": 2000,
}

resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
resp.raise_for_status()
data = resp.json()
text = data["choices"][0]["message"]["content"].strip()

lines = text.splitlines()
title = lines[0].strip().lstrip("#").strip()
body = "\n".join(lines[1:]).strip()

if not title:
    title = f"理财笔记 {date_str}"

slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
if not slug:
    slug = f"post-{date_str}-{time_str}"
slug = slug[:60]

pathlib.Path("_posts").mkdir(exist_ok=True)
filename = f"_posts/{date_str}-{slug}.md"

front_matter = f"""---
layout: post
title: "{title.replace('"', '\\"')}"
date: {date_str} 08:00:00 +0800
---

"""

pathlib.Path(filename).write_text(front_matter + body, encoding="utf-8")
print(f"Generated: {filename}")
