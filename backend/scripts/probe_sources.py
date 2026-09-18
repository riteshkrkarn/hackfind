import json

import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}


def main() -> None:
    r = httpx.get(
        "https://devpost.com/api/hackathons?status[]=upcoming&status[]=open&per_page=3",
        headers=HEADERS,
        follow_redirects=True,
        timeout=25,
    )
    data = r.json()
    print("devpost keys", list(data.keys()))
    print(json.dumps(data["hackathons"][0], indent=2)[:1500])
    print("devpost count", len(data["hackathons"]))

    for year in (2025, 2026):
        url = f"https://mlh.io/seasons/{year}/events"
        r2 = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=25)
        print("mlh", year, r2.status_code, len(r2.text))
        soup = BeautifulSoup(r2.text, "html.parser")
        classes = sorted(
            {
                c
                for tag in soup.find_all(True)
                for c in (tag.get("class") or [])
                if "event" in c.lower()
            }
        )
        print(" mlh classes", classes[:30])
        event_links = []
        for a in soup.select("a[href]"):
            href = a.get("href") or ""
            text = a.get_text(" ", strip=True)
            if "/events/" in href or "hackathon" in text.lower():
                event_links.append((text[:60], href[:120]))
        print(" mlh sample links", event_links[:12])

    for label, url in [
        ("devfolio", "https://api.devfolio.co/api/hackathons?filter=all&page=1&limit=5"),
        ("devfolio2", "https://devfolio.co/api/hackathons"),
        ("he", "https://www.hackerearth.com/challenges/hackathon/"),
    ]:
        try:
            resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=25)
            print(label, resp.status_code, resp.headers.get("content-type", "")[:40])
            print(resp.text[:350].replace("\n", " "))
        except Exception as exc:  # noqa: BLE001
            print(label, "ERR", exc)


if __name__ == "__main__":
    main()
