#!/usr/bin/env python3
"""
Luo Tirppatunnistimen sovellusikonit (kotinäytön kuvake).

Ikonit ovat valmiina tässä kansiossa, joten tätä ei tarvitse ajaa.
Aja vain jos haluat vaihtaa vareja tai kuvaa:

    pip install pillow
    python3 tee-ikonit.py

Varit alla: TAUSTA = sovelluksen tumma tausta, LINTU = sovelluksen kultainen korostusvari.
"""

from PIL import Image, ImageDraw

TAUSTA = (57, 64, 75, 255)      # #39404b
LINTU = (224, 179, 102, 255)    # #e0b366
SIIPI = (196, 150, 78, 255)     # #c4964e

S = 1024  # piirtotarkkuus, skaalataan lopuksi alas


def lintu(scale=1.0, dy=0):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    def P(pts):
        return [((x - 512) * scale + 512, (y - 512) * scale + 512 + dy) for x, y in pts]

    def E(b):
        return P([(b[0], b[1]), (b[2], b[3])])

    d.rounded_rectangle(E((288, 792, 762, 824)), radius=16 * scale, fill=LINTU)  # oksa
    d.line(P([(500, 700), (494, 796)]), fill=LINTU, width=max(2, int(22 * scale)))
    d.line(P([(578, 700), (596, 796)]), fill=LINTU, width=max(2, int(22 * scale)))
    d.polygon(P([(600, 556), (844, 662), (862, 720), (776, 712), (575, 652)]), fill=LINTU)  # pyrsto
    d.ellipse(E((372, 396, 700, 724)), fill=LINTU)  # keho
    d.ellipse(E((296, 272, 524, 500)), fill=LINTU)  # paa
    d.polygon(P([(306, 376), (180, 404), (306, 434)]), fill=LINTU)  # nokka

    # siipi: kierretty ellipsi omalla tasolla
    w = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(w).ellipse([470, 470, 700, 610], fill=SIIPI)
    w = w.rotate(-22, resample=Image.BICUBIC, center=(585, 540))
    taso = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    taso.paste(w, (0, 0), w)
    if scale != 1.0 or dy:
        taso = taso.resize((int(S * scale), int(S * scale)), Image.LANCZOS)
        pohja = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        off = int((S - S * scale) / 2)
        pohja.paste(taso, (off, off + dy), taso)
        taso = pohja
    img.alpha_composite(taso)

    d.ellipse(E((372, 344, 424, 396)), fill=TAUSTA)  # silma
    return img


def tee(tiedosto, koko, scale=1.06, dy=-26):
    img = Image.new("RGBA", (S, S), TAUSTA)
    img.alpha_composite(lintu(scale, dy))
    img.resize((koko, koko), Image.LANCZOS).convert("RGB").save(tiedosto)
    print("kirjoitettu", tiedosto)


tee("icon-192.png", 192)
tee("icon-512.png", 512)
tee("apple-touch-icon.png", 180)
tee("favicon-48.png", 48)
# maskable: Android rajaa ikonin ympyraksi, joten lintu pienempana keskelle
tee("icon-maskable-512.png", 512, scale=0.66, dy=-16)
