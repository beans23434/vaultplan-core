
import typer
import subprocess

def run_command(cmd):
    print(f"\n[Running] {cmd}")
    subprocess.run(f'python3 ~/vaultplan/vaultplan.py {cmd.replace("vaultplan ", "")}', shell=True)

def wizard():
    typer.echo("\nVaultPlan Wizard Main Menu")
    typer.echo("1. View Balance")
    typer.echo("2. Account")
    typer.echo("3. Income")
    typer.echo("4. Expense")
    typer.echo("5. Goal")
    typer.echo("6. Debits")
    typer.echo("7. Note")
    typer.echo("8. Web3")
    typer.echo("9. Summary")
    typer.echo("10. Export")
    typer.echo("0. Back")
    choice = typer.prompt("Select", type=int)

    if choice == 1:
        run_command("vaultplan balance")
    elif choice == 2:
        def account_menu():
            while True:
                typer.echo("\n=== Account Menu ===")
                typer.echo("1. Add New Account")
                typer.echo("2. Transfer Funds Between Accounts")
                typer.echo("0. Back to Main Menu")
                choice = typer.prompt("Select", type=int)
        
                if choice == 1:
                    name = typer.prompt("Account Name")
                    acc_type = typer.prompt("Account Type (bank/wallet)", default="bank")
                    balance = typer.prompt("Initial Balance", type=float, default=0.0)
                    wallet = typer.prompt("ETH Wallet Address (optional)", default="")
                    cmd = f'create-account "{name}" --type "{acc_type}" --balance {balance}'
                    if wallet:
                        cmd += f' --wallet "{wallet}"'
                    run_command(cmd)
        
                elif choice == 2:
                    from_acc = typer.prompt("From Account")
                    to_acc = typer.prompt("To Account")
                    amount = typer.prompt("Amount", type=float)
                    cmd = f'transfer "{from_acc}" "{to_acc}" {amount}'
                    run_command(cmd)
        
                elif choice == 0:
                    break
                else:
                    typer.echo("Invalid choice.")
        account_menu()
    elif choice == 3:
        def income_menu():
            while True:
                typer.echo("\n=== Income Menu ===")
                typer.echo("1. Add New Income")
                typer.echo("0. Back to Main Menu")
                choice = typer.prompt("Select", type=int)
        
                if choice == 1:
                    amount = typer.prompt("Income Amount", type=float)
                    source = typer.prompt("Source/Label", default="unknown")
                    account = typer.prompt("Account")
                    date = typer.prompt("Date (YYYY-MM-DD, default today)", default="")
                    cmd = f'add-income {amount} --source "{source}" --account "{account}"'
                    if date:
                        cmd += f' --date "{date}"'
                    run_command(cmd)
        
                elif choice == 0:
                    break
                else:
                    typer.echo("Invalid choice.")
        income_menu()
    elif choice == 4:
        def expense_menu():
            while True:
                typer.echo("\n=== Expense Menu ===")
                typer.echo("1. Add New Expense")
                typer.echo("0. Back to Main Menu")
                choice = typer.prompt("Select", type=int)
        
                if choice == 1:
                    amount = typer.prompt("Expense Amount (e.g., $4.50)")
                    category = typer.prompt("Category", default="general")
                    description = typer.prompt("Description", default="")
                    account = typer.prompt("Account")
                    metadata = typer.prompt("Metadata (JSON array, optional)", default="[]")
                    note = typer.prompt("Note (optional)", default="")
                    date = typer.prompt("Date (YYYY-MM-DD, default today)", default="")
                    cmd = f'add-expense "{amount}" --category "{category}" --description "{description}" --account "{account}" --metadata \'{metadata}\' --note "{note}"'
                    if date:
                        cmd += f' --date "{date}"'
                    run_command(cmd)
        
                elif choice == 0:
                    break
                else:
                    typer.echo("Invalid choice.")
        expense_menu()
    elif choice == 5:
        def goal_menu():
            while True:
                typer.echo("\n=== Goal Menu ===")
                typer.echo("1. Set New Goal")
                typer.echo("2. List Goals")
                typer.echo("3. Update Goal Progress")
                typer.echo("4. Complete Goal")
                typer.echo("5. Delete Goal")
                typer.echo("6. View Completed Goal History")
                typer.echo("0. Back to Main Menu")
                choice = typer.prompt("Select", type=int)
    
                if choice == 1:
                    title = typer.prompt("Goal Title")
                    target = typer.prompt("Target Amount", type=float)
                    account = typer.prompt("Account (optional)", default="")
                    priority = typer.prompt("Priority (1-5)", type=int, default=1)
                    deadline = typer.prompt("Deadline (YYYY-MM-DD, optional)", default="")
                    note = typer.prompt("Note (optional)", default="")
                    cmd = f'set-goal "{title}" {target} --account "{account}" --priority {priority} --deadline "{deadline}" --note "{note}"'
                    run_command(cmd)
    
                elif choice == 2:
                    status = typer.prompt("Status (active/completed)", default="active")
                    account = typer.prompt("Filter by Account (optional)", default="")
                    cmd = f'list-goals --status "{status}"'
                    if account.strip():
                        cmd += f' --account "{account}"'
                    run_command(cmd)
    
                elif choice == 3:
                    title = typer.prompt("Goal Title to Update")
                    amount = typer.prompt("Amount to Add", type=float)
                    account = typer.prompt("Source Account")
                    cmd = f'update-goal "{title}" --amount {amount} --account "{account}"'
                    run_command(cmd)
    
                elif choice == 4:
                    title = typer.prompt("Goal Title to Mark as Completed")
                    run_command(f'complete-goal "{title}"')
    
                elif choice == 5:
                    title = typer.prompt("Goal Title to Delete")
                    run_command(f'delete-goal "{title}"')
    
                elif choice == 6:
                    run_command("goal-history")
    
                elif choice == 0:
                    break
    
                else:
                    typer.echo("Invalid choice. Try again.")
    
        goal_menu()  # call it outside after it's defined
    elif choice == 6:
        def debit_menu():
            while True:
                typer.echo("\n=== Debit Menu ===")
                typer.echo("1. Add New Debit")
                typer.echo("2. Pay Debit")
                typer.echo("3. List Debits")
                typer.echo("0. Back to Main Menu")
                choice = typer.prompt("Select", type=int)
        
                if choice == 1:
                    label = typer.prompt("Debit Label")
                    amount = typer.prompt("Amount", type=float)
                    account = typer.prompt("Account")
                    due_date = typer.prompt("Due Date (YYYY-MM-DD, optional)", default="")
                    note = typer.prompt("Note (optional)", default="")
                    cmd = f'add-debit "{label}" {amount} "{account}"'
                    if due_date:
                        cmd += f' --due-date "{due_date}"'
                    if note:
                        cmd += f' --note "{note}"'
                    run_command(cmd)
        
                elif choice == 2:
                    label = typer.prompt("Debit Label")
                    amount = typer.prompt("Payment Amount", type=float)
                    account = typer.prompt("Account to Pay From")
                    cmd = f'pay-debit "{label}" {amount} --account "{account}"'
                    run_command(cmd)
        
                elif choice == 3:
                    account = typer.prompt("Filter by Account (optional)", default="")
                    status = typer.prompt("Status (pending/paid)", default="pending")
                    cmd = f'list-debits --status "{status}"'
                    if account.strip():
                        cmd += f' --account "{account}"'
                    run_command(cmd)
        
                elif choice == 0:
                    break
                else:
                    typer.echo("Invalid choice.")
        debit_menu()
    elif choice == 7:
        def note_menu():
            while True:
                typer.echo("\n=== Note Menu ===")
                typer.echo("1. Add New Note")
                typer.echo("2. List Recent Notes")
                typer.echo("0. Back to Main Menu")
                choice = typer.prompt("Select", type=int)
        
                if choice == 1:
                    mood = typer.prompt("Mood Rating (1-10)", type=int)
                    content = typer.prompt("Note Text")
                    account = typer.prompt("Account (optional)", default="")
                    tags = typer.prompt("Tags (JSON array, optional)", default="[]")
                    cmd = f'add-note {mood} "{content}"'
                    if account:
                        cmd += f' --account "{account}"'
                    if tags:
                        cmd += f" --tags '{tags}'"
                    run_command(cmd)
        
                elif choice == 2:
                    account = typer.prompt("Filter by Account (optional)", default="")
                    days = typer.prompt("Days to Look Back", type=int, default=7)
                    cmd = f'list-notes --days {days}'
                    if account.strip():
                        cmd += f' --account "{account}"'
                    run_command(cmd)
        
                elif choice == 0:
                    break
                else:
                    typer.echo("Invalid choice.")
        note_menu()
    elif choice == 8:
        def web3_menu():
            while True:
                typer.echo("\n=== Web3 Menu ===")
                typer.echo("1. View Web3 Summary")
                typer.echo("0. Back to Main Menu")
                choice = typer.prompt("Select", type=int)
        
                if choice == 1:
                    # Since summary_web3 is a direct function, not CLI command
                    from commands.summary_web3 import summary_web3
                    summary_web3()
                elif choice == 0:
                    break
                else:
                    typer.echo("Invalid choice.")
        web3_menu()
    elif choice == 9:
        def summary_menu():
            while True:
                typer.echo("\n=== Summary Menu ===")
                typer.echo("1. View Summary")
                typer.echo("2. Export Summary to JSON")
                typer.echo("0. Back to Main Menu")
                choice = typer.prompt("Select", type=int)
        
                if choice == 1:
                    days = typer.prompt("Days to Summarize", type=int, default=30)
                    account = typer.prompt("Account (optional)", default="")
                    cmd = f'summary --days {days}'
                    if account.strip():
                        cmd += f' --account "{account}"'
                    run_command(cmd)
        
                elif choice == 2:
                    days = typer.prompt("Days to Include", type=int, default=30)
                    directory = typer.prompt("Export Directory (default: reports)", default="reports")
                    cmd = f'summary-export --days {days} --output-dir "{directory}"'
                    run_command(cmd)
        
                elif choice == 0:
                    break
                else:
                    typer.echo("Invalid choice.")
        summary_menu()
    elif choice == 10:
        def export_menu():
            while True:
                typer.echo("1. Export Summary to JSON")
                typer.echo("0. Back to Main Menu")
                choice = typer.prompt("Select", type=int)

                if choice == 1:
                    days = typer.prompt("Days to Include", type=int, default=30)
                    directory = typer.prompt("Export Directory (default: reports)", default="reports")
                    cmd = f'summary-export --days {days} --output-dir "{directory}"'
                    run_command(cmd)
                elif choice == 0:
                    break
                else:
                    typer.echo("Invalid choice.")
        export_menu()
    elif choice == 0:
        return
