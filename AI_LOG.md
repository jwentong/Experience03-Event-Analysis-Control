# AI 使用记录

## 需求

本次需求是补全 src/hooks.py 的摘挂机检测、src/numbering.py 的号码分析、src/control.py 的呼叫控制和 src/timeouts.py 的超时处理，并完成自拟测试与实验报告。提示词主要包括四个函数的接口说明、状态表、事件字段含义，以及在 pytest 失败时贴出完整报错原文请求定位。

## 建议与采纳

AI 建议事件 e 是字典而不是对象，应使用 e["kind"]、e["user"]、e["value"] 访问；我采纳后消除了 AttributeError。AI 建议 dial_plan 实际是列表，需要同时兼容 list 和 dict；我采纳并在号码分析中统一转成字符串列表。AI 指出非法号码的结束原因应为 INVALID 而不是 INVALID_NUMBER；我采纳并修改。AI 建议主叫首次摘机时补发 DIAL_TONE 并 arm DIAL 5000；我采纳并通过 test_dial_tone。AI 建议超时处理先判断 ENDED，再校验定时器代次与 timer_kind；我采纳后旧定时器不再影响已结束或已振铃的呼叫。AI 给出的删除测试换通过的建议我没有采纳，所有测试均保留。

## 验证证据

每一步修改后都运行对应测试：pytest grading/test_hooks.py、test_numbering.py、test_control.py、test_timeouts.py 分别通过；pytest grading student_tests -q 得到 36 passed。运行 run_experiment 生成 results/call_sequence.png、call_events.jsonl、scenario_results.json，其中 scenario_results.json 的 passed=12、total=12。call_events.jsonl 中无人接听场景保留了 5000ms 的旧 DIAL 超时事件，且 before 与 after 相同。自拟测试 pytest student_tests -q 得到 4 passed。