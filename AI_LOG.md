# AI使用记录

## 需求
使用 DeepSeek 编程助手辅助实现 `src/hooks.py`、`src/numbering.py`、`src/control.py`、`src/timeouts.py` 四个待实现函数；只修改这些任务文件，不改框架、评分测试与工作流。

## 建议与采纳
AI 建议：摘挂机检测比较前后两次采样并按键排序，相同采样返回空；号码分析先判非法字符和长度，再判前缀、完整号与自呼；呼叫控制按状态表分 OFFHOOK、DIGIT、ONHOOK 处理，完整号码先 reserve 成功再进入 RINGING；超时先校验 token 与 timer_kind 再按状态处理。本人对照 README 状态表与测试后采纳，并补上“旧定时器 token 不匹配即忽略”的边界。

## 验证证据
手算正常呼叫：0ms 摘机、100/200/300/400ms 拨 1002、800ms 应答、1000ms 挂机，状态 COLLECTING→RINGING→CONNECTED→ENDED；帧 0 的 TS1=3、TS2=6，应答后 TS1=6、TS2=3。运行 `python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q`，27 项全部通过；运行 `python -m src.run_experiment` 得 12/12 场景通过；再运行 `python -m pytest grading student_tests -q` 全部通过。
