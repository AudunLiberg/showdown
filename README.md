# Showdown  ![pikachu](https://play.pokemonshowdown.com/sprites/xyani/pikachu.gif)
Showdown er et rammeverk for å lage bots til Pokémon Showdown, basert på [pmariglias bot med samme navn](https://github.com/pmariglia/showdown). Rammeverket er i første omgang laget til bruk i Bekks AlgPip-faggruppe.

## Oppsett

### Installer

1. Sørg for å ha Python 3 installert.
2. Klon repoet.
3. Installer avhengigheter med `pip install -r requirements.txt`.

### Registrer bot-bruker

1. Registrer en bruker til boten din på [https://play.pokemonshowdown.com/](https://play.pokemonshowdown.com/). E-postadresse er beleilig nok ikke påkrevd.
2. Oppgi brukernavn og passord til boten i `.env`-filen i repoet.

### Kjør
1. Start boten med `python run.py`. En kamp vil umiddelbart begynne.
2. Følg med på kampen via loggingen til konsoll eller via grensesnittet på [https://play.pokemonshowdown.com/](https://play.pokemonshowdown.com/).

## Utvikling

### Programmering av boten

Oppførselen til boten kodes i filen `./showdown/sandbox/algpip_plays_pokémon.py`. Inntil du forbedrer den er alle beslutninger vilkårlige. Se filen for nærmere instruksjoner og hjelp.

### Konfigurasjon
All konfigurasjon gjøres i `.env`-filen. I første omgang ser den slik ut:
```
WEBSOCKET_URI=sim.smogon.com:8000
PS_USERNAME=<username>
PS_PASSWORD=<password>
BOT_MODE=SEARCH_LADDER
RUN_COUNT=1
```

`RUN_COUNT` spesifiserer hvor mange kamper boten skal spille før den terminerer. `BOT_MODE` avgjør hvem boten skal spille mot. Det er tre alternativer:
1. `SEARCH_LADDER` utfordrer en tilfeldig menneskelig spiller til kamp. Disse kampene teller inn på botens Elo-rating.
2. `CHALLENGE_USER` utfordrer brukeren oppgitt i `USER_TO_CHALLENGE`-variabelen til kamp. Oppgi f.eks. `USER_TO_CHALLENGE=AlgPip1`.
3. `ACCEPT_CHALLENGE` får boten til å ta imot utfordringer fra alle som utfordrer den.
