#! /usr/bin/env python3
# vim:fenc=utf-8

"""

"""

from pathlib import Path
from urllib.parse import urlparse

import feedparser
import pdfkit
from argtoml import ArgumentParser, parse_args
from pypdf import PdfMerger


def get_title(rss):
    if "title" in rss.feed:
        return rss.feed.title
    else:
        return urlparse(rss.feed.link).netloc


def update(url: str, dir: Path, archive_dir: Path, temp_pdfs: Path, new: bool = False):
    rss = feedparser.parse(url)
    title = get_title(rss)
    pdf_path = dir / f"{title}.pdf"
    archive_path = archive_dir / f"{title}.txt"
    merger = PdfMerger()

    # Read the archive file.
    if pdf_path.exists():
        if not archive_path.exists():
            return print(f"{pdf_path} found but not {archive_path}, skipping")
        print("updating", pdf_path)
        with open(archive_path) as f:
            archive = {line.strip() for line in f.readlines()}
        merger.append(pdf_path)
    elif not new:
        return print(f'No pdf found at "{pdf_path}". Specify --new to make a new one')
    else:
        print("creating", pdf_path)
        archive_dir.mkdir(parents=True, exist_ok=True)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        archive = set()

    # Create the tempororary pdf directory if it doesn't already exist.
    temp_pdfs.mkdir(parents=True, exist_ok=True)

    # Add every rss entry not already in the pdf to the back of the pdf.
    entries = list(reversed(rss.entries))
    updated = False
    for i, entry in enumerate(entries):
        link = entry.link
        if link in archive:
            continue
        updated = True
        print(f"[{i+1}/{len(entries)}] {link}")

        temp_pdf = str(temp_pdfs / f"{i}.pdf")
        pdfkit.from_url(link, temp_pdf)
        merger.append(temp_pdf)
        archive.add(link)

    if updated:
        # Write the pdf and archive file.
        print("writing ", pdf_path)
        merger.write(pdf_path)
        with open(archive_path, "w") as f:
            f.write("\n".join(archive))
        # clean the temporary pdf directory
        for pdf in temp_pdfs.iterdir():
            pdf.unlink()


if __name__ == "__main__":
    ARGS = parse_args(description="Generate an epub from a RSS feed.", path=True)
    if ARGS.dev.debug:
        import debugpy

        debugpy.listen(5678)
        debugpy.wait_for_client()

    for url in ARGS.rss.urls:
        update(url, ARGS.out.dir, ARGS.out.archive, ARGS.out.temp_pdfs, ARGS.new)
