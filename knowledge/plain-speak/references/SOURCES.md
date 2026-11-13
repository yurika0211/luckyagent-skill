# 名词表来源

本 skill 的译名来自人类写的开源对照表，不是模型现编的。

| 文件 | 来源 | 许可 | 条数 |
|---|---|---|---|
| `computerese.tsv` | [EarsEyesMouth/computerese-cross-references](https://github.com/EarsEyesMouth/computerese-cross-references) | MIT | 1024 |
| `cjk.tsv` | [dahlia/cjk-compsci-terms](https://github.com/dahlia/cjk-compsci-terms) `tables/*.yaml` 的大陆中文列 | CC-BY-SA-4.0 | 234 |
| `overrides.tsv` | 本仓库 | MIT | 覆盖冲突译名，并补开源表没有的词 |

导入优先级：`overrides` > `cjk` > `computerese`。同一 slug 只留一条中文。

## 故意没打进 git 的表

- [JuanitoFatas/Computer-Science-Glossary](https://github.com/JuanitoFatas/Computer-Science-Glossary)（约 873 条）：仓库没有 SPDX 许可，不复制进本 MIT 仓。本机可用 `glossary.py import-juanito` 从上游拉进自己的 SQLite。
- [机器之心 AI 术语库](https://github.com/jiqizhixin/Artificial-Intelligence-Terminology-Database)（约 2442 条）：CC BY-NC-SA 4.0，不能放进 MIT 仓。本机可用 `glossary.py import-jiqizhixin`。

## 次数从哪来

`term_freq.seen_count` 只统计用户消息里这个词出现过几次。默认扫本机 Claude Code 对话：`~/.claude/projects/*/*.jsonl`。不是模型估计，也不是词表自带的。
