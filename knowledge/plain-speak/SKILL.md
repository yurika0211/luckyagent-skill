---
name: plain-speak
description: "说人话：句子必须有主语、谓语、宾语；术语只用开源名词表里的中文，禁止另造译名；第一次出现的概念当场解释，熟词不加括号。用户说黑话、看不懂、说人话、别造词、主谓宾、解释术语、glossary、名词表时使用。回复前先查本地 SQLite 词频。"
version: 1.0.0
license: MIT
metadata:
  tags: [writing, glossary, terminology, plain-language]
---

# plain-speak

译名来自 `references/*.tsv`（人类写的开源对照，见 `references/SOURCES.md`）。次数来自本机对话，存在用户目录的 SQLite，不进 git。

库默认路径：`$PLAIN_SPEAK_DB`，否则 `~/.claude/plain-speak/glossary.sqlite`。

第一次用：

```bash
python3 SKILL_DIR/scripts/glossary.py init
```

回复前：

```bash
python3 SKILL_DIR/scripts/glossary.py lookup --slugs cache,thread,agent
# 本轮没用的词不要全表倒出来。默认 lookup 只列出还要解释的词：
python3 SKILL_DIR/scripts/glossary.py lookup
python3 SKILL_DIR/scripts/glossary.py lookup --all
```

回复结束后，把本轮实际用到的 slug 记一次：

```bash
python3 SKILL_DIR/scripts/glossary.py bump --slugs cache,thread
```

## 句子

每句要有人、动作、对象。禁止无主语句、禁止一串名词堆砌。

差：缓存命中率下降导致延迟升高。
好：服务器没有在缓存里找到数据，所以用户等得更久。

## 译名

只许用 `lookup` 给出的中文。词表没有的词只写英文，不要编中文。第一次写：中文（English）。

禁止另译。缓存就是缓存，不是高速暂存区。

冲突译名以 `overrides.tsv` 为准（例如 agent = 智能体，不是开源表里的「代理」）。

## 什么时候解释

`lookup` 对每个 slug 给出一档。阈值默认 5，可用 `--threshold` 改。

| 档 | 条件 | 写法 |
|---|---|---|
| `first` | `seen_count = 0` | 必须解释：中文（English）+ 词表那句人话，或自己写一句完整的话 |
| `explain` | `0 < seen_count < 5` | 中文（English），可不加长定义 |
| `bare` | `seen_count ≥ 5` | 只写中文 |

次数来自真实用户消息，不是模型估计。重新从对话统计：

```bash
python3 SKILL_DIR/scripts/glossary.py seed-transcripts
```

## 解释怎么写

一句完整的话，说明它做什么。不要循环定义。

差：缓存是一种缓存机制。
好：缓存（cache）是一块近的临时存放处，同样的数据下次不用再去远处取。

## 不要做的

- 不要把所有术语都加括号
- 不要在 `bare` 词上讲课
- 不要用词表以外的中文译名
- 不要写无主语的技术电报
- 不要把 `JuanitoFatas` / 机器之心的原文复制进本仓库（许可不允许）
