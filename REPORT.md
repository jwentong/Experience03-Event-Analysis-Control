# 实验三报告

姓名：张志伟  
学号：2024280016  
实验日期：2026-11-22  
GitHub用户名：z05217464-dotcom

## 原理与手算

本实验用逻辑时钟和事件队列控制四用户教学交换机。用户采样是某一时刻各用户挂机状态0或摘机状态1的快照；事件只描述相邻快照之间的变化；呼叫状态保存一次呼叫已经走过的阶段。采样去重和排序后产生OFFHOOK或ONHOOK，事件再驱动状态机迁移。回铃音只表示被叫正在振铃，此时没有媒体通路；被叫摘机后还必须调用`activate`并成功写入双向T/S映射，才能进入CONNECTED。

正常呼叫中，1001在0 ms摘机进入COLLECTING并启动5000 ms收号总超时。100、200、300、400 ms依次输入1、0、0、2，完整号码通过前缀和配置表校验后预留1002，取消DIAL，进入RINGING并启动10000 ms振铃超时。800 ms被叫应答，`activate`成功后才进入CONNECTED。1000 ms主叫挂机，以NORMAL_CLEAR结束并释放双向话路；1002仍摘机，进入WAIT_ONHOOK，直到真实ONHOOK后才回到空闲。

以帧0为例，链路0的TS1输入为3、TS2输入为6。应答后，去往TS1的字节取输入TS2的值6，去往TS2的字节取输入TS1的值3，因此输出帧TS1=6、TS2=3；输出帧相对输入帧晚一帧可用。释放后相关T表和S表项被删除，目的时隙恢复空闲码0xD5（十进制213）。检查时同时读取`t_maps`、`s_map`和`pairs`，并用`sample_frame`与`exchange_frame`核对实际字节。

## 结果分析

`detect_hook_events`校验字典、用户集合和0/1取值，按用户编号排序并保持输入不变；号码分析只接受ASCII数字，按配置表区分INCOMPLETE、LOCAL、SELF_CALL和INVALID；呼叫控制按状态表处理收号、忙线、振铃、应答、释放和WAIT_ONHOOK；超时处理先比较token与`timer_kind`，再检查当前状态，旧事件只保留日志而不改变资源。

本人运行`python -m src.run_experiment`生成三个结果文件，`scenario_results.json`显示passed=12、total=12、失败场景0。日志中400 ms记录COLLECTING→RINGING，动作为STOP_DIAL_TONE、RING、RINGBACK；800 ms记录RINGING→CONNECTED，动作为STOP_RING、CONNECT；无人接听场景在10400 ms记录RINGING→ENDED、NO_ANSWER。正常场景在1000 ms挂机时记录NORMAL_CLEAR和RELEASE。

正常释放与无人接听的主要区别是：前者在CONNECTED阶段由用户ONHOOK触发NORMAL_CLEAR，后者一直停留在RINGING，直到有效RING超时执行STOP_RING和FAIL_TONE。400 ms进入RINGING后，5000 ms到达的旧DIAL事件仍在日志中，但before和after均为RINGING且actions为空；800 ms应答后，5000 ms和10400 ms的旧事件均保持CONNECTED。这是因为取消和重新arm后token、timer_kind与旧事件不匹配。

## 反例与验证

自拟测试`student_tests/test_my_case.py`包含两个边界用例。第一例让1002在C1振铃期间发送DIGIT 9，检查控制函数必须同时限定主叫和COLLECTING状态；预期状态仍为RINGING、digits仍为1002且没有建立话路。第二例只输入合法前缀10，检查收号总超时不会因输入数字重新计时；预期5000 ms后为DIAL_TIMEOUT，1001进入WAIT_ONHOOK，1002不被预留且不存在T/S映射。

执行`python -m pytest student_tests -q`得到2 passed；四个公开任务测试得到27 passed；联合运行`python -m pytest grading student_tests -q`得到39 passed。全部通过后，我又逐行检查400、800、5000和10400 ms的日志状态与动作，检查12个场景逐项passed，并直接比较交换表与输入输出字节，避免只凭曲线形状判断正确。如有异常，优先检查忙线失败是否误调用finish、超时是否先校验token，以及释放是否确实执行disconnect_pair。

## 局限

本实验使用离散逻辑时间和软件事件队列，不模拟真实信令的线程调度、网络时延、重传、终端振铃波形和精确抖动。交换矩阵采用一帧缓存模型，只验证控制表与字节映射，不代表真实数字程控交换机的全部物理层行为。用户固定为4个，号码为四位短号，也没有考虑鉴权、计费、号码归属地、恶意信令、跨节点拥塞和并发资源竞争。当前模型适合验证控制逻辑，若扩展到更大用户规模、实时媒体或生产网络，需要重新评估事件顺序、资源锁和定时器精度。
