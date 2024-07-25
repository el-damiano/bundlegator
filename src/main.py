#!/bin/env python3
# main.sh got deprecated in favor of running this program from within Newsboat

from bundle_utils import Source, get_bundles
from Bundle import Bundle
from RSS import Channel


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
