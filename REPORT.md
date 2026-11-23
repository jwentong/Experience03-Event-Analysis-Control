# 实验三报告

姓名：王真珍  
学号：2024221047

## 原理与手算

用户采样保存的是某一时刻的连续状态，事件表示相邻采样之间的变化：0 到 1 产生 OFFHOOK，1 到 0 产生 ONHOOK，相同采样不重复产生事件。呼叫状态保存的是一次接续所处的阶段。用户 1001 在 0 ms 摘机后进入 COLLECTING 并启动总长 5000 ms 的收号定时器；100、200、300、400 ms 依次输入 1、0、0、2 后，号码分析得到 LOCAL，资源预留成功，状态进入 RINGING 并启动 10000 ms 振铃定时器。800 ms 被叫 1002 摘机，activate 建立双向 T/S 映射后才进入 CONNECTED；1000 ms 主叫挂机后释放映射并进入 ENDED。

回铃音只是通知主叫正在等待被叫应答，并不代表交换网络已经接通；只有被叫应答且 activate 成功，才能发送 CONNECT 并进入通话状态。输入帧 0 的 TS1=3、TS2=6，建立双向连接后输出 TS1 得到原 TS2 的 6，输出 TS2 得到原 TS1 的 3，交换结果要晚一帧才能使用。主叫释放后两个业务时隙恢复 0xD5，pairs 为空，而仍摘机的 1002 留在 WAIT_ONHOOK，不能直接当作空闲用户。

## 结果分析

本人运行 `python -m src.run_experiment` 后得到 12/12 场景通过。`scenario_results.json` 中 normal_bidirectional、主叫/被叫释放、INVALID、SELF_CALL、USER_BUSY、DIAL_TIMEOUT、NO_ANSWER、cancel_ringing、stale_timer、duplicate_sample 和 reuse_after_release 均为 true。`call_sequence.png` 中 release_1001 依次经历 COLLECTING、RINGING、CONNECTED、ENDED；NO_ANSWER 在 400 ms 进入 RINGING，5000 ms 的旧收号超时前后状态都为 RINGING，直到 10400 ms 振铃超时才转为 ENDED，说明定时器代次校验生效。

`call_events.jsonl` 保留了每次事件的前后状态、动作和结束原因。正常接通的日志包含 RING、RINGBACK、STOP_RING 和 CONNECT；主叫挂机的原因为 NORMAL_CLEAR，而振铃阶段取消为 CALLER_CANCEL。实际抽帧验证得到输入 TS1/TS2 为 3/6，应答后输出为 6/3，释放后均为 213，即 0xD5。重复摘机采样没有创建第二个 Call，释放后再次拨号能够建立新的双向连接，说明已有资源和话路均被正确清理。

## 反例与验证

自拟测试 `student_tests/test_my_case.py` 在 0 ms 让 1001 摘机，100 ms 只输入一位号码 1，200 ms 立即挂机。预期该呼叫以 CALLER_CANCEL 结束，清除 owners 和 T/S pairs，且已经挂机的用户不进入 WAIT_ONHOOK；随后 5000 ms 到达的旧 DIAL 定时器不得改写结束状态。测试断言 TIMEOUT 日志的 before 与 after 都为 ENDED、actions 为空、原因仍为 CALLER_CANCEL。该用例能够发现两类错误：漏掉摘机后的收号定时器启动，或超时处理只检查状态而未检查 token 与 timer_kind。

初次连接框架时，公开测试暴露两个接口问题：主叫摘机分支没有发送 DIAL_TONE 和启动收号定时器，号码分析调用了不存在的 `s.dial_plan`。根据运行时定义改为 `s.numbers`，并把 OFFHOOK 初始化补入 COLLECTING 分支后，四个任务的 27 个公开测试全部通过。生成结果后执行 `python -m pytest grading student_tests -q -p no:cacheprovider`，完整核查结果为 38 passed。

## 局限

本实验用逻辑时间和事件队列代替真实设备的中断、线程与毫秒级调度，没有模拟抖动、丢包、传播时延和硬件忙闲差异。号码计划固定为四个用户，交换网络也采用一帧缓存和理想无阻塞的 T/S 映射，因此不能直接代表多局向、长话路由或真实信令网络。真实系统还需要处理线路故障、重复事件、协议超时和资源异常回滚；本次主要验证了事件排序、状态机、定时器代次以及双向话路释放的基本正确性。
