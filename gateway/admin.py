import argparse
import sys

from gateway import tokens


def main():
    parser = argparse.ArgumentParser(description="Manage the container access token")
    parser.add_argument("resource", choices=("token", "url"))
    parser.add_argument("operation", choices=("show", "reset"))
    args = parser.parse_args()
    if args.resource == "url" and args.operation != "show":
        parser.error("Use token reset to reset credentials")
    try:
        if args.operation == "reset":
            token = tokens.reset()
            print("Token reset. Update the Zotero server URL. Previously authorized requests may finish.")
            try:
                print(tokens.public_url(token))
            except ValueError:
                print(f"/access/{token}")
                print("PUBLIC_BASE_URL is unset or invalid; prepend your HTTPS origin.")
        elif args.resource == "url":
            print(tokens.public_url(tokens.current()))
        else:
            print(tokens.current())
    except (OSError, ValueError, KeyError):
        print("Cannot read/write token state or public URL configuration. Check the state volume and PUBLIC_BASE_URL.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
