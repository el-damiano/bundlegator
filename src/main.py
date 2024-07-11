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

        if not source.startswith("https://"):
            return function(source)

        request = requests.get(source, headers={'User-Agent': 'Googlebot/2.1'})
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
    try:
        return json.loads(source)
    except ValueError:
        pass

    match = re.findall(r'{.*}', source)

    if match is None:
        raise Exception('No valid JSON found')

    # no special logic needed, should be the last match
    # if not, landingPage-json-data webpack-bundle-page-data might be useful
    result = match[len(match) - 1]
    return json.loads(result)


def get_bundle_urls(source: str):
    url = source
    if url is Source.HUMBLE_BUNDLE:
        url += '/bundles'
    elif url is Source.FANATICAL:
        url += '/api/algolia/bundles?altRank=false'
    element = extract_json(url)

    try:
        bundles = []
        for category in element['data'].items():
            elements = list(category[1]['mosaic'][0]['products'])
            for element in elements:
                bundles.append(element['product_url'])
        return list(map(
            lambda past: source + past,
            bundles
        ))

    except (KeyError, TypeError):
        exit()


def main():
    bundle_urls = get_bundle_urls(Source.HUMBLE_BUNDLE)

    bundles_by_source = {'HumbleBundle': bundle_urls}
    for _, v in bundles_by_source.items():
        print(v)

    print('\n'.join(bundle_urls))


if __name__ == "__main__":
    main()
