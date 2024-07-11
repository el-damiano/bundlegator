import re
import json
import requests
from enum import Enum


class Source(str, Enum):
    HUMBLE_BUNDLE = "https://www.humblebundle.com"
    FANATICAL = "https://www.fanatical.com"

    def __str__(self) -> str:
        return self.value


def get_html(function):
    def wrapper(source: str) -> dict:
        if source.startswith("file://"):
            with open(source[7:]) as file:
                return function(file.read())

        url = ""
        match source:
            case Source.HUMBLE_BUNDLE:
                url = source + '/bundles'
            case Source.FANATICAL:
                url = source + '/en/bundle'
            case _:
                return function(source)

        request = requests.get(url)
        if request.status_code != 200:
            raise Exception(
                "GET request failed, "
                f"HTTP status code: {request.status_code}, "
                f"URL: {source}"
            )

        return function(request.text)
    return wrapper


@get_html
def extract_json(source: str) -> dict:
    match = re.findall(r'{.*}', source)

    if match is None:
        raise Exception('No valid JSON found')

    # no special logic needed, should be the last match
    # if not, landingPage-json-data webpack-bundle-page-data might be useful
    result = match[len(match) - 1]
    return json.loads(result)


def get_bundle_urls(source: str):
    element = extract_json(source)
    try:
        bundles = []
        for category in element['data'].items():
            elements = list(category[1]['mosaic'][0]['products'])
            for element in elements:
                bundles.append(element['product_url'])
        return bundles

    except KeyError:
        exit()


def main():
    BASE_URL = "https://www.humblebundle.com"
    bundle_urls = map(
        lambda url: BASE_URL + url,
        get_bundle_urls(Source.HUMBLE_BUNDLE)
    )

    if bundle_urls is None:
        exit()

    print('\n'.join(bundle_urls))


if __name__ == "__main__":
    main()
