package main

import (
	"encoding/xml"
	"fmt"
	"html/template"
	"log"
	"strings"
)

type RSSChannel struct {
	Title       string    `xml:"title"`
	Link        string    `xml:"link"`
	Description string    `xml:"description"`
	Item        []RSSItem `xml:"item"`
}

type RSSItem struct {
	Title       string `xml:"title"`
	Link        string `xml:"link"`
	Description string `xml:"description"`
	Author      string `xml:"author"`
	PubDate     string `xml:"pubDate"`
}

type RSS struct {
	Channel RSSChannel `xml:"channel"`
}

func NewFeed(bundles map[string]Bundle) RSS {
	items := make([]RSSItem, len(bundles))
	_ = items
	count := 0
	for _, bundle := range bundles {
		items[count] = RSSItem{
			Title:       bundle.Title,
			Link:        bundle.Link,
			Description: description(bundle),
			Author:      bundle.Author,
			PubDate:     bundle.DateEarliest.String(),
		}
		count += 1
	}

	return RSS{
		Channel: RSSChannel{
			Title:       "Bundlegator",
			Link:        "https://www.humblebundle.com/bundles",
			Description: "Bundles that got scraped from various websites",
			Item:        items,
		},
	}
}

// func (item *RSSItem) MarshalXML(e *Encoder, start StartElement) error {}

func description(bundle Bundle) string {

	tmpl, err := template.New("bundle item").Parse(`<br><table>
	<tr>
		<th>Name</th>
		<th>{{.Name}}</th>
	</tr>
	<tr>
		<th>Author</th>
		<th>{{.Author}}</th>
	</tr>
	<tr>
		<th>Publisher</th>
		<th>{{.Publisher}}</th>
	</tr>
	<tr>
		<th>ISBN</th>
		<th>{{.ISBN}}</th>
	</tr>
</table>`)
	if err != nil {
		return fmt.Sprintf("Error creating template %v", err)
	}

	var out strings.Builder
	_, err = out.Write([]byte(bundle.Description + "<br>"))
	if err != nil {
		return fmt.Sprintf("Error generating description %v", err)
	}

	for _, item := range bundle.Items {
		err = tmpl.Execute(&out, item)
		if err != nil {
			return fmt.Sprintf("Error generating description %v", err)
		}
	}

	return out.String()
}

func (feed *RSS) Print() {
	foo, err := xml.Marshal(feed)
	if err != nil {
		log.Fatal(err)
	}
	// TODO: avoid using this hack, might require xml.MarshalXML tho
	bar := strings.Replace(fmt.Sprintf("%s", foo), "<RSS>", "<rss version=\"2.0\">", 1)
	fmt.Println(bar)
}
