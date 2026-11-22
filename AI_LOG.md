# AI使用记录

## 需求

用户向Codex提供实验三规范并请求协助完成作业。AI读取规范及课程仓库，任务是补全摘挂机检测、号码分析、呼叫控制和超时处理四个函数，编写自拟测试，生成运行结果，并整理REPORT.md及本记录。当前版本由AI辅助编写并在本地环境执行验证；不将AI执行的验证描述为学生本人已经独立完成。

## 建议与采纳

采用按相邻采样变化产生事件、按配置进行前缀匹配、使用reserve与activate区分资源预留和实际接通、统一调用finish释放的实现方式。采用token、timer_kind与call_id联合校验，确保旧超时不影响新状态。补充八个边界测试，检查收号总超时、错误关联、无关用户、等待挂机、实际字节、同刻顺序和非ASCII字符。不采用修改教师框架、删除测试、伪造JSON或把hooks强制改为0的做法；未修改runtime、switch模块、grading或工作流。

## 验证证据

基于课程仓库提交bc54760632d8d15d868131d3094f9c7c7fdc654d，在独立Python虚拟环境安装requirements.txt。先运行python -m pytest grading/test_hooks.py grading/test_numbering.py grading/test_control.py grading/test_timeouts.py student_tests -q；再运行python -m src.run_experiment生成三项结果；最后运行python -m pytest grading student_tests -q以及python -m grading.run_grading --local进行结构化验收。实际输出保存在随附本地验证记录中。

实际结果：任务函数与自拟测试共35项通过；实验运行显示Scenarios passed: 12/12；完整公开测试加自拟测试共45项通过。课程评分器本地模式结果为实验70/70、报告结构30/30、合计100/100。该分数是当前公开规则的本地结果，不是教师已确认的最终成绩。

手算核对：振铃截止400+10000=10400 ms；帧0输入TS1=3、TS2=6，接通输出6、3，释放输出213、213。自拟断言同时检查一帧缓存标号和过期事件前后状态一致。运行记录是AI在当前环境执行的证据；学生提交前应阅读代码、理解反例并在自己的环境复现，不应将本记录改写为未使用AI。
