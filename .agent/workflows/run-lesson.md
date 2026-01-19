---
description: 运行课程文件并验证输出
---

# 运行课程文件工作流

使用此工作流运行并验证课程文件。

## 步骤

1. 激活虚拟环境

```bash
source venv/bin/activate
```

2. 确保已配置环境变量

```bash
# 检查是否存在 .env 文件
cat .env
```

3. 运行课程文件

// turbo

```bash
python {课程文件路径}
```

4. 验证输出是否正常

5. 如遇到错误，根据错误信息修复代码
