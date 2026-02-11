# utils/cli.py

from rich.console import Console
from rich.panel import Panel

console = Console()


def print_header():
    console.print(
        Panel(
            "[bold cyan]Coffee Shop ETL Pipeline[/bold cyan]\n[dim]Production Execution Mode[/dim]",
            expand=False
        )
    )


def print_step(message):
    console.print(f"\n→ [bold yellow]{message}[/bold yellow]")


def print_success(message):
    console.print(f"[green]✔ {message}[/green]")


def print_failure(message):
    console.print(
        Panel(
            f"[bold red]Pipeline Failed[/bold red]\n{message}",
            expand=False
        )
    )
