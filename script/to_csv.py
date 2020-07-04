import requests
import xml.etree.ElementTree as etree
from typing import Dict

import pandas


ACL_ANTHOLOGY_DATA_URL = "https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/{year}.{conference}.xml"
ACL_ANTHOLOGY_HOMEPAGE_URL = "https://www.aclweb.org/anthology/{path}"


def parse_child(element: 'xml.etree.ElementTree.Element') -> Dict[str, str]:
    body = {"title": None, "authors": [], "url": None}

    for tag in element:
        if tag.tag in ("title", "abstract"):
            #
            # tag.itertext for dealing with fixed-case
            #
            # <title><fixed-case>X</fixed-case>XXXX</title>
            #        ^^^^^^^^^^^^^^^^^^^^^^^^^^
            #
            body[tag.tag] = ''.join(t for t in tag.itertext())

        if tag.tag == "author":
            author_dict = {t.tag: t.text for t in tag}
            # NOTE: https://www.aclweb.org/anthology/2020.acl-main.521/
            author_name = " ".join([author_dict["first"] or "", author_dict["last"] or ""])
            body["authors"].append(author_name)
            
        if tag.tag == "url":
            body["url"] = ACL_ANTHOLOGY_HOMEPAGE_URL.format(path=tag.text)

    body["author"] = ", ".join(body["authors"])
    body.pop("authors")

    body = {key.capitalize(): value for key, value in body.items()}
    return body


def fetch(conference: str, year: int):
    url = ACL_ANTHOLOGY_DATA_URL.format(conference=conference, year=year)
    response = requests.get(url)
    tree = etree.fromstring(response.content)
    data = pandas.DataFrame([parse_child(paper) for paper in tree.findall("./volume/paper")])
    return data[["Title", "Author", "Abstract", "Url"]]


if __name__ == "__main__":
    data = fetch("acl", 2020)
    data.to_csv("acl.2020.csv", index=False)
