import recompute
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Run the Recompute server"
    )

    parser.add_argument(
        "--host", dest="host", type=str, default="0.0.0.0",
        help="IP address of the server"
    )

    parser.add_argument(
        "--port", dest="port", type=int, default=5000,
        help="Port of the server"
    )

    args = parser.parse_args()

    recompute.server.run(args.host, args.port)


if __name__ == "__main__":
    main()
