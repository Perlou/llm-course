"""
文档加载器
==========

学习目标：
    1. 理解文档加载器的作用
    2. 掌握常见文档格式的加载方法
    3. 学会处理不同类型的数据源

核心概念：
    - Document：LangChain 的文档对象
    - DocumentLoader：文档加载器基类
    - 元数据：文档的附加信息

前置知识：
    - Phase 3 LangChain 基础

环境要求：
    - pip install langchain langchain-community python-dotenv
    - pip install pypdf docx2txt unstructured
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Document 对象 ====================


def document_basics():
    """Document 对象基础"""
    print("=" * 60)
    print("第一部分：Document 对象")
    print("=" * 60)

    from langchain_core.documents import Document

    print("""
    Document 是 LangChain 中的核心数据结构：
    
    ┌─────────────────────────────────────────────┐
    │               Document                       │
    ├─────────────────────────────────────────────┤
    │  page_content: str    # 文档内容             │
    │  metadata: dict       # 元数据（来源、页码等）│
    └─────────────────────────────────────────────┘
    """)

    # 创建 Document
    doc = Document(
        page_content="这是一段示例文本内容。",
        metadata={"source": "example.txt", "page": 1},
    )

    print("📌 创建 Document：")
    print(f"  内容: {doc.page_content}")
    print(f"  元数据: {doc.metadata}")


# ==================== 第二部分：文本文件加载 ====================


def text_loader_demo():
    """文本文件加载"""
    print("\n" + "=" * 60)
    print("第二部分：文本文件加载")
    print("=" * 60)

    from langchain_community.document_loaders import TextLoader

    # 创建示例文件
    sample_file = "/tmp/sample.txt"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write("这是第一行内容。\n")
        f.write("这是第二行内容。\n")
        f.write("这是第三行内容。")

    # 加载文件
    loader = TextLoader(sample_file, encoding="utf-8")
    docs = loader.load()

    print(f"📌 加载结果：")
    print(f"  文档数量: {len(docs)}")
    print(f"  内容: {docs[0].page_content[:50]}...")
    print(f"  元数据: {docs[0].metadata}")

    # 清理
    os.remove(sample_file)


# ==================== 第三部分：目录批量加载 ====================


def directory_loader_demo():
    """目录批量加载"""
    print("\n" + "=" * 60)
    print("第三部分：目录批量加载")
    print("=" * 60)

    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    import tempfile

    # 创建临时目录和文件
    temp_dir = tempfile.mkdtemp()
    for i in range(3):
        with open(f"{temp_dir}/file{i}.txt", "w") as f:
            f.write(f"这是文件 {i} 的内容。")

    # 加载目录
    loader = DirectoryLoader(temp_dir, glob="*.txt", loader_cls=TextLoader)
    docs = loader.load()

    print(f"📌 批量加载结果：")
    print(f"  加载文件数: {len(docs)}")
    for doc in docs:
        print(f"  - {doc.metadata.get('source', 'unknown')}")

    # 清理
    import shutil

    shutil.rmtree(temp_dir)


# ==================== 第四部分：PDF 加载 ====================


def pdf_loader_demo():
    """PDF 加载演示"""
    print("\n" + "=" * 60)
    print("第四部分：PDF 加载")
    print("=" * 60)

    print("""
    常用 PDF 加载器：
    
    1. PyPDFLoader - 基础 PDF 加载
       pip install pypdf
       
    2. PyMuPDFLoader - 更快速的加载
       pip install pymupdf
       
    3. PDFPlumberLoader - 保留布局信息
       pip install pdfplumber
    """)

    code_example = """
    from langchain_community.document_loaders import PyPDFLoader
    
    # 加载 PDF
    loader = PyPDFLoader("document.pdf")
    pages = loader.load()
    
    # 每页一个 Document
    for i, page in enumerate(pages):
        print(f"第 {i+1} 页: {len(page.page_content)} 字符")
    """
    print("📌 PDF 加载示例代码：")
    print(code_example)


# ==================== 第五部分：Web 内容加载 ====================


def web_loader_demo():
    """Web 内容加载"""
    print("\n" + "=" * 60)
    print("第五部分：Web 内容加载")
    print("=" * 60)

    print("""
    常用 Web 加载器：
    
    1. WebBaseLoader - 基础网页加载
    2. UnstructuredURLLoader - 结构化提取
    3. RecursiveUrlLoader - 递归爬取
    """)

    try:
        from langchain_community.document_loaders import WebBaseLoader

        loader = WebBaseLoader("https://example.com")
        docs = loader.load()

        print(f"📌 网页加载结果：")
        print(f"  文档数: {len(docs)}")
        print(f"  内容预览: {docs[0].page_content[:100]}...")

    except Exception as e:
        print(f"⚠️ 网页加载需要网络: {e}")


# ==================== 第六部分：其他加载器 ====================


def other_loaders():
    """其他常用加载器"""
    print("\n" + "=" * 60)
    print("第六部分：其他常用加载器")
    print("=" * 60)

    print("""
    文档类型               加载器                    依赖
    ─────────────────────────────────────────────────────────
    Word (.docx)          Docx2txtLoader          docx2txt
    Markdown              UnstructuredMarkdownLoader unstructured
    CSV                   CSVLoader               -
    JSON                  JSONLoader              -
    HTML                  UnstructuredHTMLLoader  unstructured
    Excel                 UnstructuredExcelLoader openpyxl
    PowerPoint            UnstructuredPPTLoader   python-pptx
    
    数据库
    ─────────────────────────────────────────────────────────
    SQLite/MySQL          SQLDatabaseLoader       sqlalchemy
    
    云存储
    ─────────────────────────────────────────────────────────
    S3                    S3FileLoader            boto3
    Google Drive          GoogleDriveLoader       google-api-python-client
    """)


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：加载本地文件
        创建几个 txt 文件，使用 DirectoryLoader 批量加载。

        ✅ 参考答案：
        ```python
        from langchain_community.document_loaders import DirectoryLoader, TextLoader
        import os
        import tempfile

        # 创建测试目录和文件
        temp_dir = tempfile.mkdtemp()
        for i in range(3):
            with open(f"{temp_dir}/note{i}.txt", "w") as f:
                f.write(f"这是笔记文件 {i} 的内容。\\n包含多行文本。")

        # 批量加载
        loader = DirectoryLoader(
            temp_dir,
            glob="*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        docs = loader.load()

        print(f"加载了 {len(docs)} 个文档")
        for doc in docs:
            print(f"- {doc.metadata['source']}: {len(doc.page_content)} 字符")
        ```

    练习 2：处理 PDF
        下载一个 PDF 文档，用 PyPDFLoader 加载并统计页数。

        ✅ 参考答案：
        ```python
        from langchain_community.document_loaders import PyPDFLoader

        # 加载 PDF
        loader = PyPDFLoader("document.pdf")
        pages = loader.load()

        print(f"总页数: {len(pages)}")
        for i, page in enumerate(pages):
            print(f"第 {i+1} 页: {len(page.page_content)} 字符")
            print(f"  元数据: {page.metadata}")
        ```

    练习 3：网页抓取
        使用 WebBaseLoader 抓取一个新闻页面的内容。

        ✅ 参考答案：
        ```python
        from langchain_community.document_loaders import WebBaseLoader

        # 单个网页
        loader = WebBaseLoader("https://example.com/news")
        docs = loader.load()

        print(f"内容长度: {len(docs[0].page_content)} 字符")
        print(f"元数据: {docs[0].metadata}")

        # 多个网页
        loader = WebBaseLoader([
            "https://example.com/page1",
            "https://example.com/page2"
        ])
        docs = loader.load()
        ```

    思考题：
        1. 加载器如何处理编码问题？
           
           ✅ 答案：
           - TextLoader 支持 encoding 参数：`TextLoader(file, encoding="utf-8")`
           - 可以使用 autodetect_encoding=True 自动检测
           - PDF 加载器通常内置编码处理
           - 网页加载器从 HTTP 头或 meta 标签获取编码

        2. 大文件加载时的内存问题如何解决？
           
           ✅ 答案：
           - 使用 lazy_load() 延迟加载
           - 分块处理：结合 TextSplitter 边加载边分块
           - 流式处理：使用生成器模式
           - 对于 PDF：使用 load_and_split() 直接分块
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 文档加载器")
    print("=" * 60)

    try:
        document_basics()
        text_loader_demo()
        directory_loader_demo()
        pdf_loader_demo()
        web_loader_demo()
        other_loaders()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：02-text-splitters.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
