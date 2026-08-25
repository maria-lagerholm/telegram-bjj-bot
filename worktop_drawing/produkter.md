# Bänkskiva som passar våtrum, laminat och alternativ

Ritningen är gjord för 12 mm, men allt räknas om från `TOP_THICKNESS` i `specs.py`.
Kör `python make_drawing.py` så får du både kontrollen och materialtabellen.

## Djupet sorterar bort nästan allt

Tvättmaskinen är 475 mm djup och LG vill ha 100 mm luft bakom, alltså minst 575 mm.
Ritningen använder 600 mm. De färdiga badrumsbänkskivorna är gjorda för kommoder och
stannar på 460 mm, därför faller de bort direkt:

| Produkt | Material | Tjocklek | Djup | Varför inte |
| --- | --- | --- | --- | --- |
| Hafa OnTop | laminat på spånskiva | 19,6 mm | max 462 mm | 138 mm för smal |
| Svedbergs Poem, Kvarts | laminat | 20 mm | 460 mm | för smal |
| Macro Design Crown+ | Dekton | 12 mm | 460 mm | för smal |

Alla tre är i övrigt bra, fukttröga och gjorda för badrum. De passar bara inte över en
tvättmaskin. Ta inte den kampen, det finns inget sätt att göra en 462 mm skiva 600 mm djup.

## Det som är djupt nog

### Svedbergs Tvätt & Tork bänkskiva, bästa laminatvalet

Laminat på spånskiva, **28 mm tjock, 630 mm djup**, säljs i metervara upp till 2400 mm i sju
utföranden: vit, ljusgrå, mörkgrå, svart, kvarts, glimmer och skiffer.
BvB-bedömd och accepterad, SundaHus, listad i Svanens husproduktportal.

Det avgörande: Svedbergs skriver själva att skivan **passar till konsol 47920**, alltså exakt
den konsol ritningen bygger på. Detta är deras eget system för en bänk över tvättmaskin.

- BSK100 vit, **2 290 kr**, i lager hos prokakel.se
- BSK102 kvarts, **2 990 kr**, i lager hos prokakel.se
- BSK101 skiffer, BSK103 glimmer, samma upplägg

Kapas vid montering. Du kapar längden till 1100 mm och kan behålla 630 mm djup eller
klyva bakkanten till 600 mm. Framkanten är fabriksbehandlad, spara den.

Konsekvenser av 28 mm:

- färdig höjd blir **918 mm** istället för 902 mm, se tabellen nedan
- kärnan är spånskiva, alltså inte vattentät, alla kapsnitt och båda hålen måste tätas
- frihänget blir 227 mm vid 630 mm djup, men 28 mm spånskiva är styvare i böj än 12 mm
  kompaktlaminat, så det håller

### Kökslaminat 30 mm på mått med urtagen färdiga

Billigaste vägen. Samma leverantörer som redan står i ringlistan säljer laminat på mått i
610 till 635 mm djup, och laminat är deras huvudprodukt, så de svarar snabbt och gör
urtagen i fabrik enligt din DXF.

- Bänkskivabutiken **08-507 801 06**, kundservice@bankskivabutiken.se
- Bänkskivor Online, konfigurator med urtag för ho och blandare, pris direkt
- BARA Bänkskivor **0513-10450**, info@barabankskivor.se

Färdig höjd blir 920 mm. Samma spånskivekärna som ovan, samma tätningskrav.

### GetaCore 10 mm, om du vill ha tunt och vattentätt utan kompaktlaminat

Akrylbunden solid surface från Westag, skivor upp till 4100 x 1250 mm.
Westag anger att **Optimal 10 mm har samma stabilitet som 12 mm**. Porfri yta, går att limma
optiskt fogfritt, går att slipa om, bearbetas med vanliga träverktyg.

Med 10 mm blir färdig höjd **exakt 900 mm**, och skivan väger ca 8 kg, lättast av allt i
tabellen. Bänkskivabutiken har GetaCore i sortimentet, ring 08-507 801 06 och fråga om
10 mm med urtag Ø350 och hål Ø35.

## Vad tjockleken gör med höjden

Utskrift från `materials.py`. Höjd är ovansidan av skivan över golvet med 10 mm luftspalt.
Lägst är vad du kan komma ned till med 5 mm luftspalt, som är minsta rimliga för en maskin
som vibrerar och ska gå att dra ut.

```
material                              höjd  lägst   vikt  vattentät  600 djup
GetaCore 10 mm solid surface            900    895    7.9         ja        ja
kompaktlaminat 12 mm                    902    897    9.8         ja        ja
Corian 12 mm solid surface              902    897   11.5         ja        ja
kompaktlaminat 13 mm                    903    898   10.6         ja        ja
Hafa OnTop laminat 19,6 mm              910    905    8.1        nej       nej
Svedbergs Tvatt o Tork laminat 28 mm    918    913   10.7        nej        ja
kokslaminat pa spanskiva 30 mm          920    915   11.5        nej        ja
```

Två saker att läsa ur tabellen:

1. **Vikten är inget argument.** Allt landar mellan 8 och 12 kg, eftersom kompaktlaminat är
   dubbelt så tätt som spånskiva och därför väger nästan lika mycket i halva tjockleken.
   Välj alltså på höjd, vattentålighet och pris, inte på vikt.
2. **Tjockleken sätter golvet för höjden.** Maskinens topp ligger på 850 och konsolarmen är
   30 mm, så underkanten på skivan kan aldrig komma under 885. Med 28 eller 30 mm hamnar du
   på 918 till 920 mm hur du än vrider på det. Standard bänkhöjd är 900 mm.

## Om du väljer spånskivekärna, gör detta

Laminat på spånskiva är fukttrögt, inte vattentätt. Både Hafa och Svedbergs skriver i sina
egna skötselråd att snittytorna ska silikoneras vid håltagning, annars sväller kärnan.

1. Täta båda hålens kanter och alla kapsnitt med silikon, fuktspärr eller tätningslack
   innan tvättstället monteras.
2. Lägg en diffusionsspärr under skivan över maskinen, ånga från tvätten går uppåt.
3. Montera tvättstället med fog runt hela keramikkanten så vatten inte kryper ner i urtaget.
4. Torka bort stående vatten, det är det som förstör kärnan över tid.

Gör du detta håller en laminatskiva i badrum i många år, det är så gott som alla svenska
badrumsmöbler är byggda. Skippar du det sväller kanten runt urtaget inom ett par år.

## Ändra ritningen till valt material

Sätt tjocklek och densitet i `specs.py` och kör om. Densiteten är 1450 för kompaktlaminat,
1400 för GetaCore, 1700 för Corian och 680 för laminat på spånskiva.

```python
TOP_THICKNESS = 28
TOP_DENSITY = 680
```

```bash
python make_drawing.py
```

Höjdkedjan på sektion A-A, noterna och kontrollen räknas om automatiskt.
Väljer du 630 mm djup, sätt även `TOP_DEPTH = 630`. Då säger kontrollen FEL på frihänget,
227 mm mot gränsen 200 mm. Den gränsen kommer från kompaktlaminattillverkaren och gäller
inte för 28 mm spånskiva, så för Svedbergsskivan är det den enda varningen du kan ignorera.

## Ringordning

1. **prokakel.se** eller närmaste Svedbergs-återförsäljare, BSK100 eller BSK102,
   28 mm, 630 djup, passar konsol 47920. I lager.
2. **Bänkskivabutiken 08-507 801 06**, fråga om tre saker i samma samtal:
   GetaCore 10 mm, kompaktlaminat 13 mm, och kökslaminat 30 mm, alla 1100 x 600 mm
   med urtag Ø350 och hål Ø35. Be om pris på alla tre så kan du välja på höjd och pris.
3. **BARA Bänkskivor 0513-10450** om du vill ha en svensk fabrik med ritningsgodkännande.

## Ringtext

Hej, jag ska sätta en bänkskiva över en tvättmaskin i badrummet, på Svedbergs
konsol 47920. Skivan ska vara 1100 gånger 600 millimeter med urtag diameter 350
för nedsänkt tvättställ och hål diameter 35 för blandare. Jag har ritning och DXF.
Vad kan ni erbjuda i laminat eller solid surface som klarar våtrum, och hur tjock
blir skivan? Tjockleken avgör min färdiga höjd så den behöver jag veta.
