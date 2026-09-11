# Tirppatunnistin – GitHub Pages + kotinäytön sovellus (PWA)

Tämä repo julkaisee Tirppatunnistimen osoitteessa `https://<käyttäjänimi>.github.io/<repon-nimi>/`
ja tekee siitä puhelimeen asennettavan sovelluksen.

Idea: **Claude Designista ladattu HTML-tiedosto menee sellaisenaan `app/`-kansioon.**
Nimeä ei tarvitse muuttaa eikä tiedostoon tarvitse lisätä mitään. GitHub kokoaa
julkaistavan sivun automaattisesti: se ottaa uusimman HTML:n, nimeää sen
`index.html`:ksi ja lisää siihen PWA-tiedot.

---

## 1. Käyttöönotto (tehdään vain kerran)

1. Luo GitHubiin uusi julkinen repo, esim. `tirppatunnistin`.
2. Lisää sinne **kaikki tämän kansion tiedostot** (myös `.github`-kansio).
   Web-käyttöliittymässä: *Add file → Upload files*, raahaa kansion sisältö, *Commit changes*.
3. Mene repon **Settings → Pages**. Kohdassa *Build and deployment* valitse
   **Source: GitHub Actions**. (Ei "Deploy from a branch".)
4. Odota pari minuuttia. **Actions**-välilehdellä näkyy ajo *Julkaise Tirppatunnistin*;
   kun siinä on vihreä täppä, peli on auki osoitteessaan.

> Jos `.github`-kansion lataaminen ei onnistu raahaamalla, tee tiedosto käsin:
> *Add file → Create new file*, nimeksi `.github/workflows/pages.yml`, ja liitä
> sisältö tästä paketista samannimisestä tiedostosta.

---

## 2. Uuden version julkaisu (arjen rutiini)

1. Lataa peli Claude Designista (zip tai pelkkä HTML).
2. Lisää HTML-tiedosto repon **`app/`-kansioon** – millä nimellä tahansa,
   esim. `Tirppatunnistin v3.dc.html`.
3. *Commit changes*. Noin minuutin päästä uusi versio on livenä.

Vanhat versiot saavat jäädä `app/`-kansioon: julkaistavaksi valitaan aina se
HTML, joka on **viimeksi lisätty tai muutettu**. Siistimpää on silti poistaa vanha.

**Jos latasit koko zipin ja siinä on muuttunut muutakin kuin HTML**
(lintutiedot, uusi taustakuva), korvaa `app/`-kansiossa myös nämä samoista
kohdista: `bird-data.js`, `support.js`, `image-slot.js` ja tarvittavat
`uploads/`-kuvat. Zipin `screenshots/`-kansiota ja muita `uploads/`-kuvia ei
tarvita – ne olivat suunnittelun aikaisia kuvia (n. 40 MB), joita peli ei käytä.

---

## 3. Kotinäytölle asentaminen

- **iPhone / iPad (Safari):** avaa sivu → *Jaa* → *Lisää kotivalikkoon*.
- **Android (Chrome):** avaa sivu → valikko (⋮) → *Asenna sovellus* / *Lisää kotinäytölle*.

Sovellus avautuu ilman selainpalkkeja ja ikonina on kultainen lintu tummalla pohjalla.

---

## 4. Nimen, värin ja ikonin vaihtaminen

Kaikki nimet ja värit tulevat tiedostosta **`manifest.webmanifest`**
(`name`, `short_name`, `description`, `theme_color`). Sama nimi menee myös
selaimen välilehdelle ja kotinäytön kuvakkeen alle.

Ikonit ovat kansiossa `icons/`. Voit korvata ne omilla PNG-kuvilla (samat nimet
ja koot) tai ajaa `icons/tee-ikonit.py` omalla koneella, jos haluat vaihtaa värit.

---

## 5. Hyvä tietää

- Peli hakee lintujen kuvat ja äänet **Wikimedia Commonsista** ja
  React-kirjaston **unpkg.comista**, joten nettiyhteys tarvitaan pelaamiseen.
  Service worker tallentaa sovelluksen rungon välimuistiin, joten käynnistys on
  nopea ja sovellus avautuu myös hetkellisessä katkossa.
- Uusi versio korvaa vanhan välimuistin automaattisesti, kun sovellus avataan.
  Jos vanha sisältö silti jää näkyviin, sulje sovellus kokonaan ja avaa uudelleen.
- `_site/`-kansio syntyy vain koonnin aikana. Sitä ei tarvitse eikä kannata
  lisätä repoon.

## 6. Kansiot

| Polku | Mitä |
|---|---|
| `app/` | Claude Designista ladattu peli ja sen apuskriptit. **Tänne uudet versiot.** |
| `icons/` | Kotinäytön ikonit + ikonien luontiskripti |
| `manifest.webmanifest` | Sovelluksen nimi, värit ja ikonit |
| `sw.js` | Service worker (offline-välimuisti) |
| `build.py` | Kokoaa julkaistavan sivuston `_site/`-kansioon |
| `.github/workflows/pages.yml` | Automaattinen julkaisu GitHub Pagesiin |
| `vanhat/` | Aiemmat versiot (`Tirppatunnistin.dc.html`, `Tirppatunnistin dark.dc.html`). Ei julkaista. |

## 7. Jos jotain menee vikaan

Katso repon **Actions**-välilehti ja avaa viimeisin ajo – loki kertoo, minkä
HTML-tiedoston se valitsi ja mikä kaatui. Yleisimmät syyt:

- **404-sivu:** Settings → Pages → Source ei ole *GitHub Actions*.
- **Ajo ei käynnisty:** `pages.yml` ei ole polussa `.github/workflows/`.
- **"ei löytynyt yhtään .html-tiedostoa":** HTML on repon juuressa, ei `app/`-kansiossa.
