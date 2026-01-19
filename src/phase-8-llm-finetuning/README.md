# Phase 8: LLM 微调

> **学习目标**：掌握 LLM 微调技术
> **预计时长**：2 周

## 📚 本阶段内容

### 1. 微调概述

- `01-finetuning-overview.py` - 微调方法概述
- `02-dataset-preparation.py` - 数据集准备
- `03-instruction-dataset.py` - 指令数据集构建

### 2. 参数高效微调

- `04-lora-basics.py` - LoRA 原理与实现
- `05-qlora.py` - QLoRA 量化微调
- `06-peft-library.py` - PEFT 库使用

### 3. 微调实践

- `07-supervised-finetuning.py` - 监督微调 (SFT)
- `08-dpo-training.py` - DPO 训练
- `09-model-merging.py` - 模型合并

### 4. 微调评估

- `10-finetuning-evaluation.py` - 微调效果评估

## 🎯 实战项目

**领域特定助手微调**：使用 LoRA 微调开源模型，构建特定领域的专业助手。

## 📖 参考资料

- [LoRA 论文](https://arxiv.org/abs/2106.09685)
- [PEFT 文档](https://huggingface.co/docs/peft)
- [TRL 库](https://huggingface.co/docs/trl)

## ✅ 学习检查

- [ ] 理解 LoRA/QLoRA 的原理
- [ ] 能够准备微调数据集
- [ ] 掌握使用 PEFT 进行微调
- [ ] 了解 DPO 等对齐方法
