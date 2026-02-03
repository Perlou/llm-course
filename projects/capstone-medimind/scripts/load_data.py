#!/usr/bin/env python3
"""
MediMind - 数据加载脚本

加载医学文档、药品数据、检验指标数据到向量库和数据库。
"""

import json
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core import (
    DocumentParser,
    Chunker,
    get_embedder,
    get_vector_store,
)
from src.utils import log, setup_logger


def load_medical_docs(docs_dir: str = "data/medical_docs"):
    """
    加载医学文档到向量库
    
    Args:
        docs_dir: 文档目录路径
    """
    log.info("=" * 50)
    log.info("开始加载医学文档...")
    
    parser = DocumentParser()
    chunker = Chunker()
    embedder = get_embedder()
    vector_store = get_vector_store()
    
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        log.warning(f"文档目录不存在: {docs_dir}")
        return
    
    # 解析所有文档
    documents = parser.parse_directory(str(docs_path))
    
    if not documents:
        log.warning("没有找到可解析的文档")
        return
    
    # 分块和嵌入
    all_chunks = []
    for doc in documents:
        chunks = chunker.chunk_document(
            doc_id=doc.id,
            doc_title=doc.title,
            content=doc.content,
            source=doc.source,
            metadata=doc.metadata,
        )
        all_chunks.extend(chunks)
    
    log.info(f"共生成 {len(all_chunks)} 个文本块")
    
    # 生成嵌入向量
    log.info("生成嵌入向量...")
    texts = [chunk.content for chunk in all_chunks]
    embeddings = embedder.embed_documents(texts)
    
    # 存储到向量库
    log.info("存储到向量库...")
    vector_store.add(
        ids=[chunk.id for chunk in all_chunks],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[
            {
                "doc_id": chunk.doc_id,
                "doc_title": chunk.doc_title,
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in all_chunks
        ],
    )
    
    log.info(f"✅ 医学文档加载完成，共 {vector_store.count()} 个文档块")


def load_drug_data(drug_file: str = "data/drug_db/drugs.json"):
    """
    加载药品数据
    
    Args:
        drug_file: 药品数据文件路径
    """
    log.info("=" * 50)
    log.info("开始加载药品数据...")
    
    drug_path = Path(drug_file)
    if not drug_path.exists():
        log.warning(f"药品数据文件不存在: {drug_file}")
        return
    
    with open(drug_path, "r", encoding="utf-8") as f:
        drugs = json.load(f)
    
    log.info(f"加载了 {len(drugs)} 条药品数据")
    
    # 也可以将药品信息存入向量库以支持语义搜索
    embedder = get_embedder()
    vector_store = get_vector_store()
    
    # 为每个药品生成描述文本
    texts = []
    ids = []
    metadatas = []
    
    for drug in drugs:
        # 组合药品描述
        desc = f"""药品名称：{drug['name']}
通用名：{drug.get('generic_name', '')}
分类：{drug.get('category', '')}
适应症：{drug.get('indications', '')}
用法用量：{drug.get('dosage', '')}
不良反应：{drug.get('side_effects', '')}
禁忌：{drug.get('contraindications', '')}
注意事项：{drug.get('precautions', '')}"""
        
        texts.append(desc)
        ids.append(f"drug_{drug['id']}")
        metadatas.append({
            "type": "drug",
            "drug_id": drug['id'],
            "name": drug['name'],
            "is_otc": drug.get('is_otc', False),
        })
    
    # 生成嵌入并存储
    embeddings = embedder.embed_documents(texts)
    vector_store.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )
    
    log.info(f"✅ 药品数据加载完成")


def load_lab_indices(indices_file: str = "data/lab_indices/indices.json"):
    """
    加载检验指标数据
    
    Args:
        indices_file: 检验指标文件路径
    """
    log.info("=" * 50)
    log.info("开始加载检验指标数据...")
    
    indices_path = Path(indices_file)
    if not indices_path.exists():
        log.warning(f"检验指标文件不存在: {indices_file}")
        return
    
    with open(indices_path, "r", encoding="utf-8") as f:
        indices = json.load(f)
    
    log.info(f"加载了 {len(indices)} 条检验指标数据")
    
    embedder = get_embedder()
    vector_store = get_vector_store()
    
    texts = []
    ids = []
    metadatas = []
    
    for index in indices:
        # 组合指标描述
        normal_range = index.get('normal_range', {})
        range_str = ", ".join([f"{k}: {v}" for k, v in normal_range.items()])
        
        desc = f"""检验指标：{index['name']}（{index.get('abbreviation', '')}）
类别：{index.get('category', '')}
单位：{index.get('unit', '')}
正常范围：{range_str}
说明：{index.get('description', '')}
升高含义：{index.get('high_meaning', '')}
降低含义：{index.get('low_meaning', '')}"""
        
        texts.append(desc)
        ids.append(f"lab_{index['id']}")
        metadatas.append({
            "type": "lab_index",
            "index_id": index['id'],
            "name": index['name'],
            "category": index.get('category', ''),
        })
    
    embeddings = embedder.embed_documents(texts)
    vector_store.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )
    
    log.info(f"✅ 检验指标数据加载完成")


def main():
    """主函数"""
    setup_logger(level="INFO")
    
    log.info("=" * 50)
    log.info("MediMind 数据加载脚本")
    log.info("=" * 50)
    
    try:
        # 加载各类数据
        load_medical_docs()
        load_drug_data()
        load_lab_indices()
        
        # 最终统计
        vector_store = get_vector_store()
        log.info("=" * 50)
        log.info(f"🎉 数据加载完成！")
        log.info(f"📊 向量库总文档数: {vector_store.count()}")
        log.info("=" * 50)
        
    except Exception as e:
        log.error(f"数据加载失败: {e}")
        raise


if __name__ == "__main__":
    main()
