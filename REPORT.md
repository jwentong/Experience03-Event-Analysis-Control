# 实验三报告
姓名：吴培立  学号：2024280421

## 原理与手算
本实验用事件驱动程序控制一台四用户教学交换机：用户 1001–1004 分别绑定链路 0 的 TS1–TS4。事件按 (time_ms, sequence) 处理，同一时刻先入队先处理。摘机 0→1 产生 OFFHOOK，挂机 1→0 产生 ONHOOK，相同采样不产生事件。号码分析针对 4 位号码：合法前缀返回 INCOMPLETE，完整合法号返回 LOCAL，自己的号返回 SELF_CALL，非法字符、无匹配前缀或超过四位返回 INVALID。

正常呼叫的状态链为 COLLECTING→RINGING→CONNECTED→ENDED：摘机后送 DIAL_TONE 并 arm DIAL 5000ms（收号总超时从摘机起算，输入数字不重置）；每输入一位就追加 digits，号码不完整时送 STOP_DIAL_TONE；号码完整且 reserve 成功后取消收号定时器、进入 RINGING 并 arm RING 10000ms、送 RING 和 RINGBACK；被叫应答时取消定时器并 activate 建立真实双向 T/S 话路，成功才进入 CONNECTED；挂机时 finish 并 RELEASE。以 1001 拨 1002 为例：0ms 摘机，100/200/300/400ms 拨 1/0/0/2，800ms 被叫应答，1000ms 主叫挂机。帧 0 的 TS1=3、TS2=6，应答后输出 TS1=6、TS2=3，输出帧比输入帧晚一帧，释放后相关输出回到 0xD5。

## 结果分析
运行 `python -m src.run_experiment` 生成三个文件：`results/call_sequence.png`（正常释放与无人接听两条状态时序图）、`results/call_events.jsonl`（逐行记录 scenario、time_ms、event、call_id、before、after、actions、reason）、`results/scenario_results.json`（12 个场景判定）。12 个场景（双向接通、主叫挂机、被叫挂机、号码错误、自呼、被叫忙、收号超时、无人接听、振铃取消、旧定时器、重复采样、释放后复用）全部 passed，passed=12、total=12。日志显示：正常呼叫依次经过 COLLECTING→RINGING→CONNECTED→ENDED；主叫挂机后 1002 仍摘机进入 WAIT_ONHOOK；无人接听在 10400ms 以 NO_ANSWER 结束；旧定时器到达时状态与话路保持不变。

## 反例与验证
`student_tests/test_my_case.py` 自拟了测试：① 摘挂机检测对 0→1、1→0、不变分别返回 OFFHOOK、ONHOOK、空列表；② 号码分析对 '100' 返回 INCOMPLETE、'1002' 返回 LOCAL、'1001' 返回 SELF_CALL、'10022' 返回 INVALID；③ 用 Exchange 跑一次正常呼叫，验证状态为 CONNECTED 且话路建立，再挂机验证状态变为 ENDED 且话路释放。运行命令：`.\.venv\Scripts\python.exe -m pytest student_tests -q`。结果通过，与手算预期一致。

## 局限
本实验使用逻辑时钟与事件队列，不依赖真实 sleep 或线程，因此定时器是离散时间戳而非真实硬件计时；软件事件与真实信令（如 SIP 或 No.7）在编码、重传与并发处理上仍有差异。交换机为四用户单链路简化模型，未实现多级网络、路由与计费。内部资源冲突与网络拒绝只做了固定路径的处理，不做自动改路。
