import unittest
from Bundle import Source
from bundle_utils import extract_json, get_bundles


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

    def test_get_bundle(self):
        """
        Weakly test the connection to ``Source`` and validate data retrieval. Will fail if any ``Source`` is unreachable. It's fine :)
        """
        bundles = list()

        bundles += get_bundles(Source.HUMBLE_BUNDLE)
        self.assertGreater(len(bundles), 0)
        length = len(bundles)

        bundles += get_bundles(Source.HUMBLE_BUNDLE)
        self.assertEqual(len(bundles), length)

        bundles += get_bundles(Source.FANATICAL)
        self.assertGreater(len(bundles), length)
        length = len(bundles)

        bundles += get_bundles("")
        self.assertEqual(len(bundles), length)


if __name__ == "__main__":
    unittest.main()
