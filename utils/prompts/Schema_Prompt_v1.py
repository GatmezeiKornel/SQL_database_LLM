SCHEMA_PROMPT = """
This query will run on a database whose schema is represented in this string:
CREATE TABLE ATCKONYV(
ATC VARCHAR2(7), -- ATC code
MEGNEV VARCHAR2(250), --Hungarian name
ANGOL VARCHAR2(250), --English name
HATOANYAG VARCHAR2(250) --Substance name for ATC code
);

CREATE TABLE BNOHOZZAR(
EUPONT_ID INTEGER, --foreign key for EUPONT
BNO_ID_ID INTEGER --foreign key for BNOKODOK
);

CREATE TABLE BNOKODOK(
ID INTEGER PRIMARY KEY,
KOD VARCHAR2(32), --BNO code
LEIRAS VARCHAR2(4000) --BNO description
);

CREATE TABLE EUHOZZAR(
EUPONT_ID INTEGER, --foreign key for EUPONT
GYOGYSZ_ID INTEGER --foreign key for GYOGYSZ
);

CREATE TABLE EUINDIKACIOK(
ID INTEGER PRIMARY KEY,
EUPONT_ID INTEGER, --foreign key for EUPONTOK
NDX INTEGER, --Indication number
LEIRAS VARCHAR2(4000) --description of the indication
);

CREATE TABLE EUJOGHOZZAR(
EUPONT_ID INTEGER, --foreign key for EUPONTOK
KATEGORIA_ID INTEGER, --identifier of the type of prescription restrictions
KATEGORIA VARCHAR2(64), --description of the identifier of the type of prescription restrictions
JOGOSULT VARCHAR2(64), --subscription right
JIDOKORLAT INTEGER, --recommended number of months from the date of medicine prescription (if 0 it doesn't matter)
SZAKV_ID INTEGER, --foreign key for SZAKVKODOK
KIINT_ID INTEGER --foreign key for KIINTOR
);

CREATE TABLE EUPONTOK(
ID INTEGER PRIMARY KEY,
EUTIP VARCHAR2(32), --type of aid, (values: Gyógyszer: EÜ50, EÜ70, EÜ90, EÜ100, GYSE: Normatív, EÜ emelt, EÜ Kiemelt)
KODSZAM INTEGER, --first half of the indication code before "/"
PERJEL VARCHAR2(32), --second half of the indication code after "/" (ISO code)
IND_TIP VARCHAR2(4000) --indication type: 'G' if medicine, 'S' if GYSE
);

CREATE TABLE GYOGYSZ(
ID INTEGER PRIMARY KEY,
KOZHID INTEGER, --OGYÉI által kezelt, időben változatlan, egyedi termékazonosító. Ha az OGYÉI-ban még nem kapott ilyen azonosítót (centralizált törzskönyvezésnél, tápszernél fordulhat elő), akkor ideiglenesen egy 1000000 fölötti szám. (GYSE esetében nem használatos)
OEP_DAT VARCHAR2(8), --Az érvényesség kezdetének (hatálybalépésének) dátuma ééééhhnn formában
TIPUS VARCHAR2(1), --A készítmény / eszköz típusának kategóriája, G: gyógyszer, I: immun, T: tápszer, R: radiofarmakon, H: homeopátiás gyógyszer, A: alapanyag, F: FoNo, C: csomagolóanyag, K: készítési díj, S: gyógyászati segédeszköz
OEP_TTT VARCHAR2(9), --A készítmény / eszköz azonosítására a NEAK (Nemzeti Egészségbiztosítási Alapkezelő) által használt kód (TTT kód)
OEP_EAN VARCHAR2(13), --A készítmény EAN (European Article Numbering) kódja (GYSE esetében nem használatos)
OEP_TK VARCHAR2(64), --A készítmény OGYÉI által kiadott törzskönyvi száma (GYSE esetében nem használatos)
OEP_NEV VARCHAR2(255), --A készítmény / eszköz neve
OEP_KSZ VARCHAR2(7), --A készítmény kiszerelése / eszköz mennyiségi egysége
OEP_ATC VARCHAR2(128), --Az NEAK által meghatározott ATC kód (GYSE esetében nem használatos)
HATOANYAG VARCHAR2(32), --A készítmény fő hatóanyagának neve (GYSE esetében nem használatos)
ADAGMOD INTEGER, --A készítmény adagolásmódjának azonosítója (GYSE esetében nem használatos)
ID_GYFORMA INTEGER, --A gyógyszerformához rendelt ID
GYFORMA VARCHAR2(100), --A teljes gyógyszerforma szöveges leírása (GYSE esetében nem használatos)
RENDELHET VARCHAR2(3), --A készítmény rendelhetőségének azonosítója: VN: Orvosi rendelvény nélkül is kiadható gyógyszerkésztímény, V: Kizárólag orvosi rendelvényre kiadható gyógyszerkészítmény, J: Szakorvosi/kórházi diagnózist követően járóbeteg-ellátásban alkalmazható gyógyszerkészítmény, SZ vagy Sz: Szakorvosi/kórházi diagnózist követően folyamatos szakorvosi ellenőrzés mellett alkalmazható gyógyszerkészítmény, I: Rendelőintézeti járóbeteg-szakellátást vagy fekvőbeteg-szakellátást nyújtó szolgáltatók által biztosított körülmények között alkalmazható gyógyszerkészítmény (GYSE esetében nem használatos)
EGYENID INTEGER, --Az OGYÉI által megállapított egyenértékűségi csoport azonosító száma. Ha nem tartozik egyenértékűségi csoportba, akkor értéke: -1 (GYSE esetében nem használatos)
POTENCIA VARCHAR2(64), --Potencia (homeopátiás szerek) (GYSE esetében nem használatos)
OHATO_MENNY INTEGER, --Összes hatóanyag tartalom (GYSE esetében nem használatos)
HATO_MENNY INTEGER, --Egy kiszerelési egységben levő hatóanyag tartalom (GYSE esetében nem használatos)
HATO_EGYS VARCHAR2(50), --OHATO_MENNY, HATO_MENNY mezők mennyiségi egysége (pl. mg) (GYSE esetében nem használatos)
KISZ_MENNY INTEGER, --A termékben levő kiszerelési egységek száma (GYSE esetében nem használatos)
KISZ_EGYS VARCHAR2(50), --A termékben levő kiszerelési egység egységneve (pl. db) (GYSE esetében nem használatos)
DDD_MENNY INTEGER, --DDD (átlagos napi dózis) értéke (GYSE esetében nem használatos)
DDD_EGYS VARCHAR2(50), --DDD_MENNY mennyiségi egysége (pl. mg) (GYSE esetében nem használatos)
DDD_FAKTOR INTEGER, --HATO_EGYS és DDD_EGYS közti átváltó szám (pl. g és mg esetén 1000) (GYSE esetében nem használatos)
DOT INTEGER, --A kiszerelés hány napra elegendő a WHO szerint  (GYSE esetében nem használatos)
ADAG_MENNY INTEGER, --A kiszerelés hány ADAG_EGYS-nek megfelelő mennyiséget tartlamaz
ADAG_EGYS VARCHAR2(50), --Az orvos által szokásosan felírt mennyiség egysége, pl.: tabletta, csepp, adagolókanál, ml, borsónyi (krémeknél), ..., stb.
OEP_TAR INTEGER, --Termelői ár (GYSE esetében nem használatos)
OEP_NKAR INTEGER, --Nagykereskedelmi ár (GYSE esetében nem használatos)
OEP_FAN INTEGER, --Fogyasztói ár nettó
OEP_FAB INTEGER, --Fogyasztói ár bruttó
NTK INTEGER, --Napi terápiás költség (GYSE esetében nem használatos)
OEP_ITM VARCHAR2(3), --A termék régi támogatásjelzése: 0NT: nem támogatott XXX: támogatás % amennyiben nominálisan támogatott, pl. 025, FIX: fixcsoport alapú támogatás, TFX: terápiás fixcsoport alapú támogatás, KOM: kombinációs felülvizsgálat alapú támogatás, EMT: egyedi méltányosságban támogatott.
OEP_JC1 VARCHAR2(1), --I: ha a készítmény / eszköz honvédelmi jogosultsággal felírható
OEP_JC2 VARCHAR2(1), --I: ha az eszköz közgyógy ellátott betegeknek felírható (gyógyszer és gyse termékek esetén)
OEP_JC3 VARCHAR2(1), --I: ha a készítmény / eszköz üzemi baleset esetén felírható
OEP_JC4 VARCHAR2(1), --I: ha a készítmény / eszköz EÜ kiemelt jogosultsággal felírható
OEP_JC5 VARCHAR2(1), --I: ha a készítmény / eszköz EÜ emelt jogosultsággal felírható
KGYKERET INTEGER, --1: közgyógy keret meghatározásakor figyelembe vehető, 2: közgyógy keret meghatározásakor nem vehető figyelembe
EGYSEGAR INTEGER, --HATO_EGYS-nyi hatóanyag ára (GYSE esetében nem használatos)
NORM_TIP VARCHAR2(16), --Támogatásra vonatkozó megjelölés, NT: nem támogatott, C<szám>: a külökónkeretes támogatás jogcímkódja. A normatív támogatás technikái: NOMIN: nominálisan (százalékosan) támogatott, HFIX: hatóanyagfix technikával támogatott, TFX: terápiás fix technikával támogatott,FIX: GYSE fix technikával támogatott,KOMBI: a kombinációs felülvizsgálat állapította meg a támogatásátGYSE esetében lehet NEMKIV, ami azt jelenti, hogy bár van normatív támogatása, nem váltható ki, csak közgyógyra.
NORM_SZAZ INTEGER, --Támogatás mértéke %-ban normatív támogatás esetén (pl. 0, 25, 55, 80) 
NORM_FIXID INTEGER, --Normatív fixcsoport azonosítója (GYSE esetében nem használatos)
NORM_REFNTK INTEGER, --Normatív fixcsoport referencia NTK-ja (GYSE esetében nem használatos)
OEP_INN INTEGER, --Normatív támogatás nettó
OEP_INB INTEGER, --Normatív támogatás bruttó
NORM_TERDIJ INTEGER, --A beteg által fizetendő térítési díj (normatív támogatás esetén)
NTK_TD INTEGER, --A beteg által fizetendő térítési díj alapján kiszámított napi terápiás költség (normatív támogatás esetén) (GYSE esetében nem használatos)
EUEM_TIP VARCHAR2(16), --Normatív jogcímen a kihordási idő (csak GYSE esetében  használatos) Normatív jogcímen a felírható mennyiség (csak GYSE esetében  használatos). Az EÜ emelt támogatás technikája: (null) : nem támogatott NOMIN: nominálisan (százalékosan) támogatott, HFIX: hatóanyagfix technikával támogatott, TFX: terápiás fix technikával támogatott, KOMBI: a kombinációs felülvizsgálat állapította meg a támogatását, BIOL: biológiai készítményekre vonatkozó szabályok szerint támogatott, LFX: kis molekulasúlyú heparinokra vonatkozó szabályok szerint támogatott.
EUEM_SZAZ INTEGER, --Támogatás mértéke %-ban EÜ emelt támogatás esetén (pl. 50, 70, 90)
EUEM_FIXID INTEGER, --EÜ emelt fixcsoport azonosítója (GYSE esetében nem használatos)
EUEM_REFNTK INTEGER, --EÜ emelt fixcsoport referencia NTK-ja (GYSE esetében nem használatos)
OEP_EUN INTEGER, --EÜ emelt támogatás nettó
OEP_EUB INTEGER, --EÜ emelt támogatás bruttó
EUEM_TERDIJ INTEGER, --A beteg által fizetendő térítési díj (EÜ emelt támogatás esetén)
NTK_EETD INTEGER, --A beteg által fizetendő térítési díj alapján kiszámított napi terápiás költség (EÜ emelt támogatás esetén) (GYSE esetében nem használatos)
EUEM_PONTOK VARCHAR2(128), --EÜ pontok, amire a termék EÜ emelt támogatással írható (GYSE esetében nem használatos)
EUKIEM_TIP VARCHAR2(16), --Az EÜ kiemelt támogatás technikája: (null) : nem támogatott, NOMIN: nominálisan (százalékosan) támogatott, HFIX: hatóanyagfix technikával támogatott, TFX: terápiás fix technikával támogatott, KOMBI: a kombinációs felülvizsgálat állapította meg a támogatását, BIOL: biológiai készítményekre vonatkozó szabályok szerint támogatott, LFX: kis molekulasúlyú heparinokra vonatkozó szabályok szerint támogatott.
EUKIEM_SZAZ INTEGER, --Támogatás mértéke %-ban EÜ kiemelt támogatás esetén (pl. 100)
EUKIEM_FIXID INTEGER, --EÜ kiemelt fixcsoport azonosítója (GYSE esetében nem használatos)
EUKIEM_REFNTK INTEGER, --EÜ kiemelt fixcsoport referencia NTK-ja (GYSE esetében nem használatos)
OEP_EU100N INTEGER, --EÜ kiemelt támogatás nettó
OEP_EU100B INTEGER, --EÜ kiemelt támogatás bruttó
EUKIEM_TERDIJ INTEGER, --A beteg által fizetendő térítési díj (EÜ kiemelt támogatás esetén)
NTK_EKTD INTEGER, --A beteg által fizetendő térítési díj alapján kiszámított napi terápiás költség (EÜ kiemelt támogatás esetén) (GYSE esetében nem használatos)
EUKIEM_PONTOK VARCHAR2(128), --EÜ pontok, amire a termék EÜ kiemelt támogatással írható (GYSE esetében nem használatos)
FORGALOMBAN INTEGER, --0 = Nincs forgalomban, 1 = Forgalomban van. Besorolás a következő információk alapján: OWL szerint forgalomban (bejelentette OWL-ben és beküldte az első nagyker számla másolatát), P@NKA Nagykereskedői Beszerzési/raktárkészlet adatokban szerepel (az adott PUPHA érvényességhez képest 2 hónappal korábbi adat alapján), P@NKA Nagykereskedői Kiszállítási adatokban szerepel (az adott PUPHA érvényességhez képest 2 hónappal korábbi adat alapján), BÉVER Forgalmi adatokban szerepel (az adott PUPHA érvényességhez képest 2 hónappal korábbi adat alapján), Ideiglenes ellátási hiányt jelentett a forgalmazó
BESOROLAS INTEGER, --A költséghatékonysági kategória kódja jogcímenként (ld. megjegyzés) (GYSE esetében nem használatos)
PATIKA VARCHAR2(1), --K = patikán kívül is kapható gyógyszer, I = patikában is kapható gyse, ami nem írható eReceptre, E = patikában is kapható gyse, ami eReceptre is írható, (null) = ha gyógyszer: patikán kívül nem kapható, ha gyse: patikában nem kapható és így eReceptre sem 
FORGENGT VARCHAR2(128), --Gyógyszer: Forgalomba hozatali engedély jogosultja / GYSE: Gyártó
FORGENGT_ID INTEGER, --Gyógyszer: Forgalomba hozatali engedély jogosultjának azonosítója / GYSE: Gyártó azonosítója
FORGALMAZ VARCHAR2(128), --Gyógyszer / GYSE: Forgalmazó
FORGALMAZ_ID INTEGER, --Gyógyszer / GYSE: Forgalmazó azonosítója
BRANDNEV VARCHAR2(128), --A gyógyszer márkaneve (GYSE esetében nem használatos)
BRAND_ID INTEGER, --A gyógyszer márkanevének azonosítója (GYSE esetében nem használatos)
KERESZTJELZES VARCHAR2(32), --OGYÉI hatáserősség (méregosztály) jelzése, pl. +,  ++ (GYSE esetében nem használatos)
REGI_NEV DATE, --Az érvényesség vége, ha még nincs lezárva az érvényessége, akkor 2099.12.31 (Access, DBF fájlokban nem jelenik meg, mert felesleges)
PRAS_TERMEK INTEGER, --PReferált ÁrSávba tartozó termék egy 3 jegyű szám: első jegy a normatív, második az EÜ emelt, harmadik az EÜ kiemelt jogcímre vonatkozik. Ha 1 a megfelelő jegy, akkor a termék preferált ársávban van az adott jogcímen, ha 2, akkor kívül esik, ha 3, akkor nem pras csoport vagy nem értelmezhető.
NICHE_ID INTEGER, --A NICHE tábla rekordjára mutat. A hatóanyagalapú felírás melyik eleméhez tartozik az adott termék. Ha nincs besorolva: null
KEST_TERM INTEGER, --Kedvezményezett státuszú termék:1, egyébként 0
);

CREATE TABLE KIINTOR(
ID INTEGER PRIMARY KEY,
JAROFEKVO VARCHAR2(20), --J: out-patient facility, F: in-patient facility, M: other workplace constraints
MEGYE VARCHAR2(100), --region
INTKOD VARCHAR2(20), --institution code
INTEZET VARCHAR2(250), --institution name
GYFKOD VARCHAR2(20), --GYF code
EGYSEG VARCHAR2(250)
);

CREATE TABLE NICHE(
ID INTEGER PRIMARY KEY,
EGYEN_ID INTEGER, --Equivalence group identification number
LEIRAS VARCHAR2(250) --The text to be printed on the prescription identifying the medicine ordered is the name of the equivalence group given by the OGYÉI
);

CREATE TABLE ORVOSOK(
PECSETKOD VARCHAR2(6),-- doctor's seal code
SZAKV_ID INTEGER --Identifier of the qualification
);

CREATE TABLE SZAKVKODOK(
ID INTEGER PRIMARY KEY,
KOD INTEGER, --qualification code
LEIRAS VARCHAR2(250), --qualification name
MEGFELEL INTEGER --It is only filled in if it is no longer available today. If filled, it contains the code of the corresponding qualification valid today
);

--BNOKODOK.ID can be joined with BNOHOZZAR.BNO_ID
--EUPONTOK.ID can be joined with BNOHOZZAR.EUPONT_ID
--EUPONTOK.ID can be joined with EUHOZZAR.EUPONT_ID
--EUPONTOK.ID can be joined with EUINDIKACIOK.EUPONT_ID
--EUPONTOK.ID can be joined with EUJOGHOZZAR.EUPONT_ID
--GYOGYSZ.ID can be joined with EUHOZZAR.GYOGYSZ_ID
--KIINTOR.ID can be joined with EUJOGHOZZAR.KIINT_ID
--NICHE.ID can be joined with GYOGYSZ.NICHE_ID
--SZAKVKODOK.ID can be joined with EUJOGHOZZAR.SZAKV_ID
--SZAKVKODOK.ID can be joined with ORVOSOK.SZAKV_ID

"""