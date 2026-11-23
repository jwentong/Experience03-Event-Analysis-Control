# AI使用记录

## 需求

使用 Codex 协助检查四个学生函数与课程框架的接口，补全实验报告、AI 使用记录和至少一个自拟测试，并在终端生成三个结果文件、运行公开测试。需要重点确认摘机定时器、号码分析的数据来源、旧定时器失效以及挂机后的等待状态。

## 建议与采纳

AI 根据 README 状态表和 `Exchange` 字段指出，号码分析应使用 `s.numbers`，主叫摘机时还必须发送 DIAL_TONE 并调用 `s.arm(c, "DIAL", 5000)`。这两项建议与课程接口一致，已采纳并做最小修改；其余收号、预留、振铃、应答和释放逻辑保留原有实现。AI 提出的“收号中途挂机后仍将收到旧 DIAL 超时”自拟用例能够直接检查 token 和资源释放，已采纳为本人验证用例。

## 验证证据

手算确认输入帧 0 的 TS1=3、TS2=6，应答后输出为 TS1=6、TS2=3，释放后两个位置均为 0xD5；仍摘机的被叫进入 WAIT_ONHOOK。终端运行四个核心测试文件得到 27 passed，自拟测试得到 1 passed，`python -m src.run_experiment` 输出 Scenarios passed: 12/12。最终执行 `python -m pytest grading student_tests -q -p no:cacheprovider` 得到 38 passed。
