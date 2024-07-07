import re
import json
import requests


def get_html(function):
    def wrapper(source: str) -> dict:
        if source.startswith("file://"):
            with open(source[7:]) as file:
                return function(file.read())
        if source.startswith("https://"):
            request = requests.get(source)
            if request.status_code != 200:
                raise Exception(
                    "GET request failed, "
                    f"HTTP status code: {request.status_code}, "
                    f"URL: {source}"
                )

            return function(request.text)
        return function(source)
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
    BUNDLES_URL = BASE_URL + '/bundles'
    HTML_PATH = 'file://__pycache__/bundles.html'
    HTML_TEXT = """
<!doctype html>
<html lang="en" class="">
  <head>
    <title>Test Source</title>
</head>
  <body>
<script type="application/json">
  {"data": {"category": {"mosaic": [{"products": [{"product_url": "/baby"},{"product_url": "/bobo"}]}]}}}
</script>
  </body>
</html>
    """

    bundles = map(
        lambda url: BASE_URL + url,
        get_bundle_urls(HTML_PATH)
    )

    if bundles is None:
        exit()

    print('\n'.join(bundles))


if __name__ == "__main__":
    main()
