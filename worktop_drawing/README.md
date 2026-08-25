# Bänkskiva badrum 1100 x 600 x 12 mm

Ritningsunderlag för CNC skärning av en kompaktlaminatskiva med nedsänkt tvättställ och blandare.
Djupet är 600 mm eftersom LG vill ha 100 mm luft bakom tvättmaskinen.
Färdig höjd är 902 mm till skivans ovansida.

## Körning

```bash
pip install -r requirements.txt
python make_drawing.py
```

Filerna hamnar i `output/`:

- `bankskiva_badrum_plan.png` är planvyn med noter och håltabell
- `bankskiva_badrum_sektion.png` är sektion A-A med höjdkedjan
- `bankskiva_badrum_1100x600.dxf` är exakt geometri i mm för maskinen

## Moduler

- `specs.py` samlar alla mått på ett ställe, ändra bara här
- `drawing_helpers.py` ritar måttlinjer, hänvisningar och centrummarkeringar
- `plan_drawing.py` bygger planvyn med noter och håltabell
- `elevation_drawing.py` bygger sektionen som visar höjderna
- `checks.py` räknar ut marginaler och vikt och jämför mot gränsvärdena
- `dxf_export.py` skriver samma geometri som DXF
- `make_drawing.py` kör allt, skriver ut kontrollen och sparar filerna

## Höjdkedja

| Steg | Mått |
| --- | --- |
| Tvättmaskinens topp | 850 |
| Luftspalt över maskinen | + 10 |
| Konsolarmens profilhöjd, mät på din konsol | + 30 |
| Underkant skiva | = 890 |
| Skivans tjocklek | + 12 |
| Färdig höjd, ovansida skiva | = 902 |

## Kontroll

`make_drawing.py` skriver ut en rad per kontroll. Alla ska stå OK.

```
OK  frihäng framkant                 197.0  (max 200)
OK  största stödavstånd              595.0  (max 600)
OK  konsol till urtag                 15.0  (min 10)
OK  material mellan hålen             40.6  (min 30)
OK  blandarhus till keramikkant       10.6  (min 5)
OK  luft över maskinen                10.0  (min 5)
OK  färdig höjd                      902.0  (runt 900)
OK  vikt kg                            9.8  (max 15)
```

Gränserna för frihäng och stödavstånd kommer från tillverkarens anvisning för kompaktlaminat.

## Produkter

- Tvättställ: Villeroy & Boch Loop & Friends 4A590001, Ø390 mm, innerkant Ø330 mm, höjd 190 mm
- Blandare: Vesani Wilma BLWILMACH, hålkrav 32 till 35 mm, piputsprång 130 mm, blandarhus Ø55 mm
- Tvättmaskin: LG F2Y5PYP3W, 600 x 475 x 850 mm
- Konsol: 3 st Svedbergs 47920, 30 mm bred, 303 mm hög, 403 mm djup, fästs i väggen

Var skivan går att köpa i 12 mm står i `produkter.md`.
