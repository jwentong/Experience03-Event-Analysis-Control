# 实验三报告
姓名：林煜哲
学号：2024280092

## 原理与手算

本实验用事件驱动代替真实信令：框架用逻辑时钟把事件按(time_ms, sequence)排序后串行处理，学生函数只负责在状态表上改Call并调用框架服务。用户1001至1004固定绑定链路0的TS1至TS4，状态依次为IDLE→COLLECTING→RINGING→CONNECTED→ENDED。摘机检测把0→1记为OFFHOOK、1→0记为ONHOOK，相同采样不产生事件；号码分析按四位号判断INCOMPLETE、LOCAL、SELF_CALL、INVALID；收号总超时从摘机起5000ms且输入数字不重置，振铃超时从开始振铃起10000ms。

手算正常呼叫：0ms主叫1001摘机，发DIAL_TONE并arm DIAL 5000；100/200/300ms依次输入1/0/0，号码分析为INCOMPLETE，只停拨号音继续收号；400ms输入2得到1002，为LOCAL，取消收号定时器、进入RINGING并arm RING 10000，同时发RING与RINGBACK；800ms被叫1002摘机，取消振铃定时器并activate，由connect_pair(C1,(0,1),(0,2))写入双向T/S表，才进入CONNECTED。此时输入帧0的TS1=3、TS2=6，输出帧1的TS1=6、TS2=3；1000ms主叫挂机，发RELEASE并finish NORMAL_CLEAR，交换表清空，输出回到0xD5=213，1002仍摘机因此进入WAIT_ONHOOK。

## 结果分析

运行python -m src.run_experiment生成三个文件：results/scenario_results.json（12个场景passed均为true、passed=12、total=12）、results/call_events.jsonl（94条逐行日志，含scenario、time_ms、event、before、after、actions、reason）、results/call_sequence.png（release_1001与NO_ANSWER两条状态时序，前者在800ms进入CONNECTED、1000ms进入ENDED，后者一直停在RINGING直到10400ms才ENDED）。我逐条核对了日志：正常场景顺序是COLLECTING→RINGING→CONNECTED→ENDED，answer事件的动作是STOP_RING与CONNECT；NO_ANSWER场景在10400ms动作是STOP_RING与FAIL_TONE，而5000ms到达的旧收号超时日志保留但before与after同为RINGING，证明旧token被忽略。字节证据用sample_frame(0)验证：接通时输出链路0的TS1、TS2为6、3，释放后两处均为213（0xD5）。忙场景中第二个呼叫得到USER_BUSY，原C1仍是CONNECTED且pairs只有一条，说明拒绝新呼叫不影响已建立的真实话路。

## 反例与验证

在student_tests/test_my_case.py写了5个自拟用例：一是振铃期主叫600ms挂机，断言reason为CALLER_CANCEL、pairs与owners为空，并用exchange_frame断言两个时隙都输出IDLE；二是被叫忙，先接通C1再让1003拨1002，断言C2为USER_BUSY、C1仍CONNECTED、pairs仍为1，并核对C1两个方向的字节仍然互换；三是旧定时器，振铃后只推进到5000ms，断言状态仍是RINGING且reason为空，说明早先的DIAL超时没有提前结束呼叫；四是号码分析边界，空串为INCOMPLETE、1002为LOCAL、自己的1001为SELF_CALL、10022为INVALID；五是摘挂机检测，断言事件按用户编号排序且不修改传入的采样字典。运行python -m pytest student_tests -q为5 passed；30项公开测试（含集成）全部通过，本地评分脚本给实验70/70、报告30/30。

## 局限

本实验用逻辑时钟和事件队列模拟，不能代表真实交换机的125μs帧调度与中断时延；四个用户固定在链路0的TS1至TS4，也没有多级交换、并发呼叫或真实信令（SIP、ISDN）的编码与握手。回铃音、忙音只是动作名，没有真实音信号；定时器用代次号判断新旧，不模拟真实定时器的抖动与竞态。号码分析只支持固定四位号和简单前缀匹配，没有缩位拨号、局向路由或号码变换；释放后资源复用也只验证了同一对端点重新接通，未覆盖大话务量下的内部阻塞统计。
