# 实验三报告

姓名：肖昶烨
学号：2024280243

## 原理与手算

本实验采用事件驱动模型：框架按 (time_ms, sequence) 的先后顺序处理事件，同一时刻先入队先处理，不使用真实 sleep 或线程。摘挂机采样 0 表示挂机、1 表示摘机，相同采样不产生事件；只有 OFFHOOK/ONHOOK 发生变化时才生成事件。DIGIT 事件的 value 是一位数字字符，TIMEOUT 事件的 value 为 DIAL 或 RING，并通过定时器代次与 call_id 关联。

呼叫状态机为：空闲用户 OFFHOOK 后框架创建 Call，进入 COLLECTING，发出 DIAL_TONE 并 arm DIAL 5000ms；收号期间每收到一位数字就追加 digits 并 STOP_DIAL_TONE，号码不完整则继续收号；号码非法或自呼时 finish 对应原因并 FAIL_TONE 进入 ENDED；完整号码先 reserve，失败则 USER_BUSY 加 BUSY_TONE 结束，成功则取消收号定时器、进入 RINGING、arm RING 10000ms，并发出 RING 与 RINGBACK；被叫 OFFHOOK 时取消 RING 定时器，activate 成功才进入 CONNECTED 并 STOP_RING、CONNECT，失败则 NETWORK_BUSY 加 FAIL_TONE；活动呼叫收到 ONHOOK 时，通话中用 NORMAL_CLEAR，通话前用 CALLER_CANCEL，随后 RELEASE 进入 ENDED。finish 会自动释放双向话路、取消定时器、清除归属，仍摘机的用户进入 WAIT_ONHOOK，只有真实 ONHOOK 后才变空闲。

正常示例手算：0ms 1001 摘机，Call C1 进入 COLLECTING，动作 DIAL_TONE，arm DIAL 5000；100/200/300/400ms 依次拨 1/0/0/2，前三位号码不完整，每次 STOP_DIAL_TONE 继续收号，第四位 1002 判定为 LOCAL；reserve 成功后 cancel 收号定时器，进入 RINGING，arm RING 10000，动作 RING 与 RINGBACK；800ms 1002 摘机应答，cancel RING，activate 成功进入 CONNECTED，动作 STOP_RING 与 CONNECT；1000ms 1001 挂机，finish NORMAL_CLEAR，动作 RELEASE，进入 ENDED，1002 仍摘机进入 WAIT_ONHOOK。帧层面，输入帧 0 的 TS1=3、TS2=6，应答后输出帧 TS1=6、TS2=3，输出帧比输入帧晚一帧；释放后相关输出为 0xD5。无人接听示例：400ms 开始振铃，RING 定时器在 10400ms 到期，finish NO_ANSWER；5000ms 到达的旧 DIAL 超时因定时器代次不匹配被忽略，日志保留该事件但前后状态相同。

## 结果分析

运行 run_experiment 后生成三个结果文件。call_sequence.png 中可以看到两条状态时序：正常呼叫依次经过 COLLECTING、RINGING、CONNECTED、ENDED；无人接听在 RINGING 持续到 10400ms 后进入 ENDED。call_events.jsonl 逐行记录 scenario、time_ms、event、call_id、before、after、actions、reason，我逐条核对了 before 到 after 的迁移与状态表一致，actions 中 DIAL_TONE、STOP_DIAL_TONE、RING、RINGBACK、STOP_RING、CONNECT、RELEASE、FAIL_TONE、BUSY_TONE 的出现时机也与规范相符。scenario_results.json 中 12 个场景的 passed 均为 true，passed=12、total=12。

真实话路方面，activate 调用实验二已实现的 connect_pair，只有双向 T/S 映射建立成功才返回 True 并进入 CONNECTED，因此回铃音只表示正在呼叫，不等于接通。finish 负责释放双向话路、取消定时器并处理未挂机用户，释放后输出字节回到 0xD5。WAIT_ONHOOK 中的用户不会被直接改采样值，只有真实 ONHOOK 事件到达后才回到空闲，这保证了释放后复用场景的正确性。

## 反例与验证

我重点验证了旧定时器反例：当呼叫已经进入 RINGING 或 ENDED 后，5000ms 的 DIAL 超时事件仍会到达。handle_timeout 先判断 ENDED 直接返回，再校验事件定时器代次与 timer_kind 是否与当前 Call 匹配，不匹配也直接返回，因此前后状态、话路和资源都不变。call_events.jsonl 中无人接听场景保留了这个旧事件，且 before 与 after 相同，说明忽略逻辑生效。

我还验证了重复采样不产生事件、非主叫 DIGIT 被忽略、非 COLLECTING 状态下的 DIGIT 被忽略。自拟测试写在 student_tests/test_my_case.py，覆盖了相同采样只产生变化用户事件、非法采样抛 ValueError、号码分析的 INCOMPLETE/LOCAL/SELF_CALL/INVALID 四类结果，以及主叫摘机后进入 COLLECTING 且首个动作是 DIAL_TONE。运行 pytest student_tests -q 得到 4 passed。调试过程中还遇到事件是字典、号码计划是列表、非法原因字符串应为 INVALID 等细节，均通过逐条跑测试修正并验证。

## 局限

本实验使用逻辑时钟和软件事件队列，不涉及真实 sleep、真实 DTMF 噪声、线路损伤和网络时延抖动；同一时刻多个事件的处理依赖入队顺序，未对极端并发顺序做穷举；号码分析只支持四位定长号码，未覆盖可变长号段；WAIT_ONHOOK 的恢复路径只做了功能验证，未做长时间压力测试；真实交换机中的信令交互、回声和语音质量不在本实验范围内。
