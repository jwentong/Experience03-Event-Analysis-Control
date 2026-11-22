# 实验三报告
姓名：范睿恒
学号：2024271068

## 原理与手算
本实验把呼叫处理建模为离散事件系统：所有事件按 (time_ms, sequence) 排序依次处理，同一时刻先入队先处理，全程只用逻辑时钟，不使用真实 sleep 或线程。摘挂机检测是对两次采样做差分：0→1 记 OFFHOOK，1→0 记 ONHOOK，值非 0/1 或用户集合不一致抛 ValueError，事件按用户编号排序输出。号码分析按局头（dial_plan）逐级判定：已拨串是某局内号码的真前缀则 INCOMPLETE；等于局内号码则 LOCAL，若恰是主叫自身则 SELF_CALL；含非数字字符、超过四位或无前缀匹配则 INVALID。呼叫控制是状态机：空闲用户摘机后进入 COLLECTING 并发 DIAL_TONE、收号定时器 5000ms；收号期间每个数字只追加且 STOP_DIAL_TONE，不重置总超时；收满合法号后 reserve 被叫，成功则取消收号定时器、进入 RINGING 并 arm 10000ms 振铃定时器，失败则 USER_BUSY；INVALID/SELF_CALL 直接 finish 并发 FAIL_TONE。被叫摘机时先 cancel 再 activate，成功建立真实 T/S 话路进入 CONNECTED，失败按 NETWORK_BUSY 释放。定时器用 call_id 加 token（代次）关联：arm 时代次加一，cancel 使旧事件失效，因此已接通或已结束后到达的旧超时只被忽略。

字节手算：1001 绑定链路0 TS1、1002 绑定链路0 TS2。帧0 输入 TS1=1×3=3、TS2=2×3=6。双向接通后控制表为 t_maps[0][TS1]=2、t_maps[0][TS2]=1（输出指向输入），故输出帧 TS1=6、TS2=3，即两时隙内容互换；输入帧 k 的结果在输出帧 k+1 可用。释放后相关时隙输出恢复空闲码 0xD5。

## 结果分析
运行 `.venv` 中 `python -m src.run_experiment` 后，`results/scenario_results.json` 显示 12 个场景全部 passed（passed=12、total=12），覆盖双向接通、主叫/被叫挂机、INVALID、SELF_CALL、USER_BUSY、DIAL_TIMEOUT、NO_ANSWER、振铃取消、旧定时器、重复采样与释放后复用。`results/call_events.jsonl` 中逐事件核对：正常呼叫在 400ms 出现 RING/RINGBACK 且 after=RINGING，800ms 被叫 OFFHOOK 后 activate 成功、after=CONNECTED 并生成话路；1000ms 主叫挂机 finish NORMAL_CLEAR，此时 1002 仍摘机，进入 WAIT_ONHOOK 集合，直到真实 ONHOOK 才回到空闲，期间未把 hooks 直接清零。无人接听场景在 10400ms 收到 RING 超时，先 STOP_RING 再 FAIL_TONE(NO_ANSWER)；5000ms 到达的旧收号超时事件保留在日志中但 before/after 均为 RINGING，状态不变，证明 token 校验生效。`results/call_sequence.png` 绘出 release_1001 与 NO_ANSWER 两条状态轨迹：前者 COLLECTING→RINGING→CONNECTED→ENDED，后者在 RINGING 停留 10000ms 后直接 ENDED。释放后检查 `tables.pairs`、`t_maps`、`s_map` 均为空，与手算一致。

## 反例与验证
自拟测试位于 `student_tests/test_my_case.py`，共 5 个用例：(1) 收号定时器不重置——拨入 1002 后队列中 TIMEOUT 事件仍为 (5000, DIAL) 与 (10400, RING)，断言两者时刻不变；(2) 振铃起始时刻——400ms 的日志行同时含 RING 与 RINGBACK 动作且 after=RINGING、被叫已被 reserve 但 tables.pairs 为空；(3) 双向字节与释放清空——断言 y[0,1]=x[0,2]=6、y[0,2]=x[0,1]=3，挂机释放后 t_maps、s_map、pairs 全空；(4) 号码分析补充反例——'100' 为 INCOMPLETE、'1000'（局外完整号）为 INVALID、'100x' 与 '12345' 为 INVALID、配置局 '2002' 为 LOCAL；(5) 摘挂机检测排序与异常——多用户同时变化按编号排序输出，集合不一致抛 ValueError。每个用例均先写预期再写 assert，运行 `.venv` 中 `python -m pytest student_tests -q` 结果为 5 passed in 0.18s。教师公开测试 `python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q` 结果为 27 passed in 0.30s，含网络拒绝（activate 返回 False 转 NETWORK_BUSY）、配置驱动号码与同时间事件顺序（10400ms 应答先于振铃超时处理，因应答事件先入队）等反例。

## 局限
本实验用的是逻辑时钟和预先排入队列的事件序列，与真实系统差距明显：真实摘挂机来自持续线路采样的中断驱动，本框架由教师注入的 OFFHOOK/ONHOOK 事件经差分去重生成，采样周期、抖动和 simultaneous 摘机竞争均未建模；真实收号有 DTMF 识别与位间间隔，本实验把数字当作瞬时字符且不重置总超时，过长间隔的处理与真实交换机不同；号码分析只支持四位本地局内号码，无出局路由、欠长重试和二次拨号；振铃只发动作字典，没有真实铃流与回铃音的媒体通道；WAIT_ONHOOK 只记录单个用户等待挂机，多呼叫并发下的话路资源竞争仅由 connect_pair 的占用检查保证。上述简化不影响 12 个教学场景的结论，但把结论外推到真实信令系统时需要重新验证。
