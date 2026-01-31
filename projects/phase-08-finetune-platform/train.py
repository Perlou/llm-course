"""
训练脚本
执行 LoRA/QLoRA 微调
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.table import Table

from scripts.training_utils import (
    load_config,
    get_peft_config,
    get_quantization_config,
    get_training_arguments,
)
from scripts.model_utils import load_base_model, apply_lora, get_model_info


console = Console()


def create_dataset(data_config, tokenizer, max_seq_length: int):
    """创建训练数据集"""
    from datasets import load_dataset

    train_file = data_config.get("train_file", "./data/processed/train.json")
    eval_file = data_config.get("eval_file", "./data/processed/eval.json")

    dataset = load_dataset(
        "json",
        data_files={
            "train": train_file,
            "eval": eval_file if os.path.exists(eval_file) else train_file,
        },
    )

    def format_example(example):
        """格式化单个样本"""
        messages = example.get("messages", [])
        text = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                text += "<|im_start|>user\n" + content + "<|im_end|>\n"
            elif role == "assistant":
                text += "<|im_start|>assistant\n" + content + "<|im_end|>\n"
        return {"text": text}

    dataset = dataset.map(format_example)

    def tokenize(example):
        return tokenizer(
            example["text"],
            truncation=True,
            max_length=max_seq_length,
            padding="max_length",
        )

    dataset = dataset.map(tokenize, batched=True)

    return dataset


def main():
    parser = argparse.ArgumentParser(description="LoRA/QLoRA 微调训练")
    parser.add_argument("--config", "-c", default="config.yaml", help="配置文件路径")
    parser.add_argument("--output", "-o", help="输出目录（覆盖配置）")
    parser.add_argument("--resume", help="从检查点恢复训练")

    args = parser.parse_args()

    console.print("\n[bold blue]🚀 LoRA 微调训练[/bold blue]\n")

    # 加载配置
    console.print(f"加载配置: {args.config}")
    config = load_config(args.config)

    model_cfg = config.get("model", {})
    lora_cfg = config.get("lora", {})
    quant_cfg = config.get("quantization", {})
    training_cfg = config.get("training", {})
    data_cfg = config.get("data", {})

    # 输出目录
    output_dir = args.output or training_cfg.get("output_dir", "./outputs")
    os.makedirs(output_dir, exist_ok=True)

    # 加载模型
    model_name = model_cfg.get("name", "Qwen/Qwen2.5-1.5B-Instruct")
    quant_config = get_quantization_config(quant_cfg)

    model, tokenizer = load_base_model(
        model_name,
        quantization_config=quant_config,
        trust_remote_code=model_cfg.get("trust_remote_code", True),
    )

    # 应用 LoRA
    lora_config = get_peft_config(lora_cfg)
    model = apply_lora(model, lora_config)

    # 显示模型信息
    info = get_model_info(model)

    table = Table(title="模型信息")
    table.add_column("属性", style="cyan")
    table.add_column("值", style="green")

    table.add_row("总参数", f"{info['total_parameters']:,}")
    table.add_row("可训练参数", f"{info['trainable_parameters']:,}")
    table.add_row("可训练比例", f"{info['trainable_percentage']:.2f}%")
    table.add_row("数据类型", info["dtype"])
    table.add_row("设备", info["device"])

    console.print(table)

    # 创建数据集
    console.print("\n准备数据集...")
    max_seq_length = training_cfg.get("max_seq_length", 1024)
    dataset = create_dataset(data_cfg, tokenizer, max_seq_length)

    console.print(f"训练集: {len(dataset['train'])} 样本")
    console.print(f"验证集: {len(dataset['eval'])} 样本")

    # 训练参数
    training_args = get_training_arguments(training_cfg, output_dir)

    # 创建 Trainer
    from trl import SFTTrainer

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["eval"],
        tokenizer=tokenizer,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
    )

    # 开始训练
    console.print("\n[bold green]开始训练...[/bold green]\n")

    if args.resume:
        trainer.train(resume_from_checkpoint=args.resume)
    else:
        trainer.train()

    # 保存最终模型
    final_path = os.path.join(output_dir, "checkpoint-final")
    trainer.save_model(final_path)
    console.print(f"\n[green]✅ 训练完成！模型保存至: {final_path}[/green]")


if __name__ == "__main__":
    main()
