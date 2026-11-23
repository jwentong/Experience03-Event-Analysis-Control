# AI使用记录
## 需求
任务是补全实验三的四个函数：摘挂机检测 detect_hook_events、号码分析 analyze_number、呼叫控制 handle_call_event 与超时处理 handle_timeout，使 12 个场景全部通过并生成结果文件。给 AI 的提示要求：严格按 README 的状态表实现，原地修改 Call 并通过 s.arm/cancel/reserve/activate/finish 调用框架服务，不得修改 runtime 与 switch 模块、不得删除测试。

## 建议与采纳
AI 建议用 ASCII 白名单 '0123456789' 判断数字而非 str.isdigit()，理由是 isdigit 会把全角数字也判为真，导致非法字符漏判——采纳，并据此写了边界自拟测试。AI 建议 ONHOOK 一律按“通话中 NORMAL_CLEAR、通话前 CALLER_CANCEL”分支处理，并由框架 finish 负责把未挂机用户放入 WAIT_ONHOOK——采纳，避免直接改 hooks=0。AI 在超时处理中建议先比较 token 再比较 timer_kind 再判断状态，旧 token 直接返回——采纳。AI 初版自拟测试把“被叫挂机后呼叫它”误当成忙线，我据状态表修正为“被叫处于 WAIT_ONHOOK 时呼叫才忙”，予以修改。

## 验证证据
手算正常呼叫各时刻状态与定时器代次，与日志一致。运行 python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py -q 得 27 passed；python -m src.run_experiment 输出 Scenarios passed: 12/12；python -m pytest student_tests -q 得 3 passed。字节验证：接通后 TS1 由 0x03 换到 0x06、TS2 由 0x06 换到 0x03；主叫释放后输出为 0xD5。
