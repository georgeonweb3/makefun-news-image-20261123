#!/usr/bin/env python3
"""Draw the make.fun news-image-20261123 entry: a dense newspaper front page
summing up world news of Monday 23 November 2026.

Every pixel is code-drawn with Pillow (no photos, no network, no fonts
fetched at run time). The program writes entry.png next to itself:
    python3 draw.py

Layout: masthead, a COP31 hero panel, then 38 dated stories grouped into
9 region sections across two columns, plus an "Also today" strip and a
sources footer. 1024x1024, well under the 1 MiB limit.

Density discipline: each story is exactly two lines -- one bold headline
line prefixed by its red date, one detail line -- so 38 stories fit
legibly in the two columns. Headlines and details are written short on
purpose; the program prints a warning for any line that would wrap.

Facts: every story verified against 2+ outlets (see ../research.md and
../topup.md). Dropped: Brent crude levels, DRC Ebola case figures,
Tonj East 87 claim, Hodeidah 17 toll, Odesa stadium detail, Merkury
ship class, Vyshneve toll of 3. US market closes are the agreed closes
(S&P 7,237.17; Dow 49,595.31; Nasdaq 24,089.56).
"""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
COL_GAP = 20
COL_W = (W - 2 * MARGIN - COL_GAP) // 2  # 469

PAPER = (246, 241, 231)
INK = (22, 22, 22)
MUTED = (90, 84, 74)
RED = (163, 22, 33)
NAVY = (18, 33, 61)
GOLD = (198, 148, 52)
RULE = (180, 172, 156)
STRIP_BG = (232, 226, 212)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_B = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")
SANS_B = str(FONT_DIR / "DejaVuSans-Bold.ttf")

F = {
    "masthead": ImageFont.truetype(SERIF_B, 44),
    "mast_sub": ImageFont.truetype(SANS_B, 17),
    "mast_meta": ImageFont.truetype(SANS, 12),
    "hero_kicker": ImageFont.truetype(SANS_B, 13),
    "hero_head": ImageFont.truetype(SERIF_B, 25),
    "hero_body": ImageFont.truetype(SANS, 14),
    "hero_fact": ImageFont.truetype(SANS_B, 12),
    "section": ImageFont.truetype(SANS_B, 14),
    "head": ImageFont.truetype(SANS_B, 13),
    "body": ImageFont.truetype(SANS, 11),
    "strip_head": ImageFont.truetype(SANS_B, 12),
    "strip": ImageFont.truetype(SANS, 11),
    "footer": ImageFont.truetype(SANS, 10),
}

# (region, [(date, headline, detail), ...]) — every story dated, verified
# against 2+ outlets on 23 Nov 2026 (see ../research.md + ../topup.md).
SECTIONS = [
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

STRIP = [
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

HERO = {
    "kicker": "CLIMATE  \u00b7  ANTALYA, T\u00dcRKIYE  \u00b7  22 NOVEMBER 2026",
    "head": "COP31 COLLAPSES: NO DEAL AS EU REJECTS A TEXT WITH NO FOSSIL FUELS",
    "body": [
        "The UN climate summit ends without a pact \u2014 the longest COP ever \u2014 after the EU, UK and",
        "island states reject a final text that never once names fossil fuels. Stiell: \u201cThe world",
        "cannot afford a repeat.\u201d Next COP: Addis Ababa, Ethiopia, Nov 2027.",
    ],
    "facts": "LONGEST COP EVER  \u00b7  FIRST BREAKDOWN SINCE COP15 IN 2009  \u00b7  1.5\u00b0C GOAL NOW OUT OF REACH",
}

HEAD_LH, BODY_LH, STORY_GAP = 14, 11, 2
STORY_H = HEAD_LH + BODY_LH + STORY_GAP  # 27
SECTION_HDR = 20
SECTION_GAP = 4


def wrap(draw, text, font, width):
    """Greedy word-wrap to pixel width; returns a list of lines."""
    lines = []
    for raw in text.split("\n"):
        words, cur = raw.split(), ""
        for word in words:
            trial = f"{cur} {word}".strip()
            if draw.textlength(trial, font=font) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def check_fits(draw):
    """Every headline (with its date prefix) and every detail must fit one line."""
    bad = []
    for name, stories in SECTIONS:
        for date, head, detail in stories:
            hl = f"{date} \u00b7 {head}"
            if draw.textlength(hl, font=F["head"]) > COL_W:
                bad.append(f"HEADLINE WRAPS [{name}]: {hl}")
            if draw.textlength(detail, font=F["body"]) > COL_W - 4:
                bad.append(f"DETAIL WRAPS [{name}]: {detail}")
    return bad


def section_height(stories):
    return SECTION_HDR + len(stories) * STORY_H + 4


def draw_section(draw, x, y, name, stories):
    draw.rectangle([x, y, x + COL_W, y + SECTION_HDR], fill=NAVY)
    draw.text((x + 8, y + 3), name, font=F["section"], fill=(255, 255, 255))
    y += SECTION_HDR + 4
    for date, head, detail in stories:
        # headline line: red date prefix + bold headline
        dtext = f"{date} \u00b7 "
        dw = draw.textlength(dtext, font=F["head"])
        draw.text((x, y), dtext, font=F["head"], fill=RED)
        draw.text((x + dw, y), head, font=F["head"], fill=INK)
        draw.text((x + 4, y + HEAD_LH), detail, font=F["body"], fill=MUTED)
        y += STORY_H
        draw.line([x, y - 1, x + COL_W, y - 1], fill=(226, 220, 206))
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    bad = check_fits(d)
    for b in bad:
        print("WARNING:", b)
    if bad:
        raise SystemExit(f"{len(bad)} lines would wrap; shorten them first")

    # ---- masthead ----
    d.text((W // 2, 6), "THE WORLD IN ONE DAY", font=F["masthead"],
           fill=INK, anchor="ma")
    d.line([MARGIN, 62, W - MARGIN, 62], fill=INK, width=2)
    d.line([MARGIN, 66, W - MARGIN, 66], fill=RULE, width=1)
    d.text((MARGIN, 72), "MONDAY 23 NOVEMBER 2026", font=F["mast_sub"], fill=RED)
    right = "38 STORIES  \u00b7  9 REGIONS  \u00b7  EVERY STORY DATED"
    d.text((W - MARGIN, 73), right, font=F["mast_meta"], fill=MUTED, anchor="ra")

    # ---- hero: COP31 ----
    hy, hero_h = 96, 156
    d.rectangle([MARGIN, hy, W - MARGIN, hy + hero_h], fill=NAVY)
    d.rectangle([MARGIN, hy, MARGIN + 6, hy + hero_h], fill=GOLD)
    d.text((MARGIN + 18, hy + 8), HERO["kicker"], font=F["hero_kicker"], fill=GOLD)
    head_lines = wrap(d, HERO["head"], F["hero_head"], W - 2 * MARGIN - 36)
    ty = hy + 28
    for line in head_lines:
        d.text((MARGIN + 18, ty), line, font=F["hero_head"], fill=(255, 255, 255))
        ty += 27
    for line in HERO["body"]:
        d.text((MARGIN + 18, ty), line, font=F["hero_body"], fill=(214, 222, 235))
        ty += 16
    d.text((MARGIN + 18, hy + hero_h - 19), HERO["facts"], font=F["hero_fact"],
           fill=(198, 164, 92))

    # ---- body: two columns, sections balanced by optimal partition ----
    # (subset-sum over the 9 sections; order within each column preserved)
    body_top = hy + hero_h + 8
    strip_h, footer_h = 58, 18
    body_bottom = H - strip_h - footer_h - 6
    measured = [(name, stories, section_height(stories) + SECTION_GAP)
                for name, stories in SECTIONS]
    total_h = sum(h for _, _, h in measured)
    best = None
    for mask in range(1 << len(measured)):
        h0 = sum(measured[i][2] for i in range(len(measured)) if mask >> i & 1)
        h1 = total_h - h0
        score = max(h0, h1)
        if best is None or score < best[0]:
            best = (score, mask)
    _, mask = best
    col_sections = [[], []]
    for i, (name, stories, h) in enumerate(measured):
        col_sections[0 if (mask >> i) & 1 else 1].append((name, stories))
    col_heights = [sum(section_height(s) + SECTION_GAP for _, s in col)
                   for col in col_sections]
    print("column heights:", col_heights, "budget:", body_bottom - body_top)
    assert max(col_heights) <= body_bottom - body_top, "body overflow"

    for ci, sections in enumerate(col_sections):
        x = MARGIN + ci * (COL_W + COL_GAP)
        y = body_top
        for name, stories in sections:
            y = draw_section(d, x, y, name, stories)
            y += SECTION_GAP

    # ---- also-today strip ----
    sy = H - strip_h - footer_h
    d.rectangle([MARGIN, sy, W - MARGIN, sy + strip_h], fill=STRIP_BG)
    d.text((MARGIN + 8, sy + 5), "ALSO TODAY", font=F["strip_head"], fill=RED)
    bits = [f"{date} \u2014 {text}" for date, text in STRIP]
    strip_lines = ["  \u00b7  ".join(bits[i:i + 3]) for i in range(0, len(bits), 3)]
    for li, line in enumerate(strip_lines):
        if d.textlength(line, font=F["strip"]) > W - 2 * MARGIN - 16:
            raise SystemExit(f"strip line {li + 1} too long: {line}")
        d.text((MARGIN + 8, sy + 20 + li * 14), line, font=F["strip"], fill=INK)

    # ---- footer ----
    fy = H - footer_h + 2
    d.text((MARGIN, fy),
           "Sources: AP, Reuters, Al Jazeera, AFP, BBC, CNN, NBC, Anadolu, WION, Xinhua, Kyodo, Sky Sports \u2014 20\u201323 Nov 2026 editions. Tolls as reported; disputed tolls flagged in the story.",
           font=F["footer"], fill=MUTED)

    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes, {W}x{H})")
    total = sum(len(s) for _, s in SECTIONS)
    print(f"stories: {total} main + 1 hero + {len(STRIP)} strip")


if __name__ == "__main__":
    main()
