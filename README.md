# README

Download all links from an rss feed into a pdf.

From the CLI:

```sh
python -m rss2pdf --rss.urls '["https://scottaaronson.blog/?feed=rss2"]'
```

Or by editing the config.toml shipped with this package.
You can find its location with.

```sh
python -m rss2pdf --help
```

rss2pdf will keep track of entries already downloaded and only download unseen entries.

## install

rss2pdf uses the `pdfkit` package, which requires [wkhtmltopdf](https://wkhtmltopdf.org/) which should be available for all platforms.

```sh
pip install rss2pdf
```
