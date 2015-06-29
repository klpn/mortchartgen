---
title: 'Dokumentation till Mortalitetsdiagram'
author: Karl Pettersson
lang: swedish
mainlang: swedish
classoption: a4paper
fontsize: 12pt
...

#Introduktion
Syftet med denna sida är att erbjuda överskådlig information om orsaksspecifika mortalitetstrender i befolkningar. Diagram kan visas och laddas ned efter val av befolkning, åldersgrupp och dödsorsaksgrupp. De mått som redovisas i diagrammen har beräknats med hjälp av öppna data från @whomort, men WHO är inte ansvariga för något innehåll på sidan.

Det finns sedan tidigare flera webbplatser med visualiseringar av mortalitetstrender. En av de mest avancerade är @ihmecodviz, som innehåller data för alla världens länder och använder komplicerade algoritmer för att justera för osäkerhet i underliggande data. Denna webbplats genererar diagrammen dynamiskt och kan ibland vara tungrodd. Dessutom sträcker sig visualiseringarna för närvarande inte längre tillbaka än till 1980, samtidigt som @whomort för många befolkningar har data tillgängliga från 1950. @mortrends är en webbplats med en stor mängd statiska diagram baserade på @whomort. Dock underhålls denna webbplats inte längre sedan dess skapare avlidit.

Föreliggande sida är gjord för att snabbt och enkelt ta fram relevanta visualiseringar av mortalitetstrender från mitten av 1900-talet fram till våra dagar. Den innehåller ingen kod som körs på serversidan med kopplingar till några databaser. Alla diagram är färdiga SVG-filer, som jag genererat lokalt med hjälp av ett Pythonskript, som använder sig av matplotlib (@Hunter:2007). Gränssnittet för val av diagram bygger på jQuery.

#Mått på dödlighet
*Dödstal* är ett grundläggande mått på dödlighet. Dödstalet i en orsak $c$ i en befolkning $x$ under en tidsperiod t, $m_{c,t}(x)$, beräknas enligt $m_{c,t}(x)=n_{c,t}(x)/p_t(x)$, där $n_{c,t}$ är antalet dödsfall i $c$ under $t$ och $p_t(x)$ är medelfolkmängden i $x$ under $t$. Om $x$ utgör ett brett åldersintervall kommer dödstalen i olika orsaker ofta att påverkas av trender i åldersfördelningen. Stigande medelålder hos befolkningen ger ofta ökade dödstal i åldersrelaterade sjukdomsgrupper som cancer, hjärtsjukdomar och demens. @whomort tillhandahåller data över folkmängd och antal dödsfall i 5-åriga åldersintervall, med vilka det är möjligt att beräkna dödstal som inte är så känsliga för dessa trender, och därför ger ett bättre mått på direkta effekter av sådant som sjukvård och miljöfaktorer på dödlighet. Dödstal i snäva åldersintervall drabbas dock ofta av slumpmässiga förändringar i mindre befolkningar. På denna sida redovisas ovägda medelvärden av åldersspecifika dödstal i de 5-årsintervall som ingår i bredare åldersintervall (för närvarande 15--44, 45--64, 65--74 och 75--84 år).

Tillgängliga data utgår från en binär könskategorisering. För de flesta dödsorsaker varierar dödstalen signifikant mellan kvinnor och män (och även tidstrenderna divergerar ofta, t.ex.\ när det gäller ischemisk hjärtsjukdom och lungcancer), och alla diagram redovisar därför könsspecifika trender.

#Underliggande dödsorsaker och konstlade trender
Alla data gäller s.k. underliggande dödsorsaker. För varje dödsfall registreras precis en underliggande dödsorsak i befolkningarnas statistik, och den definieras som den sjukdom som inledde det morbida förlopp som ledde till döden eller omständigheterna kring den olycka eller våldshandling som orsakade den dödliga skadan [@icd10v2ed10, s. 31]. I en del fall är begreppet relativt oproblematiskt, t.ex.\ att primära tumörer och inte metastaser är underliggande dödsorsak vid dödsfall i cancer. I många fall kan emellertid tolkningen inte självklar. Detaljerade instruktioner för val av underliggande dödsorsak har ändrats mellan olika ICD-versioner, och praxis för val av underliggande dödsorsak kan skilja sig mellan olika befolkningar som använder samma ICD-version. Exempel på fall där tolkningen skiljer sig mellan befolkningar och tidsperioder, vilket kan ge upphov till konstlade trender:

* Diabetes som underliggande dödsorsak hos personer som dött av hjärtinfarkt eller slaganfall.
* Lunginflammation som underliggande dödsorsak hos personer med bakomliggande sjukdomar som ökar risken för lunginflammation.

För ICD-versionerna före ICD-10 finns inte uppgifter om dödsorsak tillgängliga på detaljnivå: i stället används förkortade listor, som de s.k.\ A-listorna i ICD-7 och ICD-8 och BTL (Basic Tabulation List) i ICD-9. Det bidrar till att det ofta är svårt att konstruera epidemiologiskt meningsfulla kategorier som någorlunda väl täcker samma sjukdomsgrupper för de olika ICD-versionerna, vilket märks t.ex.\ på de olika grupperna av infektionssjukdomar som presenteras nedan.

År då det skett byte av ICD-lista i en befolkning har markeras i rött längs $x$ i diagrammen: $07A$ och $08A$ anger ICD-7 och ICD-8 med A-lista, $09B$ anger ICD-9 med BTL, $103$ och $104$ anger ICD-10 med koder på tre respektive fyra tecken (den mest detaljerade nivån) och $10M$ anger ICD-10 med koder på tre tecken för vissa orsaker och fyra tecken för andra. Kraftiga förändringar som uppträder i anslutning till byte av klassifikation kan i regel antas vara konstlade.

#Inkluderade dödsorsaksgrupper
<!-- Infektioner generellt
:    ICD-6/7: 001--138, 340, 470--493, 600; ICD-8: 001--136, 320, 460--486, 590; ICD-9: 001--139, 279.5, 310--312, 320--322, 480--487, 590; ICD-10: A00--B99, G00, G03, J00--J22, N10--N12 *Inkluderar infektioner i inledningskapitlet i ICD-versionerna (epidemiska infektioner, sepsis etc.), meningit, luftvägsinfektioner och njurinfektioner.* -->

Tuberkulos
:    ICD-6/7: 001--019; ICD-8: 010--019; ICD-9: 010--018; ICD-10: A15--A19 *Inkluderar lungtuberkulos och andra former av tuberkulos.*

Könssjukdomar/HIV
:    ICD-6/7: 020--035; ICD-8: 090--098; ICD-9: 090--099, 279.5, 279.6; ICD-10: A50--A64, B20--B24 *Inkluderar syfilis och andra infektioner som huvudsakligen överförs sexuellt samt HIV/AIDS (från ICD-9).*

Luftvägsinfektioner 
:    ICD-6/7: 470--500; ICD-8: 460--486; ICD-9: 460--466, 480--487; ICD-10: J00--J22,  *Inkluderar influensa, lunginflammation och andra luftvägsinfektioner (ej tuberkulos). Ofta känslig för konstlade trender när det gäller rapportering av dessa som underliggande dödsorsak.*

Magtarminfektioner 
:    ICD-6/7: 040--043, 045--048, 571, 572; ICD-8: 000--003, 004, 006, 008, 009; ICD-9: 001--009; ICD-10: A00--A09  *Inkluderar olika typer av infektioner i magtarmkanalen.*

Allmänna bakterieinfektioner
:    ICD-6/7: 044, 050--053, 055--058, 060--062, 340, 600; ICD-8: 005, 007, 020--039, 320, 590; ICD-9: 020--041, 320--322, 590; ICD-10: A20--A49, G00, G03, N10--N12 *Inkluderar sepsis och andra bakteriella infektioner i inledningskapitlet i ICD-versionerna som inte ingår i ovanstående kategorier, meningit och njurinfektioner.*

Övriga infektioner
:    ICD-6/7: 036--039, 049, 054, 059, 063--138; ICD-8: 040--089, 099--136; ICD-9: 045--088, 100--139; ICD-10: A65--B19, B25--B99 *Inkluderar infektioner i inledningskapitlet i ICD-versionerna förutom de som ingår i ovanstående kategorier, som olika infektioner orsakade av virus, parasiter och svampar och ospecificerade infektioner. Dramatiska ökningar och minskningar bland framför allt yngre män i vissa befolkningar under 80- och 90-talen beror på att ospecifika koder i denna kategori använts för HIV-infektion under vissa perioder.*

Tumörer generellt
:    ICD-6/7/8/9: 140--239; ICD-10: C00--D48

Magsäckscancer
:    ICD-6/7/8/9: 151; ICD-10: C16

Lungcancer
:    ICD-6/7: 162--163; ICD-8/9: 162; ICD-10: C33--C34 *Inkluderar cancer i luftstrupe och bronk.*

Bröstcancer
:    ICD-6/7: 170; ICD-8/9: 174; ICD-10: C50

Prostatacancer
:    ICD-6/7: 177; ICD-8/9: 185; ICD-10: C61 *Inkluderar inte åldersgrupper under 45 år på grund av alltför få fall.*
Diabetes
:    ICD-6/7: 260; ICD-8/9: 250; ICD-10: E10--E14 *Diabetes mellitus (typ 1 eller typ 2). Benägenheten att rapportera diabetes snarare än komplikationer (t.ex. ischemisk hjärtsjukdom) som underliggande dödsorsak varierar ofta mellan befolkningar och tidsperioder.*

Cirkulation
:    ICD-6/7: 330--334, 400--468; ICD-8/9: 390--459; ICD-10: F01, I00--I99 *Inkluderar hjärtsjukdomar, slaganfall (för ICD-10 även vaskulär demens) och andra åkommor i cirkulationsorganen. "Hjärtkärlsjukdom" och "kardiovaskulär sjukdom" används ofta som synonyma uttryck, men de kan även syfta på undergrupper av kategorin.* 

Hjärtsjukdom
:    ICD-6/7: 400--447; ICD-8/9: 390--429; ICD-10: I00--I51 *Inkluderar hjärtrelaterade tillstånd, inklusive ischemisk hjärtsjukdom, högt blodtryck, lungkärlssjukdom, myokardit, kardiomyopati, klaffel och funktionella hjärtdiagnoser (t.ex.\ hjärtsvikt).*

Ischemisk hjärtsjukdom
:    ICD-6/7: 420--422; ICD-8/9: 410--414; ICD-10: I20--I25 *Inkluderar hjärtinfarkt och andra tillstånd som beror på otillräcklig syreförsörjning av hjärtmuskel. "Kranskärlssjukdom" används ofta som mer eller mindre synonymt uttryck. Den engelska förkortningen IHD ("ischemic heart disease") är också vanlig. Observera att begreppet inte finns i klassifikationer för ICD-8: den närmaste motsvarande kategorin i ICD-6/7, som kan tas fram utifrån de kategorier som finns tillgängliga via @whomort, är "arteriosklerotiska och degenerativa hjärtsjukdomar". För vissa befolkningar (t.ex.\ Italien och Japan) uppstår då tydliga konstlade trender vid övergången till ICD-8.*

Slaganfall
:    ICD-6/7: 330--334; ICD-8/9: 430--438; ICD-10: F01; I60--I69 *Inkluderar hjärnblödning, hjärninfarkt och andra sjukdomar i hjärnans blodkärl. För ICD-10 inkluderas även vaskulär demens.*

Övrig artärsjukdom
:    ICD-6/7: 450--456; ICD-8/9: 440--448; ICD-10: I70--I79 *Inkluderar artärsjukdomar som inte ingår i de båda ovanstående grupperna (ateroskleros utanför hjärtat eller hjärnan eller i ospecificerade delar av artärsystemet, aortabråck etc.). Inkluderar inte högt blodtryck.*

Cirkulation utom IHD
:    *Inkluderar alla koder i cirkulationskategorin utom de som ingår i ischemisk hjärtsjukdom.*

Cirkulation "icke ateroskleros"
:    *Inkluderar alla koder i cirkulationskategorin utom de som ingår i ischemisk hjärtsjukdom, slaganfall eller övrig artärsjukdom. I huvudsak rör det sig om de tillstånd som ingår i hjärtsjukdom ovan bortsett från ischemisk hjärtsjukdom. Benämningen "icke ateroskleros" skall inte tolkas för bokstavligt: denna kategori och ovanstående har medtagits p.g.a. den centrala betydelse ischemisk hjärtsjukdom och andra tillstånd som typiskt hänförts till "ateroskleros", och som ingår under slaganfall eller övrig artärsjukdom, haft när det gäller tidstrender för cirkulationskategorin som helhet i många befolkningar.*

Kronisk lungsjukdom
:    ICD-6/7: 501--527; ICD-8/9: 490--519; ICD-10: J00--J98 *Inkluderar KOL, astma och andra sjukdomar i andningsorganen utom infektioner och tumörer.*

Illa definierade orsaker
:    ICD-6/7/8/9: 780--799; ICD-10: R00--R99 *Inkluderar koder i näst sista kapitlet i ICD-klassifikationerna, som dödsfall utan specificerad orsak, symptom utan angiven bakomliggande orsak och "senilitet" (hög ålder utan angiven demens). En hög andel dödsfall i denna kategori för en befolkning och tidsperiod kan indikera bristande kvalitet hos statistiken och innebär att trender för andra dödsorsaker måste tolkas med försiktighet. Det finns koder i andra ICD-kapitel som kan betraktas som "illa definierade" när de rapporteras som underliggande dödsorsaker (t.ex. hjärt- eller andningssvikt utan angiven orsak). En del formellt väldefinierade koder kan i vissa befolkningar också överrapporteras på ett sätt som urholkar deras diagnostiska mening (t.ex. ischemisk hjärtsjukdom bland äldre).*

Yttre orsaker
:    ICD-6/7/8/9: E800--E999; ICD-10: V01--Y89 *Inkluderar olyckor, självmord, mord, legala ingripanden och även komplikationer i samband med vård (även om bakomliggande sjukdomar då ofta rapporteras som underliggande dödsorsak).*
Transportolyckor
:    ICD-6/7: E800--E866; ICD-8: E800--E845; ICD-9: E800--E848; ICD-10: V01--V99 *Inkluderar motorfordonsolyckor och andra typer av transportolyckor.*

Fallolyckor
:    ICD-6/7: E900--E904; ICD-8: E880--E887; ICD-9: E880--E888; ICD-10: W00--W19 *Trender kan påverkas av benägenheten att rapportera ospecificerade olyckor eller komplikationer vid fall (t.ex. blodpropp eller lunginflammation) som underliggande dödsorsak.*

Självmord
:    ICD-6/7: E963, E970--E979; ICD-8/9: E950--E959; ICD-10: X60--X84 *Inkluderar även fall med bakomliggande psykisk sjukdom (t.ex. depression). Inkluderar inte fall med oklar avsikt. Trender kan påverkas av benägenheten att rapportera självmord.*

#Inkluderade befolkningar
Jag inkluderar i första hand befolkningar med i stort sett kontinuerlig tillgång till data över dödsfall och befolkning från 1950-talet fram till 2000-talet. Detta innefattar till största delen länder i Västeuropa och Nordamerika samt andra höginkomstländer (t.ex.\ Australien, Nya Zeeland och Japan). Några kommentarer om enskilda befolkningar:

Israel
:    Endast data över judisk befolkning före 1975. 

Tyskland
:    Inkluderar Västtyskland före 1990. Data för Östtyskland (vars befolkning vid sammanslagningen var cirka en fjädedel av Västtysklands) och Västberlin finns inte tillgängliga för hela den föregående perioden, vilket hade gjort att kostlade trender ändå inte kunnat undvikas om inte befolkningarna redovisats separat.
