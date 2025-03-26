import argparse

import uvicorn

#
# HOW TO RUN EXAMPLES?
#   poetry run python examples/main.py --example-module security.rlac
#


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example runner:")
    parser.add_argument(
        "--example-module",
        type=str,
        required=True,
        help="Pass example module-path. For example: security.rlac",
    )
    args = parser.parse_args()

    uvicorn.run(f"{args.example_module}:app", host="localhost", port=8000, reload=True)
