"""
自动评估
========

学习目标：
    1. 掌握传统 NLP 评估指标的实现
    2. 使用基准测试评估模型
    3. 实现自动化评估流程

核心概念：
    - Perplexity：困惑度
    - BLEU/ROUGE：n-gram 匹配
    - 基准测试：标准化评估

环境要求：
    - pip install transformers torch nltk rouge-score evaluate
"""

import math
from typing import List, Dict


# ==================== 第一部分：困惑度 ====================


def perplexity_evaluation():
    """困惑度评估"""
    print("=" * 60)
    print("第一部分：困惑度 (Perplexity)")
    print("=" * 60)

    print("""
    📌 困惑度解释：
    ┌────────────────────────────────────────────────────────┐
    │  Perplexity = exp(Cross-Entropy Loss)                  │
    │                                                        │
    │  • PPL = 1    →  完美预测（不可能达到）                │
    │  • PPL = 10   →  平均每个位置有10个等概率选择         │
    │  • PPL = 100  →  模型较困惑，预测不确定               │
    │                                                        │
    │  注意：PPL只能在相同词表的模型间比较                   │
    └────────────────────────────────────────────────────────┘
    """)

    code = '''
import torch
import math
from transformers import AutoModelForCausalLM, AutoTokenizer

def calculate_perplexity(model, tokenizer, text):
    """计算文本的困惑度"""
    encodings = tokenizer(text, return_tensors='pt')

    with torch.no_grad():
        outputs = model(**encodings, labels=encodings['input_ids'])
        loss = outputs.loss

    perplexity = math.exp(loss.item())
    return perplexity

# 使用示例
# model = AutoModelForCausalLM.from_pretrained("gpt2")
# tokenizer = AutoTokenizer.from_pretrained("gpt2")
# text = "今天天气很好，适合出去散步。"
# ppl = calculate_perplexity(model, tokenizer, text)
# print(f"Perplexity: {ppl:.2f}")
'''
    print(code)


# ==================== 第二部分：BLEU 和 ROUGE ====================


def bleu_rouge_evaluation():
    """BLEU 和 ROUGE 评估"""
    print("\n" + "=" * 60)
    print("第二部分：BLEU 和 ROUGE")
    print("=" * 60)

    bleu_code = '''
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def calculate_bleu(reference, candidate):
    """计算 BLEU 分数（用于翻译和生成）"""
    reference_tokens = [reference.split()]
    candidate_tokens = candidate.split()

    # 使用平滑函数处理短文本
    smoothie = SmoothingFunction().method4

    score = sentence_bleu(
        reference_tokens,
        candidate_tokens,
        weights=(0.25, 0.25, 0.25, 0.25),  # BLEU-4
        smoothing_function=smoothie
    )
    return score

# 示例
reference = "The cat sits on the mat"
candidate = "The cat is sitting on the mat"
bleu = calculate_bleu(reference, candidate)
print(f"BLEU: {bleu:.4f}")
'''
    print(bleu_code)

    rouge_code = '''
from rouge_score import rouge_scorer

def calculate_rouge(reference, candidate):
    """计算 ROUGE 分数（用于摘要评估）"""
    scorer = rouge_scorer.RougeScorer(
        ['rouge1', 'rouge2', 'rougeL'],
        use_stemmer=True
    )
    scores = scorer.score(reference, candidate)

    return {
        'rouge1': scores['rouge1'].fmeasure,
        'rouge2': scores['rouge2'].fmeasure,
        'rougeL': scores['rougeL'].fmeasure
    }
'''
    print(rouge_code)


# ==================== 第三部分：基准测试评估 ====================


def benchmark_evaluation():
    """基准测试评估"""
    print("\n" + "=" * 60)
    print("第三部分：基准测试评估")
    print("=" * 60)

    code = '''
from tqdm import tqdm

class BenchmarkEvaluator:
    """基准测试评估器"""

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def evaluate_mmlu(self, dataset):
        """评估 MMLU（知识问答）"""
        results = {'correct': 0, 'total': 0}

        for item in tqdm(dataset):
            # 构造多选题 prompt
            prompt = self._format_mmlu_prompt(item)
            response = self._generate(prompt)
            predicted = self._extract_choice(response)

            if predicted == item['answer']:
                results['correct'] += 1
            results['total'] += 1

        results['accuracy'] = results['correct'] / results['total']
        return results

    def evaluate_gsm8k(self, dataset, use_cot=True):
        """评估 GSM8K（数学推理）"""
        correct = 0
        total = len(dataset)

        for item in tqdm(dataset):
            if use_cot:
                prompt = f"""Question: {item['question']}

Let's solve this step by step:
"""
            else:
                prompt = f"Question: {item['question']}\\nAnswer:"

            response = self._generate(prompt)
            predicted = self._extract_number(response)

            if str(predicted) == str(item['answer']):
                correct += 1

        return {'accuracy': correct / total}

    def _generate(self, prompt, max_tokens=256):
        inputs = self.tokenizer(prompt, return_tensors='pt')
        outputs = self.model.generate(**inputs, max_new_tokens=max_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
'''
    print(code)


# ==================== 第四部分：使用 Evaluate 库 ====================


def evaluate_library():
    """使用 Evaluate 库"""
    print("\n" + "=" * 60)
    print("第四部分：使用 HuggingFace Evaluate 库")
    print("=" * 60)

    code = """
import evaluate

# 加载评估指标
bleu = evaluate.load("bleu")
rouge = evaluate.load("rouge")
bertscore = evaluate.load("bertscore")

# 计算 BLEU
predictions = ["hello world", "how are you"]
references = [["hello world"], ["how are you doing"]]
bleu_result = bleu.compute(predictions=predictions, references=references)
print(f"BLEU: {bleu_result['bleu']:.4f}")

# 计算 ROUGE
rouge_result = rouge.compute(predictions=predictions, references=references)
print(f"ROUGE-L: {rouge_result['rougeL']:.4f}")

# 计算 BERTScore（语义相似度）
bert_result = bertscore.compute(
    predictions=predictions,
    references=references,
    lang="en"
)
print(f"BERTScore F1: {sum(bert_result['f1'])/len(bert_result['f1']):.4f}")
"""
    print(code)


# ==================== 第五部分：自动化评估流程 ====================


def automated_pipeline():
    """自动化评估流程"""
    print("\n" + "=" * 60)
    print("第五部分：自动化评估流程")
    print("=" * 60)

    code = '''
class AutomatedEvaluator:
    """自动化评估器"""

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.results = {}

    def run_full_evaluation(self, test_sets):
        """运行完整评估"""
        for name, dataset in test_sets.items():
            print(f"评估 {name}...")

            if name == "mmlu":
                self.results[name] = self._evaluate_mmlu(dataset)
            elif name == "gsm8k":
                self.results[name] = self._evaluate_gsm8k(dataset)
            elif name == "humaneval":
                self.results[name] = self._evaluate_humaneval(dataset)

        return self.generate_report()

    def generate_report(self):
        """生成评估报告"""
        report = "=" * 50 + "\\n"
        report += "模型评估报告\\n"
        report += "=" * 50 + "\\n"

        for name, result in self.results.items():
            report += f"\\n{name.upper()}:\\n"
            for metric, value in result.items():
                report += f"  {metric}: {value:.4f}\\n"

        return report
'''
    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现一个计算 BLEU 和 ROUGE 的函数

        ✅ 参考答案：
        ```python
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        from rouge_score import rouge_scorer
        from typing import Dict, List
        
        class TextEvaluator:
            '''文本评估器'''
            
            def __init__(self):
                self.rouge_scorer = rouge_scorer.RougeScorer(
                    ['rouge1', 'rouge2', 'rougeL'],
                    use_stemmer=True
                )
                self.smoothie = SmoothingFunction().method4
            
            def calculate_bleu(
                self, 
                reference: str, 
                candidate: str,
                weights: tuple = (0.25, 0.25, 0.25, 0.25)
            ) -> float:
                '''计算 BLEU 分数'''
                ref_tokens = [reference.split()]
                cand_tokens = candidate.split()
                
                return sentence_bleu(
                    ref_tokens, 
                    cand_tokens,
                    weights=weights,
                    smoothing_function=self.smoothie
                )
            
            def calculate_rouge(
                self, 
                reference: str, 
                candidate: str
            ) -> Dict[str, float]:
                '''计算 ROUGE 分数'''
                scores = self.rouge_scorer.score(reference, candidate)
                return {
                    'rouge1': scores['rouge1'].fmeasure,
                    'rouge2': scores['rouge2'].fmeasure,
                    'rougeL': scores['rougeL'].fmeasure
                }
            
            def evaluate(
                self, 
                reference: str, 
                candidate: str
            ) -> Dict[str, float]:
                '''综合评估'''
                return {
                    'bleu': self.calculate_bleu(reference, candidate),
                    **self.calculate_rouge(reference, candidate)
                }
        
        # 使用示例
        evaluator = TextEvaluator()
        ref = "机器学习是人工智能的一个分支"
        cand = "机器学习属于人工智能领域"
        scores = evaluator.evaluate(ref, cand)
        print(f"BLEU: {scores['bleu']:.4f}, ROUGE-L: {scores['rougeL']:.4f}")
        ```
    
    练习 2：在 MMLU 子集上评估一个小模型

        ✅ 参考答案：
        ```python
        from datasets import load_dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from tqdm import tqdm
        
        class MMLUEvaluator:
            '''MMLU 评估器'''
            
            def __init__(self, model_name: str):
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            def format_prompt(self, item: dict) -> str:
                '''格式化 MMLU 问题'''
                choices = ['A', 'B', 'C', 'D']
                prompt = f"Question: {item['question']}\\n"
                for i, choice in enumerate(item['choices']):
                    prompt += f"{choices[i]}. {choice}\\n"
                prompt += "Answer:"
                return prompt
            
            def evaluate_subset(
                self, 
                subject: str = "abstract_algebra",
                split: str = "test"
            ) -> dict:
                '''评估 MMLU 子集'''
                dataset = load_dataset("cais/mmlu", subject, split=split)
                
                correct = 0
                total = 0
                
                for item in tqdm(dataset):
                    prompt = self.format_prompt(item)
                    pred = self._generate_answer(prompt)
                    
                    if pred == ['A', 'B', 'C', 'D'][item['answer']]:
                        correct += 1
                    total += 1
                
                return {
                    'subject': subject,
                    'accuracy': correct / total,
                    'correct': correct,
                    'total': total
                }
        
        # 使用示例
        # evaluator = MMLUEvaluator("Qwen/Qwen2-0.5B-Instruct")
        # result = evaluator.evaluate_subset("high_school_physics")
        # print(f"Accuracy: {result['accuracy']:.2%}")
        ```

    思考题：为什么自动评估指标有时与人类评估不一致？

        ✅ 答：
        1. 词汇匹配局限 - BLEU/ROUGE 基于 n-gram 匹配，无法理解语义等价
        2. 创造性忽视 - 自动指标惩罚创造性表达，即使更好
        3. 主观偏好 - 人类偏好难以量化（如幽默感、文风）
        4. 上下文理解 - 自动指标难以评估上下文适当性
        5. 任务特异性 - 通用指标无法捕捉特定任务的关键要素
    """)


def main():
    perplexity_evaluation()
    bleu_rouge_evaluation()
    benchmark_evaluation()
    evaluate_library()
    automated_pipeline()
    exercises()
    print("\n课程完成！下一步：03-llm-as-judge.py")


if __name__ == "__main__":
    main()
