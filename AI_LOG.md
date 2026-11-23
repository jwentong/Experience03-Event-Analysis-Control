# AI使用记录
## 需求
要求 AI 按 README 状态表补全 src/hooks.py、src/numbering.py、src/control.py、src/timeouts.py 四个函数，实现摘挂机检测、四位号码分析、收号与振铃应答释放、以及带 token 校验的超时处理，并生成结果文件与自拟测试，最后完成提交。

## 建议与采纳
采纳按事件类型分支的状态机写法：OFFHOOK 分收号与应答两种情形，DIGIT 仅接受主叫在 COLLECTING 时输入，ONHOOK 按是否已接通区分 NORMAL_CLEAR 与 CALLER_CANCEL。采纳用 s.numbers 作为号码表而不是硬编码，便于配置驱动号码。采纳超时处理先比较 e['token'] 与 c.timer、再比较 e['value'] 与 c.timer_kind 的顺序，避免旧定时器改状态。数字位为空串时的前缀判断最初写错，经测试反馈改为返回 INCOMPLETE；漏掉摘机的 DIAL_TONE 与 arm DIAL 也由测试发现后补上，未采纳先改测试的做法。

## 验证证据
运行 python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q 得到 27 passed；运行 python -m src.run_experiment 得到 Scenarios passed: 12/12，并生成三个结果文件；运行 python -m pytest grading student_tests -q 全部通过。手算核对帧 0 的 TS1=3、TS2=6，接通后互换为 6 与 3，释放后为 0xD5，与日志和图形一致。
