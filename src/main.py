from bundle_utils import Source, get_bundle_urls


def main():
    bundle_urls = get_bundle_urls(Source.HUMBLE_BUNDLE)

    bundles_by_source = {'HumbleBundle': bundle_urls}
    for _, v in bundles_by_source.items():
        print(v)

    print('\n'.join(bundle_urls))


if __name__ == "__main__":
    main()
