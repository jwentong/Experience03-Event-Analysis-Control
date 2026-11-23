# AI使用记录

## 需求

使用 OpenAI Codex 辅助阅读实验三 PRD、理解事件驱动呼叫控制和四个任务接口。要求只修改 src/hooks.py、src/numbering.py、src/control.py、src/timeouts.py、报告、AI 记录和自拟测试，不修改 runtime、switch_*、grading 或工作流。先手算正常呼叫状态和定时器，再逐项实现和验证。

## 建议与采纳

AI 建议把事件与 Call 状态分开处理：OFFHOOK/ONHOOK 先由摘挂机检测去重，DIGIT 只在主叫 COLLECTING 时追加；完整合法号码调用 reserve，成功后才取消 DIAL 定时器并进入 RINGING；被叫应答必须先 cancel 再 activate，只有 activate 成功才进入 CONNECTED。超时处理先比较 token 和 timer_kind，再按 COLLECTING/RINGING 处理，旧定时器直接忽略。以上建议已采纳，并用公开测试、自拟反例和 12 个固定场景验证。

## 验证证据

手算正常流程：0 ms 1001 摘机，100/200/300/400 ms 输入 1002，800 ms 1002 应答，1000 ms 1001 挂机；状态依次为 COLLECTING、RINGING、CONNECTED、ENDED，1002 仍摘机进入 WAIT_ONHOOK。运行 27 项公开测试和 2 项自拟测试全部通过；scenario_results.json 为 passed=12、total=12；call_events.jsonl 和 call_sequence.png 已由本人实现生成；旧 DIAL 定时器日志前后状态保持 CONNECTED。
