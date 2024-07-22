import unittest
from Bundle import Bundle
from bundle_utils import Source


class TestBundleUtils(unittest.TestCase):

    HUMBLE_BUNDLE_GAMES = [
        {
            "whatever": "won't be used",
            "goo goo": "gaa gaa",
            "bundleData": {
                "author": "epic game authors",
                "basic_data": {
                    "human_name": "my fav games",
                    "end_time_datetime": "2024-07-21 13:37",
                    "msrp|money": {
                        "currency": "EUR",
                        "amount": 69.420
                    }
                },
                "tier_item_data": {
                    "eldenring": {
                        "publishers": [
                            {
                                "publisher-name": "BANDAI NAMCO",
                                "publisher-url": "https://en.bandainamcoent.eu/"
                            }
                        ],
                        "min_price|money": {
                            "currency": "EUR",
                            "amount": 0.1
                        },
                        "developers": [
                            {
                                "developer-name": "FromSoftware",
                                "developer-url": "https://www.fromsoftware.jp/ww/"
                            }
                        ],
                        "platforms_and_oses": {
                            "game": {
                                "steam": [
                                    "windows"
                                ]
                            }
                        },
                        "human_name": "Elden Ring",
                    },
                    "drg": {
                        "publishers": [],
                        "min_price|money": {
                            "currency": "EUR",
                            "amount": "WE'RE RICH"
                        },
                        "developers": [
                            {
                                "developer-name": "FOR ROCK AND STONE",
                                "developer-url": "https://rock.eu/"
                            }
                        ],
                        "platforms_and_oses": {
                            "game": {
                                "steam": [
                                    "windows"
                                ]
                            }
                        },
                        "human_name": "Deep Rock Galactic",
                    },
                    "minecraft": {
                        "publishers": [],
                        "min_price|money": {},
                        "developers": [],
                        "platforms_and_oses": {},
                        "human_name": None,
                    },
                    "Monster Hunter World": {}
                },
                "page_url": "my gaming library",
            },
            "at_time|datetime": "2024-07-03 04:20",
            69: 420
        },
        {}
    ]

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

    def test_humble_bundle_bundles(self):

        book_bundles = list(map(
            lambda bundle: Bundle(Source.HUMBLE_BUNDLE, bundle),
            self.HUMBLE_BUNDLE_BOOKS
        ))

        self.assertTrue(book_bundles)
        self.assertEqual(len(book_bundles), 2)

        self.assertEqual(book_bundles[0].name, "my fav books")
        self.assertEqual(book_bundles[1].name, None)
        self.assertEqual(book_bundles[0].authors, "epic book authors")
        self.assertEqual(book_bundles[1].authors, None)
        self.assertEqual(book_bundles[0].url, "https://www.humblebundle.com/my library")
        self.assertEqual(book_bundles[1].url, "https://www.humblebundle.com/bundles")
        self.assertEqual(book_bundles[0].start_date, "2024-07-03 04:20")
        self.assertEqual(book_bundles[1].start_date, None)
        self.assertEqual(book_bundles[0].end_date, "2024-07-21 13:37")
        self.assertEqual(book_bundles[1].end_date, None)
        self.assertEqual(book_bundles[0].total_price, ['EUR', 69.42])
        self.assertEqual(book_bundles[1].total_price, None)

        self.assertTrue(book_bundles[0].items)
        self.assertFalse(book_bundles[1].items)

        items = book_bundles[0].items
        bundle_one_tiers = items.keys()
        bundle_one_items = list(items.values())
        self.assertEqual(bundle_one_tiers, {0.1, 0.2})

        book_one = bundle_one_items[0][0]
        self.assertEqual(book_one.name, 'Automate the Boring Stuff with Python, 2nd Edition')
        self.assertEqual(book_one.authors, ['El Seigart', None, None])
        self.assertEqual(book_one.publisher, ['NoStarch'])
        self.assertEqual(book_one.platforms, {'ebook': {'download': ['pdf', 'epub', 'mobi']}})
        self.assertTrue(book_one.isbn)
        self.assertTrue(book_one.release_date)

        book_two = bundle_one_items[1][0]
        self.assertEqual(book_two.name, 'Introduction to Algorithms, 4th Edition')
        self.assertEqual(book_two.authors, ['Thomas,H.,Cormen, Charles,E.,Leiserson, Ronald L. Rivest, Clifford Stein', None, None])
        self.assertEqual(book_two.publisher, ['The MIT Press'])
        self.assertEqual(book_two.platforms, {'ebook': {'download': ['pdf']}})
        self.assertTrue(book_two.isbn)
        self.assertTrue(book_two.release_date)

        game_bundles = list(map(
            lambda bundle: Bundle(Source.HUMBLE_BUNDLE, bundle),
            self.HUMBLE_BUNDLE_GAMES
        ))

        self.assertTrue(game_bundles)
        self.assertEqual(len(game_bundles), 2)

        self.assertEqual(game_bundles[0].name, "my fav games")
        self.assertEqual(game_bundles[1].name, None)
        self.assertEqual(game_bundles[0].authors, "epic game authors")
        self.assertEqual(game_bundles[1].authors, None)
        self.assertEqual(game_bundles[0].url, "https://www.humblebundle.com/my gaming library")
        self.assertEqual(game_bundles[1].url, "https://www.humblebundle.com/bundles")
        self.assertEqual(game_bundles[0].start_date, "2024-07-03 04:20")
        self.assertEqual(game_bundles[1].start_date, None)
        self.assertEqual(game_bundles[0].end_date, "2024-07-21 13:37")
        self.assertEqual(game_bundles[1].end_date, None)
        self.assertEqual(game_bundles[0].total_price, ['EUR', 69.42])
        self.assertEqual(game_bundles[1].total_price, None)

        self.assertTrue(game_bundles[0].items)
        self.assertFalse(game_bundles[1].items)

        items = game_bundles[0].items
        bundle_one_tiers = items.keys()
        bundle_one_items = list(items.values())
        self.assertEqual(bundle_one_tiers, {0.1, "WE'RE RICH", 'Other'})

        book_one = bundle_one_items[0][0]
        self.assertEqual(book_one.name, 'Elden Ring')
        self.assertEqual(book_one.authors, ['FromSoftware'])
        self.assertEqual(book_one.publisher, ['BANDAI NAMCO'])
        self.assertEqual(book_one.platforms, {'game': {'steam': ['windows']}})
        self.assertFalse(book_one.isbn)
        self.assertFalse(book_one.release_date)

        book_two = bundle_one_items[1][0]
        self.assertEqual(book_two.name, 'Deep Rock Galactic')
        self.assertEqual(book_two.authors, ['FOR ROCK AND STONE'])
        self.assertEqual(book_two.publisher, None)
        self.assertEqual(book_two.platforms, {'game': {'steam': ['windows']}})
        self.assertFalse(book_two.isbn)
        self.assertFalse(book_two.release_date)
