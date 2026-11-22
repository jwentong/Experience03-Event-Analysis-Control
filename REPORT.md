# 实验三报告
姓名：尹俊杰
学号：2024280377

## 原理与手算
本实验把交换机控制抽象为“事件→状态迁移→动作”的离散事件过程：采样经 detect_hook_events 去重后产生 OFFHOOK/ONHOOK 事件，DIGIT 逐位触发四位号码分析，TIMEOUT 事件携带 call_id 与 token 用于关联定时器代次。正常呼叫 C1：0ms 时 1001 摘机进入 COLLECTING 并 arm DIAL 5000ms；100~400ms 依次拨 1/0/0/2，前三位是合法前缀（INCOMPLETE），第四位得到 LOCAL，reserve 1002 成功，cancel 收号定时器、转入 RINGING 并 arm RING 10000ms；800ms 时 1002 摘机应答，cancel 后 activate 成功建立双向话路，进入 CONNECTED。手算帧 0：1001/1002 分别绑定链路 0 的 TS1/TS2，sample_frame(0) 的 TS1=(0×101+1×3+0×17) mod 256=3、TS2=6；connect_pair 写入 t_maps[0][2]=1、t_maps[0][1]=2 及对应空间映射，交换后输出帧 TS1=6、TS2=3，输出帧比输入帧晚一帧。释放时 disconnect_pair 清除双向映射并 cancel 定时器，输出对应时隙回到空闲码 0xD5=213。

## 结果分析
运行 python -m src.run_experiment 后生成三个结果文件：scenario_results.json 为 passed=12、total=12；call_events.jsonl 共 94 行；call_sequence.png 中 release_1001 与 NO_ANSWER 两条时序分别呈 COLLECTING→RINGING→CONNECTED→ENDED 与 COLLECTING→RINGING→ENDED（10400ms）。逐条核对日志：400ms 拨完号码时依次记录 STOP_DIAL_TONE、RING（user=1002）、RINGBACK（user=1001）；800ms 应答记录 STOP_RING、CONNECT；1000ms 主叫挂机记录 RELEASE、reason=NORMAL_CLEAR，1002 进入 WAIT_ONHOOK，直到 1100ms 真正挂机才回到空闲。USER_BUSY 场景中 C1 保持 CONNECTED 且 tables.pairs 只有一条映射。旧的 5000ms 收号超时和 10400ms 振铃超时在已接通或已结束的呼叫上均记录 before=after、actions=[]。实测字节：应答后输出帧 TS1=6、TS2=3，释放后交换帧 TS1、TS2 均为 0xD5，与规范一致。

## 反例与验证
自拟测试 student_tests/test_my_case.py 覆盖公开用例之外的边界：①在 5000ms 同一逻辑时刻先处理预入队的四位 DIGIT、后处理 DIAL 超时，断言呼叫进入 RINGING 且旧超时被忽略，验证“同一时间先入队先处理”和 token 机制；②正常接续后主叫挂机再交换一帧，断言 TS1、TS2 均变为 IDLE 码 0xD5，验证真实话路已释放；③detect_hook_events 对用户集合不一致抛 ValueError、analyze_number 对超长与非法字符返回 INVALID、配置驱动号码返回 LOCAL。验证命令：pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py 全部通过，pytest grading student_tests 全部通过；另把本机 call_events.jsonl 与 examples/teacher_results 参考日志 94 行逐字段严格比较，结果完全一致。

## 局限
本实验用逻辑时间与软件事件队列代替真实时钟和中断，定时器不受 CPU 调度、信号抖动影响，而真实交换机中振铃、应答、挂机可能并发到达。T/S 交换只用 32 个时隙的单帧和一帧缓存抽象 8kHz 帧同步与多帧连续交换，也未模拟听音，拨号音/忙音仅记录动作名而不产生 PCM 码流。功能上只覆盖 4 个用户、2 条链路的正常和少量异常流程，没有超时重传、信令确认、掉电恢复和跨交换机中继；被叫应答失败的 NETWORK_BUSY 分支通过替换 activate 模拟，真实网络拒绝的原因与恢复过程更复杂。
