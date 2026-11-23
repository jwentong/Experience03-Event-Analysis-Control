# AI 使用记录

## 需求

使用 AI 助手辅助理解实验三的课程规范与教师框架：请它讲解事件驱动模型、Call 状态机与 token 定时器机制，并逐条核对 src/runtime.py 中 arm、cancel、reserve、activate、finish 的接口语义以及 grading 测试的边界条件。随后本人据此完成四个任务函数，再请 AI 对实现做边界与顺序检查。

## 建议与采纳

采纳：OFFHOOK 在 COLLECTING（新呼叫）与 RINGING（被叫应答）下语义不同；超时处理需同时校验 token、timer_kind 与当前状态；cancel 必须先于 arm。修改：AI 最初建议用 digits.isdigit() 判断数字，会把空串误判为 INVALID，本人改为字符集判断以正确处理空串。拒绝：AI 建议在收到第一位数字时重置拨号定时器，与"总超时从摘机起算"冲突，未采纳；AI 建议挂机时直接清空 s.hooks，会破坏 WAIT_ONHOOK 语义，未采纳。

## 验证证据

本机实测：python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q 输出 27 passed；python -m src.run_experiment 输出 Scenarios passed: 12/12；python -m pytest grading student_tests -q 输出 40 passed。手算核对：帧 0 输入 TS1=3、TS2=6，接通后输出 TS1=6、TS2=3，释放后为 0xD5；NO_ANSWER 场景 5000ms 的旧 TIMEOUT 事件 before 与 after 均为 RINGING。自拟测试三个用例见 student_tests/test_my_case.py，均通过。
