import typer
from . import chat

app = typer.Typer()
app.command("chat")(chat.chat)
