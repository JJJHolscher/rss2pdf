#! /usr/bin/env python3
# vim:fenc=utf-8

"""

"""

from pathlib import Path
from typing import List
from urllib.parse import urlparse

import debugpy
import feedparser
import pdfkit
from argtoml import parse_args
from pypdf import PdfMerger


def string_for_os(string):
    def safe_char(c):
        return c.isalnum() or c in {".", "-", "_", " "}

    return "".join(c for c in string if safe_char(c))


def get_feed_title(rss):
    title = ""
    if "title" in rss.feed:
        title = rss.feed.title
    else:
        title = urlparse(rss.feed.link).netloc
    return string_for_os(title)


def get_chapter_title(rss_entry):
    title = ""
    if "title" in rss_entry:
        title = rss_entry.title
    else:
        title = urlparse(rss_entry.link).path
    return string_for_os(title)


def update(url: str, folder: Path, archive_dir: Path, new: bool = False):
    rss = feedparser.parse(url)
    feed_title = get_feed_title(rss)
    archive_path = archive_dir / f"{feed_title}.txt"
    folder = folder / feed_title

    # Read the archive file.
    if folder.exists():
        if not archive_path.exists():
            return print(f"{folder} found but not {archive_path}, skipping")
        print("updating", folder)
        with open(archive_path) as f:
            archive = {line.strip() for line in f.readlines()}
    elif not new:
        return print(f'No dir found at "{folder}". Specify new to make a new one')
    else:
        print("creating", folder)
        archive_dir.mkdir(parents=True, exist_ok=True)
        folder.mkdir(parents=True, exist_ok=True)
        archive = set()

    # Download every rss entry into their own pdf.
    entries = list(rss.entries)
    updated = False
    with open(archive_path, "a") as archive_file:
        for i, entry in enumerate(entries):
            link = entry.link
            if link in archive:
                continue
            updated = True

            chapter_title = get_chapter_title(entry)
            pdf_path = folder / f"{chapter_title}.pdf"
            print(f"[{i+1}/{len(entries)}] {chapter_title}\t{link}")
            pdfkit.from_url(link, pdf_path)
            archive_file.write(link + "\n")

    return updated


def update_merge(
    url: str, folder: Path, archive_dir: Path, tmp_folder: Path, new: bool = False
):
    feed_title = get_feed_title(feedparser.parse(url))
    pdf_path = folder / f"{feed_title}.pdf"
    if not pdf_path.exists() and not new:
        return print(f'No pdf found at "{pdf_path}". Specify new to make a new one')

    tmp_folder = tmp_folder / feed_title
    tmp_folder.mkdir(parents=True, exist_ok=True)

    update(url, tmp_folder.parent, archive_dir, new=True)
    if len(list(tmp_folder.iterdir())) == 0:
        return False

    # Merge all pdfs found in the temporary folder into one.
    merger = PdfMerger()
    if pdf_path.exists():
        merger.append(pdf_path)

    for pdf in tmp_folder.iterdir():
        merger.append(pdf)
    print(f"Merging all downloaded pdfs to {pdf_path}.")
    merger.write(pdf_path)

    for pdf in tmp_folder.iterdir():
        pdf.unlink()
    return True


def download(
    urls: List[str],
    out_dir: Path,
    archive: Path,
    temp_dir: Path,
    new: bool,
    merge=False,
):
    if len(urls) == 0:
        print("no rss urls to check")

    for url in urls:
        if merge:
            update_merge(url, out_dir, archive, temp_dir, new)
        else:
            update(url, out_dir, archive, new)


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
