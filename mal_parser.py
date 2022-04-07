import os
import sys
import time
import uuid
import urllib
from datetime import datetime
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup as bs

from variables import connection
from functions import get_info_by_rank


class AccessError(Exception):
    pass


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def to_dict(object: List[object], rank_by: str = "id") -> Dict:
    dict_ = {}

    print("Collecting database...")
    for anime in object:
        dict_[anime[rank_by]] = anime

    return dict_


def get_links(start: int = 0) -> List[str]:
    print("Finding last MAL Top Anime page...")

    i = 390
    pages_ = []
    while True:
        page = f"limit={50 * i}"

        try:
            urllib.request.urlopen(
                f"https://www.myanimelist.net/topanime.php?{page}"
            )
        except urllib.error.HTTPError as err:
            if err.code == 404:
                print(f"Last page = {50 * (i - 1)}")
                break

            raise AccessError("MAL is offline")
        else:
            i += 1

    print(f"Last page = {i}")
    for j in range(start, i):
        page = f"limit={j * 50}"
        pages_.append(f"https://www.myanimelist.net/topanime.php?{page}")

    return pages_


def get_html(link: str) -> str:
    tries = 0

    while True:
        try:
            if tries >= 60:
                raise AccessError("Failed 60 retries.")
            html = urllib.request.urlopen(link)
        except urllib.request.HTTPError:
            tries += 1
            print("\nForbidden access... retrying")
            time.sleep(29)
        else:
            break

    return html.read().decode()


def wipe_remaining(cursor: object, remaining: Dict) -> None:
    left = len(remaining)
    print(f"Wiping leftovers... ({left})")

    if left:
        with connection:
            cursor.execute(f"""
                DELETE FROM anime
                WHERE id IN ({'?, ' * (left - 1)}?)
            """, tuple(remaining.keys()))


def update_anime(cursor: object, anime: Dict, new_rank: int, new_score: float,
                 new_premiere: str, new_type: str, new_episode: int) -> None:
    if new_rank == "N/A" or new_rank > 10000:
        value = 0
    else:
        value = int(get_info_by_rank(new_rank)["mult"] *
                    (10_000 - new_rank)) + 1

    with connection:
        cursor.execute("""
            UPDATE anime
            SET rank=:rank, score=:score, premiere=:prem,
            type=:type, episodes=:eps, value=:value
            WHERE id=:code
        """, {"rank": new_rank, "score": new_score, "prem": new_premiere,
              "type": new_type, "eps": new_episode, "code": anime["id"],
              "value": value})


def add_anime(cursor: object, code: str) -> bool:
    link = f"https://myanimelist.net/anime/{code}/"
    html = get_html(link)

    data = parse_details(html)
    data["id"] = code

    if data["rank"] == "N/A" or int(data["rank"]) > 10000:
        value = 0
    else:
        rank = int(data["rank"])
        value = int(get_info_by_rank(rank)["mult"] *
                    (10_000 - rank)) + 1

    data["value"] = value

    try:
        cursor.execute("""
            INSERT INTO anime VALUES
            (:id, :type, :premiere, :image, :broadcast,
            :score, :episodes, :airing, :name, :rank, :alt_name, :value)
            ON CONFLICT(id) DO UPDATE SET
            type=:type, premiere=:premiere, image=:image,
            broadcast=:broadcast, score=:score, episodes=:episodes,
            airing=:airing, name=:name, rank=:rank, alt_name=:alt_name,
            value=:value
        """, data)
    except Exception as err:
        print(err)
    else:
        print(f"Added {data['name']}")

    for studio in data["studios"]:
        try:
            cursor.execute("""
                INSERT INTO studio VALUES (:id, :name)
            """, {"id": str(uuid.uuid4()), "name": studio})
        except Exception as err:
            print(err)
        else:
            print(f"Added {studio} Studio")

    for genre in data["genres"]:
        try:
            cursor.execute("""
                INSERT INTO genre VALUES (:id, :name)
            """, {"id": str(uuid.uuid4()), "name": genre})
        except Exception as err:
            print(err)
        else:
            print(f"Added {genre} Genre")

    for studio in data["studios"]:
        try:
            cursor.execute("""
                INSERT INTO produced (anime_id, studio_id)
                SELECT :fk_anime_id, id FROM studio WHERE name=:studio
            """, {"fk_anime_id": code, "studio": studio})
        except Exception as err:
            print(err)
        else:
            print(f"Added {data['name']} <-> {studio} 'produced' relation")

    for genre in data["genres"]:
        try:
            cursor.execute("""
                INSERT INTO has (anime_id, genre_id)
                SELECT :fk_anime_id, id FROM genre WHERE name=:genre
            """, {"fk_anime_id": code, "genre": genre})
        except Exception as err:
            print(err)
        else:
            print(f"Added {data['name']} <-> {genre} 'has' relation")

    connection.commit()


def parse_details(html: str) -> Dict:
    doc = bs(html, "html.parser")

    type_ = doc.find(text="Type:").parent.parent.a
    if type_ is not None:
        type_ = type_.string

    premiere = doc.find(text="Aired:")
    if premiere is not None:
        premiere = premiere.parent.parent.decode_contents()
        premiere = premiere.split("</span>")[1].strip()

    image = doc.find(class_="borderClass").div.div.a.img
    if image is not None:
        image = image["data-src"]

    broadcast = doc.find(text="Broadcast:")
    if broadcast is not None:
        broadcast = broadcast.parent.parent.decode_contents()
        broadcast = broadcast.split("</span>")[1].strip()

    score = doc.find(class_="score-label").string

    episodes = doc.find(text="Episodes:")
    if episodes is not None:
        episodes = episodes.parent.parent.decode_contents()
        episodes = episodes.split("</span>")[1].strip()

    airing = doc.find_all(text="Status:")[1].parent.parent. \
        decode_contents().split("</span>")[1].strip()
    name = doc.find(class_="title-name").string
    rank = doc.find(text="Ranked ").parent.strong.string.strip("#")

    alt_name = doc.find(class_="title-english")
    if alt_name is not None:
        alt_name = alt_name.string

    genres = doc.find(text="Genres:")
    genres = genres if genres is not None else doc.find(text="Genre:")
    if genres is not None:
        try:
            genres = list(map(lambda x: x["title"],
                              genres.parent.parent.find_all("a")))
        except KeyError:
            genres = []
    else:
        genres = []

    studios = doc.find(text="Studios:")
    studios = studios if studios is not None else doc.find(text="Studio:")
    if studios is not None:
        try:
            studios = list(map(lambda x: x["title"],
                               studios.parent.parent.find_all("a")))
        except KeyError:
            studios = []
    else:
        studios = []

    return {
        "type": type_, "premiere": premiere, "image": image,
        "broadcast": broadcast, "score": score, "episodes": episodes,
        "airing": airing, "name": name, "rank": rank, "genres": genres,
        "studios": studios, "alt_name": alt_name
    }


def parse_animes(html: str) -> Tuple[Tuple[int, str]]:
    doc = bs(html, "html.parser")

    ranks = list(map(lambda x: int(x.string) if x.string != "-" else "N/A",
                     doc.find_all(class_="top-anime-rank-text"
                                  )))
    scores = list(map(lambda x: float(x.span.string)
                      if x.span.string != "N/A" else "N/A",
                      doc.find_all(
        class_="js-top-ranking-score-col di-ib al")
    ))
    codes = list(map(lambda x: x["href"].split("/")[4], doc.find_all(
        class_="hoverinfo_trigger fl-l ml12 mr8"
    )))

    infos = list(map(lambda x: list(map(lambda x: x.strip(),
                                        x.decode_contents().split("<br/>"))),
                     doc.find_all(class_="information di-ib mt4")
                     ))

    premieres = []
    types = []
    episodes = []

    for info in infos:
        info.extend(info[0].replace("(", "").split()[:2])

        del info[0]
        del info[1]

        premieres.append(info[0])
        types.append(info[1])
        episodes.append(info[2])

    return tuple(zip(
        ranks, scores, codes,
        premieres, types, episodes
    ))


def update_database() -> None:
    cursor = connection.cursor()

    db_animes = to_dict(list(cursor.execute("SELECT * FROM anime")))
    links = get_links()

    for count, link in enumerate(links, 1):
        links[count - 1] = None
        print(f"{count}/{len(links)}", end="\r")

        html = get_html(link)
        animes = parse_animes(html)

        for rank, score, code, premiere, type_, episode in animes:
            anime = db_animes.get(code)

            if (anime is None) or (anime["airing"] == "Currently Airing") \
                    or (anime["airing"] == "Not yet aired" and score != "N/A"):
                add_anime(cursor, code)
            elif anime["airing"] == "Finished Airing":
                update_anime(cursor, db_animes[code], rank, score,
                             premiere, type_, episode
                             )
            if anime is not None:
                del db_animes[code]

    wipe_remaining(cursor, db_animes)
    cursor.close()


def main():
    while True:
        start = time.time()

        try:
            with HiddenPrints():
                update_database()
        except Exception as err:
            print(err)

        print(f"Last update: {datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}")
        time.sleep(86_400 - (time.time() - start))


if __name__ == "__main__":
    main()
