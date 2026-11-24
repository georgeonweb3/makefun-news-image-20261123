#!/usr/bin/env python3
"""Front page for Monday 23 November 2026, drawn entirely in code.

Run from this directory:
    python3 draw.py        # writes entry.png next to this file

The picture is a newspaper front page: masthead, one big hero story
(COP31 collapses), then the rest of the day's news in dated two-line
items grouped under nine region banners across two columns, an
"Also today" strip, and a sources footer. Everything is rendered with
Pillow from the story table below; no photos, no fonts fetched, no
network. The output is 1024x1024 and about 250 KB.

Facts come from the research notes in the parent directory
(research.md, topup.md). Every item was checked against at least two
outlets; figures the outlets disagreed on (Brent crude, the DRC Ebola
case count, the Tonj East 87 claim, the Hodeidah 17 toll, the Odesa
stadium detail, the Merkury ship class) are left off the page, and
the US market closes printed are the ones all outlets agreed on.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
PAD = 28
GAP = 20
COL = (PAGE_W - 2 * PAD - GAP) // 2

PALETTE = {
    "paper": (246, 241, 231),
    "ink": (22, 22, 22),
    "grey": (90, 84, 74),
    "red": (163, 22, 33),
    "navy": (18, 33, 61),
    "gold": (198, 148, 52),
    "rule": (180, 172, 156),
    "strip": (232, 226, 212),
    "hero_body": (214, 222, 235),
    "hairline": (226, 220, 206),
}

DEJAVU = Path("/usr/share/fonts/truetype/dejavu")


def load_fonts():
    def f(name, size):
        return ImageFont.truetype(str(DEJAVU / name), size)

    return {
        "masthead": f("DejaVuSerif-Bold.ttf", 44),
        "mast_sub": f("DejaVuSans-Bold.ttf", 17),
        "mast_meta": f("DejaVuSans.ttf", 12),
        "kicker": f("DejaVuSans-Bold.ttf", 13),
        "hero_head": f("DejaVuSerif-Bold.ttf", 25),
        "hero_body": f("DejaVuSans.ttf", 14),
        "hero_fact": f("DejaVuSans-Bold.ttf", 12),
        "banner": f("DejaVuSans-Bold.ttf", 14),
        "head": f("DejaVuSans-Bold.ttf", 13),
        "detail": f("DejaVuSans.ttf", 11),
        "strip_head": f("DejaVuSans-Bold.ttf", 12),
        "strip": f("DejaVuSans.ttf", 11),
        "footer": f("DejaVuSans.ttf", 10),
    }


# date, headline, one-line detail. Section order is the display order.
NEWS = [
    ("MIDDLE EAST", [
        ("23 NOV", "Trump threatens fresh Iran strikes in the new year",
         "Vows to sink blockade runners; Iran says Hormuz could reopen in two days."),
        ("22 NOV", "Houthis claim a strike on Saudi Rabigh refinery",
         "Claim a \u201cdirect hit\u201d; coalition says it downed a missile. No verification."),
        ("22 NOV", "Israeli strikes kill eight in Gaza, including a boy",
         "Hamas seeks emergency mediator talks after a drone hit a food van."),
        ("22 NOV", "Iran strike wounds two at Bahrain industrial site",
         "Bahrain rejects IRGC radar claim; Trump seeks a \u201cpermanent deal\u201d."),
        ("22 NOV", "Israel hits southern Lebanon despite the ceasefire",
         "Ground and air attacks on the south; UNIFIL hands posts to the army."),
    ]),
    ("EUROPE", [
        ("23 NOV", "NATO sends AWACS to Poland after missile incursion",
         "All three objects were Kh-101s, made Oct\u2013Nov 2026; no Article 4 invoked."),
        ("23 NOV", "Dymer toll final at 11; at least 14 in Kyiv region",
         "Boy, 7, pulled alive after 14 hours under rubble; day of mourning held."),
        ("23 NOV", "Zelenskyy claims Ukraine sank the Merkury off Libya",
         "Seven sea drones; a Ka-27 helicopter destroyed; cargo ship Angara also hit."),
        ("23 NOV", "Ukraine hits Kaleykino pumping station \u2014 again",
         "Four oil tanks ablaze in a repeat strike; Perm refinery hit the same night."),
        ("23 NOV", "Odesa in blackout; schools remote for the week",
         "Russia targets power lines to isolate Odesa; fresh strikes hit Izmail port."),
        ("22 NOV", "Le Pen declines Zelenskyy\u2019s Kyiv invitation",
         "Will meet in Paris or Brussels; no trips abroad during the campaign."),
        ("23 NOV", "Burnham pitches \u2018landmark\u2019 closer EU ties for UK",
         "Miliband: closer ties give Britain a say on Brussels decisions."),
    ]),
    ("AFRICA", [
        ("23 NOV", "Bayelsa boat toll rises to at least 32",
         "500+ aboard a 200-capacity boat; crane lifts the wreck; Tinubu gives N250m."),
        ("22 NOV", "Troops rescue 18 abducted Kaduna children",
         "Four still missing; soldiers hunt the gang behind the Brigade abduction."),
        ("22 NOV", "Kenya and DR Congo agree to restore full ties",
         "Ambassadors to return after nearly three years; joint commission revived."),
        ("23 NOV", "Tonj East cattle-camp raid toll rises to at least 24",
         "Seven children among the dead; raiders blamed from Unity State."),
        ("22 NOV", "Sudan drones kill at least four, hit a UN building",
         "Children among the dead in Khartoum and Omdurman; power output collapses."),
    ]),
    ("ASIA-PACIFIC", [
        ("23 NOV", "Nepal PM Shah meets Modi; 8 deals, new train",
         "Sarayu-Kamala Express flagged off; Rs 15,000 crore package; extra port access."),
        ("23 NOV", "Singapore and China strike 29 deals at JCBC",
         "Hainan poultry and eggs approved; digital-trade pact; FTA upgrade talks."),
        ("22 NOV", "Eight killed in Tamil Nadu road accident",
         "Modi announces Rs 2 lakh ex-gratia for each victim\u2019s family."),
        ("23 NOV", "Molly Meldrum dies aged 83; state funeral planned",
         "Countdown host who championed AC/DC and Kylie Minogue; tributes pour in."),
        ("21 NOV", "WHO issues Ebola update for DRC, Kenya, Nigeria",
         "Bundibugyo virus outbreak; weekly situation report published 21 Nov."),
    ]),
    ("AMERICAS", [
        ("23 NOV", "Nvidia reinstates Jensen Huang as CEO; shares +31%",
         "Board reverses course after Trump call-in; probe continues; House hearing 1 Dec."),
        ("23 NOV", "US forms team to shield air traffic for Thanksgiving",
         "Move follows the nationwide ground-stop crisis earlier in the month."),
        ("23 NOV", "Trump blames voters for ignoring his warnings",
         "After Democrats retook the House and Senate; Jeffries targets Iran war, tariffs."),
        ("23 NOV", "G20 peace talks eyed for Miami, 14\u201315 December",
         "Zelenskyy agrees to US-proposed three-way talks; Putin invited, Kyiv not yet."),
        ("22 NOV", "Intel chief: Putin is \u2018not America\u2019s friend in Ukraine\u2019",
         "DNI Clayton, on ABC: \u2018Not at all. Not at all.\u2019 \u2014 defending Trump\u2019s \u2018friend\u2019 line."),
    ]),
    ("SPORT", [
        ("22 NOV", "Verstappen wins chaotic Las Vegas Grand Prix",
         "Norris 2nd, Piastri 3rd; 35 lead changes; the Ferraris collide. Antonelli champion."),
        ("22 NOV", "Liverpool hammer Man Utd 4\u20130 in Pochettino debut",
         "Yoro off after 8 minutes; Szoboszlai, Wirtz, Ngumoha, Mu\u00f1oz score."),
        ("23 NOV", "Brentford thrash Everton 4\u20130 on Monday night",
         "Lewis-Potter brace; Janelt stunner; Tarkowski off; Moyes\u2019 record 593rd game."),
    ]),
    ("SCIENCE", [
        ("23 NOV", "Deepest explosive eruption found in Challenger Deep",
         "Pyroclastic rock at 6,148 m \u2014 pressure should have stopped it, scientists say."),
        ("23 NOV", "NHS launches world\u2019s largest AI breast-screening trial",
         "First women join the EDITH trial in Cambridgeshire; AI to aid mammograms."),
        ("23 NOV", "MIT: small AI can design analogue chips faster",
         "SLIC beats a 763B-param model on design tasks; preprint, not yet peer-reviewed."),
    ]),
    ("ECONOMY", [
        ("23 NOV", "Markets roar back: S&P +4.7%, Nasdaq +6.5%",
         "S&P 7,237.17; Dow 49,595.31 (+3.0%); biggest one-day gains since April 2025."),
        ("20 NOV", "Anthropic shares slump a day after blockbuster IPO",
         "Down sharply on its first full trading day; symbol of the AI-trade turn."),
        ("23 NOV", "Oil lower, gold jumps above $3,632 on safe-haven rush",
         "Gold +3.3% as investors flee the AI sell-off; Iran war limits oil\u2019s fall."),
    ]),
    ("CLIMATE", [
        ("23 NOV", "World \u2018cannot afford a repeat\u2019 of COP31, says Stiell",
         "Guterres voices \u2018profound frustration\u2019; Gore blasts petrostates\u2019 veto."),
        ("22 NOV", "90+ countries sign electrification pledge anyway",
         "\u201835 by 35\u2019 goal survives the collapse; adaptation finance to triple by 2035."),
    ]),
]

ALSO = [
    ("23 NOV", "Treasury sanctions hit Iran exchanges"),
    ("23 NOV", "Houthi media: 10 killed in Hodeidah strike"),
    ("22 NOV", "Broncos 38\u201324 Raiders; Commanders 22\u201320 Bengals"),
    ("22 NOV", "Giants 23\u201318 Jaguars; India declare 720/9"),
    ("22 NOV", "F1: Antonelli champion, 402 pts; Mercedes 666"),
    ("21 NOV", "Zelenskyy formalises E5 negotiating group"),
    ("23 NOV", "Europe\u2019s cloud-sovereignty push gains ground"),
    ("22 NOV", "Iraq probes deadly Basra pipeline fire"),
    ("23 NOV", "Iran demands $290bn damages from US"),
]

HERO_KICKER = "CLIMATE  \u00b7  ANTALYA, T\u00dcRKIYE  \u00b7  22 NOVEMBER 2026"
HERO_HEAD = "COP31 COLLAPSES: NO DEAL AS EU REJECTS A TEXT WITH NO FOSSIL FUELS"
HERO_BODY = (
    "The UN climate summit ends without a pact \u2014 the longest COP ever \u2014 after the EU, UK and",
    "island states reject a final text that never once names fossil fuels. Stiell: \u201cThe world",
    "cannot afford a repeat.\u201d Next COP: Addis Ababa, Ethiopia, Nov 2027.",
)
HERO_FACTS = "LONGEST COP EVER  \u00b7  FIRST BREAKDOWN SINCE COP15 IN 2009  \u00b7  1.5\u00b0C GOAL NOW OUT OF REACH"

BANNER_H = 20
ITEM_H = 27          # headline 14 + detail 11 + 2 gap
HEADLINE_Y = 14      # detail sits this far below the headline
SECTION_PAD = 4
COL_GAP_AFTER = 4    # space after a section inside a column


def split_lines(canvas, text, font, max_w):
    """Break text into lines no wider than max_w (greedy, word by word)."""
    out = []
    for chunk in text.split("\n"):
        words = chunk.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if canvas.textlength(candidate, font=font) <= max_w:
                current = candidate
            else:
                if current:
                    out.append(current)
                current = word
        if current:
            out.append(current)
    return out


def lines_that_overflow(canvas, fonts):
    """Return every story line that would not fit on one line."""
    problems = []
    for section, items in NEWS:
        for date, headline, detail in items:
            full = f"{date} \u00b7 {headline}"
            if canvas.textlength(full, font=fonts["head"]) > COL:
                problems.append(f"{section}: headline too long: {full}")
            if canvas.textlength(detail, font=fonts["detail"]) > COL - 4:
                problems.append(f"{section}: detail too long: {detail}")
    return problems


def block_height(n_items):
    return BANNER_H + n_items * ITEM_H + SECTION_PAD


def partition_columns():
    """Split the nine sections into two columns with near-equal height.

    Brute force over all 2**9 splits; keep the split whose taller column
    is shortest. Sections keep their NEWS order inside each column.
    """
    heights = [block_height(len(items)) + COL_GAP_AFTER for _, items in NEWS]
    total = sum(heights)
    best_mask, best_score = 0, total
    for mask in range(1 << len(heights)):
        left = sum(h for i, h in enumerate(heights) if mask & (1 << i))
        score = max(left, total - left)
        if score < best_score:
            best_mask, best_score = mask, score
    left, right = [], []
    for i, (section, items) in enumerate(NEWS):
        (left if best_mask & (1 << i) else right).append((section, items))
    return left, right


def paint_masthead(canvas, fonts):
    canvas.text((PAGE_W // 2, 6), "THE WORLD IN ONE DAY", font=fonts["masthead"],
                fill=PALETTE["ink"], anchor="ma")
    canvas.line([PAD, 62, PAGE_W - PAD, 62], fill=PALETTE["ink"], width=2)
    canvas.line([PAD, 66, PAGE_W - PAD, 66], fill=PALETTE["rule"], width=1)
    canvas.text((PAD, 72), "MONDAY 23 NOVEMBER 2026", font=fonts["mast_sub"],
                fill=PALETTE["red"])
    canvas.text((PAGE_W - PAD, 73), "38 STORIES  \u00b7  9 REGIONS  \u00b7  EVERY STORY DATED",
                font=fonts["mast_meta"], fill=PALETTE["grey"], anchor="ra")


def paint_hero(canvas, fonts):
    top, height = 96, 156
    canvas.rectangle([PAD, top, PAGE_W - PAD, top + height], fill=PALETTE["navy"])
    canvas.rectangle([PAD, top, PAD + 6, top + height], fill=PALETTE["gold"])
    canvas.text((PAD + 18, top + 8), HERO_KICKER, font=fonts["kicker"],
                fill=PALETTE["gold"])
    y = top + 28
    for line in split_lines(canvas, HERO_HEAD, fonts["hero_head"], PAGE_W - 2 * PAD - 36):
        canvas.text((PAD + 18, y), line, font=fonts["hero_head"], fill="white")
        y += 27
    for line in HERO_BODY:
        canvas.text((PAD + 18, y), line, font=fonts["hero_body"],
                    fill=PALETTE["hero_body"])
        y += 16
    canvas.text((PAD + 18, top + height - 19), HERO_FACTS, font=fonts["hero_fact"],
                fill=(198, 164, 92))
    return top + height + 8


def paint_section(canvas, fonts, x, y, section, items):
    canvas.rectangle([x, y, x + COL, y + BANNER_H], fill=PALETTE["navy"])
    canvas.text((x + 8, y + 3), section, font=fonts["banner"], fill="white")
    y += BANNER_H + SECTION_PAD
    for date, headline, detail in items:
        stamp = f"{date} \u00b7 "
        stamp_w = canvas.textlength(stamp, font=fonts["head"])
        canvas.text((x, y), stamp, font=fonts["head"], fill=PALETTE["red"])
        canvas.text((x + stamp_w, y), headline, font=fonts["head"],
                    fill=PALETTE["ink"])
        canvas.text((x + 4, y + HEADLINE_Y), detail, font=fonts["detail"],
                    fill=PALETTE["grey"])
        y += ITEM_H
        canvas.line([x, y - 1, x + COL, y - 1], fill=PALETTE["hairline"])
    return y


def paint_strip(canvas, fonts, y, height):
    canvas.rectangle([PAD, y, PAGE_W - PAD, y + height], fill=PALETTE["strip"])
    canvas.text((PAD + 8, y + 5), "ALSO TODAY", font=fonts["strip_head"],
                fill=PALETTE["red"])
    cells = [f"{date} \u2014 {text}" for date, text in ALSO]
    rows = ["  \u00b7  ".join(cells[i:i + 3]) for i in range(0, len(cells), 3)]
    for i, row in enumerate(rows):
        if canvas.textlength(row, font=fonts["strip"]) > PAGE_W - 2 * PAD - 16:
            raise SystemExit(f"strip row {i + 1} too long: {row}")
        canvas.text((PAD + 8, y + 20 + i * 14), row, font=fonts["strip"],
                    fill=PALETTE["ink"])


def paint_footer(canvas, fonts):
    y = PAGE_H - 16
    canvas.text(
        (PAD, y),
        "Sources: AP, Reuters, Al Jazeera, AFP, BBC, CNN, NBC, Anadolu, WION, Xinhua, Kyodo, Sky Sports \u2014 20\u201323 Nov 2026 editions. Tolls as reported; disputed tolls flagged in the story.",
        font=fonts["footer"], fill=PALETTE["grey"])


def build():
    fonts = load_fonts()
    page = Image.new("RGB", (PAGE_W, PAGE_H), PALETTE["paper"])
    canvas = ImageDraw.Draw(page)

    problems = lines_that_overflow(canvas, fonts)
    for problem in problems:
        print("WARNING:", problem)
    if problems:
        raise SystemExit(f"{len(problems)} lines would wrap; shorten them first")

    paint_masthead(canvas, fonts)
    body_top = paint_hero(canvas, fonts)

    strip_h, footer_h = 58, 18
    body_bottom = PAGE_H - strip_h - footer_h - 6
    left, right = partition_columns()
    heights = [
        sum(block_height(len(items)) + COL_GAP_AFTER for _, items in col)
        for col in (left, right)
    ]
    print("column heights:", heights, "budget:", body_bottom - body_top)
    if max(heights) > body_bottom - body_top:
        raise SystemExit("body overflow")

    for col_i, sections in enumerate((left, right)):
        x = PAD + col_i * (COL + GAP)
        y = body_top
        for section, items in sections:
            y = paint_section(canvas, fonts, x, y, section, items)
            y += COL_GAP_AFTER

    paint_strip(canvas, fonts, PAGE_H - strip_h - footer_h, strip_h)
    paint_footer(canvas, fonts)

    out = Path(__file__).resolve().parent / "entry.png"
    page.save(out, optimize=True)
    total = sum(len(items) for _, items in NEWS)
    print(f"wrote {out} ({out.stat().st_size} bytes, {PAGE_W}x{PAGE_H})")
    print(f"stories: {total} main + 1 hero + {len(ALSO)} strip")


if __name__ == "__main__":
    build()
