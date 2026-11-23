# AI使用记录

## 需求
实现实验三四个学生任务函数：src/hooks.py detect_hook_events（摘挂机检测）、src/numbering.py analyze_number（号码分析）、src/control.py handle_call_event（呼叫控制）、src/timeouts.py handle_timeout（超时处理），并生成 REPORT.md 与 AI_LOG.md、自拟测试及运行结果文件。

## 建议与采纳
采用事件驱动状态机实现，严格遵循 README 状态表：COLLECTING 收号、RINGING 振铃、CONNECTED 通话、ENDED 结束。采纳了“旧 token 直接忽略”“DIGIT 仅接受主叫在 COLLECTING 时输入”“仍摘机用户进入 WAIT_ONHOOK 集合”等框架约束。拒绝了直接修改 hooks 置 0 的做法，改为仅在真实 ONHOOK 后让框架处理 waiting 集合。

## 验证证据
运行命令：`/f/anaconda/python.exe -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q`，结果 27 passed。
运行命令：`/f/anaconda/python.exe -m pytest grading student_tests -q`，全部通过。
运行命令：`/f/anaconda/python.exe -m src.run_experiment`，生成 scenario_results.json（passed=12, total=12）、call_events.jsonl、call_sequence.png。
手算验证：正常呼叫状态 COLLECTING→RINGING→CONNECTED→ENDED；无人接听 400ms 振铃、10400ms NO_ANSWER；旧收号超时在 5000ms 被忽略且前后状态相同。
