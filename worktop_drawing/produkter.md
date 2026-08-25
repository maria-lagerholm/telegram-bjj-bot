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

## Går vanlig spånlaminatskiva i badrum? Ja, med två villkor

**Reglerna säger inget om bänkskivor.** BBR, GVK och BKR handlar om tätskikt på golv och
väggar. En bänkskiva är inte ett ytskikt på golv eller vägg, så ingen regel förbjuder en
spånlaminatskiva i ett badrum. Vad som faktiskt regleras är att väggens tätskikt är intakt
och att konsolernas skruvhål tätas mot tätskiktet enligt Säker Vatteninstallation.
Skivan ska inte stå i våtzon 1, alltså inte i duschens direkta stänkzon. Över en tvättmaskin
är den inte det.

**Branschen säljer själv precis detta.** Hafa OnTop är laminat på kärna av spånskiva eller MDF,
säljs uttryckligen för badrum, anges hos Hornbach med användningsområde Inomhus och Våtrum,
och har 25 års garanti. Svedbergs Tvätt & Tork bänkskiva är också spånskiva med laminat, är
BvB-accepterad och listad i Svanens husproduktportal. Så svaret är ja, det är standardlösningen.

**Men köp inte en köksbänkskiva till det.** IKEA skriver rakt ut på EKBACKEN och SÄLJAN
"Bör ej användas i våtutrymmen", och 25-årsgarantin gäller inte i våtrum. IKEA:s egen
kundtjänstartikel säger att EKBACKEN och SÄLJAN passar i tvättstuga som inte är våtrum, och
att man för våtrum ska välja TOLKEN, ÅLSKEN eller HEMTRÄSK. Det betyder inte att skivan
förstörs på en månad. Det betyder att du står för risken själv och att tätningen längst ned
i denna fil inte är valfri.

Så: vill du ha garanti, ta en skiva vars tillverkare menar den för badrum, alltså Svedbergs.
Vill du ha billigast, ta en köksskiva och gör tätningen själv.

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

### Billigaste vägen, köksbänkskiva i spånlaminat som du kapar

Ingen våtrumsgaranti, men 649 kr istället för 2 290 kr, och du får marmoreffekten.

- **IKEA EKBACKEN**, spånskiva med laminat, **28 mm tjock, 635 mm djup**, kantlist medföljer
  för de kapade ändarna. 186 cm kostar **649 kr**, 246 cm kostar **799 kr**. Finns i
  **vit marmormönstrad**, alltså den marmoreffekt du frågade om från början. 186 cm-skivan
  väger 22,6 kg hel, din bit blir ca 11 kg.
- **Bauhaus**, LG Collection laminat 3020 x 610 x 28 mm. Baksidan har Spantex laminatbalans
  med inbyggd fuktspärr, vilket är bra just över en tvättmaskin.
- **Byggmax** och **Hornbach** har motsvarande laminatskivor i butik.

Vid 635 mm djup blir frihänget 232 mm framför konsolarmarna. Kontrollen säger FEL på det mot
gränsen 200 mm, men den gränsen gäller kompaktlaminat. 28 mm spånskiva är styvare i böj och
klarar det. Vill du ligga inom gränsen, klyv bakkanten till 600 mm.

### Vem gör vad om du köper i bygghandeln

| Arbete | Vem |
| --- | --- |
| Kapa till 1100 x 600, raka snitt | Bauhaus tillsågning, mot avgift på varor köpta hos dem. Hornbach sågservice. |
| Urtag Ø350 och hål Ø35 | Inte bygghandeln. Bauhaus skriver uttryckligen att de inte gör hål för hoar. Snickare med sticksåg, eller Ekdahls 0370-733 70. |
| Allt färdigt i ett paket | Bänkskivabutiken 08-507 801 06, BARA 0513-10450, Bänkskivor Online. |

I 28 mm spånskiva är hålen enkla, vanlig sticksåg med fintandat blad räcker. Det är i
kompaktlaminat det krävs fräs. Så den här vägen är den som en vanlig snickare gör snabbast.

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

## Tätning, det enda du inte får hoppa över

Laminat på spånskiva är fukttrögt, inte vattentätt. Både Hafa och Svedbergs skriver i sina
egna skötselråd att snittytorna ska silikoneras vid håltagning, annars sväller kärnan.
Ritningen lägger till en not om detta automatiskt när `TOP_DENSITY` är satt under 1000.

1. Täta båda hålens kanter och alla kapsnitt med silikon, fuktspärr eller tätningslack
   innan tvättstället monteras. Detta är det viktigaste momentet i hela jobbet.
2. Lägg en diffusionsspärr under skivan över maskinen, ånga från tvätten går uppåt.
3. Montera tvättstället med fog runt hela keramikkanten så vatten inte kryper ner i urtaget.
4. Sätt kantlist eller fasa och täta de kapade ändarna, IKEA levererar list till EKBACKEN.
5. Täta konsolernas skruvhål i väggen mot tätskiktet, det är det enda som branschreglerna
   faktiskt kräver av dig här.
6. Torka bort stående vatten, det är det som förstör kärnan över tid.

Gör du detta håller en laminatskiva i badrum i många år, det är så gott som alla svenska
badrumsmöbler är byggda. Skippar du punkt 1 sväller kanten runt urtaget inom ett par år.

## Ändra ritningen till valt material

Sätt material, tjocklek och densitet i `specs.py` och kör om. Densiteten är 1450 för
kompaktlaminat, 1400 för GetaCore, 1700 för Corian och 680 för laminat på spånskiva.

```python
MATERIAL_NAME = "laminat pa spanskiva"
TOP_THICKNESS = 28
TOP_DENSITY = 680
```

Rubrik, noter, höjdkedja, måttsättning och kontroll räknas om från dessa tre rader.
Är densiteten under 1000 lägger ritningen själv till noten om att täta kapsnitt och hålkanter.

```bash
python make_drawing.py
```

Höjdkedjan på sektion A-A, noterna och kontrollen räknas om automatiskt.
Väljer du 630 mm djup, sätt även `TOP_DEPTH = 630`. Då säger kontrollen FEL på frihänget,
227 mm mot gränsen 200 mm. Den gränsen kommer från kompaktlaminattillverkaren och gäller
inte för 28 mm spånskiva, så för Svedbergsskivan är det den enda varningen du kan ignorera.

## Kostnad och risk, hela bilden

| Väg | Pris för skivan | Avsedd för våtrum | Färdig höjd |
| --- | --- | --- | --- |
| IKEA EKBACKEN 186 cm, kapa själv | 649 kr | nej, garantin gäller ej | 918 |
| Bauhaus eller Hornbach laminat plus sågservice | ca 1 000 till 1 500 kr | nej | 918 till 920 |
| Svedbergs BSK100 vit | 2 290 kr | ja | 918 |
| Svedbergs BSK102 kvarts | 2 990 kr | ja | 918 |
| Kökslaminat på mått med urtag från fabrik | offert | nej | 920 |
| Kompaktlaminat 12 mm på mått | offert, ca 4 000 kr och uppåt | ja, vattentät | 902 |
| GetaCore 10 mm på mått | offert | ja, vattentät | 900 |

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
