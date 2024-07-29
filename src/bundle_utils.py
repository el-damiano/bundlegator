import os
import re
import json
import requests
from enum import Enum


# consider refactoring `bundle_utils` and `Source` enum when more sources will be supported
class Source(str, Enum):
    HUMBLE_BUNDLE = "https://www.humblebundle.com"
    FANATICAL = "https://www.fanatical.com"

    def __str__(self) -> str:
        return self.value


def get_html(function):
    def wrapper(source_location: str) -> dict:
        if source_location.startswith("file://"):
            with open(source_location[7:]) as file:
                return function(file.read())

        if not source_location.startswith("https://"):
            return function(source_location)

        request = requests.get(source_location, headers={'User-Agent': 'Googlebot/2.1'})
        if request.status_code != 200:
            raise Exception(
                "GET request failed, "
                f"HTTP status code: {request.status_code}, "
                f"URL: {source_location}"
            )

        return function(request.text)
    return wrapper


@get_html
def extract_json(source_document: str) -> dict:
    """
    Extract a JSON document from ``str`` to a Python ``dict``.

    Validates if the JSON is valid, without checking if ``str`` contains it.
    Only supports HumbleBundle and Fanatical.
    """
    try:
        return json.loads(source_document)
    except ValueError:
        pass

    match = re.findall(r'{.*}', source_document)

    if match is None:
        raise TypeError('No valid JSON found')

    # no special logic needed, should be the last match
    # if not, landingPage-json-data webpack-bundle-page-data might be useful
    result = match[len(match) - 1]
    return json.loads(result)


def get_bundles(source: str) -> list[dict] | dict:
    url = source
    # hardcode due to quick deprecation of main.sh
    HUMBLE_BUNDLE_CACHE = os.path.expanduser('~') + "/.cache/humble_bundle"

    try:
        if url is Source.HUMBLE_BUNDLE:
            url += '/bundles'
            element = extract_json(url)

            # ideally I'd cache all relevant bundle info including the google api books results
            # but for that I'd need to refactor a bunch of stuff
            # cause instead of using a simple dict I went with stupid objects
            cache_file = open(HUMBLE_BUNDLE_CACHE, 'r+')
            cached_elements = cache_file.read().splitlines()
            cache_file.truncate(0)
            cache_file.seek(0)

            bundles = []
            for _, category in element.get('data', {}).items():
                elements = category.get('mosaic', [{}])[0].get('products', [])

                for element in elements:
                    machine_name = element.get("machine_name")
                    if machine_name not in cached_elements:
                        bundles.append(extract_json(source + element['product_url']))
                    cache_file.write(machine_name + "\n")

            cache_file.close()

            return bundles

        elif url is Source.FANATICAL:
            url += '/api/algolia/bundles?altRank=false'
            elements = extract_json(url)
            return elements

    except (KeyError, TypeError):
        raise KeyError("JSON document doesn't conform to schema")

    return list()
