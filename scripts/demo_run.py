from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.agent import SecureAgent


def main() -> None:
    agent = SecureAgent()
    for event in agent.stream("企业 Agent 如何防 Prompt Injection 和工具越权？", "cli-demo"):
        print(event)


if __name__ == "__main__":
    main()
