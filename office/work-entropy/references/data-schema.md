# 事件与 CLI

## 公共入口

```bash
python3 "$HOME/.codex/skills/work-entropy/scripts/ledger.py" init
python3 "$HOME/.codex/skills/work-entropy/scripts/ledger.py" event project.add --data-file /tmp/project.json --source-ref "用户当前任务说明" --key "SOURCE_ID:project"
python3 "$HOME/.codex/skills/work-entropy/scripts/report.py" status --project PROJECT_ID
```

所有脚本支持放在子命令之前的 `--store DIRECTORY`。正常使用唯一默认个人账本；示例与测试使用独立目录。event 的数据用 UTF-8 JSON 对象文件，或短参数 --data-json；下列都是 data 的结构，不是需要手写的完整事件。

首次登记顺序：project.add → task.add → atom.add / work.add → baseline.add。代理从资料推断字段，不要求用户按表填写。新增原子点属于范围增长；需要正式使用新预算时新增基线，不覆盖旧 ID。

## 公共事件信封

程序生成 schema_version=1、model_version=0.2、递增 seq、event_id、key、intent_hash、occurred_at、recorded_at、prev_hash 与 hash。用户/代理只提供 type、data、actor、source，以及可选 --at 和 --key。

- actor：user / assistant / automation / external。focus 的活动主体只能为 user；评估由 assistant 记账时，个人证据来源仍必须是用户消息或观察到的用户行为。
- source.kind：user_message / assistant_message / artifact / test / observed_action / explicit_timer / manual_report / chat_inference / system。
- source.ref：具体文件与版本/行号、消息标识或计时事件引用；不是“据我判断”这样的空引用。程序验证结构，不替代理联网核验来源真实性。
- --at：带时区的 ISO8601；省略为当前时钟。禁止未来已发生事件，预测记录也不能回填日期。只有日期不够精确时不要补时间。
- --key：来源稳定标识。同 key、同意图的重试返回原事件；同 key 不同意图拒绝。未提供则生成新 ID；即使重复评估被记成多条事件，也不按事件数增加进度，指标由当前状态重算。

JSONL 采用文件锁、fsync 和哈希链；写入前完整重放、校验与试算。半行、损坏、未知事件和版本不兼容均报错，不自动截断。不要手工编辑已有行；用以下更正/重开事件。哈希链是意外损坏检测，不是防恶意篡改的签名。

## 项目、任务、原子点

```json
{"id":"fa","title":"FA 数据链路","unmodeled":["真实源键契约","同步实现"]}
```

project.add 必须 id/title，unmodeled 可省略。这里是已识别但尚未建模的模块列表，不是全项目覆盖百分比。

```json
{"id":"fa-identity","project_id":"fa","title":"定稿记录身份设计","work_type":"design","received_at":null}
```

task.add 必须 id/project_id/title/work_type。received_at 可空；只有日期时可另外记录 received_date，例如 2026-11-17。work_type 应稳定，例如 design/research/implementation/debugging，不能为凑足样本把不同类型都改成一样。

```json
{"id":"fa-row-identity","project_id":"fa","task_ids":["fa-identity"],"topic":"record-identity","kind":"decision","question":"本地主键是否与源记录标识分开？","closure":"明确记录生成方、源唯一范围及方案适用边界","candidates":["直接复用源键作为本地主键","本地主键由 Toolkit 生成，源记录键独立保存"],"budget":1,"dependencies":[]}
```

atom.add 必须 id/project_id/task_ids/topic/kind/question/closure。kind 为 fact/decision/competency，candidates 可空；budget 为正数，省略时按模型默认。dependencies 只引用已存在的同项目原子点。group 可作为分类标签，但不声称自动解决概率依赖。

复用知识点：`atom.link` 数据为 `{"id":"fa-row-identity","task_id":"另一任务ID"}`。不重复创建同一命题。这里的 ID 在一个账本内唯一，推荐带项目前缀。

## 项目证据、个人证据与重开

```json
{"id":"fa-row-identity","remaining":["本地主键由 Toolkit 生成，源记录键独立保存"],"reason":"已发布设计明确选择本地主键与源记录唯一键分离"}
```

atom.resolve 需要 artifact/test/user_message/observed_action 来源；remaining 必须是当前剩余候选的非空子集。一个候选时 resolved=true，但这不是个人掌握评估。

```json
{"id":"fa-row-identity","grade":0.75,"task_id":"fa-identity","reason":"用户在新的跨 FA 重复键情景中正确推演唯一范围，并解释本地主键不能代替源键去重"}
```

atom.assess 的 grade 仅为 0/.25/.5/.75/1。source.kind 必须 user_message 或 observed_action；引用真实的用户表现。自动测试、AI 产物和助手自己的解释不能直接给个人分。一个原子点关联多个任务时必须给 task_id；否则可由唯一任务推断。

`atom.reopen`：`{"id":"fa-row-identity","reason":"新反例推翻了原结论","reset_personal":true}`。恢复初始候选集，默认同时撤销个人证据积分。若只需重开项目事实而个人已理解其不确定性，可明确 reset_personal=false 并说明依据。新增独立问题用新 atom，不能修改旧候选来伪造初始熵。

## 工作包与基线

```json
{"id":"fa-design-note","task_id":"fa-identity","title":"记录身份方案文档","acceptance":["区分本地主键与源记录身份","SQL、图和写入规则一致"],"weight":1,"required":true}
```

work.add 需要 id/task_id/title/acceptance，weight 默认 1，required 默认 true。只登记叶子工作包。设计文档与对应实现是不同工作包，按当前用户任务范围登记，不能擅自把设计请求扩大为代码落地。

`work.verify`：`{"id":"fa-design-note","verified":true,"reason":"已检查对应文档、SQL 和图一致"}`，来源 artifact/test/user_message/observed_action。verified=false 撤销验收并重开任务。

```json
{"scope":"task:fa-identity","id":"fa-identity-v1","reason":"首次固定当前范围与证据状态"}
```

baseline.add 的 scope 为 task:ID 或 project:ID，自动保存当前范围的原子预算、等级、解释集和工作权重。需要至少一个原子点。版本 ID 在账本内唯一；同范围新基线成为默认，但旧基线可用 report status --baseline ID 查询。

`task.complete`：`{"id":"fa-identity"}`，至少一个必需工作包且全部通过验收、该任务计时已结束。事件时间是这次有证据的验收时间，不偷偷反推成“最早完成时刻”。`task.reopen`：`{"id":"fa-identity","reason":"工作范围或验收结果发生变化"}`。

`task.coverage`：`{"id":"fa-identity","complete":true,"reason":"用户确认全部相关专注区间均已记录，未遗漏历史投入"}`。来源必须 user_message/manual_report/observed_action，不能自动推断完整覆盖。

`task.sample`：`{"id":"fa-identity"}`。仅用于已完成、时间与进度配对且完整的任务，给后续同项目、同 work_type 预测提供历史样本。一个 task/baseline 只登记一次；纯执行零熵减仍可作为整包时长样本。

## 同主题计时

```bash
python3 "$HOME/.codex/skills/work-entropy/scripts/ledger.py" focus start --task fa-identity --topic record-identity --atom fa-row-identity --phase understand --source-ref "用户明确现在开始专注"
python3 "$HOME/.codex/skills/work-entropy/scripts/ledger.py" focus pause --source-ref "用户明确暂停"
```

switch 与 start 的参数相同，先结束上一段再开始新段。start 不允许已有活动段，pause 不允许没有活动段；切换/结束必须晚于开始。已完成任务不允许继续记录新的工作，先 reopen；可在完成后补录确实发生在完成前的历史区间。

历史回填必须来自用户/可靠活动记录，例如：

```bash
python3 "$HOME/.codex/skills/work-entropy/scripts/ledger.py" focus import --task fa-identity --topic record-identity --atom fa-row-identity --start '2026-11-17T10:00:00+08:00' --end '2026-11-17T10:30:00+08:00' --estimated --unconfirmed --source-kind chat_inference --source-ref "仅用于展示导入参数，实际使用时替换为真实来源"
```

上述日期是参数格式说明，不是用户真实工时，不要直接执行成真实记录。去掉 estimated/unconfirmed 需要有确认依据。phase 可取 understand/execute/verify/rework/wait/mixed；wait 不计人的专注小时。

漏停或错误记录更正：`focus invalidate --id INTERVAL_EVENT_ID --reason '具体原因' --source-ref '更正依据'`。更正后的新区间另外导入，原始记录保留。程序会排除不同任务、主题和 phase 的重叠冲突，不自动选择哪一段真实。

## 报告、预测、回测

```bash
python3 "$HOME/.codex/skills/work-entropy/scripts/report.py" status --task fa-identity --format json
python3 "$HOME/.codex/skills/work-entropy/scripts/report.py" forecast --task fa-identity
python3 "$HOME/.codex/skills/work-entropy/scripts/report.py" forecast --task fa-identity --rate-range 1 2 --known-execution-hours 3 --daily-focus-hours 1.5
```

最后一条仅在速率和工时由调用者明确提供时使用，不能为了出数字自行填入 1/2/3。它表示显式情景，不是通过历史学习的预测。

forecast 参数：mode=decomposed（默认）或 whole；known-execution-hours 默认 0，daily-focus-hours 未提供时不输出日历情景；seed 默认 17，simulations 默认 2000。whole 不允许额外叠加执行工时或速率区间，且需要目标已投入工时有完整依据。

```bash
python3 "$HOME/.codex/skills/work-entropy/scripts/report.py" forecast --task TASK_ID --record --source-ref "本次开始时记录的真实预测" --key "SOURCE_ID:forecast"
python3 "$HOME/.codex/skills/work-entropy/scripts/report.py" calibration --task TASK_ID --format json
```

预测快照不会接收过去的 --at，不利用后来的完成结果回填历史预测。回测只比较预测之后的剩余工时；基线/原子范围变化、时间缺失或无概率输出的情景不会装成有效概率验证。

status/forecast/calibration 均支持 --format markdown/json 和 --output PATH。默认输出到终端；显式路径存在时需 --replace，避免覆盖用户笔记。Markdown 默认最多展示 5 个原子点，JSON 保留全部。
