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
    try:
        if url is Source.HUMBLE_BUNDLE:
            url += '/bundles'
            element = extract_json(url)

            bundles = []
            # using unsafe subscripting to get an exception in case HumbleBundle changes their schema
            for _, category in element['data'].items():
                elements = list(category['mosaic'][0]['products'])
                for element in elements:
                    bundles.append(extract_json(source + element['product_url']))

            return bundles

        elif url is Source.FANATICAL:
            url += '/api/algolia/bundles?altRank=false'
            elements = extract_json(url)
            return elements

    except (KeyError, TypeError):
        pass

    return list()
