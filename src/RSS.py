from Bundle import Bundle, BundleItem


class Channel:

    def __init__(self, bundles: list[Bundle]) -> None:
        self.title = "Various Bundles"
        self.link = "https://www.humblebundle.com/bundles"
        self.description = "Bundles that got scraped from various websites"
        self.items = list(map(
            lambda bundle: ChannelItem(bundle),
            bundles,
        ))

    def __repr__(self) -> str:
        return f"""<rss version="2.0">
    <channel>
    <title>{self.title}</title>
    <link>{self.link}</link>
    <description>{self.description}</description>
    {[item for item in self.items]}
    </channel>
</rss> """


class ChannelItem:

    def __init__(self, bundle: Bundle) -> None:
        self.title = bundle.name
        self.link = bundle.url

        self.author = None
        self.pubDate = None
        self.description = bundle.items

    def __repr__(self) -> str:
        return f"""
<item>
    <title>{self.title}</title>
    <link>{self.link}</link>
    <guid>{self.link}</guid>
    <pubDate>{self.pubDate}</pubDate>
    <description><![CDATA[
        <br>
        {self.description}
        <br>
    ]]></description>
</item>
        """
