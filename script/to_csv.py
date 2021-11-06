import xml.etree.ElementTree as etree
from typing import Dict

import pandas
import requests
import typer


ACL_ANTHOLOGY_DATA_URL = "https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/{year}.{conference}.xml"  # NOQA
ACL_ANTHOLOGY_HOMEPAGE_URL = "https://www.aclweb.org/anthology/{path}"
OUTPUT_FILE_NAME = "{conference}.{year}.csv"


def parse_child(element: 'xml.etree.ElementTree.Element') -> Dict[str, str]:
    body = {"title": None, "authors": [], "url": None}

    for tag in element:
        if tag.tag in ("title", "abstract"):
            # NOTE: For <fixed-case>, it calls itertext.
            #
            # <title><fixed-case>X</fixed-case>XXXX</title>
            #        ^^^^^^^^^^^^^^^^^^^^^^^^^^
            #
            body[tag.tag] = ''.join(t for t in tag.itertext())

        if tag.tag == "author":
            # NOTE: First or last name could be None.
            #
            # ref. https://www.aclweb.org/anthology/2020.acl-main.521/
            #
            author_dict = {t.tag: t.text for t in tag}
            author_name = (author_dict.get("first") or "") + (author_dict.get("last") or "")
            body["authors"].append(author_name)
            
        if tag.tag == "url":
            body["url"] = ACL_ANTHOLOGY_HOMEPAGE_URL.format(path=tag.text)

    body["author"] = ", ".join(body["authors"])
    body.pop("authors")

    body = {key.capitalize(): value for key, value in body.items()}
    return body


def fetch(conference: str, year: int) -> pandas.DataFrame:
    url = ACL_ANTHOLOGY_DATA_URL.format(conference=conference, year=year)
    response = requests.get(url)
    tree = etree.fromstring(response.content)
    data = pandas.DataFrame([parse_child(paper) for paper in tree.findall("./volume/paper")])
    return data[["Title", "Author", "Abstract", "Url"]]


def download(conference: str = "acl", year: int = "2020") -> None:
    """
    Args:

        conference: name of conference, should be lowercase.

        year: year of a conference.

    """
    print("conference: ", conference, ", year: ", year)
    data = fetch(conference, year)
    data.to_csv(OUTPUT_FILE_NAME.format(conference=conference, year=year), index=False)


if __name__ == "__main__":
    typer.run(download)
