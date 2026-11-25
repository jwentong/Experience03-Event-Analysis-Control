# AI使用记录
## 需求

本次实验三用AI辅助补全四个任务函数：src/hooks.py的detect_hook_events、src/numbering.py的analyze_number、src/control.py的handle_call_event、src/timeouts.py的handle_timeout。允许改动的只有这四个文件以及REPORT.md、AI_LOG.md、student_tests/test_my_case.py；src/runtime.py、src/switch_*.py、grading和workflow保持教师版本，不修改测试换通过。提示中要求先读README状态表与runtime职责，再按“事件→状态→服务调用”的顺序一次只补一个函数。

## 建议与采纳

AI建议先读src/runtime.py和src/scenarios.py再写代码，确认Call由框架创建、arm/cancel/finish/reserve/activate由框架提供，控制函数只负责状态迁移和动作名，我采纳后避免了重复实现事件队列。AI建议hooks先校验集合与取值再逐用户比较，保证非法输入不产生半截事件，我采纳。号码分析上AI建议先判长度和非法字符，再判完整号与前缀，我采纳并补充了空串按前缀处理为INCOMPLETE的细节。超时处理上AI建议先比对token与timer_kind再按状态分支，这样旧定时器自然被忽略，我采纳；同时按状态表区分通话中NORMAL_CLEAR与通话前CALLER_CANCEL。

## 验证证据

手算证据：0ms摘机、400ms拨完1002、800ms被叫应答，帧0的TS1=3、TS2=6在输出帧1变为6、3，释放后为0xD5=213。命令证据：python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q为27 passed；python -m src.run_experiment为12/12场景通过并生成三个结果文件；python -m pytest grading student_tests -q全部通过；本地评分脚本输出实验70/70、报告30/30。
