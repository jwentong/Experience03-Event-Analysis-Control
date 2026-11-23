# 实验三报告
姓名：陈泓帆
学号：2023280241

## 原理与手算

本实验以事件驱动方式控制四用户教学交换机。用户1001~1004分别绑定链路0的TS1~TS4，采样0为挂机、1为摘机。事件按 (time_ms, sequence) 依次处理，同一时间先入队先处理，全部使用逻辑时钟，不使用真实 sleep 或线程。

摘挂机检测：对比 previous 与 current 两次采样，0→1 产生 OFFHOOK，1→0 产生 ONHOOK，相同采样不产生事件，按用户编号排序返回；集合不一致或值非 0/1 抛 ValueError。

号码分析：四位号码，先检查非法字符、长度超过四位为 INVALID；等于本机号为 SELF_CALL；在拨号计划中为完整四位号为 LOCAL；是某个合法前缀的严格前缀为 INCOMPLETE；其余为 INVALID。

正常呼叫状态变化：空闲用户 OFFHOOK → 框架创建 Call，发 DIAL_TONE，arm DIAL 5000ms，进入 COLLECTING；主叫输入数字追加 digits，合法前缀且不完整则继续收号；完整合法号且 reserve 成功则取消收号定时器，进入 RINGING，arm RING 10000ms，发 RING/RINGBACK；被叫 OFFHOOK 则 activate 成功进入 CONNECTED，发 STOP_RING/CONNECT；任一方 ONHOOK 则 finish，释放话路，进入 ENDED。

定时器：收号总超时 5000ms 从摘机起计时，输入数字不重置；振铃超时 10000ms 从开始振铃起计时。旧 token 或类型不匹配的超时直接忽略，不影响已接通或结束的呼叫。

## 结果分析

运行 `python -m src.run_experiment` 生成三个结果文件：`results/call_sequence.png`、`results/call_events.jsonl`、`results/scenario_results.json`。

12 个场景全部通过：双向接通、主叫挂机、被叫挂机、号码错误、自呼、被叫忙、收号超时、无人接听、振铃取消、旧定时器、重复采样、释放后复用。`scenario_results.json` 中 passed=12，total=12。

正常示例中，0ms 主叫摘机，100/200/300/400ms 拨 1/0/0/2，800ms 被叫应答，1000ms 主叫挂机，状态按 COLLECTING→RINGING→CONNECTED→ENDED 迁移。无人接听示例中，400ms 开始振铃，10400ms 结束为 NO_ANSWER，5000ms 到达的旧收号超时被正确忽略，日志保留该事件但前后状态相同。

时序图中，应答后双向话路真实建立：帧0的 TS1=3、TS2=6，应答后输出 TS1=6、TS2=3，释放后相关输出恢复为 0xD5，验证了 T/S 交换网络的真实话路切换与释放。

## 反例与验证

自拟测试 `student_tests/test_my_case.py` 中包含多条有效断言：

1. 号码分析边界：`analyze_number('1002', P, '1001') == 'LOCAL'`，`analyze_number('1001', P, '1001') == 'SELF_CALL'`，`analyze_number('9999', P, '1001') == 'INVALID'`，`analyze_number('1', P, '1001') == 'INCOMPLETE'`。
2. 摘挂机检测：`detect_hook_events({'1001':0}, {'1001':1}) == [{'user':'1001','kind':'OFFHOOK'}]`，相同采样返回空列表。
3. 超时处理：仅摘机不拨号，运行后 `reason == 'DIAL_TIMEOUT'`，且 `owners` 为空，验证定时器正确释放。

运行 `pytest student_tests -q` 全部通过，说明自拟测试能够正确捕捉各功能模块的预期行为。

## 局限

1. 全程使用逻辑时钟代替真实墙钟时间，不涉及操作系统实时调度，无法模拟真实信令的抖动与延迟。
2. 事件为软件模拟采样，未接入真实电话机或物理线路，OFFHOOK/ONHOOK 由框架采样去重而非硬件中断。
3. 仅支持四位号码与四个固定用户，扩展至更大号码段需修改拨号计划与用户绑定。
4. 话路预留与释放在内存中完成，未考虑断电、链路故障等异常恢复机制。
