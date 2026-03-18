"""CLI for vastu."""
import sys, json, argparse
from .core import Vastu

def main():
    parser = argparse.ArgumentParser(description="Vastu — AI Floor Plan Generator. Generate Vastu-compliant floor plans with AI space optimization.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Vastu()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.generate(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"vastu v0.1.0 — Vastu — AI Floor Plan Generator. Generate Vastu-compliant floor plans with AI space optimization.")

if __name__ == "__main__":
    main()
