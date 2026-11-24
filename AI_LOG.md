# AI使用记录
## 需求
任务是补全 hooks、numbering、control、timeouts 四个文件的核心逻辑。提示词中明确要求根据测试文件和 runtime.py 框架实现状态机。

## 建议与采纳
AI 建议在超时处理时，必须校验 token 和 timer_kind，以防旧的定时器干扰当前呼叫；并建议在拨号阶段根据号码分析结果分别处理 INVALID 和 LOCAL。我采纳了这些建议，修改了 timeouts.py 中的校验逻辑。

## 验证证据
根据文档手算推演状态流转，运行 `pytest grading/...` 后，实际结果为 27 项测试全绿通过（27 passed）。生成结果文件后，检查日志验证了状态切换和字节交换完全符合预期。