# AI使用记录

## 需求

工具：DeepSeek Harness 编码助手（deepseek-flash），Python 3.12，pytest 9。

任务：按教师仓库 README 的状态表与 `docs` 约定，补全 `src/hooks.py`、`src/numbering.py`、`src/control.py`、`src/timeouts.py` 四个函数，实现摘挂机检测、四位号码分析、呼叫控制与超时处理；不修改 `src/runtime.py`、`src/switch_*.py`、grading 与工作流，并生成 `results/` 下的两个 JSON 与一张 PNG。

允许修改：上述四个任务文件、`student_tests/test_my_case.py`、`REPORT.md`、`AI_LOG.md`。

## 建议与采纳

**建议一：控制函数按“状态优先、事件来源其次”分支。** 同一个 `OFFHOOK` 在 `COLLECTING` 是主叫摘机（送拨号音、起收号定时器），在 `RINGING` 是被叫应答（取消振铃、`activate` 建话路）。采纳：`handle_call_event` 先看 `c.state` 再判断 `e['user']` 是否等于 `caller` 或 `callee`，避免把被叫摘机当成新的主叫。

**建议二：定时器必须带代次校验。** 收号完成后取消定时器、振铃后又重新 `arm`，旧的 `TIMEOUT` 事件仍留在队列里。采纳：`handle_timeout` 依次校验 `call_id`、`token == c.timer`、`value == c.timer_kind` 和当前状态，任一项不符就原样返回，不改变状态、话路和资源。

**建议三：号码分析按“前缀 → 完整 → 自己”顺序判定。** 采纳：先看是否有号码以输入为前缀（空串也算），再判断是否满四位且命中号码表，最后区分 `SELF_CALL`；长度超过四位、含非数字、无前缀一律 `INVALID`。

**建议四：挂机释放统一走 `s.finish`。** 不直接改 `hooks`，由框架把仍摘机的用户放进 `WAIT_ONHOOK`。采纳，并在自拟测试里验证“主叫先挂机、被叫后摘机”不会接续旧呼叫。

## 验证证据

**手算预期**：0 ms 摘机、100/200/300/400 ms 拨 1002、800 ms 应答、1000 ms 主叫挂机，状态应为 `COLLECTING→RINGING→CONNECTED→ENDED`；帧 0 的 TS1=3、TS2=6，接通后输出帧 1 的 TS1=6、TS2=3，释放后回到 `0xD5`。

**实际命令与结果**：

```
python -m src.run_experiment
Scenarios passed: 12/12

python -m pytest grading -q
37 passed

python -m pytest student_tests -q
2 passed

python grading/run_grading.py --local
实验 70/70，报告 30/30，总分 100/100
```

**边界验证**：自拟测试确认非主叫的 `DIGIT` 被忽略（`digits` 保持空串）、振铃中主叫挂机后旧呼叫为 `CALLER_CANCEL` 且 `pairs` 为空、被叫随后摘机只会新建 C2。旧定时器场景中日志保留了 5000 ms 的 `TIMEOUT` 行，但 `before` 与 `after` 相同、`actions` 为空，证明代次校验生效。
