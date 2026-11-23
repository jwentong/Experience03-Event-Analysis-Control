# 实验三报告
姓名：刘梓皓
学号：2024280422

## 原理与手算
事件与状态是两层概念：采样值是某一时刻用户的物理状态（0 挂机、1 摘机），本身不是“事件”；摘挂机检测比较相邻两次采样，只有由 0 变 1 才生成 OFFHOOK、由 1 变 0 才生成 ONHOOK，相同采样不产生事件。Call 的 state 则是呼叫当前所处阶段（COLLECTING/RINGING/CONNECTED/ENDED），由收到的事件驱动迁移。

以正常呼叫手算：0ms 主叫 1001 摘机，进入 COLLECTING，发 DIAL_TONE 并 arm DIAL 5000（此时 token=1）。100/200/300ms 依次收到 1、0、0，前三位对拨号计划属合法前缀，判定 INCOMPLETE，每次 STOP_DIAL_TONE 后继续收号，收号总超时不因输入数字而重置。400ms 收到 2 组成 1002，号码分析得 LOCAL，reserve 被叫成功（1002 挂机且未被占用），cancel 使 DIAL 定时器作废（token 增到 2），进入 RINGING，arm RING 10000（token=2），并发 RING 与 RINGBACK。800ms 被叫 1002 摘机，cancel 定时器，activate 调用实验二 connect_pair 成功建立双向 T/S 映射后进入 CONNECTED，发 STOP_RING 与 CONNECT。1000ms 主叫 1001 挂机，状态为 CONNECTED 故以 NORMAL_CLEAR 调用 finish，发 RELEASE 进入 ENDED；被叫 1002 仍摘机，进入 WAIT_ONHOOK 集合，必须等其真实 ONHOOK 才回到空闲。

## 结果分析
运行 src.run_experiment 生成的 call_sequence.png 同时给出两条状态时序：release_1001（COLLECTING→RINGING→CONNECTED→ENDED 的完整正常流程）和 NO_ANSWER（COLLECTING→RINGING→在 10400ms 因 RING 超时进入 ENDED），阶梯线的平台段与状态表中的动作时刻一一对应。scenario_results.json 中 12 个场景 passed 全为 true，passed=12、total=12，覆盖双向接通、主叫/被叫挂机、号码错误、自呼、被叫忙、收号超时、无人接听、振铃取消、旧定时器、重复采样与释放后复用。真实话路用字节验证：connected 后取帧 0 输入，TS1=0x03、TS2=0x06，经 T/S 交换后输出 TS1=0x06、TS2=0x03，两时隙内容互换且输出帧比输入帧晚一帧，证明接通是真实建立了互换映射而非仅改状态名。主叫释放后 disconnect_pair 删除映射，再取输出为 0xD5（空闲字节），且 owners 与 pairs 均清空，说明释放真实回收了资源。

## 反例与验证
自拟测试 student_tests/test_my_case.py 含三个用例。第一个检查号码边界：全角数字“１００２”必须返回 INVALID（表明实现用 ASCII 白名单 '0123456789' 而不是宽松的 str.isdigit，否则全角会被误判为数字）、10022 因超过四位返回 INVALID、1004 为 LOCAL、10 为 INCOMPLETE。第二个检查摘挂机双向排序：输入 {'1002':0,'1001':1} 到 {'1002':1,'1001':0}，期望按号码升序得到 [1001 ONHOOK, 1002 OFFHOOK]，并断言原字典未被修改（纯函数）。第三个检查等待挂机语义：正常接通后主叫挂机使被叫 1002 进入 WAIT_ONHOOK，此时 1003 呼叫 1002 应得 USER_BUSY，且 1002 仍在 waiting 集合而非被直接置为可被叫。运行 python -m pytest student_tests -q 得到 3 passed；四个任务官方测试 pytest grading/test_hooks.py test_numbering.py test_control.py test_timeouts.py 得到 27 passed。

## 局限
本实验用逻辑时钟与事件队列代替真实 sleep 和线程，同一时刻仅按入队顺序串行处理，因此不涉及真实并发、抢占与调度抖动；摘挂机检测依赖框架对采样去重，简化了真实线路上的抖动与毛刺。场景只建模四位号码与静态拨号计划，缺少鉴权、计费、号码移机与号码变更；话路只验证字节互换，不涉及语音质量、丢包与回声。信令层面用动作字典模拟 DIAL_TONE/RING 等，并非真实 ISDN/No.7 消息，定时器也只有 DIAL 与 RING 两类，异常处理未覆盖网络中断与二次振铃等更复杂情形。
