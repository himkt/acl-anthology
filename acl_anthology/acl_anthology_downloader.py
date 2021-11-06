from typing import Dict
import xml.etree.ElementTree as etree

import pandas
import requests


class AclAnthologyDownloader:
    ACL_ANTHOLOGY_DATA_URL = (
        "https://raw.githubusercontent.com"
        "/acl-org/acl-anthology/master/data/xml/{year}.{conference}.xml"
    )
    ACL_ANTHOLOGY_HOMEPAGE_URL = "https://www.aclweb.org/anthology/{path}"
    OUTPUT_FILE_NAME = "{conference}.{year}.csv"


    def __init__(self, conference: str, year: int) -> None:
        self._conference = conference
        self._year = year

    def download(self) -> None:
        data = self._fetch(self._conference, self._year)
        data.to_csv(
            self.OUTPUT_FILE_NAME.format(
                conference=self._conference,
                year=self._year,
            ),
            index=False,
        )

    def _fetch(self, conference: str, year: int) -> pandas.DataFrame:
        url = self.ACL_ANTHOLOGY_DATA_URL.format(conference=conference, year=year)
        response = requests.get(url)
        tree = etree.fromstring(response.content)
        data = pandas.DataFrame([self._parse_child(paper) for paper in tree.findall("./volume/paper")])
        return data[["Title", "Author", "Abstract", "Url"]]

    def _parse_child(self, element: etree.Element) -> Dict[str, str]:
        body = {"title": None, "authors": [], "url": None}

        for tag in element:
            if tag.tag in ("title", "abstract"):
                # NOTE: For <fixed-case>, it calls itertext.
                #
                # <title><fixed-case>X</fixed-case>XXXX</title>
                #        ^^^^^^^^^^^^^^^^^^^^^^^^^^
                #
                body[tag.tag] = "".join(t for t in tag.itertext())

            if tag.tag == "author":
                # NOTE: First or last name could be None.
                #
                # ref. https://www.aclweb.org/anthology/2020.acl-main.521/
                #
                author_dict = {t.tag: t.text for t in tag}
                first_name = author_dict.get("first") or ""
                last_name = author_dict.get("last") or ""
                author_name = f"{first_name} {last_name}"
                body["authors"].append(author_name)

            if tag.tag == "url":
                body["url"] = self.ACL_ANTHOLOGY_HOMEPAGE_URL.format(path=tag.text)

        body["author"] = ", ".join(body["authors"])
        body.pop("authors")

        body = {key.capitalize(): value for key, value in body.items()}
        return body
