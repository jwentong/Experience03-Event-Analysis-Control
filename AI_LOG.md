# AI使用记录

## 需求

本实验使用生成式人工智能作为辅助工具，主要用于梳理实验三 PRD 中的任务要求、解释事件与状态的关系、整理四个待实现函数的处理流程，并协助分析摘挂机检测、号码分析、呼叫控制和超时处理中的边界条件。提示内容包括要求 AI 根据教师提供的函数接口、状态表和测试文件给出实现建议，同时不得修改教师框架和评分测试。

## 建议与采纳

AI 辅助给出了按任务依赖顺序实现和验证的建议，并提供了代码结构示例。本人结合 `runtime.py` 中的 Exchange、Call、reserve、activate、finish、arm 和 cancel 接口，对建议逐项检查后完成代码。采纳了用户集合与采样值校验、配置驱动号码分析、应答后再激活真实话路、通过 token 和 timer_kind 过滤旧定时器等建议。对于实验结果，没有仅根据时序图判断正确性，而是进一步检查了测试、场景汇总和话路状态。教师提供的 runtime、switch 模块、grading 测试和工作流均未修改。

## 验证证据

本人分别运行了 `pytest grading/test_hooks.py -q`、`pytest grading/test_numbering.py -q`、`pytest grading/test_control.py -q` 和 `pytest grading/test_timeouts.py -q`，并运行四项联合测试，实际结果为 27 passed。随后执行 `python -m src.run_experiment`，生成时序图、事件日志和场景汇总文件，`scenario_results.json` 显示 passed=12、total=12，全部场景均为 true。另在 `student_tests/test_my_case.py` 中设计异常呼叫结束后等待真实挂机再复用的测试，通过状态、原因、等待集合和呼叫数量等断言验证处理过程。最终再使用 `pytest grading student_tests -q` 对代码、结果文件、自拟测试和报告进行统一检查。