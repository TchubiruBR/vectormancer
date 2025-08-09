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
def query(question, top_k, show_sources, config):
    vm = Vectormancer(config_path=config)
    hits = vm.query(question, top_k=top_k, show_sources=show_sources)
    for i, h in enumerate(hits, 1):
        click.echo(f"[{i}] ({h['score']:.3f}) {h.get('path','')}\n{h['text'][:200]}\n")