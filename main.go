package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

type Config struct {
	Blacklist    map[string]struct{}
	BlacklistDir string
	AppCacheDir  string
}

func (cfg *Config) blacklistLoad() error {
	cfg.Blacklist = make(map[string]struct{})

	cfg.BlacklistDir = cfg.AppCacheDir + "/blacklist.txt"
	blacklistFile, err := os.OpenFile(
		cfg.BlacklistDir,
		os.O_CREATE|os.O_APPEND|os.O_RDWR,
		0644,
	)
	if err != nil {
		return err
	}
	defer blacklistFile.Close()

	scanner := bufio.NewScanner(blacklistFile)
	for scanner.Scan() {
		cfg.Blacklist[scanner.Text()] = struct{}{}
	}

	err = scanner.Err()
	if err != nil {
		return err
	}
	return nil
}

func (cfg *Config) blacklistSave() error {
	err := os.Truncate(cfg.BlacklistDir, 0)
	if err != nil {
		return err
	}

	var keys []string
	for key := range cfg.Blacklist {
		keys = append(keys, key)
	}
	keysToSave := []byte(strings.Join(keys, "\n"))

	err = os.WriteFile(cfg.BlacklistDir, keysToSave, 0600)
	if err != nil {
		return err
	}

	return nil
}

type Bundle struct {
	Title        string
	Author       string
	Link         string
	DateEnd      time.Time
	DateEarliest time.Time
	Description  string
	Items        []BundleItem
}

// getting data from Google Books API was a waste of time due to how unreliable
// the results were. The problem is that HumbleBundle might choose to include
// abbreviations in the author/publisher/title fields, like "book name, 5ed".
// Fanatical already includes the ISBN so it's fine.
// If you know how to approach this problem, feel free to make a PR :)
type BundleItem struct {
	Name      string
	Author    string
	Publisher string
	ISBN      string
}

type SourceName string

const (
	HumbleBundle SourceName = "HumbleBundle"
	Fanatical    SourceName = "Fanatical"
)

type Source struct {
	Name      SourceName
	BaseURL   string
	BundleURL string
}

func dataFetch(client *http.Client, url string, sourceName SourceName) ([]byte, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "Googlebot/2.1")

	res, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	data, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	if sourceName == HumbleBundle {
		// HumbleBundle embeds the JSON in the HTML, so we extract it by
		// grabbing what's in the last <script type="application/json"> element
		separatorFirst := []byte("application/json\">\n")
		separatorEnd := []byte("\n</script>")

		jsonStartIdx := bytes.LastIndex(data, separatorFirst)
		dataCut := data[jsonStartIdx+len(separatorFirst):]
		jsonEndIdx := bytes.LastIndex(dataCut, separatorEnd)
		data = dataCut[:jsonEndIdx]
	}

	return data, nil
}

func bundlesGet(sources []Source, blacklist map[string]struct{}) map[string]Bundle {
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	bundles := map[string]Bundle{}
	for _, source := range sources {

		data, err := dataFetch(client, source.BundleURL, source.Name)
		if err != nil {
			continue
		}

		if source.Name == HumbleBundle {
			var Resp HumbleBundleAllResp
			err = json.Unmarshal(data, &Resp)
			if err != nil {
				continue
			}

			categories := []HumbleBundleCategoryResp{
				Resp.Data.Books,
				Resp.Data.Games,
				Resp.Data.Software,
			}

			for _, category := range categories {
				for _, mosaic := range category.Mosaic {
					for _, product := range mosaic.Products {
						bundleURL := source.BaseURL + product.ProductURL

						_, ok := blacklist[bundleURL]
						if ok {
							continue
						}

						data, err := dataFetch(client, bundleURL, source.Name)
						if err != nil {
							continue
						}

						var Resp HumbleBundleBundleResp
						err = json.Unmarshal(data, &Resp)
						if err != nil {
							continue
						}

						count := 0
						blacklist[bundleURL] = struct{}{}
						bundleItems := make([]BundleItem, len(Resp.BundleData.TierItemData))
						for _, item := range Resp.BundleData.TierItemData {

							developers := make([]string, len(item.Developers))
							for i, dev := range item.Developers {
								developers[i] = dev.DeveloperName
							}
							publishers := make([]string, len(item.Publishers))
							for i, pub := range item.Publishers {
								publishers[i] = pub.PublisherName
							}

							bundle := BundleItem{
								Name:      item.HumanName,
								Author:    strings.Join(developers, ", "),
								Publisher: strings.Join(publishers, ", "),
								ISBN:      "",
							}
							bundleItems[count] = bundle
							count += 1
						}

						dateEnd, err := time.Parse("2006-01-02T15:04:05", Resp.BundleData.BasicData.EndTimeDatetime)
						if err != nil {
							dateEnd = time.Time{}
						}
						dateEarliest, err := time.Parse("2006-01-02T15:04:05", Resp.BundleData.AtTimeDatetime)
						if err != nil {
							dateEarliest = time.Time{}
						}

						price := 0.0
						for _, pricing := range Resp.BundleData.TierPricingData {
							if pricing.PriceMoney.Amount > price {
								price = pricing.PriceMoney.Amount
							}
						}

						bundles["humblebundle-"+product.MachineName] = Bundle{
							Title:        Resp.BundleData.BasicData.HumanName,
							Author:       "HumbleBundle",
							Link:         fmt.Sprintf("%s?%d", bundleURL, dateEnd.Unix()), // Unix timestamp for unique URL
							DateEnd:      dateEnd,
							DateEarliest: dateEarliest,
							Description:  fmt.Sprintf("Bundle for %0.2f until %s", price, dateEnd),
							Items:        bundleItems,
						}
					}
				}
			}

		} else if source.Name == Fanatical {
			var Resp FanaticalAllResp
			err = json.Unmarshal(data, &Resp)
			if err != nil {
				continue
			}

			for _, r := range Resp {
				bundleURL := fmt.Sprintf("%s/en/%s/%s", source.BaseURL, r.Type, r.Slug)
				_, ok := blacklist[bundleURL]
				if ok {
					continue
				}

				// can be either "pick-a-mix" or
				// "products-group" which is the same as "bundle"
				typeAPI := r.Type
				if r.Type == "bundle" {
					typeAPI = "products-group"
				}
				bundleApiURL := fmt.Sprintf("%s/api/%s/%s/en", source.BaseURL, typeAPI, r.Slug)

				data, err := dataFetch(client, bundleApiURL, source.Name)
				if err != nil {
					log.Fatalf("error fetching fanatical bundle: %v", err)
					continue
				}

				var Resp FanaticalBundleResp
				err = json.Unmarshal(data, &Resp)
				if err != nil {
					log.Fatalf("Error unmarshaling json data: %v", err)
					continue
				}

				var bundleItems []BundleItem
				blacklist[bundleURL] = struct{}{}

				price := 0.0 // price logic will differ between normal and pick-and-mix bundles
				for _, bundle := range Resp.Bundles {
					if bundle.Price.Eur > price {
						price = bundle.Price.Eur
					}
					for _, game := range bundle.Games {

						publishers := make([]string, len(game.Publishers))
						for i, pub := range game.Publishers {
							publishers[i] = pub.Name
						}

						bundleItems = append(bundleItems, BundleItem{
							Name:      game.Name,
							Author:    strings.Join(game.Authors, ", "),
							Publisher: strings.Join(publishers, ", "),
							ISBN:      game.Isbn,
						})
					}
				}

				for _, product := range Resp.Products {
					if product.Price.Eur > price {
						price = product.Price.Eur
					}

					bundleItems = append(bundleItems, BundleItem{
						Name:      product.Name,
						Author:    strings.Join(product.Authors, ", "),
						Publisher: strings.Join(product.Publishers, ", "),
					})
				}

				dateEnd := time.Unix(int64(r.AvailableValidUntil), 0)
				dateEarliest := time.Unix(int64(r.AvailableValidFrom), 0)
				price /= 100 // Fanatical pricing puts main currency and subunit before the decimal point, so we move it 2 spaces to the left

				description := ""
				if r.Type == "bundle" {
					description = fmt.Sprintf(
						"%s with %d items for %0.2f until %s\n",
						r.Type,
						len(bundleItems),
						price,
						dateEnd)
				} else if r.Type == "pick-and-mix" {
					for _, tier := range Resp.Tiers {
						description = fmt.Sprintf(
							"%s with %d/%d items for %0.2f avg until %s\n",
							r.Type,
							tier.Quantity,
							len(bundleItems),
							price,
							dateEnd)
					}
				}

				bundles["fanatical-"+r.Slug] = Bundle{
					Title:        r.Name,
					Author:       "Fanatical",
					Link:         fmt.Sprintf("%s?%d", bundleURL, r.AvailableValidUntil), // Unix timestamp for unique URL
					DateEnd:      dateEnd,
					DateEarliest: dateEarliest,
					Description:  description,
					Items:        bundleItems,
				}

			}
		}
	}

	return bundles
}

func main() {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		log.Fatalf("Error getting user home directory %v", err)
	}

	cfg := &Config{
		AppCacheDir: homeDir + "/.cache/bundlegator",
	}

	_, err = os.Stat(cfg.AppCacheDir)
	if err != nil && os.IsNotExist(err) {
		err = os.Mkdir(cfg.AppCacheDir, 0700)
		if err != nil {
			log.Fatalf("Error creating dir %v", err)
		}
	}

	err = cfg.blacklistLoad()
	if err != nil {
		log.Fatalf("Error loading blacklist %v", err)
	}

	sources := []Source{{
		Name:      HumbleBundle,
		BaseURL:   "https://www.humblebundle.com",
		BundleURL: "https://www.humblebundle.com/bundles",
	}, {
		Name:      Fanatical,
		BaseURL:   "https://www.fanatical.com",
		BundleURL: "https://www.fanatical.com/api/algolia/bundles?altRank=false",
	}}

	bundles := bundlesGet(sources, cfg.Blacklist)

	err = cfg.blacklistSave()
	if err != nil {
		log.Fatalf("Error saving blacklist %v", err)
	}

	feed := NewFeed(bundles)
	feed.Print()
}
