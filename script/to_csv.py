from argparse import ArgumentParser
from logging import basicConfig
from logging import INFO

from acl_anthology import AclAnthologyDownloader


if __name__ == "__main__":
    basicConfig(level=INFO, format="[%(asctime)s] %(message)s")

    parser = ArgumentParser()
    parser.add_argument("--conference", type=str, default="acl")
    parser.add_argument("--year", type=int, default=2021)
    args = parser.parse_args()
    downloader = AclAnthologyDownloader(conference=args.conference, year=args.year)
    downloader.download()
