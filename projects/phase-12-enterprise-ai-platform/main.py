#!/usr/bin/env python3
"""
企业级 AI 平台 - 命令行界面
============================

交互式命令行工具，提供平台的所有核心功能。
"""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from services.chat import get_chat_service
from services.knowledge_base import get_kb_manager
from services.agent import get_agent
from modules.qa import QAModule
from modules.document import DocumentProcessor
from modules.content import ContentCreator, ContentType, ContentStyle
from modules.analytics import DataAnalyzer


console = Console()


def print_header():
    """打印头部"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]🏢 企业级 AI 平台[/bold blue]\n"
        "[dim]综合性 AI 服务平台 - Phase 12 实战项目[/dim]",
        border_style="blue",
    ))
    console.print(f"[dim]当前模型: {config.get_model_info()}[/dim]\n")


def print_menu():
    """打印主菜单"""
    table = Table(title="功能菜单", show_header=False, border_style="blue")
    table.add_column("选项", style="cyan")
    table.add_column("功能")

    table.add_row("[1]", "💬 智能对话")
    table.add_row("[2]", "📚 知识库管理")
    table.add_row("[3]", "🔍 知识问答")
    table.add_row("[4]", "📄 文档处理")
    table.add_row("[5]", "✏️  内容创作")
    table.add_row("[6]", "🤖 Agent 任务")
    table.add_row("[7]", "🌐 启动 API 服务")
    table.add_row("[0]", "退出")

    console.print(table)


# ==================== 功能模块 ====================


def chat_mode():
    """智能对话模式"""
    console.print("\n[bold cyan]💬 智能对话模式[/bold cyan]")
    console.print("[dim]输入 'quit' 或 'q' 退出对话[/dim]\n")

    service = get_chat_service()
    session = service.create_session()

    while True:
        try:
            user_input = Prompt.ask("[bold green]你[/bold green]")

            if user_input.lower() in ["quit", "q", "exit"]:
                console.print("[dim]退出对话[/dim]")
                break

            if not user_input.strip():
                continue

            console.print("[bold blue]AI[/bold blue]: ", end="")

            # 流式输出
            for chunk in service.stream(user_input, session_id=session.id):
                console.print(chunk, end="")

            console.print("\n")

        except KeyboardInterrupt:
            console.print("\n[dim]对话中断[/dim]")
            break


def knowledge_base_mode():
    """知识库管理模式"""
    console.print("\n[bold cyan]📚 知识库管理[/bold cyan]\n")

    manager = get_kb_manager()

    while True:
        # 显示知识库列表
        kbs = manager.list_knowledge_bases()

        if kbs:
            table = Table(title="知识库列表")
            table.add_column("序号", style="cyan")
            table.add_column("名称")
            table.add_column("ID", style="dim")
            table.add_column("文档数")
            table.add_column("片段数")

            for i, kb in enumerate(kbs, 1):
                table.add_row(
                    str(i),
                    kb.name,
                    kb.id,
                    str(kb.document_count),
                    str(kb.chunk_count),
                )

            console.print(table)
        else:
            console.print("[yellow]暂无知识库[/yellow]")

        console.print("\n[dim]操作: [c]创建 [d]删除 [a]添加文档 [q]返回[/dim]")
        action = Prompt.ask("请选择", choices=["c", "d", "a", "q"], default="q")

        if action == "q":
            break
        elif action == "c":
            name = Prompt.ask("知识库名称")
            desc = Prompt.ask("描述（可选）", default="")
            kb = manager.create_knowledge_base(name, desc)
            console.print(f"[green]✓ 已创建知识库: {kb.name} ({kb.id})[/green]")

        elif action == "d" and kbs:
            idx = Prompt.ask("输入要删除的序号")
            try:
                kb = kbs[int(idx) - 1]
                if Confirm.ask(f"确认删除 '{kb.name}'?"):
                    manager.delete_knowledge_base(kb.id)
                    console.print(f"[green]✓ 已删除[/green]")
            except (ValueError, IndexError):
                console.print("[red]无效的序号[/red]")

        elif action == "a" and kbs:
            idx = Prompt.ask("选择知识库序号")
            try:
                kb = kbs[int(idx) - 1]
                file_path = Prompt.ask("文件路径")
                path = Path(file_path).expanduser()

                if path.exists():
                    chunks = manager.add_document(kb.id, path)
                    console.print(f"[green]✓ 已添加 {chunks} 个文本片段[/green]")
                else:
                    console.print("[red]文件不存在[/red]")
            except (ValueError, IndexError):
                console.print("[red]无效的输入[/red]")
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")

        console.print()


def qa_mode():
    """知识问答模式"""
    console.print("\n[bold cyan]🔍 知识问答[/bold cyan]")

    manager = get_kb_manager()
    kbs = manager.list_knowledge_bases()

    if not kbs:
        console.print("[yellow]请先创建知识库并添加文档[/yellow]")
        return

    # 选择知识库
    console.print("\n可用的知识库:")
    for i, kb in enumerate(kbs, 1):
        console.print(f"  [{i}] {kb.name}")

    idx = Prompt.ask("选择知识库", default="1")
    try:
        kb = kbs[int(idx) - 1]
    except (ValueError, IndexError):
        kb = kbs[0]

    console.print(f"\n[dim]已选择: {kb.name}[/dim]")
    console.print("[dim]输入 'q' 退出[/dim]\n")

    qa = QAModule()

    while True:
        question = Prompt.ask("[bold green]问题[/bold green]")

        if question.lower() in ["q", "quit", "exit"]:
            break

        if not question.strip():
            continue

        with console.status("思考中..."):
            result = qa.query(question, kb_id=kb.id)

        console.print(f"\n[bold blue]回答[/bold blue]: {result.answer}\n")

        if result.sources:
            console.print("[dim]来源:[/dim]")
            for s in result.sources:
                console.print(f"  - {s['filename']}")

        console.print()


def document_mode():
    """文档处理模式"""
    console.print("\n[bold cyan]📄 文档处理[/bold cyan]\n")

    console.print("[1] 文档摘要")
    console.print("[2] 信息提取")
    console.print("[0] 返回")

    choice = Prompt.ask("选择功能", choices=["1", "2", "0"], default="0")

    if choice == "0":
        return

    processor = DocumentProcessor()

    if choice == "1":
        file_path = Prompt.ask("文件路径")
        path = Path(file_path).expanduser()

        if not path.exists():
            console.print("[red]文件不存在[/red]")
            return

        with console.status("正在分析..."):
            doc = processor.load_document(path)
            summary = processor.summarize(doc.content)

        console.print(f"\n[bold]标题[/bold]: {summary.title}")
        console.print(f"\n[bold]摘要[/bold]: {summary.summary}")

        if summary.key_points:
            console.print("\n[bold]关键要点[/bold]:")
            for point in summary.key_points:
                console.print(f"  • {point}")

        if summary.keywords:
            console.print(f"\n[bold]关键词[/bold]: {', '.join(summary.keywords)}")

    elif choice == "2":
        text = Prompt.ask("输入文本（或文件路径）")

        # 检查是否是文件
        path = Path(text).expanduser()
        if path.exists():
            with open(path) as f:
                text = f.read()

        with console.status("正在提取..."):
            result = processor.extract_info(text)

        console.print("\n[bold]提取的实体[/bold]:")
        for entity_type, entities in result.entities.items():
            if entities:
                console.print(f"  {entity_type}: {', '.join(entities)}")

        if result.facts:
            console.print("\n[bold]关键事实[/bold]:")
            for fact in result.facts:
                console.print(f"  • {fact}")


def content_mode():
    """内容创作模式"""
    console.print("\n[bold cyan]✏️  内容创作[/bold cyan]\n")

    topic = Prompt.ask("创作主题")

    console.print("\n风格选项:")
    console.print("  [1] 轻松 (casual)")
    console.print("  [2] 正式 (formal)")
    console.print("  [3] 技术 (technical)")
    console.print("  [4] 营销 (marketing)")

    style_choice = Prompt.ask("选择风格", choices=["1", "2", "3", "4"], default="1")
    style_map = {
        "1": ContentStyle.CASUAL,
        "2": ContentStyle.FORMAL,
        "3": ContentStyle.TECHNICAL,
        "4": ContentStyle.MARKETING,
    }
    style = style_map[style_choice]

    console.print("\n长度选项:")
    console.print("  [1] 短 (300-500字)")
    console.print("  [2] 中 (800-1200字)")
    console.print("  [3] 长 (1500-2500字)")

    length_choice = Prompt.ask("选择长度", choices=["1", "2", "3"], default="2")
    length_map = {"1": "short", "2": "medium", "3": "long"}
    length = length_map[length_choice]

    creator = ContentCreator()

    with console.status("创作中..."):
        result = creator.generate(
            topic=topic,
            content_type=ContentType.ARTICLE,
            style=style,
            length=length,
        )

    console.print("\n" + "=" * 50)
    console.print(Markdown(f"# {result.title}\n\n{result.content}"))
    console.print("=" * 50)
    console.print(f"\n[dim]字数: {result.word_count}[/dim]")


def agent_mode():
    """Agent 任务模式"""
    console.print("\n[bold cyan]🤖 Agent 任务[/bold cyan]")
    console.print("[dim]输入任务描述，Agent 将自动完成[/dim]")
    console.print("[dim]输入 'q' 退出[/dim]\n")

    agent = get_agent()

    while True:
        task = Prompt.ask("[bold green]任务[/bold green]")

        if task.lower() in ["q", "quit", "exit"]:
            break

        if not task.strip():
            continue

        console.print("\n[bold]Agent 执行中...[/bold]\n")

        result = agent.run(task)

        if result.success:
            console.print(f"[bold blue]结果[/bold blue]: {result.output}\n")

            if result.steps:
                console.print("[dim]执行步骤:[/dim]")
                for i, step in enumerate(result.steps, 1):
                    console.print(f"  {i}. {step.action}({step.action_input[:50]}...)")
        else:
            console.print(f"[red]执行失败: {result.error}[/red]")

        console.print()


def start_api_server():
    """启动 API 服务"""
    console.print("\n[bold cyan]🌐 启动 API 服务[/bold cyan]\n")
    console.print(f"地址: http://{config.api_host}:{config.api_port}")
    console.print(f"文档: http://{config.api_host}:{config.api_port}/docs")
    console.print("\n[dim]按 Ctrl+C 停止服务[/dim]\n")

    from app import main as start_app
    start_app()


# ==================== 主程序 ====================


def main():
    """主程序入口"""
    # 验证配置
    if not config.validate():
        console.print("[red]请配置必要的环境变量后重试[/red]")
        return

    print_header()

    while True:
        print_menu()

        try:
            choice = Prompt.ask("\n请选择功能", choices=["0", "1", "2", "3", "4", "5", "6", "7"], default="0")

            if choice == "0":
                console.print("\n[dim]再见！👋[/dim]\n")
                break
            elif choice == "1":
                chat_mode()
            elif choice == "2":
                knowledge_base_mode()
            elif choice == "3":
                qa_mode()
            elif choice == "4":
                document_mode()
            elif choice == "5":
                content_mode()
            elif choice == "6":
                agent_mode()
            elif choice == "7":
                start_api_server()

        except KeyboardInterrupt:
            console.print("\n")
            continue
        except Exception as e:
            console.print(f"\n[red]错误: {e}[/red]\n")


if __name__ == "__main__":
    main()
