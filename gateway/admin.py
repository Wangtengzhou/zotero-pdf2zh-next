import argparse
import sys

from gateway import tokens


def main():
    parser = argparse.ArgumentParser(description="Manage the container access token")
    parser.add_argument("resource", choices=("token", "url"))
    parser.add_argument("operation", choices=("show", "reset"))
    parser.add_argument("--base-url", help="Optional HTTP(S) origin for displaying a full URL; does not bind the gateway")
    args = parser.parse_args()
    if args.resource == "url" and args.operation != "show":
        parser.error("Use token reset to reset credentials")
    base = ""
    if args.resource == "url" or args.operation == "reset":
        try:
            base = tokens.public_base(args.base_url)
        except ValueError:
            print("Invalid display URL. Use an HTTP(S) origin without a path, credentials or query.", file=sys.stderr)
            return 1
    try:
        if args.operation == "reset":
            token = tokens.reset()
            print("Token reset. Update the Zotero server URL. Previously authorized requests may finish.")
            print(tokens.public_url(token, base))
        elif args.resource == "url":
            print(tokens.public_url(tokens.current(), base))
        else:
            print(tokens.current())
    except (OSError, ValueError, KeyError) as error:
        print(tokens.state_error_message(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
