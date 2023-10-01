#! /usr/bin/env python3
# vim:fenc=utf-8

from argtoml import parse_args
import debugpy

from .dl import download

if __name__ == "__main__":
    ARGS = parse_args(description="Generate an epub from a RSS feed.")
    if ARGS.dev.debug:
        debugpy.listen(5678)
        debugpy.wait_for_client()

    download(
        ARGS.rss.urls,
        ARGS.out.dir,
        ARGS.out.archive,
        ARGS.out.temp_pdfs,
        ARGS.new,
        ARGS.merge,
    )
