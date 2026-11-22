# AI使用记录
## 需求
使用 AI 编程智能体协助完成实验三的四个任务函数：摘挂机事件检测、四位号码分析、按状态表实现呼叫控制、超时处理。约束是不修改 src/runtime.py、src/switch_*.py 和 grading 目录，不得删除测试，并保证四个评分测试文件全部通过、运行 src.run_experiment 生成 results 下三个结果文件。

## 建议与采纳
AI 建议按 README 状态表把控制逻辑拆成 OFFHOOK、DIGIT、ONHOOK、TIMEOUT 四个分支，超时处理必须先校验 token 与 timer_kind 再按状态处理；并把任务拆成 hooks/numbering 与 control/timeouts 两条并行实现线。上述建议全部采纳。动作字段方面，按参考日志确认 RING 携带 user=被叫、RINGBACK 携带 user=主叫、FAIL_TONE 携带 reason。AI 曾建议把号码判断硬编码为 1001~1004，本人未采纳，改为通过 Exchange.numbers 读取配置，使配置驱动号码用例也能通过。实现完成后 AI 建议用教师参考日志做逐字段回归比对，该建议被采纳并发现无差异。

## 验证证据
手算 sample_frame(0) 的 TS1=3、TS2=6，应答后输出 TS1=6、TS2=3，释放后对应时隙为 0xD5，运行结果与手算一致。命令 .\.venv\Scripts\python.exe -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q 与 .\.venv\Scripts\python.exe -m pytest grading student_tests -q 均通过；.\\.venv\\Scripts\\python.exe -m src.run_experiment 输出 12/12 场景通过。AI 生成的代码与报告初稿均由本人复跑 pytest、核对 call_events.jsonl 日志和帧字节后才保留。
