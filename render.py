import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE = 1024
PAPER = "#f4efe4"
INK = "#171b1c"
RED = "#9e302d"
MUTED = "#656563"
RULE = "#c9c1b4"
CARD = "#faf7f0"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"


def font(size, face=SANS):
    return ImageFont.truetype(face, size)


def wrap_words(draw, text, face, width):
    lines = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=face)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, text, x, y, width, face, color, leading, max_lines=None):
    lines = wrap_words(draw, text, face, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        ending = lines[-1]
        while ending and draw.textlength(f"{ending}…", font=face) > width:
            ending = ending[:-1]
        lines[-1] = f"{ending.rstrip()}…"
    for index, line in enumerate(lines):
        draw.text((x, y + index * leading), line, font=face, fill=color)
    return y + len(lines) * leading


def draw_panel(draw, box, kicker, headline, summary, title_size=21):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=8, fill=CARD, outline=RULE, width=2)
    draw.rectangle((x1, y1 + 12, x1 + 5, y2 - 12), fill=RED)
    draw.text((x1 + 20, y1 + 10), kicker, font=font(15, SANS_BOLD), fill=RED)
    title_face = font(title_size, SANS_BOLD)
    title_end = draw_wrapped(
        draw, headline, x1 + 20, y1 + 34, x2 - x1 - 38,
        title_face, INK, title_size + 3, max_lines=2
    )
    draw_wrapped(
        draw, summary, x1 + 20, title_end + 4, x2 - x1 - 38,
        font(18), INK, 22, max_lines=3
    )


def draw_storm_scene(image, draw, box):
    x1, y1, x2, y2 = box
    width, height = x2 - x1, y2 - y1
    draw.rectangle(box, fill="#d9e2df")
    sea_top = y1 + 93
    draw.rectangle((x1, sea_top, x2, y2), fill="#294d61")

    land = [
        (x1 + 405, y1), (x2, y1), (x2, y2), (x1 + 330, y2),
        (x1 + 365, y1 + 197), (x1 + 342, y1 + 167),
        (x1 + 389, y1 + 140), (x1 + 371, y1 + 111),
        (x1 + 430, y1 + 78),
    ]
    draw.polygon(land, fill="#c6c7a8")
    shoreline = [
        (x1 + 405, y1), (x1 + 430, y1 + 78), (x1 + 371, y1 + 111),
        (x1 + 389, y1 + 140), (x1 + 342, y1 + 167),
        (x1 + 365, y1 + 197), (x1 + 330, y2),
    ]
    draw.line(shoreline, fill="#788a78", width=5, joint="curve")

    for offset in (0, 1, 2):
        y = y1 + 185 + offset * 8
        draw.line(
            (x1 + 26 + offset * 13, y, x1 + 168 + offset * 15, y - 4),
            fill="#7fa0a8", width=3
        )

    cx, cy = x1 + 233, y1 + 105
    cloud = "#738991"
    for degrees in range(0, 360, 45):
        angle = math.radians(degrees)
        px = cx + math.cos(angle) * 55
        py = cy + math.sin(angle) * 40
        draw.ellipse((px - 39, py - 31, px + 39, py + 31), fill=cloud)
    draw.ellipse((cx - 72, cy - 54, cx + 72, cy + 54), fill=cloud)

    for phase, color, line_width in ((0.0, "#e4e9e5", 11), (0.32, "#a9bbc0", 6)):
        points = []
        for step in range(151):
            fraction = step / 150
            angle = phase + fraction * math.pi * 5.2
            radius = 5 + fraction * 66
            points.append((cx + math.cos(angle) * radius,
                           cy + math.sin(angle) * radius * 0.72))
        draw.line(points, fill=color, width=line_width, joint="curve")
    draw.ellipse((cx - 7, cy - 6, cx + 7, cy + 6), fill="#f3f0e8")

    rain_color = "#8faab0"
    for index in range(9):
        rx = x1 + 115 + index * 34
        ry = y1 + 18 + (index % 3) * 11
        draw.line((rx, ry, rx - 22, ry + 42), fill=rain_color, width=3)
    for index in range(4):
        rx = x1 + 414 + index * 23
        ry = y1 + 58 + (index % 2) * 12
        draw.line((rx, ry, rx - 18, ry + 34), fill=rain_color, width=3)

    town_x, town_y = x1 + 432, y1 + 165
    for offset, building_height in ((0, 24), (35, 33), (73, 21)):
        bx = town_x + offset
        draw.rectangle((bx, town_y + 29 - building_height,
                        bx + 25, town_y + 29), fill="#475849")
        draw.polygon(
            ((bx - 4, town_y + 29 - building_height),
             (bx + 12, town_y + 17 - building_height),
             (bx + 29, town_y + 29 - building_height)),
            fill=RED
        )
        draw.rectangle((bx + 9, town_y + 14, bx + 14, town_y + 29),
                       fill="#e1d8c4")
    draw.text((x1 + 28, y2 - 27), "BAY OF BENGAL",
              font=font(14, SANS_BOLD), fill="#e7eee8")
    draw.text((x1 + 423, y2 - 27), "ODISHA COAST",
              font=font(14, SANS_BOLD), fill="#38483d")


def draw_bottom_card(draw, x, width, kicker, headline, detail, title_size=20):
    y1, y2 = 698, 842
    draw.rounded_rectangle((x, y1, x + width, y2), radius=8,
                           fill=CARD, outline=RULE, width=2)
    draw.text((x + 16, y1 + 11), kicker, font=font(14, SANS_BOLD), fill=RED)
    title_end = draw_wrapped(
        draw, headline, x + 16, y1 + 34, width - 32,
        font(title_size, SANS_BOLD), INK, title_size + 2, max_lines=2
    )
    draw_wrapped(
        draw, detail, x + 16, title_end + 5, width - 32,
        font(17), INK, 21, max_lines=2
    )


def build_page():
    image = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(image)

    draw.text((40, 22), "THE WORLD / FRIDAY EDITION",
              font=font(17, SANS_BOLD), fill=RED)
    draw.text((37, 43), "WORLD NEWS",
              font=font(62, SERIF_BOLD), fill=INK)
    draw.text((42, 116), "FRIDAY 20 NOVEMBER 2026",
              font=font(23, SANS_BOLD), fill=INK)
    draw.text((982, 30), "A ONE-DAY GLOBAL BRIEF",
              font=font(15, SANS_BOLD), fill=MUTED, anchor="ra")
    draw.line((40, 153, 984, 153), fill=INK, width=3)

    draw.text((42, 171), "LEAD  •  WEATHER",
              font=font(17, SANS_BOLD), fill=RED)
    draw.text((39, 197), "AKVAN HITS INDIA'S",
              font=font(35, SANS_BOLD), fill=INK)
    draw.text((39, 237), "EAST COAST",
              font=font(35, SANS_BOLD), fill=INK)
    draw.text((42, 279), "Cyclone landfall  •  Odisha–Andhra coast",
              font=font(17, SANS_BOLD), fill=MUTED)

    draw_storm_scene(image, draw, (40, 309, 588, 546))
    draw_wrapped(
        draw,
        "Severe Cyclonic Storm Akvan crosses between Machilipatnam and Puri. "
        "Coastal evacuations are under way; Odisha schools are shut.",
        42, 560, 542, font(19), INK, 26, max_lines=4
    )

    right_x, right_w, panel_h, panel_gap = 610, 374, 151, 15
    panel_y = 169
    draw_panel(
        draw, (right_x, panel_y, right_x + right_w, panel_y + panel_h),
        "DIPLOMACY  •  BRUSSELS",
        "EU TO SUMMON RUSSIA'S ENVOY",
        "After 19 Nov Kyiv strikes damaged Austrian and Dutch embassy "
        "buildings; no staff were hurt.",
        title_size=20
    )
    panel_y += panel_h + panel_gap
    draw_panel(
        draw, (right_x, panel_y, right_x + right_w, panel_y + panel_h),
        "DIPLOMACY  •  SHENZHEN",
        "TRUMP–PUTIN PEACE STATEMENT",
        "Shared statement omits Ukraine, after the 19 Nov trilateral with Xi.",
        title_size=19
    )
    panel_y += panel_h + panel_gap
    draw_panel(
        draw, (right_x, panel_y, right_x + right_w, panel_y + panel_h),
        "ASIA  •  SEOUL",
        "HAN DUCK-SOO CONVICTION OVERTURNED",
        "South Korea's top court reverses the former PM's conviction in the "
        "2024 martial-law case.",
        title_size=19
    )

    card_width = 300
    draw_bottom_card(
        draw, 40, card_width, "PACIFIC  •  FIJI",
        "DROUGHT DISASTER",
        "National state of disaster declared over El Niño drought."
    )
    draw_bottom_card(
        draw, 362, card_width, "AMERICAS  •  WASHINGTON",
        "US–VENEZUELA DEAL",
        "Signed deal to restore military ties, US defence chief says."
    )
    draw_bottom_card(
        draw, 684, card_width, "BUSINESS  •  AI",
        "ANTHROPIC • $1.5 TRILLION",
        "Valuation reportedly reaches $1.5tn amid the AI boom.",
        title_size=18
    )

    draw.rectangle((40, 850, 984, 966), fill=INK)
    draw.text(
        (58, 859),
        "MORE  •  BAHRAIN BAPCO REFINERY NEARS FULL RESTART AFTER SIX CONFLICT STRIKES",
        font=font(17, SANS_BOLD), fill="#fffaf0"
    )
    draw.text(
        (58, 885),
        "GULF  •  SIX-NATION RAIL PLAN TO CUT STRAIT OF HORMUZ RELIANCE",
        font=font(17, SANS_BOLD), fill="#fffaf0"
    )
    draw.text(
        (58, 911),
        "SPORT  •  NZ v INDIA FIRST TEST: NICHOLLS 113* ON DAY ONE IN WELLINGTON",
        font=font(17, SANS_BOLD), fill="#fffaf0"
    )
    draw.text(
        (58, 937),
        "GTA VI  •  MIDNIGHT LAUNCHES REACH AMERICAS; GAME WENT LIVE IN NZ 19 NOV",
        font=font(17, SANS_BOLD), fill="#fffaf0"
    )

    draw.text((42, 978), "20 NOV 2026",
              font=font(14, SANS_BOLD), fill=INK)
    draw.text((512, 978), "SOURCES: BBC  •  REUTERS  •  AP  •  AL JAZEERA",
              font=font(14, SANS_BOLD), fill=MUTED, anchor="ma")
    draw.text((982, 978), "WORLD BRIEF",
              font=font(14, SANS_BOLD), fill=INK, anchor="ra")
    draw.line((40, 1008, 984, 1008), fill=RED, width=3)

    return image


if __name__ == "__main__":
    output = Path(__file__).with_name("entry.png")
    build_page().save(output, format="PNG", optimize=True)
