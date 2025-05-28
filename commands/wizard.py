import typer
from commands import fullwizard  # This prevents auto-execution

def wizard():
    while True:
        typer.echo("\nVaultPlan Launcher")
        typer.echo("1. Menu")
        typer.echo("0. Exit")
        choice = typer.prompt("Select", type=int)
        if choice == 1:
            fullwizard.wizard()  # Only calls full menu when chosen
        elif choice == 0:
            typer.echo("Goodbye.")
            break
        else:
            typer.echo("Invalid selection.")
