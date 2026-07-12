#!/usr/bin/env python3
"""HolySpiritOS verse lookup — KJV 1769, stdlib only.

Usage:
  lookup.py "John 3:16"            single verse
  lookup.py "John 3:16-18"         verse range
  lookup.py "Psalm 23"             whole chapter
  lookup.py --search "shepherd"    case-insensitive text search (default cap 20)
  lookup.py --search "love" --book "1 John" --limit 10
  lookup.py --books                list all 66 books with chapter counts
  lookup.py --raw "John 3:16"      keep the 1769 pilcrow (¶) paragraph markers
  lookup.py --self-test            verify the foundation files are intact

Reads foundation/ next to this script's parent directory, or set
HSOS_FOUNDATION to the directory containing verses-1769.json.

Note on text conventions: [square brackets] mark words the 1769 translators
supplied for readability (printed in italics in print editions); ¶ marks
original paragraph breaks. Both are part of the authentic text.
"""

import argparse
import json
import os
import re
import sys
import unicodedata

# Common abbreviations -> canonical book names as used in verses-1769.json.
ABBREV = {
    "gen": "Genesis", "ge": "Genesis", "gn": "Genesis",
    "exod": "Exodus", "exo": "Exodus", "ex": "Exodus",
    "lev": "Leviticus", "lv": "Leviticus",
    "num": "Numbers", "nm": "Numbers", "nu": "Numbers",
    "deut": "Deuteronomy", "deu": "Deuteronomy", "dt": "Deuteronomy",
    "josh": "Joshua", "jos": "Joshua",
    "judg": "Judges", "jdg": "Judges", "jg": "Judges",
    "ruth": "Ruth", "ru": "Ruth",
    "1 sam": "1 Samuel", "1sam": "1 Samuel", "1 sa": "1 Samuel",
    "2 sam": "2 Samuel", "2sam": "2 Samuel", "2 sa": "2 Samuel",
    "1 kgs": "1 Kings", "1 ki": "1 Kings", "1kgs": "1 Kings",
    "2 kgs": "2 Kings", "2 ki": "2 Kings", "2kgs": "2 Kings",
    "1 chr": "1 Chronicles", "1 chron": "1 Chronicles", "1chr": "1 Chronicles",
    "2 chr": "2 Chronicles", "2 chron": "2 Chronicles", "2chr": "2 Chronicles",
    "ezra": "Ezra", "ezr": "Ezra",
    "neh": "Nehemiah", "ne": "Nehemiah",
    "esth": "Esther", "est": "Esther",
    "job": "Job", "jb": "Job",
    "ps": "Psalms", "psa": "Psalms", "psalm": "Psalms", "pss": "Psalms",
    "prov": "Proverbs", "pro": "Proverbs", "pr": "Proverbs",
    "eccl": "Ecclesiastes", "ecc": "Ecclesiastes", "qoh": "Ecclesiastes",
    "song": "Song of Solomon", "sos": "Song of Solomon",
    "song of songs": "Song of Solomon", "cant": "Song of Solomon",
    "solomon's song": "Song of Solomon", "solomons song": "Song of Solomon",
    "isa": "Isaiah", "is": "Isaiah",
    "jer": "Jeremiah", "je": "Jeremiah",
    "lam": "Lamentations", "la": "Lamentations",
    "ezek": "Ezekiel", "eze": "Ezekiel", "ezk": "Ezekiel",
    "dan": "Daniel", "da": "Daniel", "dn": "Daniel",
    "hos": "Hosea", "ho": "Hosea",
    "joel": "Joel", "jl": "Joel",
    "amos": "Amos", "am": "Amos",
    "obad": "Obadiah", "ob": "Obadiah",
    "jonah": "Jonah", "jon": "Jonah",
    "mic": "Micah", "mi": "Micah",
    "nah": "Nahum", "na": "Nahum",
    "hab": "Habakkuk", "hb": "Habakkuk",
    "zeph": "Zephaniah", "zep": "Zephaniah",
    "hag": "Haggai", "hg": "Haggai",
    "zech": "Zechariah", "zec": "Zechariah",
    "mal": "Malachi", "ml": "Malachi",
    "matt": "Matthew", "mat": "Matthew", "mt": "Matthew",
    "mark": "Mark", "mk": "Mark", "mrk": "Mark",
    "luke": "Luke", "lk": "Luke", "luk": "Luke",
    "john": "John", "jn": "John", "jhn": "John",
    "acts": "Acts", "ac": "Acts",
    "rom": "Romans", "ro": "Romans", "rm": "Romans",
    "1 cor": "1 Corinthians", "1cor": "1 Corinthians", "1 co": "1 Corinthians",
    "2 cor": "2 Corinthians", "2cor": "2 Corinthians", "2 co": "2 Corinthians",
    "gal": "Galatians", "ga": "Galatians",
    "eph": "Ephesians", "ep": "Ephesians",
    "phil": "Philippians", "php": "Philippians",
    "col": "Colossians",
    "1 thess": "1 Thessalonians", "1 thes": "1 Thessalonians", "1thess": "1 Thessalonians",
    "2 thess": "2 Thessalonians", "2 thes": "2 Thessalonians", "2thess": "2 Thessalonians",
    "1 tim": "1 Timothy", "1tim": "1 Timothy", "1 ti": "1 Timothy",
    "2 tim": "2 Timothy", "2tim": "2 Timothy", "2 ti": "2 Timothy",
    "titus": "Titus", "tit": "Titus",
    "phlm": "Philemon", "philem": "Philemon", "phm": "Philemon",
    "heb": "Hebrews", "he": "Hebrews",
    "jas": "James", "jam": "James", "jms": "James",
    "1 pet": "1 Peter", "1pet": "1 Peter", "1 pe": "1 Peter", "1 pt": "1 Peter",
    "2 pet": "2 Peter", "2pet": "2 Peter", "2 pe": "2 Peter", "2 pt": "2 Peter",
    "1 jn": "1 John", "1jn": "1 John", "1 jo": "1 John",
    "2 jn": "2 John", "2jn": "2 John", "2 jo": "2 John",
    "3 jn": "3 John", "3jn": "3 John", "3 jo": "3 John",
    "jude": "Jude", "jud": "Jude",
    "rev": "Revelation", "re": "Revelation", "rv": "Revelation",
    "revelations": "Revelation",
}

ROMAN = {"i": "1", "ii": "2", "iii": "3"}


def foundation_dir():
    env = os.environ.get("HSOS_FOUNDATION")
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "foundation")


def load_verses():
    path = os.path.join(foundation_dir(), "verses-1769.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"error: verses-1769.json not found at {path} "
                 "(set HSOS_FOUNDATION to the foundation directory)")


def canonical_books(verses):
    books, seen = [], set()
    for key in verses:
        book = key[:key.rfind(" ")]
        if book not in seen:
            seen.add(book)
            books.append(book)
    return books


def normalize_book(name, books):
    q = unicodedata.normalize("NFKC", name).strip().rstrip(".").lower()
    q = re.sub(r"\s+", " ", q)
    # Roman numeral prefixes: "II Cor" -> "2 cor"
    m = re.match(r"^(i{1,3})\s+(.*)$", q)
    if m and m.group(1) in ROMAN:
        q = ROMAN[m.group(1)] + " " + m.group(2)
    if q in ABBREV:
        return ABBREV[q]
    for book in books:
        if q == book.lower():
            return book
    # Unambiguous prefix match ("philip" -> Philippians)
    hits = [b for b in books if b.lower().startswith(q)]
    if len(hits) == 1:
        return hits[0]
    return None


def clean(text, raw=False):
    return text if raw else text.replace("¶ ", "").replace("¶", "").strip()


def parse_reference(ref):
    """Return (book, chapter, verse_start, verse_end); chapter/verses may be None."""
    ref = ref.strip()
    m = re.match(r"^(.*?)\s+(\d+)(?::(\d+)(?:\s*-\s*(\d+))?)?$", ref)
    if not m:
        return ref, None, None, None
    book, ch = m.group(1), int(m.group(2))
    vs = int(m.group(3)) if m.group(3) else None
    ve = int(m.group(4)) if m.group(4) else vs
    return book, ch, vs, ve


def cmd_reference(ref, raw):
    verses = load_verses()
    books = canonical_books(verses)
    book_part, ch, vs, ve = parse_reference(ref)
    book = normalize_book(book_part, books)
    if not book:
        sys.exit(f"error: unknown book {book_part!r} — try lookup.py --books")
    if ch is None:
        sys.exit(f"error: give a chapter, e.g. \"{book} 1\" or \"{book} 1:1\"")
    if vs is None:
        keys = []
        v = 1
        while f"{book} {ch}:{v}" in verses:
            keys.append(f"{book} {ch}:{v}")
            v += 1
        if not keys:
            sys.exit(f"error: {book} has no chapter {ch}")
    else:
        if ve < vs:
            vs, ve = ve, vs
        keys = [f"{book} {ch}:{v}" for v in range(vs, ve + 1)]
        missing = [k for k in keys if k not in verses]
        if missing:
            sys.exit(f"error: verse not found: {missing[0]}")
    for k in keys:
        print(f"{k}  {clean(verses[k], raw)}")


def cmd_search(term, book_filter, limit, raw):
    verses = load_verses()
    books = canonical_books(verses)
    book = None
    if book_filter:
        book = normalize_book(book_filter, books)
        if not book:
            sys.exit(f"error: unknown book {book_filter!r}")
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    shown = total = 0
    for key, text in verses.items():
        if book and not key.startswith(book + " "):
            continue
        if pattern.search(text):
            total += 1
            if shown < limit:
                print(f"{key}  {clean(text, raw)}")
                shown += 1
    if total > shown:
        print(f"... {total - shown} more matches (raise --limit to see them)")
    if total == 0:
        print(f"no matches for {term!r}" + (f" in {book}" if book else ""))


def cmd_books():
    meta_path = os.path.join(foundation_dir(), "kjv-metadata.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        for book, info in meta["books"].items():
            print(f"{book}  ({info['chapters']} chapters)")
        return
    except FileNotFoundError:
        pass
    verses = load_verses()
    for book in canonical_books(verses):
        print(book)


def cmd_self_test():
    verses = load_verses()
    checks = {
        "Genesis 1:1": "In the beginning God created the heaven and the earth.",
        "Song of Solomon 2:1": "I [am] the rose of Sharon, [and] the lily of the valleys.",
        "Revelation 22:21": "The grace of our Lord Jesus Christ [be] with you all. Amen.",
    }
    ok = len(verses) == 31102
    print(f"verse count: {len(verses)} (expected 31102) {'OK' if ok else 'FAIL'}")
    for ref, expected in checks.items():
        got = clean(verses.get(ref, ""))
        good = got == expected
        ok = ok and good
        print(f"{ref}: {'OK' if good else 'FAIL — got ' + repr(got)}")
    n_books = len(canonical_books(verses))
    print(f"book count: {n_books} (expected 66) {'OK' if n_books == 66 else 'FAIL'}")
    ok = ok and n_books == 66
    sys.exit(0 if ok else 1)


def main():
    p = argparse.ArgumentParser(description="KJV 1769 verse lookup (HolySpiritOS)")
    p.add_argument("reference", nargs="?", help='e.g. "John 3:16", "John 3:16-18", "Psalm 23"')
    p.add_argument("--search", metavar="TEXT", help="case-insensitive text search")
    p.add_argument("--book", metavar="BOOK", help="restrict --search to one book")
    p.add_argument("--limit", type=int, default=20, help="max search results (default 20)")
    p.add_argument("--raw", action="store_true", help="keep ¶ paragraph markers")
    p.add_argument("--books", action="store_true", help="list the 66 books")
    p.add_argument("--self-test", action="store_true", help="verify foundation integrity")
    args = p.parse_args()

    if args.self_test:
        cmd_self_test()
    elif args.books:
        cmd_books()
    elif args.search:
        cmd_search(args.search, args.book, args.limit, args.raw)
    elif args.reference:
        cmd_reference(args.reference, args.raw)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
