# 实验三报告
姓名：卢学翔
学号：2024280318

## 原理与手算
事件是一次离散输入（OFFHOOK、ONHOOK、DIGIT、TIMEOUT），状态是呼叫在事件之间保持的属性。同一状态遇到不同事件走向不同分支，因此控制器只做“当前状态 + 事件 → 动作与下一状态”的查表，而不保存任何隐藏流程。

正常呼叫的手算（用户 1001 呼 1002）：0ms 1001 摘机，采样 0→1 产生 OFFHOOK，框架新建 C1，控制器发 DIAL_TONE 并 arm DIAL 5000，timer 代次变为 1；100、200、300ms 依次拨 1、0、0，三次都仍是合法前缀，回 INCOMPLETE，只发 STOP_DIAL_TONE 保持 COLLECTING；400ms 拨 2 得到 1002，判 LOCAL，reserve 成功（1002 挂机且未被占用），于是 cancel 使 timer=2、进入 RINGING、arm RING 10000 使 timer=3，并发 RING 与 RINGBACK；800ms 1002 摘机，控制器先 cancel 再 activate，connect_pair 建立两条方向（链路0 TS2←TS1、链路0 TS1←TS2），返回 True 后置 CONNECTED 并 STOP_RING、CONNECT。

字节手算：sample_frame(0) 中链路0 的时隙值为 (0*101 + 3*时隙 + 0)，故 TS1=3、TS2=6。T 级把输入 TS1 搬到输出 TS2、输入 TS2 搬到输出 TS1，S 级仍留在链路0，所以输出帧 TS1=6、TS2=3，正好互换，未被占用的时隙保持 0xD5。1000ms 1001 挂机时状态是 CONNECTED，判 NORMAL_CLEAR，finish 拆除双向映射、cancel 使 timer=5、清除归属；1002 采样仍为 1，只能进入 WAIT_ONHOOK，直到真实 ONHOOK 才回 IDLE。

## 结果分析
运行 python -m src.run_experiment 输出三个文件。scenario_results.json 中 12 个场景全部 passed=true，passed=12、total=12；call_events.jsonl 逐行记录 scenario、time_ms、event、before、after、actions、reason；call_sequence.png 给出 release_1001 与 NO_ANSWER 两条时序，前者是 IDLE→COLLECTING→RINGING→CONNECTED→ENDED，后者在 400ms 进 RINGING 并在 10400ms 到 ENDED。

真实话路证据来自字节而不是图形：接通后对 sample_frame(0) 做 exchange_frame，输出链路0 的 TS1=6、TS2=3，与输入 TS1=3、TS2=6 严格互换，未用槽位为 0xD5；释放后 tables.pairs 为空、owners 为空，再交换同一帧时 TS1 与 TS2 都回到 0xD5，说明双向映射确实被拆除而不是只改了状态字符串。日志还显示 5000ms 的旧 DIAL 超时事件 before=CONNECTED、after=CONNECTED、actions 为空，10400ms 的旧 RING 超时同样被忽略，因为应答时的 cancel 已使这两个 token 失效。

## 反例与验证
自拟测试 test_cancel_in_collecting_ignores_old_dial 构造 0ms 摘机、100ms 拨“1”、200ms 挂机的序列，断言 C1 为 ENDED、reason=CALLER_CANCEL、tables.pairs 与 owners 为空、1001 不进入 WAIT_ONHOOK，并且 5000ms 到达的旧 DIAL 定时器在日志中前后状态都是 ENDED、actions 为空。另一条 test_number_prefix_with_configured_plan 用 2001、2002 的拨号计划验证前缀、本局、自呼与非法四个分支。

三个刻意构造的反例说明了实现细节的必要性。其一，超时处理若只比较 timer_kind 而不比较 token，无人接听场景会在 5000ms 被旧的 DIAL 定时器提前打断，test_old_dial_after_ringing 直接失败。其二，收号完整进入 RINGING 时若忘记 cancel，旧 DIAL 定时器仍被当作有效，日志会出现 RINGING→ENDED 的错误跳变。其三，应答时若只把状态改成 CONNECTED 而不调用 activate，字节断言 out[0,1]==a[0,2] 必然失败，因为输出仍是 0xD5。实际运行结果是四组评分测试 27 passed，完整评分与自拟测试也全部通过。

## 局限
逻辑时钟与事件队列代替真实时间，没有 sleep 和线程，无法体现调度抖动、采样丢帧和帧同步误差。摘挂机检测以整表快照为输入，只能看到两次采样之间的净变化，短于采样周期的拍叉会漏检。号码分析固定四位十进制且只做前缀匹配，没有号首分析、路由选择和计费。交换部分只模拟 T/S 控制表与单帧缓存，未涉及真实信令（如 No.7）的握手、监视与异常释放流程。
