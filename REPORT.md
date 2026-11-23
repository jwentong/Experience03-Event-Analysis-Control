# 实验三报告
姓名：张锋烨
学号：2023352050

## 原理与手算
事件是采样层检测到的跳变，状态是交换机为一次呼叫维护的上下文，事件驱动状态迁移，动作只描述结果而不直接改硬件。一次正常呼叫的时序：0 ms 主叫 1001 摘机，框架建 Call 并进入 COLLECTING，发 DIAL_TONE 并 arm DIAL 5000；100/200/300/400 ms 依次收到 1/0/0/2，前三位的分析结果为 INCOMPLETE，只追加 digits；第四位补齐后为 LOCAL，取消收号定时器，reserve 1002 成功，进入 RINGING，arm RING 10000 并输出 RING、RINGBACK；800 ms 被叫摘机，取消定时器并 activate，双向 T/S 映射建立后才进入 CONNECTED；1000 ms 主叫挂机，finish 释放话路并写 NORMAL_CLEAR，1002 仍在摘机态，进入 WAIT_ONHOOK，不会直接变空闲。定时器以 timer 代次区分：arm 和 cancel 都使代次加一，只有代次与类型同时匹配的超时才有效。手算字节：帧 0 的 TS1=(0*101+1*3+0)=3、TS2=6，接通后输出帧 TS1=6、TS2=3，输出比输入晚一帧；释放后两个方向回到空闲码 0xD5。

## 结果分析
运行 python -m src.run_experiment 输出 Scenarios passed: 12/12，results/scenario_results.json 中 passed=12、total=12，results/call_events.jsonl 逐条记录 before/after 与 actions，results/call_sequence.png 中 release_1001 为 COLLECTING→RINGING→CONNECTED→ENDED 的阶梯，NO_ANSWER 在 10400 ms 由 RINGING 跳到 ENDED。逐条核对日志可见：400 ms 的 DIGIT 事件后状态变 RINGING 且无 pairs；800 ms 应答事件后 actions 为 STOP_RING、CONNECT，pairs 长度 1；1000 ms 挂机后 pairs 清空、owners 清空、waiting={'1002'}。5000 ms 到达的旧 DIAL 超时在日志中保留，但 before 与 after 同为 RINGING，说明旧代次被忽略。把 tables 代入 sample_frame(0) 交换后，link0 的 TS1 与 TS2 互换，值为 6 和 3；disconnect 后再算同一帧，两个时隙均为 0xD5。

## 反例与验证
自拟用例 student_tests/test_my_case.py：拨 1009（四位但不在号码表），期望前三位为 INCOMPLETE、第四位判 INVALID，呼叫以 INVALID 结束且主叫仍摘机时进入 WAIT_ONHOOK，话路与归属全部释放；随后在 5100 ms 真实挂机、5200 ms 再摘机，期望新建 C2 处于 COLLECTING 且 waiting 为空。断言检查 digits=='1009'、reason=='INVALID'、waiting=={'1001'}、pairs 为空，以及 C2 状态与 waiting。运行 pytest student_tests -q 得到 1 passed，pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q 得到 27 passed。另用旧定时器反例验证：接通后 10400 ms 的 RING 超时因 token 不匹配被忽略，状态仍为 CONNECTED 且 pairs 长度 1。

## 局限
全程使用逻辑时钟与单线程事件队列，没有真实采样抖动、丢帧和媒体时延；用户在振铃期间摘机的时序完全由脚本给定，不能反映真实话机的机械抖动与拍叉。号码分析只覆盖四位等长号码，没有区号、缩位和号码变换表；呼叫控制只允许两方通话，未实现三方、呼叫等待和遇忙回叫。activate 只检查 T/S 映射能否建立，未模拟中继拥塞与信令失败的真实概率。结果图形的形状只说明状态迁移顺序，字节正确性仍需逐帧核对。
