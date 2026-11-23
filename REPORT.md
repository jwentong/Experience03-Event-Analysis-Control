# 实验三报告

姓名：吕林敏  
学号：2024280019

## 原理与手算

本实验用事件驱动方式控制 1001 至 1004 四个用户。用户 1001 至 1004 分别绑定链路 0 的 TS1 至 TS4。OFFHOOK 表示从挂机 0 变为摘机 1，ONHOOK 表示从 1 变为 0；采样相同不产生事件。呼叫控制把“事件”与“状态”分开：事件是一次输入，状态是 Call 当前所处的 COLLECTING、RINGING、CONNECTED 或 ENDED，同一事件在不同状态下可以产生不同动作。

正常流程手算：0 ms 用户 1001 摘机，框架创建 Call，控制函数发出 DIAL_TONE，设置 DIAL 定时器 5000 ms，状态为 COLLECTING。100/200/300/400 ms 依次输入 1/0/0/2，号码 1002 完整且为 LOCAL；调用 reserve 成功后被叫 1002 被预留，取消 DIAL 定时器，状态变为 RINGING，设置 RING 定时器 10000 ms，并发出 RING 和 RINGBACK。800 ms 被叫 1002 摘机，取消 RING 定时器，activate 成功建立双向 T/S 连接，状态变为 CONNECTED，发出 STOP_RING 和 CONNECT。1000 ms 主叫 1001 挂机，finish 释放双向话路，原因为 NORMAL_CLEAR，状态变为 ENDED；被叫 1002 仍摘机，因此进入 WAIT_ONHOOK，只有真实 ONHOOK 后才回到空闲。

T/S 数据面的手算：输入帧 0 中链路 0 的 TS1=3、TS2=6。1001 与 1002 接通后，输出帧 1 的 TS1 应为 6、TS2 应为 3，输出比输入晚一帧。释放后这两个位置回到 IDLE=0xD5。定时器方面，收号总超时从摘机开始计算，输入数字不重置；振铃超时从开始振铃计算 10000 ms，旧 token 的 TIMEOUT 必须被忽略。

## 结果分析

运行 src.run_experiment 后，scenario_results.json 中 12 个场景全部 passed=true，passed=12、total=12。场景覆盖双向接通、主叫挂机、被叫挂机、号码错误、自呼、被叫忙、收号超时、无人接听、振铃取消、旧定时器、重复采样和释放后复用。call_sequence.png 给出正常释放和无人接听两条状态时序；call_events.jsonl 逐行记录时间、事件、call_id、前后状态、动作和结束原因。

正常接通场景中，C1 从 COLLECTING 进入 RINGING，再在 800 ms 被叫应答后进入 CONNECTED；1000 ms 主叫挂机后变为 ENDED，pairs 为空，1002 进入 WAIT_ONHOOK。无人接听场景中，400 ms 开始振铃，10400 ms 的有效 RING 超时把状态结束为 NO_ANSWER；5000 ms 到达的旧 DIAL 超时日志保留，但前后状态仍为 RINGING，说明旧 token 没有破坏当前状态。释放场景验证了双向 T/S 表项被删除，正常通话的真实字节在释放后回到 IDLE。重复采样场景只创建一个 Call，说明事件去重有效；释放后复用场景说明资源确实可以重新建立连接。

## 反例与验证

自拟测试 test_number_analysis_boundaries 验证空串、部分号码、完整号码、自呼、无匹配号码、超长号码和非法字符的边界，断言分别为 INCOMPLETE、LOCAL、SELF_CALL 和 INVALID。第二个自拟测试 test_stale_dial_timer_after_answer_is_ignored 在正常接通后继续运行事件队列，确认 5000 ms 的旧 DIAL 定时器日志存在，但 Call 仍为 CONNECTED 且 T/S 连接仍保留，防止旧定时器误释放通话。

实际运行结果：四个任务共 27 项公开测试通过，学生自拟测试 2 项通过，12 个固定场景全部通过。运行命令为：

python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q
python -m src.run_experiment
python -m pytest grading student_tests -q

## 局限

本实验使用逻辑时间和软件事件队列，不依赖真实 sleep、线程或实时操作系统，因此结果不能直接等同于真实交换机的实时性能。它没有实现真实 SIP 信令、音频编解码、网络传输或硬件摘挂机采样；T/S 数据面采用固定的先 T 后 S 单路径，存在内部阻塞，也不做自动绕路。定时器只验证 token 和类型，真实系统还需要处理时钟漂移、并发事件和设备故障。报告中的状态、动作和字节结果是课堂模型的验证，不代表完整电话网的总体行为。
