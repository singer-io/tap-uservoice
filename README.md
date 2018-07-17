# tap-uservoice

Author: Connor McArthur (connor@fishtownanalytics.com)

This is a [Singer](http://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

It:

- Generates a catalog of available data in Uservoice
- Extracts the following resources:
  - [Categories](https://developer.uservoice.com/docs/api/v2/reference/#/Category)
  - [Comments](https://developer.uservoice.com/docs/api/v2/reference/#/Comment)
  - [External Accounts](https://developer.uservoice.com/docs/api/v2/reference/#/ExternalAccount)
  - [External Users](https://developer.uservoice.com/docs/api/v2/reference/#/ExternalUser)
  - [Feature Statuses](https://developer.uservoice.com/docs/api/v2/reference/#/FeatureStatus)
  - [Features](https://developer.uservoice.com/docs/api/v2/reference/#/Feature)
  - [Forums](https://developer.uservoice.com/docs/api/v2/reference/#/Forum)
  - [Labels](https://developer.uservoice.com/docs/api/v2/reference/#/Label)
  - [NPS Ratings](https://developer.uservoice.com/docs/api/v2/reference/#/NPSRating)
  - [Product Areas](https://developer.uservoice.com/docs/api/v2/reference/#/ProductArea)
  - [Requests](https://developer.uservoice.com/docs/api/v2/reference/#/Feedback)
  - [Segmented Values](https://developer.uservoice.com/docs/api/v2/reference/#/SegmentedValue)
  - [Segments](https://developer.uservoice.com/docs/api/v2/reference/#/Segment)
  - [Status Updates](https://developer.uservoice.com/docs/api/v2/reference/#/StatusUpdate)
  - [Statuses](https://developer.uservoice.com/docs/api/v2/reference/#/Status)
  - [Suggestions](https://developer.uservoice.com/docs/api/v2/reference/#/Suggestion)
  - [Supporters](https://developer.uservoice.com/docs/api/v2/reference/#/Supporter)
  - [Teams](https://developer.uservoice.com/docs/api/v2/reference/#/Team)
  - [Users](https://developer.uservoice.com/docs/api/v2/reference/#/User)

### Quick Start

1. Install

```bash
git clone git@github.com:fishtown-analytics/tap-uservoice.git
cd tap-uservoice
pip install .
```

2. Get credentials from Uservoice. You'll need your:

- Uservoice subdomain,
- and a client ID and secret. See Uservoice's [instructions on how to generate these](https://developer.uservoice.com/docs/api/v2/getting-started/).

3. Create the config file.

There is a template you can use at `config.json.example`, just copy it to `config.json` in the repo root and insert your client ID and secret.

4. Run the application to generate a catalog.

```bash
tap-uservoice -c config.json --discover > catalog.json
```

5. Select the tables you'd like to replicate

Step 4 created a file called `catalog.json` that specifies all the available endpoints and fields. You'll need to open the file and select the ones you'd like to replicate. See the [Singer guide on Catalog Format](https://github.com/singer-io/getting-started/blob/c3de2a10e10164689ddd6f24fee7289184682c1f/BEST_PRACTICES.md#catalog-format) for more information on how tables are selected.

6. Run it!

```bash
tap-uservoice -c config.json --properties catalog.json
```

---

Copyright &copy; 2018 Stitch
