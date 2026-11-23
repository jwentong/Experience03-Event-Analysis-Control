# AI使用记录

## 需求
让 AI 阅读实验规范 PRD 与仓库 README、状态表和服务接口说明，给出四个函数的实现：摘挂机检测、号码分析、呼叫控制和超时处理，并要求不修改 runtime、switch 与 grading。提示词中明确要求先解释状态表每一行对应的动作，再逐条落成代码，最后给出可自查的日志证据而不是只报通过数。

## 建议与采纳
采纳：采样比较用 sorted() 固定事件顺序，并先校验用户集合与 0/1 取值再比较，抛 ValueError。采纳：号码分析先判非法字符与超长，再判前缀，避免非法输入被前缀逻辑掩盖。修改：AI 建议收号阶段每个数字都追加一次 STOP_DIAL_TONE，我保留该行为但逐条核对日志，确认它只影响动作列表、不改变状态与定时器。拒绝：AI 曾建议在控制函数里硬编码 1001 至 1004，我改为从交换机配置 s.numbers 读取拨号计划，使号码分析可以配置驱动。拒绝：AI 建议在应答时直接置 CONNECTED，我坚持先 activate 再按返回值决定 CONNECTED 或 NETWORK_BUSY。

## 验证证据
手算：sample_frame(0) 链路0 的 TS1=3、TS2=6，接通后输出 TS1=6、TS2=3，释放后两槽均为 0xD5。运行命令：pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q 得 27 passed；python -m src.run_experiment 得 Scenarios passed: 12/12；pytest grading student_tests -q 全部通过。日志核对：5000ms 旧 DIAL 超时与 10400ms 旧 RING 超时在 call_events.jsonl 中 before 与 after 相同、actions 为空，证明 token 校验生效。
