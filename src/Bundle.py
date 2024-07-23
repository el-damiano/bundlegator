import time
import json
import requests
from requests.models import Response
from datetime import datetime
from bundle_utils import Source


class Bundle:

    def __init__(self, source: Source, document: dict):
        if source is Source.HUMBLE_BUNDLE:
            bundle_data = document.get("bundleData", {})
            basic_data = bundle_data.get("basic_data", {})
            self.name = basic_data.get("human_name")
            self.authors = bundle_data.get("author")
            self.url = source + "/" + (bundle_data.get("page_url") or "bundles")
            self.start_date = document.get("at_time|datetime")
            self.end_date = basic_data.get("end_time_datetime")
            self.total_price = [value for value in basic_data.get("msrp|money", {}).values()] or None
            self.items = self.get_humble_bundle_items(bundle_data.get("tier_item_data"))

        elif source is Source.FANATICAL:
            unix_time = document.get("release_date")
            self.name = document.get("name")
            self.authors = "Fanatical"
            self.url = source + "/" + (document.get("type") or "en") + "/" + (document.get("slug") or "bundle")
            self.start_date = str(datetime.fromtimestamp(unix_time)) if unix_time else None
            self.end_date = None
            self.total_price = (str(document.get("fullPrice", {}).get("EUR")) + " EUR") or None
            self.items = self.get_fanatical_bundle_items(document.get("bundle_covers"))

    def get_humble_bundle_items(self, items: dict | None) -> dict:
        if items is None:
            return {}

        items_by_tier = {}
        for _, value in items.items():
            tier = value.get("min_price|money", {}).get("amount") or "Other"
            if tier not in items_by_tier:
                items_by_tier[tier] = list()
            items_by_tier[tier].append(BundleItem(Source.HUMBLE_BUNDLE, value))

        return items_by_tier

    def get_fanatical_bundle_items(self, items: list | None) -> dict:
        if items is None:
            return {}

        # just to keep it unified with how it's done with HumbleBundle
        items_by_tier = {'fakeTier': list()}
        for item in items:
            items_by_tier['fakeTier'].append(BundleItem(Source.FANATICAL, item))
        return items_by_tier


class BundleItem:

    def __init__(self, source: Source, item_data: dict):
        if source is Source.HUMBLE_BUNDLE:
            self.item_data = item_data
            self.name = item_data.get("human_name")
            self.authors = [dev.get("developer-name") for dev in item_data.get("developers", {})] or None
            self.publisher = [pub.get("publisher-name") for pub in item_data.get("publishers", {})] or None
            self.platforms = item_data.get("platforms_and_oses", {})
            self.isbn = None
            self.release_date = None

            if "ebook" in self.platforms.keys():
                self.fill_in_book_data()

        elif source is Source.FANATICAL:
            self.item_data = item_data
            self.name = item_data.get("name")
            self.authors = None
            self.publisher = None
            self.platforms = None
            self.isbn = None
            self.release_date = None

            # deprecated for now due to lack of caching functionality to avoid unnecessary requests
            # if item_data.get("type") == "book":
            #     self.fill_in_book_data()

    def fill_in_book_data(self) -> None:
        """
        Query Google API and set `self.isbn` and `self.release_date` in-place.
        """
        self.isbn = ""
        self.release_date = ""

        GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes?lr=langRestrict=en&q="
        request_url = GOOGLE_BOOKS_URL

        if self.name:
            request_url += f"intitle:\"{self.name}\""
        if self.authors:
            # authors = map(
            #     lambda author: f"inauthor:\"{author.split(',')}\"",
            #     self.authors.copy()
            # )
            # print(list(authors))
            authors = self.authors.copy()
            for author in authors:
                if author is None:
                    continue
                # this is attrocious, but it avoids scuffed api results
                # authors are not listed in an uniform fashion
                # a single entry can mean
                # - a single author
                # - a single author, whose first and last name are comma-separated
                # - a group of authors, comma-seperated
                # this way there can also be more keywords than allowed, so cut em short
                request_url += str("".join(list(
                    map(
                        lambda keyword: f"inauthor:\"{keyword}\"",
                        author.split(',')
                    )
                )[:7]))

        request = Response()
        while True:
            request = requests.get(request_url, headers={'User-Agent': 'Googlebot/2.1'})
            if request.status_code == 429:
                print('too many requests, waiting for 10s')
                time.sleep(5)
                continue
            elif request.status_code != 200:
                raise Exception(
                    "GET request failed, "
                    f"HTTP status code: {request.status_code}, "
                    f"URL: {request_url}"
                )
            break

        items = json.loads(request.text).get("items")
        if items is None:
            return

        i = 0
        for item in items:
            # don't display too many matches, just indicate it
            if i == 3:
                self.isbn += "+ more"
                self.release_date += "+ more"
                break
            i += 1

            volume_info = item.get("volumeInfo", {})
            if volume_info is None or volume_info.get("language") != "en":
                continue

            self.isbn += "".join(
                [identifier.get("identifier") or "Unknown" for
                    identifier in volume_info.get("industryIdentifiers", {})
                    if identifier["type"] == "ISBN_13"]
            ) + " "
            self.release_date += (volume_info.get("publishedDate") or "Unknown") + " "
