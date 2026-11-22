# AI使用记录

## 需求

本次需求是依据实验三PRD、README和状态表完成四用户教学交换机的事件驱动控制，包括摘挂机检测、号码分析、呼叫控制和超时处理；补充至少一个自拟测试，生成12个集成场景与实际T/S字节结果，填写REPORT.md、AI_LOG.md和Word报告，并提交到教师仓库的Pull Request。待解决的核心问题是把号码分析、振铃、应答、双向前向话路和过期定时器正确串起来。

## 建议与采纳

AI建议使用统一状态机处理COLLECTING、RINGING、CONNECTED和ENDED；号码分析直接读取运行时`dial_plan`；所有结束路径统一调用`finish`；超时先比较token和`timer_kind`，再按状态处理。上述建议被采纳，因为它们直接对应PRD状态表且可以通过公开测试和实际字节验证。未采纳“看到被叫OFFHOOK就直接置CONNECTED”的方案，因为`activate`可能因网络拒绝而失败，必须以返回值确认双向映射。AI没有修改`src/runtime.py`、`src/switch_*.py`、`grading`或工作流。

## 验证证据

先运行四个任务测试得到27 passed。运行`python -m src.run_experiment`得到Scenarios passed: 12/12，生成`results/scenario_results.json`、`results/call_events.jsonl`和`results/call_sequence.png`。日志显示正常场景在400 ms进入RINGING、800 ms进入CONNECTED、1000 ms以NORMAL_CLEAR释放；无人接听在10400 ms以NO_ANSWER结束；5000 ms旧DIAL不改变状态。读取实际字节得到输入TS1=3、TS2=6，输出TS1=6、TS2=3，释放后0xD5。自拟测试得到2 passed，联合运行`python -m pytest grading student_tests -q`得到39 passed。
