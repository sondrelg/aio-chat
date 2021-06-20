import subprocess

from rich.panel import Panel
from rich.table import Table


def render_messages(messages: list[str]) -> Panel:
    clear_console()

    items_table = Table.grid(padding=(0, 1))
    items_table.width = 100

    for message in messages or ['Welcome! Type something to get started :pile_of_poo:']:
        items_table.add_row(message)

    return Panel.fit(
        items_table,
        title='messages',
        border_style="scope.border",
        padding=(0, 1),
    )


def clear_console():
    command = 'clear'
    subprocess.run(command)
