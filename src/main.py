#!/bin/env python3
# main.sh got deprecated in favor of running this program from within Newsboat

from bundle_utils import Source, get_bundles
from Bundle import Bundle
from RSS import Channel

HUMBLE_BUNDLE_BOOKS = [
    {
        "whatever": "won't be used",
        "goo goo": "gaa gaa",
        "bundleData": {
            "author": "epic book authors",
            "basic_data": {
                "human_name": "my fav books",
                "end_time_datetime": "2024-07-21 13:37",
                "msrp|money": {"currency": "EUR", "amount": 69.420}
            },
            "tier_item_data": {
                "automatetheboringstuffwithpython": {
                    "publishers": [
                        {
                            "publisher-name": "NoStarch",
                            "publisher-url": "https://nostarch.com/"
                        }
                    ],
                    "min_price|money": {
                        "currency": "EUR",
                        "amount": 0.1
                    },
                    "developers": [
                        {
                            "developer-name": "El Seigart",
                        },
                        {
                            "developer-name": None,
                        },
                        {}
                    ],
                    "platforms_and_oses": {
                        "ebook": {"download": ["pdf", "epub", "mobi"]}
                    },
                    "human_name": "Automate the Boring Stuff with Python, 2nd Edition",
                },
                "Introduction to Algorithms, Fourth Edition": {
                    "publishers": [
                        {
                            "publisher-name": "The MIT Press",
                            "publisher-url": "https://mitpress.mit.edu/"
                        }
                    ],
                    "min_price|money": {
                        "currency": "EUR",
                        "amount": 0.2
                    },
                    "developers": [
                        {
                            "developer-name": "Thomas,H.,Cormen, Charles,E.,Leiserson, Ronald L. Rivest, Clifford Stein",
                        },
                        {
                            "developer-name": None,
                        },
                        {}
                    ],
                    "platforms_and_oses": {
                        "ebook": {"download": ["pdf"]}
                    },
                    "human_name": "Introduction to Algorithms, 4th Edition",
                }
            },
            "page_url": "my library",
        },
        "at_time|datetime": "2024-07-03 04:20",
        69: 420
    },
    {}
]


def main():

    bundles = list()
    bundles += list(map(
        lambda bundle: Bundle(Source.HUMBLE_BUNDLE, bundle),
        get_bundles(Source.HUMBLE_BUNDLE)
    ))
    bundles += list(map(
        lambda bundle: Bundle(Source.FANATICAL, bundle),
        get_bundles(Source.FANATICAL)
    ))

    rss_feed = Channel(bundles)
    print(rss_feed)


if __name__ == "__main__":
    main()
