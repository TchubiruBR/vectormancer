import click
from vectormancer import Vectormancer

@click.group()
def main():
    """Vectormancer CLI"""

@main.command()
@click.argument("path", type=str)
@click.option("--config", type=str, default=None, help="Path to config.yaml")
@click.option("--rebuild", is_flag=True, help="Rebuild the index from scratch")
def index(path, config, rebuild):
    vm = Vectormancer(config_path=config)
    vm.index(path)
    click.echo(f"Indexed: {path}")

@main.command()
@click.argument("question", type=str)
@click.option("--top-k", type=int, default=5)
@click.option("--show-sources", is_flag=True, default=True)
@click.option("--config", type=str, default=None, help="Path to config.yaml")
@click.option("--verbose", is_flag=True, help="Print debug info when no results")
def query(question, top_k, show_sources, config, verbose):
    vm = Vectormancer(config_path=config)
    hits = vm.query(question, top_k=top_k, show_sources=show_sources)

    if not hits:
        click.echo("No results found.\n"
                   "Tips: ensure you’ve indexed in **this** session "
                   "(current MVP store is in-memory), or re-run:\n"
                   "  vectormancer index <PATH>\n")
        if verbose:
            click.echo(f"[debug] question='{question}', top_k={top_k}, config={config}")
        return

    for i, h in enumerate(hits, 1):
        path = h.get("path", "")
        text = h.get("text", "")[:400].replace("\n", " ")
        click.echo(f"[{i}] ({h['score']:.3f}) {path}\n{text}\n")
