import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin


URL = "https://www.cricbuzz.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def scrape_matches():

    matches = []

    try:
        response = requests.get(
            URL,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.select("div.shadow.rounded-md.overflow-hidden")

        for card in cards:

            link = card.select_one(
                'a[href*="/live-cricket-scores/"]'
            )

            if not link:
                continue

            # Match name
            match_name = link.get("title", "").strip()

            if not match_name:
                continue

            match_name = match_name.rstrip()

            # Series information
            series_tag = link.select_one("span.text-xs")

            series = (
                series_tag.get_text(" ", strip=True)
                if series_tag else "N/A"
            )

            # Team names and scores
            team_rows = link.select(
                "div.flex.items-center.gap-4.justify-between"
            )

            team_data = []

            for row in team_rows:

                team_container = row.select_one(
                    "div.flex.items-center.gap-2"
                )

                team_name = "N/A"

                if team_container:
                    for span in team_container.find_all("span"):
                        name = span.get_text(" ", strip=True)

                        if name:
                            team_name = name
                            break

                # Score is a direct child span with w-1/2
                score = "N/A"

                for span in row.find_all("span", recursive=False):

                    if "w-1/2" in span.get("class", []):
                        score_text = span.get_text(" ", strip=True)

                        if score_text:
                            score = score_text

                        break

                team_data.append({
                    "team": team_name,
                    "score": score
                })

            # Assign team names and scores
            team1 = team_data[0] if len(team_data) > 0 else {
                "team": "N/A", "score": "N/A"
            }

            team2 = team_data[1] if len(team_data) > 1 else {
                "team": "N/A", "score": "N/A"
            }

            # Match status
            status = "N/A"

            for span in link.find_all("span", recursive=False):

                classes = span.get("class", [])

                status_classes = [
                    "text-cbLive",
                    "text-cbComplete",
                    "text-cbPreview"
                ]

                if any(name in status_classes for name in classes):

                    status = span.get_text(" ", strip=True)

                    if not status and "text-cbPreview" in classes:
                        status = "Upcoming (time not available)"

                    break

            # Match URL
            match_link = urljoin(URL, link.get("href", ""))

            match = {
                "Match": match_name,
                "Series": series,
                "Team 1": team1["team"],
                "Score 1": team1["score"],
                "Team 2": team2["team"],
                "Score 2": team2["score"],
                "Status": status,
                "Link": match_link
            }

            matches.append(match)

        return matches

    except requests.exceptions.Timeout:
        print("Error: Request timed out.")

    except requests.exceptions.ConnectionError:
        print("Error: Check your internet connection.")

    except requests.exceptions.HTTPError as error:
        print("HTTP Error:", error)

    except requests.exceptions.RequestException as error:
        print("Request Error:", error)

    except Exception as error:
        print("Unexpected Error:", error)

    return matches


def display_matches(matches):

    if not matches:
        print("No matches found.")
        return

    for index, match in enumerate(matches, start=1):

        print(f"\n{index}. {match['Match']}")
        print(f"   Series: {match['Series']}")
        print(f"   {match['Team 1']}: {match['Score 1']}")
        print(f"   {match['Team 2']}: {match['Score 2']}")
        print(f"   Status: {match['Status']}")
        print(f"   Link: {match['Link']}")

    print(f"\nTotal matches found: {len(matches)}")


def save_csv(matches):

    if not matches:
        print("No data available to save.")
        return

    fieldnames = [
        "Match",
        "Series",
        "Team 1",
        "Score 1",
        "Team 2",
        "Score 2",
        "Status",
        "Link"
    ]

    try:
        with open(
            "cricket_matches.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(matches)

        print("\nData successfully saved to cricket_matches.csv")

    except OSError as error:
        print("Error saving CSV:", error)


def main():

    print("Fetching Cricket Match Information...\n")

    matches = scrape_matches()

    display_matches(matches)

    save_csv(matches)


if __name__ == "__main__":
    main()
