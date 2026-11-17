# 计量标准 0.2

## 范围与原子点

project 包含已识别模块；unmodeled 显式列出尚未分析的部分。task 是明确交付目标。atom 是一个可判定问题，必须有 question、kind、closure、topic 和资料归属；work 是带验收条件的交付工作包。

kind 为 fact、decision 或 competency。事实需要与适用代码/数据版本一致；决策需要可追溯的选择和适用条件；能力需要目标用户的表现。项目决策关闭不代表对应实现完成，也不代表用户掌握。

同一项目、同类型、规范化问题完全相同的重复创建会被拒绝；语义去重仍由代理负责。跨任务复用 atom.link。依赖必须先登记，在创建原子点时引用现有同项目原子点，因此不会形成前向循环。dependencies 用于提示，不能因某个事实未明就强制阻塞一个允许带风险作出的设计决策。group 是可选的人类分类，当前不自动拟合联合概率。

## 项目与任务模型熵

候选集存在时采用等概率假设 `h=log2(N)`。候选集必须合理、非空、互斥；无法形成有限解释集时保留 null，不假装只有零未知。resolve 只能排除原有候选，并需要证据；假设失效使用 reopen，不能偷偷往旧候选集中加选项。

competency 不计入项目事实/决策总熵。其余原子点去重后的 h 求和输出为 `model_bit_upper_sum`，是加性工程近似。相关命题不能据此宣称得到精确联合熵；dependent_atoms 列出依赖，不是已估计的条件熵。未量化点、待验证点和未覆盖模块必须同时展示。即使一个暂定候选使 h=0，只要还未 resolve，项目状态仍是待关闭。

## 个人未验证负荷

每点保存工程预算 B；默认 `max(1, log2(初始候选数))`，没有候选时默认 1。代理可显式给出另一个正预算，但必须解释其基线含义，不得称其为测得的香农熵。

证据等级 c：

| 等级 | 表现要求 | 含义 |
|---|---|---|
| 0，assessed=false | 无有效用户表现证据 | 未测，不判为不会 |
| 0.25 | 能辨认相关对象 | 已验证初步识别 |
| 0.5 | 能准确解释职责、因果 | 已验证解释能力 |
| 0.75 | 能处理不同情景或有效反例 | 已验证应用能力 |
| 1 | 满足 closure 的充分验证条件 | 本点验证完成，不代表领域全部掌握 |

明确错误可记录 assessed=true、grade=0 和错误证据。只存在 AI 文档、自动测试或“懂了”的确认时不能凭空提高等级。

`U=ΣB(1-c)`，单位熵点。它量化还缺多少验证证据，不是掌握概率，也不是脑内熵。基线时保存 B 和 c；`G=U_baseline−U_current_on_baseline_atoms`。重新打开可使 G 为负。新增点影响当前 U，但不静默改变旧基线预算。明确重建基线后使用新 ID，旧报告仍可按旧 ID 重算。

全项目按唯一原子点汇总。共享原子点在一个任务学习后可供其他任务复用，但效率归属要有具体 task_id；同一次学习不应在多个任务各计一份有效工时产出。

## 交付

work 有固定 weight、acceptance、required。基线交付率是已验收基线工作包权重占比，不含基线后新增项；新增项与未通过的必需项另列。父项仅汇总，不重复计分。task.complete 至少需要一个必需工作包，且当前必需工作包全部已验证、计时已结束。撤销验收会重新打开任务。

## 时间

received_at 是有来源的任务接收时间，不默认等于注册账本的时间。只知道日期用 received_date，精确日历耗时留空。结束采用验收完成时间，未结束采用观察时钟。

所有时间有时区并转换为 UTC。occurred_at 表示事件发生时间，recorded_at 表示记账时刻。可回填已知历史事实，但不能伪造其证据；预测快照禁止回填为历史日期。

focus 为人的活动区间，phase 为 understand / execute / verify / rework / wait / mixed；AI/机器运行不是人的专注时间。默认一个个人账本管理多个项目，只有一个人的活动计时器。start/pause/switch 明确划分边界。

只统计结束、confirmed=true、precision=second 的区间。estimated、未确认和未关闭区间单列。相同任务/主题/类型重叠区间取并集；不同任务/主题/类型冲突部分从可靠时间中扣除，并阻止可靠速率，不擅自决定哪段真实。wait 单列，不计专注小时。

本地窗口/输入活动只可辅助分类。安静阅读可能是工作，持续打开编辑器也不代表持续工作。task.coverage 需要来源依据确认任务时间记录完整；它不是从“只有这些记录”推断出的完整性。

## 泛均、窄均与配对

同一个范围、基线和观察窗口下：

`泛均 = G / 精确日历天数`；`窄均 = G / 已确认同主题专注小时`。

预算和等级都是工程规则，效率单位为熵点/天、熵点/专注小时。没有基线、确认时间、完整覆盖，或有估计/冲突/未关闭区间时不给可靠速率。每个正增益原子点都要与本任务、同主题的有效计时配对；个人评估落在任务完成之后时，不回填到原任务时间窗口。

统计包含该任务窗口内失败尝试、无增益工作和返工，不能只算最后验证成功的分钟。若只覆盖了部分历史劳动，不把全部历史增益放入分子。已知执行期间熵减可能为零，不代表没有有效工作，需同时看交付。

learning_rate 仅在样本完全由 understand / verify / rework 构成时提供；含 execute/mixed 的整体速率不能用作纯澄清速率。

## 预测

只自动选同账本中、同项目、同 work_type、相同模型版本的已完成样本。登记样本前需完整时间与增益配对，使用 task.sample；每个 task/baseline 只登记一次。后续变更、撤销或工时更正使样本不匹配时会排除，不偷偷沿用。

- decomposed：`剩余 U / 纯澄清速率 + 显式 known_execution_hours`。两部分不能重叠；调试、执行与学习交织时应改用整包模式。
- whole：目标必须是一个同规模工作包；用已投入工时之后仍可能完成的同类历史样本估计剩余时长，不把短于当前已投入的历史任务截成零，也不再加执行工时。
- rate_range：调用者显式给定正速率区间的情景演算，不依赖历史，不输出概率标签。不得偷偷填一个“默认人均效率”。

至少 10 个有效同类样本才给经验 P50/P85。这是工程门槛，不是统计保证。重采样默认 2000 次、seed=17，保持可重放。计量状态、历史样本与观察时钟相同时，结果一致。

无明确每日可投入小时，不输出日历换算。提供 daily_focus_hours 后仅给固定投入下的日历天数情景，不模拟休息、任务依赖、资源竞争、并行等待和范围增长。不得把历史日历周期已经包含的等待再加一遍。

forecast --record 保存预测当时可见状态；calibration 在完成后比较预测之后的实际工时，记录 P85 覆盖率、中位绝对误差及阈值事件的 Brier 诊断。同任务多次预测有关联，不能把记录条数当独立任务数证明已校准。范围/基线改变或最终时间不完整的预测排除并解释；区间仍然宽不等于预测有用。

## 方法来源

- [PMI WBS](https://www.pmi.org/learning/library/creating-effective-wbs-recognize-quality-7541)：围绕交付拆解范围，防止父子和跨分支重复计量。
- [ETS ECD](https://www.ets.org/research/policy_research_reports/publications/report/2003/hsgs.html)：主张、证据和任务之间的对应；[Knowledge Tracing 原论文](https://perso.liris.cnrs.fr/pierre-antoine.champin/2014/m2iade-ia2/_static/893CorbettAnderson1995.pdf)：基于表现更新知识判断。当前工程等级不冒充已拟合的 BKT。
- [ActivityWatch 数据模型](https://docs.activitywatch.net/en/latest/buckets-and-events.html)：有来源的时间区间和活动分类；当前 Skill 不自动安装或后台运行活动监控。
- [Kanban Guide](https://kanbanguides.org/open-guide-to-kanban/2025.7/pdf/open-guide-to-kanban.en-us.pdf) 与 [ActionableAgile](https://55degrees.atlassian.net/wiki/spaces/AA4A/pages/2407694552/Monte%2BCarlo%2BWhen)：利用历史分布作条件时间预测。
- [Gneiting 与 Raftery](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf)：用实际结果检验概率预测与校准。
