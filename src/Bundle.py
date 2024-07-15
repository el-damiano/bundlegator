class Bundle:

    def __init__(self, document: dict) -> None:
        self.name = document["name"]
        self.url = None
        self.start_date = None
        self.end_date = None
        self.charity = None
        self.total_price = None
        self.contents = None  # dict item_by_tier
