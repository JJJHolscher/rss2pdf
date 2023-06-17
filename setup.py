#! /usr/bin/env python3

import sys
import tomllib
from distutils.core import setup
from pathlib import Path

import __main__
import tomli_w


def init_pyproject(pp):
    name = Path(__main__.__file__).parent.name
    pp["name"] = name
    pp["version"] = "0.0.0"
    pp["url"] = pp["authors"][0]["github"] + f"/{name}"
    return pp


if __name__ == "__main__":
    with open("pyproject.toml", "rb+") as f:
        pp = tomllib.load(f)

        if pp["name"] == "":
            pp = init_pyproject(pp)
            tomli_w.dump(pp, f)

        elif "--bump" in sys.argv:
            major, minor, patch = [int(i) for i in pp["version"].split(".")]
            pp["version"] = f"{major}.{minor}.{patch + 1}"
            tomli_w.dump(pp, f)

    setup(
        name=pp["name"],
        version=pp["version"],
        author=pp["authors"][0]["name"],
        author_email=pp["authors"][0]["email"],
        url=pp["url"],
        description=pp["abstract"],
        long_description=pp["description"],
        long_description_content_type="text/markdown",
        license=pp["license"],
        packages=[pp["name"]],
        # install_requires=[],
    )
