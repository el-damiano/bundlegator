package main

type HumbleBundleCategoryResp struct {
	Mosaic []struct {
		Products []struct {
			MachineName       string   `json:"machine_name"`
			ProductURL        string   `json:"product_url"`
			HoverHighlights   []string `json:"hover_highlights"`
			Author            string   `json:"author"`
			StartDateDatetime string   `json:"start_date|datetime"`
			EndDateDatetime   string   `json:"end_date|datetime"`
		} `json:"products"`
	} `json:"mosaic"`
}

type HumbleBundleAllResp struct {
	Data struct {
		Books    HumbleBundleCategoryResp `json:"books"`
		Games    HumbleBundleCategoryResp `json:"games"`
		Software HumbleBundleCategoryResp `json:"software"`
	} `json:"data"`
}

type HumbleBundleBundleResp struct {
	BundleData struct {
		MachineName    string `json:"machine_name"`
		Author         string `json:"author"`
		AtTimeDatetime string `json:"at_time|datetime"`
		BasicData      struct {
			EndTimeDatetime string `json:"end_time|datetime"`
			HumanName       string `json:"human_name"`
		} `json:"basic_data"`
		TierPricingData map[string]struct {
			PriceMoney struct {
				Currency string  `json:"currency"`
				Amount   float64 `json:"amount"`
			} `json:"price|money"`
		} `json:"tier_pricing_data"`
		TierItemData map[string]struct {
			Developers []struct {
				DeveloperName string `json:"developer-name"`
			} `json:"developers"`
			HumanName   string `json:"human_name"`
			MachineName string `json:"machine_name"`
			Publishers  []struct {
				PublisherName string `json:"publisher-name"`
				PublisherURL  string `json:"publisher-url"`
			} `json:"publishers"`
		} `json:"tier_item_data"`
	} `json:"bundleData"`
}

type FanaticalAllResp []struct {
	Name                string `json:"name"`
	Slug                string `json:"slug"`
	Type                string `json:"type"`
	AvailableValidFrom  int    `json:"available_valid_from"`
	AvailableValidUntil int    `json:"available_valid_until"`
	BundleCovers        []struct {
	} `json:"bundle_covers"`
}

type FanaticalBundleResp struct {
	Bundles []struct {
		Price struct {
			Eur float64 `json:"EUR"`
		} `json:"price"`
		Games []struct {
			Name       string   `json:"name"`
			Authors    []string `json:"authors"`
			Isbn       string   `json:"isbn"`
			Publishers []struct {
				Name string `json:"name"`
			} `json:"publishers"`
		}
	} `json:"bundles"`
	Products []struct {
		Authors []string `json:"authors"`
		Name    string   `json:"name"`
		Price   struct {
			Eur float64 `json:"EUR"`
		} `json:"price"`
		Publishers []string `json:"publishers"`
		Isbn       string   `json:"isbn"`
	} `json:"products"`
	Tiers []struct {
		Quantity int `json:"quantity"`
		Price    struct {
			Eur float64 `json:"EUR"`
		} `json:"price"`
	} `json:"tiers"`
}
