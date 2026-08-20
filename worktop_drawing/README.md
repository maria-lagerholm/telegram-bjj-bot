# Bänkskiva badrum 1100 x 600 mm

Ritningsunderlag för CNC skärning av en kompaktlaminatskiva med nedsänkt tvättställ och blandare.
Djupet är 600 mm eftersom LG vill ha 100 mm luft bakom tvättmaskinen.

## Körning

```bash
pip install -r requirements.txt
python make_drawing.py
```

Filerna hamnar i `output/`:

- `bankskiva_badrum_1100x600.png` är bilden som skickas till verkstaden
- `bankskiva_badrum_1100x600.dxf` är exakt geometri i mm för maskinen

## Moduler

- `specs.py` samlar alla mått på ett ställe, ändra bara här
- `drawing_helpers.py` ritar måttlinjer, hänvisningar och centrummarkeringar
- `plan_drawing.py` bygger planvyn med noter och håltabell
- `dxf_export.py` skriver samma geometri som DXF
- `make_drawing.py` kör allt och sparar filerna

## Produkter

- Tvättställ: Villeroy & Boch Loop & Friends 4A590001, Ø390 mm, innerkant Ø330 mm, höjd 190 mm
- Blandare: Vesani Wilma BLWILMACH, hålkrav 32 till 35 mm, piputsprång 130 mm, blandarhus Ø55 mm
- Tvättmaskin: LG F2Y5PYP3W, 600 x 475 x 850 mm
- Konsol: 3 st Svedbergs 47920, 30 till 40 x 303 x 403 mm (BxHxD), fästs i väggen
