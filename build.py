#!/usr/bin/env python3
"""
Kokoaa julkaistavan sivuston kansioon _site/.

GitHub Actions ajaa tämän automaattisesti joka kerta kun repoon lisätään tiedostoja.
Voit ajaa saman myös omalla koneella: python3 build.py

Mitä tämä tekee:
  1. etsii app/-kansiosta uusimman Claude Designista ladatun HTML-tiedoston
  2. kopioi sen nimellä index.html ja lisää siihen PWA-tiedot (manifest, ikonit, service worker)
  3. kopioi mukaan app/-kansion muut tiedostot sekä ikonit, manifestin ja sw.js:n
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "app"
OUT = ROOT / "_site"
JUURI_TIEDOSTOT = ["manifest.webmanifest", "sw.js"]
JUURI_KANSIOT = ["icons"]
PRECACHE_MAX = 3_000_000  # yli 3 MB tiedostoja ei tallenneta offline-välimuistiin
OHITA = {".DS_Store", "Thumbs.db", ".thumbnail"}


def virhe(viesti):
    print("VIRHE: " + viesti, file=sys.stderr)
    sys.exit(1)


def git_aika(polku):
    """Milloin tiedosto on viimeksi commitattu. 0 jos ei tiedossa."""
    try:
        ulos = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(polku.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        ).stdout.strip()
        return int(ulos) if ulos else 0
    except Exception:
        return 0


def valitse_html():
    """Uusin app/-kansion HTML-tiedosto: ensin commit-aika, sitten muokkausaika, sitten nimi."""
    ehdokkaat = [p for p in sorted(APP.glob("*.html")) if p.name not in OHITA]
    if not ehdokkaat:
        virhe("app/-kansiosta ei löytynyt yhtään .html-tiedostoa. "
              "Lataa peli Claude Designista ja lisää tiedosto app/-kansioon.")
    if len(ehdokkaat) == 1:
        return ehdokkaat[0]
    ehdokkaat.sort(key=lambda p: (git_aika(p), p.stat().st_mtime, p.name), reverse=True)
    print("app/-kansiossa on useita HTML-tiedostoja:")
    for p in ehdokkaat:
        print("   - " + p.name)
    return ehdokkaat[0]


def pwa_tagit(mani):
    nimi = mani.get("name", "Sovellus")
    lyhyt = mani.get("short_name", nimi)
    vari = mani.get("theme_color", "#000000")
    kuvaus = mani.get("description", "")
    rivit = [
        '<!-- PWA-tiedot lisätty automaattisesti (build.py). Älä lisää näitä Claude Designin tiedostoon. -->',
        '<link rel="manifest" href="manifest.webmanifest">',
        '<meta name="theme-color" content="%s">' % vari,
        '<meta name="mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-status-bar-style" content="black">',
        '<meta name="apple-mobile-web-app-title" content="%s">' % lyhyt,
        '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">',
        '<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">',
        '<link rel="icon" type="image/png" sizes="48x48" href="icons/favicon-48.png">',
    ]
    if kuvaus:
        rivit.append('<meta name="description" content="%s">' % kuvaus)
    return nimi, rivit


def kirjoita_index(lahde, mani):
    html = lahde.read_text(encoding="utf-8")
    nimi, rivit = pwa_tagit(mani)

    if "<title" not in html.lower():
        rivit.insert(1, "<title>%s</title>" % nimi)

    if "<html" in html.lower() and " lang=" not in html[:200].lower():
        html = html.replace("<html>", '<html lang="%s">' % mani.get("lang", "fi"), 1)

    lisays = "\n" + "\n".join(rivit) + "\n"
    if "</head>" in html:
        html = html.replace("</head>", lisays + "</head>", 1)
    elif "<body>" in html:
        html = html.replace("<body>", "<body>" + lisays, 1)
    else:
        html = lisays + html

    rekisterointi = (
        "\n<script>\n"
        "if ('serviceWorker' in navigator) {\n"
        "  window.addEventListener('load', function () {\n"
        "    navigator.serviceWorker.register('sw.js').catch(function () {});\n"
        "  });\n"
        "}\n"
        "</script>\n"
    )
    if "</body>" in html:
        html = html.replace("</body>", rekisterointi + "</body>", 1)
    else:
        html += rekisterointi

    (OUT / "index.html").write_text(html, encoding="utf-8")
    return nimi


def kopioi_app(valittu):
    for polku in APP.rglob("*"):
        if polku.name in OHITA:
            continue
        suht = polku.relative_to(APP)
        if polku.is_dir():
            (OUT / suht).mkdir(parents=True, exist_ok=True)
            continue
        # muut .html-tiedostot jätetään pois (vain valittu julkaistaan index.html:nä)
        if polku.suffix.lower() == ".html":
            continue
        (OUT / suht).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(polku, OUT / suht)


def kirjoita_sw(build_id):
    lahde = (ROOT / "sw.js").read_text(encoding="utf-8")
    lista = []
    for polku in sorted(OUT.rglob("*")):
        if not polku.is_file():
            continue
        suht = polku.relative_to(OUT).as_posix()
        if suht == "sw.js" or polku.stat().st_size > PRECACHE_MAX:
            continue
        lista.append("./" + suht)
    if "./index.html" in lista:
        lista.insert(0, "./")
    ulos = lahde.replace("__BUILD__", build_id)
    ulos = ulos.replace("__PRECACHE__", json.dumps(lista, indent=2, ensure_ascii=False))
    (OUT / "sw.js").write_text(ulos, encoding="utf-8")
    return lista


def main():
    if not APP.is_dir():
        virhe("app/-kansiota ei löydy.")

    mani_polku = ROOT / "manifest.webmanifest"
    if not mani_polku.is_file():
        virhe("manifest.webmanifest puuttuu.")
    mani = json.loads(mani_polku.read_text(encoding="utf-8"))

    valittu = valitse_html()

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    kopioi_app(valittu)
    for nimi in JUURI_TIEDOSTOT:
        if (ROOT / nimi).is_file():
            shutil.copy2(ROOT / nimi, OUT / nimi)
    for kansio in JUURI_KANSIOT:
        if (ROOT / kansio).is_dir():
            shutil.copytree(ROOT / kansio, OUT / kansio,
                            ignore=shutil.ignore_patterns("*.py", *OHITA))

    nimi = kirjoita_index(valittu, mani)
    build_id = os.environ.get("GITHUB_SHA", "")[:12] or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    precache = kirjoita_sw(build_id)

    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    print("")
    print("Julkaistava peli: %s  ->  index.html" % valittu.name)
    print("Sovelluksen nimi: %s" % nimi)
    print("Build:            %s" % build_id)
    print("Offline-välimuisti: %d tiedostoa" % len(precache))
    print("Valmis kansiossa _site/")


if __name__ == "__main__":
    main()
