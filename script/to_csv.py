from argparse import ArgumentParser

from acl_anthology import AclAnthologyDownloader


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--conference", type=str, default="acl")
    parser.add_argument("--year", type=int, default=2021)
    args = parser.parse_args()
    downloader = AclAnthologyDownloader(conference=args.conference, year=args.year)
    downloader.download()
