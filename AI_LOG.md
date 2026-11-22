# AI使用记录
## 需求
2026-11-22 完成《现代交换原理》实验三时使用了 AI 助手（WorkBuddy，GLM 模型）。提供的输入为桌面上的《实验三_PRD_用户事件号码分析与呼叫控制.docx》与教师仓库 README，提出的任务为：克隆教师仓库，补全 src/hooks.py、src/numbering.py、src/control.py、src/timeouts.py 四个函数，通过全部公开测试并生成 results 三个结果文件，再按模板撰写 REPORT.md 与 AI_LOG.md。未使用 AI 的部分：环境搭建（Python venv、pip 安装依赖）和所有运行命令均按 README 在本机执行。

## 建议与采纳
AI 先通读框架源码（runtime.py 的 Exchange、switch_connections.py 的 connect_pair）和 grading 全部测试，再给出实现建议，采纳情况如下：摘挂机检测采用集合一致性检查加按编号排序差分，采纳；号码分析用"先完整匹配、再前缀匹配"的顺序，并把 SELF_CALL 判定放在 LOCAL 之前，采纳；呼叫控制按状态表逐行实现，其中"非法号码也先输出 STOP_DIAL_TONE 再 FAIL_TONE""BUSY_TONE 不带 reason 字段"两个细节是 AI 对照 examples/teacher_results/call_events.jsonl 教师参考日志核对后修正的，采纳；超时处理用 token 与 timer_kind 双重校验、ENDED 状态直接返回，采纳。AI 提醒了一个易错点：10400ms 同时刻事件顺序由入队次序决定——测试先 enqueue 应答事件、框架在处理拨号事件时才 arm 振铃定时器，故应答先处理、旧超时因 cancel 失效，无需在 handle_timeout 中加特殊逻辑，该分析经核对后采纳并写入手算。AI 建议可以直接参考教师结果文件编写日志，本人拒绝复制参考日志，所有结果文件均由本地实际运行生成。

## 验证证据
验证分三层。第一层手算：帧0 输入 TS1=3、TS2=6，接通后按 t_maps 输出应为 TS1=6、TS2=3，自拟测试断言 y[0,1]==x[0,2]==6、y[0,2]==x[0,1]==3，实际通过。第二层命令与输出：`.venv/Scripts/python.exe -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q` 输出 27 passed in 0.30s；`.venv/Scripts/python.exe -m src.run_experiment` 输出 Scenarios passed: 12/12；`python -m pytest student_tests -q` 输出 5 passed in 0.18s；`python -m pytest grading student_tests -q` 全部通过后未再改动代码。第三层结果核对：results/scenario_results.json 中 12 个场景 passed 均为 true；逐行抽查 call_events.jsonl 确认 400ms 振铃、800ms 接通、10400ms NO_ANSWER、5000ms 旧 DIAL 超时保持状态不变等关键日志与手算预期一致。
