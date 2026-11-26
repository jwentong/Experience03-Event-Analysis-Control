# AI使用记录
## 需求
完成现代交换原理实验三，编写 `control.py` 里的 `handle_call_event` 呼叫状态机代码；定位并修复 IndexError、KeyError、定时器 timeout 相关报错，保证框架测试用例能够通过；后续按实验要求书写自测用例。
提示词：从 hooks 开始写，先写 detect_hook_events，接着编写 numbering 号码分析，再写 control 呼叫事件处理，排查 Index 越界、字典键缺失、定时器联动报错，最小改动修复 bug，不要额外引入不存在的框架接口。
## 建议与采纳
1. 建议：优先定位 IndexError 根源，判断是动作列表 actions 为空追加失败、还是呼叫对象 caller 初始化时机错误；不要一次性大量改动代码。先锁定`caller`赋值顺序问题，只做最小修改。
2. 建议：timeout 定时器函数和 control 代码互相联动，修复 control 时不要破坏 timeout 原有逻辑。采纳，增加空值、状态合法性校验，避免定时器事件触发时报错。
3. 建议：自测使用框架原生格式编写，不额外自定义测试结构。采纳，按照实验任务书格式编写 student 自测用例。
4. 建议：不要新增框架不存在的分配端点 API，避免`same endpoint`新报错。采纳，回退多余新增逻辑，只保留状态流转和动作下发逻辑。
## 验证证据
运行实验自带测试脚本，control 模块、timeout 模块全部测试用例执行通过，无 IndexError、KeyError；
自测场景：摘机收号、号码合法振铃、被叫应答通话、挂机释放、拨号超时，状态机流转符合实验状态表；
运行命令示例：`python -m pytest test_control.py -v`，所有用例 PASS，输出无报错日志。
