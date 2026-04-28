import sys
import os
import subprocess

def print_help():
    print("Project Rita - Entry Point")
    print("Usage: python main.py <command>")
    print("\nAvailable commands:")
    print("  bot      Start the Telegram bot")
    print("  api      Start the FastAPI server")
    print("  import   Run the data import from Excel")

def run_bot():
    print("Starting Telegram bot...")
    subprocess.run([sys.executable, "-m", "app.bot.main"])

def run_api():
    print("Starting API server...")
    subprocess.run(["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"])

def run_import():
    print("Starting data import...")
    # This runs the local scripts
    subprocess.run([sys.executable, "app/scripts/parse_excel.py"])
    subprocess.run([sys.executable, "-m", "app.scripts.load_data"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "bot":
        run_bot()
    elif command == "api":
        run_api()
    elif command == "import":
        run_import()
    else:
        print(f"Error: Unknown command '{command}'")
        print_help()
        sys.exit(1)
