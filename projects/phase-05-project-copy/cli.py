"""
为企业文书智能内网索引系统定制的终端交互演示面板 (CLI) V2
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from rich.markdown import Markdown

from config import config
from engine.pipeline import SearchPipeline

console = Console()


def format_latency_stats(stats: dict) -> Table:
    table = Table(
        title="系统整体搜索检索性能与延时 (Pipeline Metrics)",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("工作阶段阶段", style="cyan")
    table.add_column("耗时 (毫秒 ms)", justify="right")
    table.add_column("执行细节说明", style="dim")

    table.add_row(
        "查询引擎意图路由",
        f"{stats.get('routing_time_ms', 0):.1f}",
        "利用大模型实施 HyDE 幻觉假设并拆解用户的词汇短语",
    )
    table.add_row(
        "双频并行检索出击",
        f"{stats.get('retrieval_time_ms', 0):.1f}",
        f"BM25 词法定准: 命中 {stats.get('raw_bm25_hits', 0)} 条记录, Dense 模糊大意: 命中 {stats.get('raw_dense_hits', 0)} 条记录",
    )
    table.add_row(
        "RRF 算法强行交会对切",
        f"{stats.get('fusion_time_ms', 0):.1f}",
        f"去重除杂后统合得到的总候选文库数量: {stats.get('unique_fused_candidates', 0)}",
    )
    table.add_row(
        "交叉评级 (Cross-Encoder) 严苛把关",
        f"{stats.get('rerank_time_ms', 0):.1f}",
        f"使用本地开源 BGE 模型完成超快全维度对比推理",
    )
    table.add_row(
        "端到端全搜索流光阴流逝",
        f"[bold green]{stats.get('total_latency_ms', 0):.1f}[/bold green]",
        "完整检索闭环总耗时",
    )
    return table


def display_results(results: list, query: str):
    if not results:
        console.print(
            "\n[yellow]抱歉。并没有打捞出能够解答您的任何相关档案卷宗碎片。[/yellow]\n"
        )
        return

    console.print("\n[bold green]极智搜索最终精选呈现:[/bold green]")
    for res in results:
        doc = res["document"]
        score = res.get("cross_encoder_score", 0.0)
        rank = res.get("final_rank", "?")
        source = doc.metadata.get("source", "未知出处文档")

        # 首推能包裹着全文语境段的 Parent Context 否则回退屈就用匹配用的原味 child chunk
        content = res.get("parent_context", doc.page_content)
        # 为防止刷屏过度显示终端面板将予以智能裁剪
        if len(content) > 300:
            content = content[:300] + "..."

        panel = Panel(
            content,
            title=f"[bold]🏆 排序第 {rank} 位 | 📚 卷宗档案: {os.path.basename(source)}[/bold] (核心相似交叉比对分值: {score:.2f})",
            border_style="blue",
        )
        console.print(panel)


def main():
    console.print(
        Panel.fit(
            "[bold blue]企业级知识大脑搜索引擎系统 V2[/bold blue]\n[dim]正在加电唤醒各种数据链路与装载本地轻巧但强劲的硅片推理模型集...[/dim]"
        )
    )

    pipeline = SearchPipeline()
    pipeline.initialize_index(config.docs_dir)

    console.print(
        "[bold green]系统全面就绪！随时可以发问！[/bold green] (输入 'exit' 或 'quit' 命令优雅退出并掐断能源。)"
    )

    while True:
        try:
            query = console.input("\n[bold cyan]搜索大脑 > [/bold cyan]").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                break

            console.print("[dim]底层引擎光速推演比对中 ...[/dim]")
            response = pipeline.search(query)

            # 显示精美结果报表呈现给人类长官
            console.print(format_latency_stats(response["stats"]))
            display_results(response["results"], query)

        except KeyboardInterrupt:
            console.print("\n[dim]手动打断进程，挥别系统下线。[/dim]")
            break
        except Exception as e:
            console.print(
                f"[bold red]严重警报！搜索运转途中系统核心崩溃报错:[/bold red] {e}"
            )


if __name__ == "__main__":
    main()
