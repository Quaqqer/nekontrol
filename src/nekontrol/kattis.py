import configparser
from os import path

import requests

from .language import Language

_HEADERS = {"User-Agent": "nekontrol"}


def submit(lang: Language, problem: str):
    files = lang.submit_files

    try:
        with open(path.expanduser("~/.kattisrc"), "r") as kattisrc:
            cfg = configparser.ConfigParser()
            cfg.read(kattisrc.read())

            username = cfg.get("user", "username")
            token = cfg.get("user", "token")

            loginurl = cfg.get("kattis", "loginurl")
            submissionurl = cfg.get("kattis", "submissionurl")
            submissionsurl = cfg.get("kattis", "submissionsurl")

            login_r = requests.post(
                loginurl, data={"user": username, "token": token}, headers=_HEADERS
            )
            assert login_r.ok

            data = {"submit": "true",
                    "submit_ctr": 2,
                    "language": lang.kattis_name,
                    "mainclass": }

    except FileNotFoundError:
        print(
            "Could not read ~/.kattisrc,"
            + " make sure to download it from <kattis>/download/kattisrc"
        )
