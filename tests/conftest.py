from pathlib import Path

# Auto-load .env if present
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(env_file)
    except ImportError:
        pass
