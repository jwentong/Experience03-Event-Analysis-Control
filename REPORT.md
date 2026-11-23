# 实验三报告

姓名：姚智烁　学号：2024280127

## 原理与手算

本实验把一次呼叫拆成两层：事件是外部发生了什么（摘机、按键、挂机、定时器到期），状态是这台交换机走到哪一步（COLLECTING、RINGING、CONNECTED、ENDED）。控制函数只做一件事——看当前状态和事件，原地修改 Call，再通过 arm、cancel、reserve、activate、finish 这几个服务去操作真实资源。框架按 (time_ms, sequence) 串行派发事件，同一时刻先入队先处理，所以整个过程不需要 sleep，也不会出现竞态。

正常呼叫手算：0ms 1001 摘机，框架创建 C1、状态 COLLECTING，发 DIAL_TONE 并 arm DIAL 5000，此时 c.timer=1。100、200、300ms 收到 1、0、0，号码分析返回 INCOMPLETE，只停拨号音，收号定时器不重置（从摘机起算 5000ms）。400ms 收到 2，digits=1002 判定 LOCAL，reserve 成功占住 1002，cancel 使收号超时作废（timer=2），状态转 RINGING，arm RING 10000（timer=3），发 RING 与 RINGBACK。800ms 1002 摘机，先 cancel（timer=4）再 activate，T 表写入 t_maps[0][2]=1、t_maps[0][1]=2，S 表写入 (0,1)、(0,2) 两条映射，状态 CONNECTED。1000ms 1001 挂机，finish(NORMAL_CLEAR) 删除两条路由、清空归属，1002 仍在摘机，进入 WAIT_ONHOOK。

令牌手算：5000ms 到期的收号超时带 token=1，而届时 c.timer 已经是 4，两者不等，必须忽略；10400ms 到期的振铃超时带 token=3，若已接通 c.timer=4，同样忽略。这就是"旧定时器不得影响已接通呼叫"的实现方式。

字节手算：sample_frame(0) 的取值是 (link*101 + slot*3 + frame*17) % 256，所以帧 0 的 TS1=3、TS2=6。接通后输出 TS1 取输入 TS2（6），输出 TS2 取输入 TS1（3）；释放后 disconnect_pair 删除映射，输出重新填 0xD5（空闲码）。

## 结果分析

运行 python -m src.run_experiment 输出 Scenarios passed: 12/12，results/scenario_results.json 中 passed=12、total=12，12 个场景全部为 true：normal_bidirectional、release_1001、release_1002、INVALID、SELF_CALL、USER_BUSY、DIAL_TIMEOUT、NO_ANSWER、cancel_ringing、stale_timer、duplicate_sample、reuse_after_release。

call_sequence.png 的两条曲线分别对应 release_1001 和 NO_ANSWER。前者 0ms 从 IDLE 进入 COLLECTING，400ms 到 RINGING，800ms 到 CONNECTED，1000ms 到 ENDED，是四级台阶；后者一直停在 RINGING，直到 10400ms 才跳到 ENDED 并记录 NO_ANSWER。

逐条核对 call_events.jsonl 得到三个证据。其一，release_1001 在 1000ms 的 ONHOOK 之后 pairs 为空、owners 为空、waiting 含 1002，说明双向话路确实被拆除，而仍在摘机的一方进入等待挂机。其二，NO_ANSWER 场景中 5000ms 的那条 TIMEOUT 事件仍然被记录，但 before 与 after 都是 RINGING，说明旧收号定时器被正确忽略。其三，normal_bidirectional 用帧 0 校验，输入 TS1=3、TS2=6，输出 TS1=6、TS2=3，与手算一致；释放后同一时隙输出 0xD5。

## 反例与验证

自拟测试 student_tests/test_my_case.py 有三个用例。用例一：0ms 让 1003 先摘机，100ms 让 1001 拨 1003，期望新呼叫 C2 的结束原因是 USER_BUSY，同时 C1 仍停留在 COLLECTING，实测通过，说明 reserve 对"已摘机但尚未占位"的被叫同样拒绝，且忙线不会误伤另一条呼叫。用例二：四个用户同时跳变时，detect_hook_events 必须按 1001、1003、1004 排序返回，并保证入参字典没有被修改，实测通过。用例三：用 dial_plan = ['2001','2002','2003'] 验证配置驱动，2002 返回 LOCAL、2003 对 2003 返回 SELF_CALL、'2' 返回 INCOMPLETE、2009 返回 INVALID，实测通过。

反例实验做了三组"改坏再修好"。其一，把超时处理简化成只按事件类型处理，既不比对 token 也不检查状态：5000ms 的旧收号超时把振铃中的呼叫结束成 DIAL_TIMEOUT，test_old_dial_after_ringing 失败；10400ms 的旧振铃超时把已接通的呼叫结束成 NO_ANSWER，test_old_ring_after_answer 失败。其二，把 LOCAL 分支的 cancel 移到 arm 之后，timer_kind 被清空、token 又加一，10400ms 的振铃超时永远配不上，呼叫停在 RINGING 且 reason 为空，NO_ANSWER 场景失败。其三，三道校验都保留、但把收号超时的结束原因写成 CALLER_CANCEL，scenario_results.json 里 DIAL_TIMEOUT 变成 false，说明评分看的是原因字符串而不只是状态。三处改回原实现后重新运行，全部恢复通过。

运行结果：python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q 输出 27 passed；python -m pytest grading student_tests -q 输出 40 passed。

## 局限

本实验的时间是逻辑时间：事件按 (time_ms, sequence) 排队，没有真实时钟抖动、处理延迟和重传，因此无法反映真实交换机在高负载下的定时精度。事件接口是自定义的软件事件，不是 ISDN 或 No.7 信令消息，缺少协议分层、状态编号与差错流程。交换网络只建模了 T 接线器与 S 接线器的一帧缓存，没有媒体流、语音编码和回声抑制。用户数固定为 4、超时值写死在状态机里、号码固定四位，都不支持配置扩展。测试覆盖了正常接续与常见异常，但对多路呼叫同时竞争同一时隙的情况只做了预留冲突的简化处理。
