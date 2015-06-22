import recompute
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Recompute now"
    )

    parser.add_argument(
        "url", dest="port", type=int, default=5000,
        help="GitHub URL containing the project to be recomputed"
    )

    args = parser.parse_args()

    print "TODO"


if __name__ == "__main__":
    main()
