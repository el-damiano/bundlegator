import unittest
from bundle_utils import (
    Source,
    get_html,
    extract_json,
    get_bundle_urls
)


class TestBundleUtils(unittest.TestCase):
    def test_extract_json(self):
        text_empty = ""
        text_without_json = "69420"  # this will be a valid json, but honestly idc since it'll fail to extract any useful info
        text_html = """
        <!doctype html>
        <html lang="en" class="">
          <head>
            <title>Test Source</title>
        </head>
          <body>
        <script type="application/json">
          {"data": {"category": {"mosaic": [{"products": [{"product_url": "/googoo"},{"product_url": "/gaagaa"}]}]}}}
        </script>
          </body>
        </html>
        """
        text_json = '{"data": {"category": {"mosaic": [{"products": [{"product_url": "/googoo"}, {"product_url": "/gaagaa"}]}]}}}'

        expected_json = dict({"data": {"category": {"mosaic": [
            {"products": [
                {"product_url": "/googoo"},
                {"product_url": "/gaagaa"}
            ]}
        ]}}})

        with self.assertRaises((ValueError, IndexError, TypeError)):
            extract_json(text_empty)

        self.assertEqual(expected_json, extract_json(text_html))
        self.assertEqual(expected_json, extract_json(text_json))
        self.assertNotEqual(expected_json, extract_json(text_without_json))


if __name__ == "__main__":
    unittest.main()
