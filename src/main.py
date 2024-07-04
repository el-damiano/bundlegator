import re
import json
import requests


def get_html(function):
    def wrapper(url: str) -> str:
        request = requests.get(url)
        if request.status_code != 200:
            raise Exception(
                "GET request failed, "
                f"HTTP status code: {request.status_code}, "
                f"URL: {url}"
            )

        return function(request.text)
    return wrapper


@get_html
def extract_json(source: str):
    match = re.findall(r'{.*}', source)

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

    print(extract_json(BUNDLES_URL))


if __name__ == "__main__":
    main()
