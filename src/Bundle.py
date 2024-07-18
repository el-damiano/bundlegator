from bundle_utils import Source
from datetime import datetime


class Bundle:

    def __init__(self, source: Source, document: dict):
        if source is Source.HUMBLE_BUNDLE:
            self.name = "Humble Bundle: " + document["bundleData"]["basic_data"]["human_name"] or "Unknown"
            self.author = document.get("bundleData", {}).get("author") or "Unkown"
            self.url = source + document.get("bundleData", {}).get("page_url") or "/bundles"
            self.start_date = document.get("at_time|datetime") or "Unkown"
            self.end_date = str(document.get("bundleData", {}).get("basic_data", {}).get("end_time_datetime")) or "Unknown"
            self.charity = None
            self.total_price = None
            self.items = None  # dict item_by_tier
        elif source is Source.FANATICAL:
            self.name = "Fanatical: " + document["name"] or "Unkown"
            self.author = "Fanatical"
            self.url = source + "/" + (document.get("type") or "en") + "/" + (document.get("slug") or "bundle")
            unix_time = document.get("release_date")
            self.start_date = str(datetime.fromtimestamp(unix_time)) if unix_time else "Unkown"
            self.end_date = "Unkown"
            self.charity = None
            self.total_price = None
            self.items = None  # dict item_by_tier
