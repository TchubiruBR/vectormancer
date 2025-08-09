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
@click.option("--window", type=int, default=1200, help="Context window size for RAG snippets")
@click.option("--show-sources", is_flag=True, default=True)
@click.option("--config", type=str, default=None, help="Path to config.yaml")
@click.option("--persist-dir", type=str, default=None, help="Directory to store/load the index")
@click.option("--verbose", is_flag=True, help="Print debug info when no results")
def query(question, top_k, window, show_sources, config, persist_dir, verbose):
    vm = Vectormancer(config_path=config, persist_dir=persist_dir)
    hits = vm.query(question, top_k=top_k, show_sources=show_sources, window=window)
    if not hits:
        click.echo("No results found.\n"
                   "Tips: run `vectormancer index <PATH>` first.\n"
                   "Use --persist-dir to control index location.\n")
        if verbose:
            click.echo(f"[debug] question={question!r}, top_k={top_k}, persist_dir={persist_dir or '~/.vectormancer/index'}")
        return
    for i, h in enumerate(hits, 1):
        path = h.get("path", "")
        score = h.get("score", 0.0)
        context = h.get("context", h.get("text",""))[:400].replace("\n", " ")
        cit = h.get("citation", {})
        click.echo(f"[{i}] ({score:.3f}) {path}  "
                   f"[citation offset={cit.get('offset','?')} len={cit.get('length','?')}]")
        click.echo(context + "\n")
