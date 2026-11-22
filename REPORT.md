# 实验三报告

姓名：陈梓潮　学号：2024280220　GitHub：alvin11vct11

## 原理与手算

**事件与状态的区别**：事件是外部世界发生的变化（摘机、挂机、按下一个数字键、定时器到期），本实验用 `OFFHOOK`、`ONHOOK`、`DIGIT`、`TIMEOUT` 四类事件表示；状态是交换机内部对一通呼叫的记录（`COLLECTING`、`RINGING`、`CONNECTED`、`ENDED`）。控制函数不做“等待”，只把“当前状态 + 一个事件”映射成“若干动作 + 新状态”，时间由逻辑时钟推进。

**正常呼叫的手算**：0 ms 用户 1001 摘机 → 创建呼叫 C1，状态 `COLLECTING`，送 `DIAL_TONE`，并启动收号定时器 `DIAL` 5000 ms（从摘机起算，输入数字不重置）。100/200/300 ms 依次拨 1、0、0，号码分别是 `1`、`10`、`100`，都属于 1001～1004 的前缀，返回 `INCOMPLETE`，只发 `STOP_DIAL_TONE`，状态不变。400 ms 拨入 2，号码 `1002` 完整合法且不是自己，返回 `LOCAL`：先 `cancel` 掉收号定时器（token 失效），再 `reserve` 被叫 1002，成功则状态转 `RINGING`，启动 `RING` 10000 ms，并发出 `RING`、`RINGBACK`。800 ms 被叫 1002 摘机，属于 `RINGING` 状态下的应答：`cancel` 振铃定时器后调用 `activate`，它通过实验二的 `connect_pair` 真正建立双向 T/S 映射，成功才转 `CONNECTED` 并发 `STOP_RING`、`CONNECT`。1000 ms 主叫挂机，`CONNECTED` 状态下原因记为 `NORMAL_CLEAR`，发 `RELEASE` 并 `finish`，双向话路释放，仍摘机的 1002 进入 `WAIT_ONHOOK`，必须等真实挂机才回到空闲。

**字节手算**：`sample_frame(0)` 中链路 0 的 TS1（1001）为 `0×101+1×3+0=3`，TS2（1002）为 `6`。接通后交换结果在下一帧可用，故输出帧 1 的 TS1 读到 6、TS2 读到 3；释放后这两个输出位置回到空闲码 `0xD5`。

**定时器代次**：每次 `arm` 或 `cancel` 都会让 `c.timer` 自增，超时事件携带当时的 token。因此收号完成后 5000 ms 才到达的旧 `DIAL` 超时，其 token 已经小于当前代次，必须原样忽略；振铃超时同理，接通后再到的 `RING` 超时也不能拆掉已建立的话路。

## 结果分析

运行 `python -m src.run_experiment` 生成 `results/scenario_results.json`、`results/call_events.jsonl` 和 `results/call_sequence.png`。

**12 个场景全部通过**（`passed=12`、`total=12`）：双向接通、主叫挂机、被叫挂机、号码错误、自呼、被叫忙、收号超时、无人接听、振铃取消、旧定时器、重复采样、释放后复用。其中“双向接通”不是只看状态字符串，而是取一帧真实字节比较 `out[0,1]==a[0,2]` 且 `out[0,2]==a[0,1]`；“释放后复用”还要求第二次接通后 `len(tables.pairs)==1`，证明旧连接没有残留。

**时序图**：`call_sequence.png` 上下两幅分别是 `release_1001` 与 `NO_ANSWER` 的状态阶梯图，横轴为逻辑时间。正常释放曲线为 `IDLE→COLLECTING→RINGING→CONNECTED→ENDED`；无人接听曲线在 10400 ms 从 `RINGING` 直接落到 `ENDED`。

**事件日志**：`call_events.jsonl` 逐行记录 `scenario`、`time_ms`、`event`、`call_id`、`before`、`after`、`actions`、`reason`。检查“旧定时器”场景可以看到 5000 ms 的 `TIMEOUT` 行仍然存在（事件没有被丢弃），但 `before` 与 `after` 都是 `RINGING`、`actions` 为空、`reason` 为空，说明旧 token 被正确忽略；检查“被叫忙”场景可以看到 C2 结束时 `reason=USER_BUSY`，而 C1 仍为 `CONNECTED`、`pairs` 仍有 1 条。

**释放与复用**：主叫或被叫挂机后 `tables.pairs` 为空，两个方向的输出位置读回 `0xD5`；1002 挂机后再次摘机可建立新呼叫并成功接通，说明 `waiting` 集合的清理和资源释放都正确。

## 反例与验证

自拟测试写在 `student_tests/test_my_case.py`，两个用例都直接调用 `Exchange` 与场景函数：

1. **`test_digit_from_non_caller_is_ignored`**：0 ms 1001 摘机，50 ms 由 1002 送一个 `DIGIT` 字符 `1`。手算预期：`DIGIT` 只接受主叫在 `COLLECTING` 状态输入，1002 不是本呼叫主叫，因此 `digits` 必须仍为空、状态仍是 `COLLECTING`。断言 `call.digits == ''`、`call.state == 'COLLECTING'`。这个用例能揭示“只判断状态、不判断事件来源”的错误实现。

2. **`test_caller_hangup_before_answer_ends_call`**：0～400 ms 拨 1002，600 ms 主叫在振铃中挂机，800 ms 被叫摘机。手算预期：主叫先挂机应 `finish(CALLER_CANCEL)` 并释放被叫，之后被叫摘机只能创建新呼叫 C2，绝不能让旧呼叫变成 `CONNECTED`。断言 C1 为 `ENDED` 且原因为 `CALLER_CANCEL`、`tables.pairs` 为空、`1002` 不在 `waiting`、C2 存在且处于 `COLLECTING`。这个用例能揭示“挂机只改状态、不释放资源或不清 owner”的错误实现。

实际运行：

```
python -m pytest student_tests -q       → 2 passed
python -m pytest grading -q             → 37 passed
python grading/run_grading.py --local   → 总分 100/100
```

## 局限

本实验用**逻辑时间**和软件事件队列代替真实时钟与中断，没有真实 125 μs 帧同步、去抖和采样抖动；真实交换机的摘挂机检测要处理机械抖动与线路干扰，这里把采样直接抽象成 0/1。

呼叫控制只覆盖单局四个用户的基本呼叫，没有拨号音与回铃音的真实音频、没有信令编码（如中国 No.7 或 SIP）、没有计费、转移、会议和遇忙回叫；`WAIT_ONHOOK` 也只是课堂约定，真实设备会用更复杂的端口状态机。

交换网络沿用实验二的单级 T→S 结构，只有 2 条输入/输出链路，固定路径存在内部阻塞，不自动绕路；结论不能外推到多级网络或真实电话网。
