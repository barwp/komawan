from pathlib import Path
import sys


APP_DIR = Path(__file__).parent / "sentimentcloud-lite"
sys.path.insert(0, str(APP_DIR))

from app import main  # noqa: E402


if __name__ == "__main__":
    main()
