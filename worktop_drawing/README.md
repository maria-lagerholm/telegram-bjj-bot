# Bänkskiva badrum 1100 x 600 x 28 mm

Ritningsunderlag för skärning av urtag i en IKEA EKBACKEN måttbeställd bänkskiva med nedsänkt
tvättställ och blandare. Djupet är 600 mm eftersom LG vill ha 100 mm luft bakom tvättmaskinen.

## Körning

```bash
pip install -r requirements.txt
python make_drawing.py
python checks.py
python drain_check.py
```

Filerna hamnar i `output/`:

- `bankskiva_badrum_1100x600.png` är bilden som skickas till verkstaden
- `bankskiva_badrum_1100x600.dxf` är exakt geometri i mm för maskinen

## Moduler

- `specs.py` samlar alla mått på ett ställe, ändra bara här
- `drawing_helpers.py` ritar måttlinjer, hänvisningar och centrummarkeringar
- `plan_drawing.py` bygger planvyn med noter och håltabell
- `edge_detail.py` ritar snittet genom urtagets kant
- `dxf_export.py` skriver samma geometri som DXF
- `checks.py` skriver ut alla marginaler så måtten kan kontrolleras
- `heights.py` samlar höjdmåtten för avloppet, fyll i uppmätt färdig höjd här
- `drain_check.py` räknar ut anslutningshöjder och hur långt förlängningsrör som behövs
- `make_drawing.py` kör allt och sparar filerna

## Produkter

- Bänkskiva: IKEA EKBACKEN måttbeställd, ljusgrå betongmönstrad, laminat på spånskiva, 28 mm,
  djupklass 45,1 till 63,5 cm, kantlist på alla 4 sidor
- Tvättställ: Villeroy & Boch Loop & Friends 4A590001, Ø390 mm, innerkant Ø330 mm, höjd 190 mm
- Blandare: Vesani Wilma BLWILMACH, hålkrav 32 till 35 mm, piputsprång 130 mm, blandarhus Ø55 mm
- Tvättmaskin: LG F2Y5PYP3W, 600 x 475 x 850 mm, minst 100 mm bakom och 20 mm på sidorna
- Konsol: 3 st Svedbergs 47920, 30 till 40 x 303 x 403 mm (BxHxD), fästs i väggen
- Avlopp: Purus Design S-böj G32xØ40 krom (RSK 8075422) med Purus tvättmaskinsanslutning
  G32/G40 x 32 mm (RSK 8077137)
- Förlängning vid för hög färdig höjd: Faluplast förkromat avloppsrör 40 x 950 mm (RSK 2912963)
  och klämringskoppling Ø40/Ø40 (RSK 2912020)
