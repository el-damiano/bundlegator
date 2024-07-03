import re
import json
import requests


def scrape(url: str) -> str:
    request = requests.get(url)
    if request.status_code != 200:
        raise Exception(
            "GET request failed, "
            f"HTTP status code: {request.status_code}, "
            f"URL: {url}"
        )

    return request.text


def extract_json(html: str):
    match = re.findall(r'{.*}', html)

    if match is None:
        raise Exception('No valid JSON found')

    # no special logic needed, should be the last match
    # if something changes then these can be useful
    # <script id="landingPage-json-data" type="application/json">
    # <script id="webpack-bundle-page-data" type="application/json">
    result = match[len(match) - 1]
    return json.loads(result)


def main():
    BASE_URL = "https://www.humblebundle.com/"
    BUNDLES_URL = BASE_URL + 'bundles'

    raw_html = scrape(BUNDLES_URL)
    print(extract_json(raw_html))


if __name__ == "__main__":
    main()
