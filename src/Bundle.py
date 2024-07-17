from bundle_utils import Source
from datetime import datetime


class Bundle:

    def __init__(self, source: Source, document: dict):
        self.name = self.get_name(source, document)
        self.author = self.get_author(source, document)
        self.url = self.get_url(source, document)
        self.start_date = None
        self.end_date = None
        self.charity = None
        self.total_price = None
        self.items = None  # dict item_by_tier

    def get_name(self, source: Source, document: dict) -> str:
        if source == Source.HUMBLE_BUNDLE:
            return "Humble Bundle: " + document["bundleData"]["basic_data"]["human_name"] or "Unknown"
        elif source == Source.FANATICAL:
            return "Fanatical: " + document["name"] or "Unkown"

    def get_author(self, source: Source, document: dict) -> str:
        if source == Source.HUMBLE_BUNDLE:
            return document.get("bundleData", {}).get("author") or "Unkown"
        elif source == Source.FANATICAL:
            return "Fanatical: " + document["name"] or "Unkown"

    def get_url(self, source: Source, document: dict) -> str:
        if source == Source.HUMBLE_BUNDLE:
            return Source.HUMBLE_BUNDLE + document.get("bundleData", {}).get("page_url") or "/bundles"
        elif source == Source.FANATICAL:
            return f"{Source.FANATICAL}/{document.get("type") or "en"}/{document.get("slug") or "bundle"}"

    def get_start_date(self, source: Source, document: dict) -> str:
        if source == Source.HUMBLE_BUNDLE:
            return document.get("at_time|datetime") or "Unkown"
        elif source == Source.FANATICAL:
            unix_time = document.get("release_date")
            return str(datetime.fromtimestamp(unix_time)) if unix_time else "Unkown"

    def get_end_date(self, source: Source, document: dict) -> str:
        if source == Source.HUMBLE_BUNDLE:
            return str(document.get("bundleData", {}).get("basic_data", {}).get("end_time_datetime")) or "Unknown"
        elif source == Source.FANATICAL:
            return "Unkown"
