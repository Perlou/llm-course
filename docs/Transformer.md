# 从零深入解析 Transformer 架构

---

## 目录

1. [为什么需要 Transformer？](#1-为什么需要-transformer)
2. [整体架构总览](#2-整体架构总览)
3. [输入表示：词嵌入与位置编码](#3-输入表示词嵌入与位置编码)
4. [核心机制：自注意力（Self-Attention）](#4-核心机制自注意力self-attention)
5. [多头注意力（Multi-Head Attention）](#5-多头注意力multi-head-attention)
6. [前馈神经网络（Feed-Forward Network）](#6-前馈神经网络feed-forward-network)
7. [残差连接与层归一化（Add & Norm）](#7-残差连接与层归一化add--norm)
8. [编码器（Encoder）详解](#8-编码器encoder详解)
9. [解码器（Decoder）详解](#9-解码器decoder详解)
10. [最终输出层](#10-最终输出层)
11. [训练细节](#11-训练细节)
12. [完整前向传播流程](#12-完整前向传播流程)
13. [PyTorch 简易实现](#13-pytorch-简易实现)
14. [Transformer 的变体与影响](#14-transformer-的变体与影响)
15. [总结](#15-总结)

---

## 1. 为什么需要 Transformer？

### 1.1 RNN / LSTM 的困境

在 Transformer 出现之前，序列建模的主力是 **RNN**（循环神经网络）及其变体 **LSTM / GRU**。它们存在以下问题：

| 问题               | 说明                                       |
| ------------------ | ------------------------------------------ |
| **串行计算**       | 必须按时间步逐个处理，无法并行，训练速度慢 |
| **长距离依赖衰减** | 即使有门控机制，信息在很长的序列中仍会丢失 |
| **梯度消失/爆炸**  | 反向传播路径长，梯度不稳定                 |

### 1.2 注意力的萌芽

2015 年，Bahdanau 等人在 Seq2Seq 模型中引入了 **Attention 机制**，让解码器在每一步都能"回看"编码器的所有隐状态，缓解了长距离依赖问题。但底层仍依赖 RNN。

### 1.3 Transformer 的诞生

2017 年，Google 的论文 **"Attention Is All You Need"** 提出了 **Transformer**：

> **完全抛弃循环和卷积，仅用注意力机制构建模型。**

核心优势：

- ✅ **完全并行化**：所有位置同时计算
- ✅ **O(1) 的路径长度**：任意两个位置之间直接建立连接
- ✅ **可扩展性强**：为后来的大模型（BERT、GPT 等）奠定基础

---

## 2. 整体架构总览

Transformer 采用经典的 **Encoder-Decoder** 结构：

```
┌─────────────────────────────────────────────────────────┐
│                    Transformer                          │
│                                                         │
│   ┌──────────────┐          ┌──────────────────┐        │
│   │              │          │                  │        │
│   │   Encoder    │──────────▶    Decoder       │        │
│   │  (N=6 层)    │  K, V    │   (N=6 层)       │        │
│   │              │          │                  │        │
│   └──────▲───────┘          └────────┬─────────┘        │
│          │                           │                  │
│    Input Embedding            Output Embedding          │
│    + Positional Enc.          + Positional Enc.          │
│          │                           │                  │
│     输入序列                    输出序列(右移)            │
│  "I love you"              "<sos> 我 爱 你"             │
└─────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                              Linear + Softmax
                                       │
                                 "我 爱 你 <eos>"
```

### 关键超参数（原论文默认值）

| 符号        | 含义                 | 默认值             |
| ----------- | -------------------- | ------------------ |
| $d_{model}$ | 模型维度（嵌入维度） | 512                |
| $N$         | 编码器/解码器层数    | 6                  |
| $h$         | 注意力头数           | 8                  |
| $d_k = d_v$ | 每个头的维度         | $d_{model}/h = 64$ |
| $d_{ff}$    | 前馈网络隐层维度     | 2048               |

---

## 3. 输入表示：词嵌入与位置编码

### 3.1 词嵌入（Token Embedding）

将离散的 token（单词/子词）映射为连续向量：

$$\mathbf{x}_i = \text{Embedding}(token_i) \in \mathbb{R}^{d_{model}}$$

论文中，嵌入权重乘以 $\sqrt{d_{model}}$ 进行缩放：

$$\mathbf{x}_i = \text{Embedding}(token_i) \times \sqrt{d_{model}}$$

> **缩放的原因**：嵌入初始化时值较小，乘以 $\sqrt{d_{model}}$ 使其与位置编码在同一数量级，避免位置编码"淹没"嵌入信息。

### 3.2 位置编码（Positional Encoding）

Transformer 没有递归结构，**无法感知序列中的顺序**。为此，需要注入位置信息。

论文采用**正弦/余弦位置编码**：

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

其中：

- $pos$：token 在序列中的位置（0, 1, 2, ...）
- $i$：维度索引（0, 1, ..., $d_{model}/2 - 1$）

#### 为什么用正弦/余弦？

1. **值域有界**：始终在 $[-1, 1]$ 之间
2. **唯一性**：每个位置产生唯一的编码向量
3. **相对位置可学习**：对于固定偏移 $k$，$PE_{pos+k}$ 可以表示为 $PE_{pos}$ 的线性变换
4. **可外推**：能处理训练时未见过的序列长度

#### 可视化理解

```
位置编码矩阵 (序列长度 × d_model)：

pos=0  [sin(0/1), cos(0/1), sin(0/10000^{2/512}), cos(0/10000^{2/512}), ...]
pos=1  [sin(1/1), cos(1/1), sin(1/10000^{2/512}), cos(1/10000^{2/512}), ...]
pos=2  [sin(2/1), cos(2/1), sin(2/10000^{2/512}), cos(2/10000^{2/512}), ...]
 ...

低维度：高频振荡 → 捕捉精细位置差异
高维度：低频振荡 → 捕捉粗粒度位置关系
```

### 3.3 最终输入

$$\mathbf{X} = \text{TokenEmbedding}(\text{tokens}) \times \sqrt{d_{model}} + \text{PE}$$

$$\mathbf{X} \in \mathbb{R}^{n \times d_{model}}$$

---

## 4. 核心机制：自注意力（Self-Attention）

自注意力是 Transformer 的灵魂，让我们从最直觉的角度一步步推导。

### 4.1 直觉理解

给定一个句子："**The animal didn't cross the street because it was too tired**"

当模型处理 "**it**" 这个词时，自注意力机制让模型去关注序列中的其他位置——发现 "**it**" 指的是 "**animal**" 而不是 "**street**"。

> 自注意力 = **序列中每个位置去"查询"其他所有位置，计算相关度，然后加权汇总信息。**

### 4.2 Q、K、V 的概念

自注意力引入三个概念，类比于**信息检索**：

| 角色  | 全称          | 类比            | 作用                     |
| ----- | ------------- | --------------- | ------------------------ |
| **Q** | Query（查询） | 你的搜索关键词  | "我在找什么信息？"       |
| **K** | Key（键）     | 文档的标题/标签 | "我有什么信息可以提供？" |
| **V** | Value（值）   | 文档的内容      | "我实际的信息内容"       |

### 4.3 计算步骤

#### Step 1：线性投影生成 Q、K、V

对输入矩阵 $\mathbf{X} \in \mathbb{R}^{n \times d_{model}}$，通过三个独立的权重矩阵进行投影：

$$\mathbf{Q} = \mathbf{X} \mathbf{W}^Q, \quad \mathbf{K} = \mathbf{X} \mathbf{W}^K, \quad \mathbf{V} = \mathbf{X} \mathbf{W}^V$$

$$\mathbf{W}^Q, \mathbf{W}^K \in \mathbb{R}^{d_{model} \times d_k}, \quad \mathbf{W}^V \in \mathbb{R}^{d_{model} \times d_v}$$

#### Step 2：计算注意力分数

用点积衡量 Query 和 Key 的相似度：

$$\text{score}_{ij} = \mathbf{q}_i \cdot \mathbf{k}_j = \sum_{d=1}^{d_k} q_{id} \cdot k_{jd}$$

矩阵形式：

$$\text{Scores} = \mathbf{Q}\mathbf{K}^T \in \mathbb{R}^{n \times n}$$

#### Step 3：缩放（Scale）

$$\text{ScaledScores} = \frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}$$

> **为什么要除以 $\sqrt{d_k}$？**
>
> 当 $d_k$ 较大时，点积的方差会随 $d_k$ 线性增长。假设 $q$ 和 $k$ 的各分量独立且均值为 0、方差为 1，则 $\mathbf{q} \cdot \mathbf{k}$ 的方差为 $d_k$。
>
> 大方差会导致 Softmax 的输入值过大，使梯度极小（Softmax 饱和区），训练困难。除以 $\sqrt{d_k}$ 将方差归一化为 1。

#### Step 4：Softmax 归一化

$$\alpha_{ij} = \text{softmax}_j\left(\frac{\mathbf{q}_i \cdot \mathbf{k}_j}{\sqrt{d_k}}\right) = \frac{\exp\left(\frac{\mathbf{q}_i \cdot \mathbf{k}_j}{\sqrt{d_k}}\right)}{\sum_{l=1}^{n}\exp\left(\frac{\mathbf{q}_i \cdot \mathbf{k}_l}{\sqrt{d_k}}\right)}$$

得到的 $\alpha_{ij}$ 是位置 $i$ 对位置 $j$ 的**注意力权重**，满足：$\sum_j \alpha_{ij} = 1$

#### Step 5：加权求和

$$\mathbf{z}_i = \sum_{j=1}^{n} \alpha_{ij} \mathbf{v}_j$$

矩阵形式：

$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)\mathbf{V}$$

### 4.4 一个具体的数值例子

假设 $d_k = 4$，序列长度 = 3：

```
输入 X = [[1,0,1,0],    ← 位置0
          [0,1,0,1],    ← 位置1
          [1,1,1,0]]    ← 位置2

Q·Kᵀ = [[ 2,  0,  2],     # 位置0 与各位置的原始相似度
         [ 0,  2,  1],     # 位置1 与各位置的原始相似度
         [ 2,  1,  3]]     # 位置2 与各位置的原始相似度

÷ √4 = [[ 1.0, 0.0, 1.0],
         [ 0.0, 1.0, 0.5],
         [ 1.0, 0.5, 1.5]]

Softmax → [[0.39, 0.22, 0.39],   # 位置0 主要关注位置0和2
            [0.25, 0.43, 0.32],   # 位置1 主要关注自己
            [0.27, 0.16, 0.57]]   # 位置2 主要关注自己

× V → 加权求和得到每个位置的输出
```

### 4.5 注意力矩阵的含义

$$\text{Attention Matrix} = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right) \in \mathbb{R}^{n \times n}$$

```
         Key位置 →
         pos0  pos1  pos2  pos3
Q pos0 [ 0.1   0.7   0.1   0.1 ]  ← "I" 主要关注 "love"
u pos1 [ 0.05  0.1   0.8   0.05]  ← "love" 主要关注 "you"
e pos2 [ 0.3   0.4   0.2   0.1 ]  ← "you" 主要关注 "I" 和 "love"
r pos3 [ ...   ...   ...   ... ]
y
```

> 每一行是一个概率分布，表示该位置对所有位置的"关注程度"。

---

## 5. 多头注意力（Multi-Head Attention）

### 5.1 为什么需要多头？

单一的注意力只能捕捉**一种**关系模式。但自然语言中的关系是多样的：

- **语法关系**：主谓宾、修饰关系
- **语义关系**：指代消解、同义词
- **位置关系**：相邻词、远距离依赖

多头注意力让模型**同时从不同的表示子空间中学习不同类型的关系**。

### 5.2 计算过程

```
                    ┌──── Head 1: Attention(XW₁Q, XW₁K, XW₁V) ────┐
                    │                                                │
Input X ───────────├──── Head 2: Attention(XW₂Q, XW₂K, XW₂V) ────├──── Concat ──── W^O ──── Output
                    │                                                │
                    ├──── ...                                        │
                    │                                                │
                    └──── Head h: Attention(XWhQ, XWhK, XWhV) ────┘
```

数学表达：

$$\text{head}_i = \text{Attention}(\mathbf{X}\mathbf{W}_i^Q, \mathbf{X}\mathbf{W}_i^K, \mathbf{X}\mathbf{W}_i^V)$$

$$\text{MultiHead}(\mathbf{X}) = \text{Concat}(\text{head}_1, \text{head}_2, \ldots, \text{head}_h) \mathbf{W}^O$$

其中：

- $\mathbf{W}_i^Q, \mathbf{W}_i^K \in \mathbb{R}^{d_{model} \times d_k}$
- $\mathbf{W}_i^V \in \mathbb{R}^{d_{model} \times d_v}$
- $\mathbf{W}^O \in \mathbb{R}^{hd_v \times d_{model}}$
- $d_k = d_v = d_{model} / h = 512 / 8 = 64$

### 5.3 计算量分析

| 方式               | 参数量                                             | 计算量                      |
| ------------------ | -------------------------------------------------- | --------------------------- |
| 单头 ($d_k = 512$) | $3 \times 512 \times 512$                          | $O(n^2 \times 512)$         |
| 8头 ($d_k = 64$)   | $3 \times 8 \times 512 \times 64 + 512 \times 512$ | $O(n^2 \times 64 \times 8)$ |

> 多头注意力的总计算量与单头全维度注意力**几乎相同**，但表达能力更强。

### 5.4 不同头学到什么？

研究表明，不同的注意力头确实学到了不同模式：

```
Head 1: 可能关注相邻词（局部语法结构）
Head 2: 可能关注动词与主语的关系
Head 3: 可能关注指代词与先行词
Head 4: 可能关注标点符号和句子边界
...
```

---

## 6. 前馈神经网络（Feed-Forward Network）

### 6.1 结构

每个 Encoder/Decoder 层中，注意力之后有一个**逐位置的前馈网络**（Position-wise FFN）：

$$\text{FFN}(\mathbf{x}) = \text{ReLU}(\mathbf{x}\mathbf{W}_1 + \mathbf{b}_1)\mathbf{W}_2 + \mathbf{b}_2$$

其中：

- $\mathbf{W}_1 \in \mathbb{R}^{d_{model} \times d_{ff}}$（512 → 2048，升维）
- $\mathbf{W}_2 \in \mathbb{R}^{d_{ff} \times d_{model}}$（2048 → 512，降维）

```
输入 (512) ──→ Linear(512→2048) ──→ ReLU ──→ Linear(2048→512) ──→ 输出 (512)
                   ↑ 升维扩展                    ↑ 降维压缩
```

### 6.2 为什么需要 FFN？

- **注意力层**是线性运算（加权求和），需要非线性来增强表达力
- FFN 可以看作 **两层的 1×1 卷积**
- 起到**"思考"**的作用：注意力负责"收集信息"，FFN 负责"处理信息"
- 升维到 $4 \times d_{model}$ 提供了更大的容量来存储知识

### 6.3 "逐位置"的含义

每个位置的 token **独立**通过同一个 FFN（共享参数）：

```
位置0 的向量 ──→ FFN ──→ 输出0
位置1 的向量 ──→ FFN ──→ 输出1   ← 相同的 W₁, W₂, b₁, b₂
位置2 的向量 ──→ FFN ──→ 输出2
```

> 不同位置之间的信息交互完全由注意力层完成，FFN 只在维度层面做变换。

---

## 7. 残差连接与层归一化（Add & Norm）

### 7.1 残差连接（Residual Connection）

$$\text{output} = \mathbf{x} + \text{SubLayer}(\mathbf{x})$$

```
      ┌──────────────────────────┐
      │                          │
x ────┤                          ├───(+)──→ output
      │     SubLayer(x)         │    ↑
      │  (Attention 或 FFN)     │    │
      └──────────┬───────────────┘    │
                 │                    │
                 └────────────────────┘
                    残差 "捷径"
```

**作用**：

- 缓解深层网络的**梯度消失**
- 让梯度可以"直通"底层
- 使模型更容易学习恒等映射（"什么也不做"也是一个有效选择）

### 7.2 层归一化（Layer Normalization）

$$\text{LayerNorm}(\mathbf{x}) = \gamma \odot \frac{\mathbf{x} - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta$$

其中：

- $\mu = \frac{1}{d_{model}} \sum_{i=1}^{d_{model}} x_i$（对单个样本的特征维度求均值）
- $\sigma^2 = \frac{1}{d_{model}} \sum_{i=1}^{d_{model}} (x_i - \mu)^2$（方差）
- $\gamma, \beta \in \mathbb{R}^{d_{model}}$（可学习的缩放和偏移参数）
- $\epsilon$：防止除零的小常数

### 7.3 Layer Norm vs Batch Norm

| 特性            | Batch Norm          | Layer Norm       |
| --------------- | ------------------- | ---------------- |
| 归一化维度      | 跨 batch 的同一特征 | 单样本的所有特征 |
| 依赖 batch size | 是                  | **否**           |
| 适合变长序列    | 不适合              | **适合**         |
| 推理时行为      | 需要维护运行均值    | 无需             |

### 7.4 完整的子层公式

$$\text{output} = \text{LayerNorm}(\mathbf{x} + \text{SubLayer}(\mathbf{x}))$$

> **Post-Norm**（原论文）vs **Pre-Norm**（后续改进）：
>
> - Post-Norm：$\text{LN}(x + \text{SubLayer}(x))$ ← 原论文
> - Pre-Norm：$x + \text{SubLayer}(\text{LN}(x))$ ← 训练更稳定，GPT-2 等采用

---

## 8. 编码器（Encoder）详解

### 8.1 单层编码器结构

```
输入 x
   │
   ├─────────────────────┐
   ▼                     │ (残差)
Multi-Head Self-Attention │
   │                     │
   ▼                     │
  (+) ◀──────────────────┘
   │
   ▼
Layer Norm
   │
   ├─────────────────────┐
   ▼                     │ (残差)
Feed-Forward Network     │
   │                     │
   ▼                     │
  (+) ◀──────────────────┘
   │
   ▼
Layer Norm
   │
   ▼
输出 (传入下一层 / 最终输出)
```

### 8.2 N层堆叠

```
Input Embedding + PE
        │
   ┌────▼────┐
   │Encoder 1│
   └────┬────┘
        │
   ┌────▼────┐
   │Encoder 2│
   └────┬────┘
        │
       ...
        │
   ┌────▼────┐
   │Encoder 6│   ← 最后一层的输出作为 K, V 送给每一层 Decoder
   └────┬────┘
        │
  Encoder Output
  (n × d_model)
```

### 8.3 编码器自注意力的特点

- **双向的**：每个位置可以看到序列中**所有**其他位置
- 没有 Mask（或者只有 padding mask）
- Q、K、V 全部来自**同一个输入**

```
"I love machine learning"

位置0("I"):      可以看到 → I, love, machine, learning
位置1("love"):   可以看到 → I, love, machine, learning
位置2("machine"):可以看到 → I, love, machine, learning
位置3("learning"):可以看到 → I, love, machine, learning
```

---

## 9. 解码器（Decoder）详解

### 9.1 单层解码器结构

```
输入 y (目标序列，右移一位)
   │
   ├──────────────────────────┐
   ▼                          │ (残差)
Masked Multi-Head              │
Self-Attention ← ⚠️ 因果掩码   │
   │                          │
   ▼                          │
  (+) ◀───────────────────────┘
   │
   ▼
Layer Norm
   │
   ├──────────────────────────┐
   ▼                          │ (残差)
Multi-Head Cross-Attention     │
   Q=解码器, K=V=编码器输出     │
   │                          │
   ▼                          │
  (+) ◀───────────────────────┘
   │
   ▼
Layer Norm
   │
   ├──────────────────────────┐
   ▼                          │ (残差)
Feed-Forward Network           │
   │                          │
   ▼                          │
  (+) ◀───────────────────────┘
   │
   ▼
Layer Norm
   │
   ▼
输出
```

解码器相比编码器多了两个关键特性：**因果掩码** 和 **交叉注意力**。

### 9.2 因果掩码（Causal Mask / Look-ahead Mask）

在生成任务中，解码器不能"偷看"未来的 token。通过掩码实现：

$$\text{Mask}_{ij} = \begin{cases} 0 & \text{if } j \leq i \quad \text{(允许关注)} \\ -\infty & \text{if } j > i \quad \text{(禁止关注)} \end{cases}$$

```
掩码矩阵（下三角 = 可见，上三角 = 不可见）：

          Key 位置
          pos0  pos1  pos2  pos3
Q pos0 [  0    -∞    -∞    -∞  ]   ← "我" 只能看到 "我"
  pos1 [  0     0    -∞    -∞  ]   ← "爱" 能看到 "我"、"爱"
  pos2 [  0     0     0    -∞  ]   ← "你" 能看到 "我"、"爱"、"你"
  pos3 [  0     0     0     0  ]   ← "<eos>" 能看到全部
```

应用方式：

$$\text{Attention} = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}} + \text{Mask}\right)\mathbf{V}$$

> 加上 $-\infty$ 后，经过 Softmax 变为 0，相当于完全屏蔽。

### 9.3 交叉注意力（Cross-Attention / Encoder-Decoder Attention）

这是编码器和解码器之间的**信息桥梁**：

$$\mathbf{Q} = \text{解码器上一层的输出} \times \mathbf{W}^Q$$
$$\mathbf{K} = \text{编码器最终输出} \times \mathbf{W}^K$$
$$\mathbf{V} = \text{编码器最终输出} \times \mathbf{W}^V$$

```
解码器 Q: "在目标语言中，我当前需要什么信息？"
编码器 K: "源语言中有哪些信息可以提供？"
编码器 V: "源语言中实际的信息内容"

     编码器输出（源语言表示）
     "I"  "love"  "you"
      │     │      │
      K     K      K     ← Key: 源端的"标签"
      V     V      V     ← Value: 源端的"内容"
      ↑     ↑      ↑
      └─────┼──────┘
            │
    Q ← "我" (解码器当前位置)

    "我" 通过 Q 与所有源端 K 比较
    → 发现与 "I" 的 K 最匹配
    → 取 "I" 对应的 V 的信息
```

### 9.4 三种注意力对比

| 类型           | Q 来源     | K, V 来源      | 掩码             | 位置              |
| -------------- | ---------- | -------------- | ---------------- | ----------------- |
| 编码器自注意力 | 编码器输入 | 编码器输入     | 无（仅 padding） | Encoder           |
| 解码器自注意力 | 解码器输入 | 解码器输入     | **因果掩码**     | Decoder 第1个子层 |
| 交叉注意力     | 解码器     | **编码器输出** | 无（仅 padding） | Decoder 第2个子层 |

---

## 10. 最终输出层

### 10.1 线性层 + Softmax

解码器最后一层的输出经过一个线性层，映射到词汇表大小，然后用 Softmax 转换为概率分布：

$$P(y_t | y_{<t}, \mathbf{X}) = \text{softmax}(\mathbf{z}_t \mathbf{W}_{vocab} + \mathbf{b})$$

其中：

- $\mathbf{z}_t \in \mathbb{R}^{d_{model}}$：解码器最后一层在位置 $t$ 的输出
- $\mathbf{W}_{vocab} \in \mathbb{R}^{d_{model} \times |V|}$：$|V|$ 是词汇表大小

### 10.2 权重共享（Weight Tying）

原论文中，以下三个嵌入矩阵**共享权重**：

1. 编码器的输入嵌入层
2. 解码器的输入嵌入层
3. 最终输出线性层

> 这减少了参数量，同时建立了输入输出空间的一致性。

---

## 11. 训练细节

### 11.1 损失函数

使用标准的**交叉熵损失**：

$$\mathcal{L} = -\sum_{t=1}^{T} \log P(y_t^* | y_{<t}, \mathbf{X})$$

其中 $y_t^*$ 是真实的目标 token。

同时使用了 **Label Smoothing**（$\epsilon_{ls} = 0.1$）：

$$y_{smooth} = (1 - \epsilon) \cdot y_{one-hot} + \frac{\epsilon}{|V|}$$

> 将 100% 的确信度降到 90%，剩余 10% 均匀分配给其他词，防止过度自信，提升泛化。

### 11.2 优化器

使用 Adam 优化器，配合特殊的**学习率调度**（Warmup + Decay）：

$$lr = d_{model}^{-0.5} \cdot \min(step^{-0.5}, \; step \cdot warmup\_steps^{-1.5})$$

```
学习率
  ↑        ╱╲
  │       ╱  ╲
  │      ╱    ╲
  │     ╱      ╲────────
  │    ╱              ╲─────
  │   ╱                    ╲──────
  │──╱
  └──────────────────────────────→ step
     ↑
   warmup=4000步
   线性增长     之后按 step^(-0.5) 衰减
```

### 11.3 正则化

| 方法                | 位置                          | 参数             |
| ------------------- | ----------------------------- | ---------------- |
| **Dropout**         | 注意力权重、子层输出、嵌入+PE | $P_{drop} = 0.1$ |
| **Label Smoothing** | 损失函数                      | $\epsilon = 0.1$ |

### 11.4 Teacher Forcing

训练时，解码器的输入是**真实的目标序列**（右移一位），而不是模型自己生成的序列：

```
训练时 Decoder 输入: <sos>  我  爱  你
       Decoder 目标:  我   爱  你  <eos>
```

> 这确保训练效率，但会导致训练和推理的不一致（Exposure Bias）。

---

## 12. 完整前向传播流程

以机器翻译 "I love you" → "我爱你" 为例：

```
═══════════════════ 编码器 ═══════════════════

① 输入: ["I", "love", "you"]
   ↓ Tokenize
   Token IDs: [34, 892, 156]
   ↓ Embedding × √d_model + PE
   X ∈ ℝ^(3×512)

② Encoder Layer 1~6:
   ↓ Multi-Head Self-Attention (Q=K=V=X)
   ↓ Add & Norm
   ↓ FFN
   ↓ Add & Norm

   Encoder Output ∈ ℝ^(3×512)   ← 保存，供所有Decoder层使用

═══════════════════ 解码器（训练时）═══════════════════

③ 目标输入 (右移): ["<sos>", "我", "爱", "你"]
   ↓ Embedding × √d_model + PE
   Y ∈ ℝ^(4×512)

④ Decoder Layer 1~6:
   ↓ Masked Multi-Head Self-Attention (Q=K=V=Y, + 因果掩码)
   ↓ Add & Norm
   ↓ Multi-Head Cross-Attention (Q=Decoder, K=V=Encoder Output)
   ↓ Add & Norm
   ↓ FFN
   ↓ Add & Norm

   Decoder Output ∈ ℝ^(4×512)

═══════════════════ 输出层 ═══════════════════

⑤ Linear (512 → vocab_size) + Softmax
   ↓
   Predictions: ["我", "爱", "你", "<eos>"]

⑥ 与真实目标 ["我", "爱", "你", "<eos>"] 计算交叉熵损失
   ↓
   反向传播更新参数
```

### 推理时（自回归生成）

```
Step 0: 输入 <sos>         → 预测 "我"
Step 1: 输入 <sos> 我      → 预测 "爱"
Step 2: 输入 <sos> 我 爱   → 预测 "你"
Step 3: 输入 <sos> 我 爱 你 → 预测 "<eos>"  → 停止
```

---

## 13. PyTorch 简易实现

### 13.1 缩放点积注意力

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q, K, V: (batch, heads, seq_len, d_k)
    mask: (batch, 1, 1, seq_len) 或 (batch, 1, seq_len, seq_len)
    """
    d_k = Q.size(-1)
    # (batch, heads, seq_len, seq_len)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    attn_weights = F.softmax(scores, dim=-1)
    output = torch.matmul(attn_weights, V)
    return output, attn_weights
```

### 13.2 多头注意力

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)

        # 线性投影并拆分为多头
        # (batch, seq_len, d_model) → (batch, num_heads, seq_len, d_k)
        Q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # 缩放点积注意力
        attn_output, attn_weights = scaled_dot_product_attention(Q, K, V, mask)

        # 拼接多头
        # (batch, num_heads, seq_len, d_k) → (batch, seq_len, d_model)
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)

        # 输出投影
        output = self.W_o(attn_output)
        return output
```

### 13.3 位置编码

```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)  # 偶数维
        pe[:, 1::2] = torch.cos(position * div_term)  # 奇数维

        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)  # 不参与训练

    def forward(self, x):
        # x: (batch, seq_len, d_model)
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)
```

### 13.4 前馈网络

```python
class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.linear2(self.dropout(F.relu(self.linear1(x))))
```

### 13.5 编码器层

```python
class EncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, x, src_mask=None):
        # 自注意力 + 残差 + 归一化
        attn_output = self.self_attn(x, x, x, src_mask)
        x = self.norm1(x + self.dropout1(attn_output))

        # 前馈网络 + 残差 + 归一化
        ffn_output = self.ffn(x)
        x = self.norm2(x + self.dropout2(ffn_output))

        return x
```

### 13.6 解码器层

```python
class DecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.cross_attn = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.dropout3 = nn.Dropout(dropout)

    def forward(self, x, enc_output, src_mask=None, tgt_mask=None):
        # 1. 带因果掩码的自注意力
        attn_output = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout1(attn_output))

        # 2. 交叉注意力 (Q=Decoder, K=V=Encoder)
        cross_output = self.cross_attn(x, enc_output, enc_output, src_mask)
        x = self.norm2(x + self.dropout2(cross_output))

        # 3. 前馈网络
        ffn_output = self.ffn(x)
        x = self.norm3(x + self.dropout3(ffn_output))

        return x
```

### 13.7 完整 Transformer

```python
class Transformer(nn.Module):
    def __init__(self, src_vocab_size, tgt_vocab_size, d_model=512,
                 num_heads=8, num_layers=6, d_ff=2048, max_len=5000, dropout=0.1):
        super().__init__()

        # 嵌入层
        self.src_embedding = nn.Embedding(src_vocab_size, d_model)
        self.tgt_embedding = nn.Embedding(tgt_vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len, dropout)

        self.d_model = d_model

        # 编码器和解码器
        self.encoder_layers = nn.ModuleList(
            [EncoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)]
        )
        self.decoder_layers = nn.ModuleList(
            [DecoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)]
        )

        # 输出层
        self.output_linear = nn.Linear(d_model, tgt_vocab_size)

    def encode(self, src, src_mask=None):
        x = self.pos_encoding(self.src_embedding(src) * math.sqrt(self.d_model))
        for layer in self.encoder_layers:
            x = layer(x, src_mask)
        return x

    def decode(self, tgt, enc_output, src_mask=None, tgt_mask=None):
        x = self.pos_encoding(self.tgt_embedding(tgt) * math.sqrt(self.d_model))
        for layer in self.decoder_layers:
            x = layer(x, enc_output, src_mask, tgt_mask)
        return x

    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        enc_output = self.encode(src, src_mask)
        dec_output = self.decode(tgt, enc_output, src_mask, tgt_mask)
        output = self.output_linear(dec_output)  # (batch, tgt_len, tgt_vocab_size)
        return output

# 生成因果掩码
def generate_causal_mask(size):
    """生成上三角为 False（被遮蔽）的因果掩码"""
    mask = torch.tril(torch.ones(size, size)).bool()
    return mask.unsqueeze(0).unsqueeze(0)  # (1, 1, size, size)
```

### 13.8 参数量计算

```python
model = Transformer(src_vocab_size=32000, tgt_vocab_size=32000)
total_params = sum(p.numel() for p in model.parameters())
print(f"总参数量: {total_params:,}")
# 约 65M 参数（Base 模型）
```

参数量详细分解：

| 组件              | 计算                      | 参数量   |
| ----------------- | ------------------------- | -------- |
| 源嵌入层          | 32000 × 512               | 16.4M    |
| 目标嵌入层        | 32000 × 512               | 16.4M    |
| 单层 Encoder MHA  | 4 × 512 × 512             | 1.05M    |
| 单层 Encoder FFN  | 512×2048 + 2048×512       | 2.1M     |
| 单层 Encoder LN×2 | 2 × 2 × 512               | 2K       |
| 6层 Encoder 合计  | 6 × (1.05M + 2.1M + 2K)   | ~19M     |
| 6层 Decoder 合计  | 6 × (1.05M×2 + 2.1M + 3K) | ~25.5M   |
| 输出线性层        | 512 × 32000               | 16.4M    |
| **总计**          |                           | **~65M** |

---

## 14. Transformer 的变体与影响

### 14.1 主要后续模型

```
                        Transformer (2017)
                       ╱          │          ╲
                      ╱           │           ╲
            仅 Encoder      Encoder-Decoder      仅 Decoder
                │                 │                  │
             BERT (2018)       T5 (2019)         GPT (2018)
             RoBERTa           BART              GPT-2 (2019)
             ALBERT            mBART             GPT-3 (2020)
             DeBERTa           MarianMT          GPT-4 (2023)
             ELECTRA                             LLaMA
                │                                Mistral
                │                                Claude
           理解类任务                            生成类任务
         (分类/NER/QA)                      (对话/写作/推理)
```

### 14.2 架构改进

| 改进方向       | 方法                     | 说明                                |
| -------------- | ------------------------ | ----------------------------------- |
| **位置编码**   | RoPE（旋转位置编码）     | 更好的外推能力，LLaMA 等采用        |
|                | ALiBi                    | 直接在注意力分数加位置偏置          |
| **归一化**     | Pre-Norm（前置LN）       | 训练更稳定                          |
|                | RMSNorm                  | 去掉均值中心化，计算更快            |
| **激活函数**   | GELU, SwiGLU             | 替代 ReLU，效果更好                 |
| **注意力效率** | Flash Attention          | IO 感知的精确注意力加速             |
|                | MQA / GQA                | 多查询/分组查询注意力，减少 KV 缓存 |
|                | 稀疏注意力               | 线性复杂度的近似注意力              |
| **架构变化**   | Mixture of Experts (MoE) | 稀疏激活，扩大容量                  |

### 14.3 复杂度分析

| 层类型         | 时间复杂度       | 序列长度瓶颈            |
| -------------- | ---------------- | ----------------------- |
| Self-Attention | $O(n^2 \cdot d)$ | 长序列时 $n^2$ 成为瓶颈 |
| FFN            | $O(n \cdot d^2)$ | 与序列长度线性          |
| RNN            | $O(n \cdot d^2)$ | 串行，无法并行          |

> 这也是为什么后续出现了大量**高效注意力**研究（Linformer、Performer、Flash Attention 等）。

---

## 15. 总结

### 核心组件回顾

```
┌────────────────────────────────────────────────────────┐
│                     TRANSFORMER                        │
│                                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  1. Input Embedding × √d_model + Positional Enc │   │
│  │     → 将离散 token 转为连续向量 + 位置信息       │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │  2. Multi-Head Self-Attention                    │   │
│  │     → Q·Kᵀ/√d_k → Softmax → ×V               │   │
│  │     → 多头并行，捕捉不同类型的依赖关系           │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │  3. Add & Layer Norm                             │   │
│  │     → 残差连接 + 层归一化，稳定训练              │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │  4. Position-wise Feed-Forward Network           │   │
│  │     → 512→2048→512，引入非线性变换              │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │  5. Add & Layer Norm (again)                     │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                             │
│            重复 N 次（堆叠 N 层）                      │
│                                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  6. Output Linear + Softmax                      │   │
│  │     → 映射到词汇表，生成概率分布                 │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

### 一句话总结

> **Transformer = 自注意力（建立全局依赖） + 前馈网络（非线性变换） + 残差归一化（稳定训练） × N层堆叠**

### 学习路线建议

```
基础理解
  ├── 1. 理解注意力机制的直觉（信息检索类比）
  ├── 2. 手算一遍 Scaled Dot-Product Attention
  └── 3. 理解多头的意义

深入掌握
  ├── 4. 用 PyTorch 从零实现完整 Transformer
  ├── 5. 理解训练细节（Warmup、Label Smoothing）
  └── 6. 对比 Encoder-only / Decoder-only / Encoder-Decoder

前沿跟进
  ├── 7. 阅读 BERT / GPT 系列论文
  ├── 8. 学习 Flash Attention、RoPE 等优化
  └── 9. 实践大模型微调（LoRA、QLoRA 等）
```

---

## 参考文献

1. Vaswani, A. et al. (2017). **"Attention Is All You Need"**. NeurIPS. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
2. Bahdanau, D. et al. (2015). **"Neural Machine Translation by Jointly Learning to Align and Translate"**. ICLR.
3. Devlin, J. et al. (2018). **"BERT: Pre-training of Deep Bidirectional Transformers"**. NAACL.
4. Radford, A. et al. (2018/2019). **"Improving Language Understanding by Generative Pre-Training (GPT/GPT-2)"**.
5. Su, J. et al. (2021). **"RoFormer: Enhanced Transformer with Rotary Position Embedding"**.
6. Dao, T. et al. (2022). **"FlashAttention: Fast and Memory-Efficient Exact Attention"**.

---

> _本文档旨在提供 Transformer 架构的完整解析。如需进一步深入某个具体模块或变体，欢迎继续探讨。_
