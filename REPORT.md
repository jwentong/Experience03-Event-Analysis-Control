# 实验三 用户事件 号码分析与呼叫控制

姓名：郭梦真
学号：2024280011

## 原理与手算

摘挂机采样描述用户在某一时刻的物理状态，事件描述相邻两次采样之间的变化。只有采样从0变为1或从1变为0时，框架才生成OFFHOOK或ONHOOK；重复采样不会重复创建呼叫。一次呼叫建立过程由Call对象保存主叫、被叫、号码、状态、定时器代次和结束原因。回铃音只说明系统正在等待被叫应答，并不表示话路已经接通；只有被叫OFFHOOK触发activate，并且connect_pair成功写入双向T/S映射后，状态才由RINGING进入CONNECTED。

正常示例的状态变化如下：

| 时间 | 事件 | 状态与动作 | 定时器或话路 |
|------|------|-----------|-------------|
| 0 ms | 1001摘机 | COLLECTING，发送DIAL_TONE | DIAL token=1，5000 ms后超时 |
| 100至400 ms | 依次拨1、0、0、2 | 每次停止拨号音；400 ms时号码完整，预留1002并发送RING、RINGBACK | DIAL token失效，RING token=3，10400 ms超时 |
| 800 ms | 1002摘机应答 | RINGING变为CONNECTED，停止振铃并建立双向话路 | 取消RING定时器 |
| 1000 ms | 1001挂机 | 原因NORMAL_CLEAR，释放话路，状态ENDED | 1002仍摘机，进入WAIT_ONHOOK |

手算帧0时，链路0的TS1样值为`0*101+1*3+0=3`，TS2样值为`0*101+2*3+0=6`。接通1001的TS1与1002的TS2后，方向TS1到TS2使输出TS2等于输入TS1，方向TS2到TS1使输出TS1等于输入TS2，因此应答后的输出帧TS1为6、TS2为3，与输入帧交换结果相反。输入帧k的交换结果按一帧缓存规则在k+1可用。挂机后disconnect_pair删除两个方向的T/S表项，原本承载业务数据的TS1、TS2输出恢复空闲字节0xD5，pairs集合也应为空。

## 结果分析

运行`python -m src.run_experiment`后，`scenario_results.json`记录`passed=12`、`total=12`，12个场景全部通过。完整日志包含双向接通、主叫挂机、被叫挂机、非法号码、自呼、被叫忙、收号超时、无人接听、振铃取消、旧定时器、重复采样和释放后复用。生成的JSON与JSONL内容和参考结果逐字核对一致，说明状态、动作和原因字段并非只靠图形外观判断。

正常释放曲线在0至400 ms保持COLLECTING，400 ms进入RINGING，800 ms应答后进入CONNECTED，1000 ms主叫挂机后进入ENDED。无人接听曲线在同一时刻进入RINGING，但在10400 ms才由RING超时进入ENDED，原因为NO_ANSWER。5000 ms到达的旧DIAL超时仍写入日志，但事件前后均为RINGING，动作数组为空，因为该事件的token为1，而当前RING定时器token为3，并且timer_kind已经是RING。

真实话路检查使用样例帧得到连通前TS1=3、TS2=6，应答后输出TS1=6、TS2=3。释放场景中`tables.pairs`为空，相关输出时隙恢复0xD5。被叫忙场景中第二次呼叫结束为USER_BUSY，但原C1仍保持CONNECTED且pairs数量保持1，说明失败呼叫没有破坏已有话路。

## 反例与验证

自拟测试`student_tests/test_my_case.py::test_partial_digits_do_not_extend_dial_timeout`专门检查“收号总超时从摘机起算，输入数字不重置定时器”。测试在0 ms让1001摘机，1000 ms输入1，2000 ms输入0，然后运行到事件队列结束。预期5000 ms的DIAL超时到达时，Call状态为ENDED、原因为DIAL_TIMEOUT、已收号码仍为`10`，并且不存在已建立话路；断言同时检查这四项。

第一轮场景运行时发现振铃取消未生效：RINGING分支先过滤了非应答事件并提前返回，主叫600 ms挂机没有执行finish，最终被10400 ms的振铃超时错误结束为NO_ANSWER。修复方式是在状态分支前统一优先处理活动呼叫的ONHOOK，并保留“通话中NORMAL_CLEAR、通话前CALLER_CANCEL”的原因选择。再次运行后得到12/12，cancel_ringing在600 ms记录RELEASE并结束为CALLER_CANCEL。

标准环境中可执行以下验证命令：

```powershell
python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q
python -m src.run_experiment
python -m pytest grading student_tests -q
```

实际运行场景的输出为`Scenarios passed: 12/12`。生成文件包括`results/call_sequence.png`、`results/call_events.jsonl`和`results/scenario_results.json`，其中JSON与JSONL已逐行核对，状态图也已检查。

## 局限

本实验采用逻辑时间、串行事件队列和软件采样，不模拟真实线路的抖动、连续信号、媒体编码或并发CPU调度。回铃音、忙音和失败音只记录为动作，不生成真实音频。网络拒绝场景通过注入activate失败来验证控制分支，没有覆盖物理链路故障。T/S交换模块使用固定32时隙和单帧缓存，适合手算验证，但不等同于完整交换机的多级网络、时钟同步和信令协议。当前模型重点验证控制逻辑与资源一致性，实际工程还需考虑信令重传、并发竞争、掉电恢复和端到端媒体质量。
