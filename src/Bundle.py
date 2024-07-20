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
            self.author = bundle_data.get("author")
            self.url = source + "/" + (bundle_data.get("page_url") or "bundles")
            self.start_date = document.get("at_time|datetime")
            self.end_date = str(basic_data.get("end_time_datetime"))
            self.total_price = [value for value in basic_data.get("msrp|money").values()]
            self.items = self.get_humble_bundle_items(bundle_data.get("tier_item_data"))

        elif source is Source.FANATICAL:
            unix_time = document.get("release_date")
            self.name = document.get("name") or "Unkown"
            self.author = "Fanatical"
            self.url = source + "/" + (document.get("type") or "en") + "/" + (document.get("slug") or "bundle")
            self.start_date = str(datetime.fromtimestamp(unix_time)) if unix_time else "Unkown"
            self.end_date = "Unkown"
            self.total_price = str(document.get("fullPrice", {}).get("EUR")) + " EUR"
            self.items = self.get_fanatical_bundle_items(document.get("bundle_covers"))

    def get_humble_bundle_items(self, items: dict | None) -> dict | None:
        if items is None:
            return None

        items_by_tier = {}
        for _, value in items.items():
            tier = value.get("min_price|money", {}).get("amount") or "Other"
            if tier not in items_by_tier:
                items_by_tier[tier] = list()
            items_by_tier[tier].append(BundleItem(Source.HUMBLE_BUNDLE, value))

        return items_by_tier

    def get_fanatical_bundle_items(self, items: list | None) -> dict | None:
        if items is None:
            return None

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
            self.author = [dev.get("developer-name") for dev in item_data.get("developers", {})]
            self.publisher = [pub.get("publisher-name") for pub in item_data.get("publishers", {})]
            self.platforms = item_data.get("platforms_and_oses", {})
            self.isbn = None
            self.release_date = None

            if "ebook" in self.platforms.keys():
                self.fill_in_book_data()

        elif source is Source.FANATICAL:
            self.item_data = item_data
            self.name = item_data.get("name")
            self.author = None
            self.publisher = None
            self.platforms = None
            self.isbn = None
            self.release_date = None

            if item_data.get("type") == "book":
                self.fill_in_book_data()

    def fill_in_book_data(self) -> None:
        """
        Query Google API and set `self.isbn` and `self.release_date` in-place.
        """
        self.isbn = ""
        self.release_date = ""

        GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes?lr=lang_en&q="
        request_url = GOOGLE_BOOKS_URL

        if self.name:
            request_url += f"intitle:\"{self.name}\""
        if self.author:
            for author in self.author:
                # sometimes multiple authors are in a list
                # but sometimes they're in one entry, with a comma as the separator
                # but also some single authors have their names separated with a comma
                # and these mess up the api request and the results are scuffed
                # so just go with the first one if there's a comma, still better than nothing
                author = author.split(',')[0]
                request_url += f"inauthor:\"{author}\" "

        request = Response()
        while (True):
            request = requests.get(request_url, headers={'User-Agent': 'Googlebot/2.1'})
            if request.status_code == 429:
                print('too many requests, waiting for 10s')
                time.sleep(10)
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
