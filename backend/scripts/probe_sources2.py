import json
import re

import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/html",
}


def main() -> None:
    r = httpx.get(
        "https://api.devfolio.co/api/hackathons?filter=open&page=1&limit=3",
        headers=HEADERS,
        follow_redirects=True,
        timeout=25,
    )
    print("devfolio", r.status_code)
    data = r.json()
    print("keys", data.keys() if isinstance(data, dict) else type(data))
    item = (data.get("result") or data.get("hackathons") or data)[0]
    print(json.dumps(item, indent=2)[:1800])

    # HackerEarth possible APIs
    for url in [
        "https://www.hackerearth.com/challenges/api/hackathon/",
        "https://www.hackerearth.com/AJAX/filter-challenges/?format=json&type=HACKATHON",
        "https://www.hackerearth.com/challenges/?format=json",
    ]:
        try:
            resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=20)
            print("he", resp.status_code, url, resp.headers.get("content-type", "")[:40])
            print(resp.text[:300].replace("\n", " "))
        except Exception as exc:  # noqa: BLE001
            print("he ERR", url, exc)

    # MLH events.mlh.io listing?
    r3 = httpx.get(
        "https://events.mlh.io/events?per_page=5&page=1",
        headers=HEADERS,
        follow_redirects=True,
        timeout=25,
    )
    print("events.mlh", r3.status_code, r3.headers.get("content-type", "")[:40])
    print(r3.text[:400].replace("\n", " "))

    soup = BeautifulSoup(
        httpx.get(
            "https://mlh.io/seasons/2026/events",
            headers=HEADERS,
            follow_redirects=True,
            timeout=25,
        ).text,
        "html.parser",
    )
    # __NEXT_DATA__?
    nxt = soup.find("script", id="__NEXT_DATA__")
    print("next_data", bool(nxt), (len(nxt.string) if nxt and nxt.string else 0))
    if nxt and nxt.string:
        payload = json.loads(nxt.string)
        print("next keys", payload.keys())
        print(json.dumps(payload, indent=2)[:800])


if __name__ == "__main__":
    main()
