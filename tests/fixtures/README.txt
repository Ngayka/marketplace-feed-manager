Fixtures based on real Viatec XML fragments supplied by the user.

Files:
- viatec_video.xml: 3 real-style video surveillance offers
- viatec_network.xml: 3 real-style network/server offers
- viatec_intercom.xml: 3 real-style intercom/access-control offers
- empty_feed.xml: valid YML with zero offers
- invalid_feed.xml: intentionally malformed XML

Important edge cases included:
- offer without price and currencyId
- available=true and available=false
- CDATA descriptions
- HTML entities
- apostrophes and quotation marks
- vendor and param elements
- category parentId attributes
- UAH and USD currencies
