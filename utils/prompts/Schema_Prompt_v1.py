SCHEMA_PROMPT = """
This query will run on a database whose schema is represented in this string:
CREATE TABLE ATCKONYV(
ATC VARCHAR(7), -- ATC code
MEGNEV VARCHAR(250), --Hungarian name of ATC code
ANGOL VARCHAR(250), --English name of ATC code
HATOANYAG VARCHAR(250) --Substance name for ATC code
);

CREATE TABLE BNOHOZZAR(
EUPONT_ID INTEGER, --foreign key for EUPONT
BNO_ID INTEGER --foreign key for BNOKODOK
);

CREATE TABLE BNOKODOK(
ID INTEGER PRIMARY KEY,
KOD VARCHAR(32), --BNO code
LEIRAS VARCHAR(4000) --BNO description
);

CREATE TABLE EUHOZZAR(
EUPONT_ID INTEGER, --foreign key for EUPONT
GYOGYSZ_ID INTEGER --foreign key for GYOGYSZ
);

CREATE TABLE EUINDIKACIOK(
ID INTEGER PRIMARY KEY,
EUPONT_ID INTEGER, --foreign key for EUPONTOK
NDX INTEGER, --Indication number
LEIRAS VARCHAR(4000) --description of the indication
);

CREATE TABLE EUJOGHOZZAR(
EUPONT_ID INTEGER, --foreign key for EUPONTOK
KATEGORIA_ID INTEGER, --identifier of the type of prescription restrictions
KATEGORIA VARCHAR(64), --description of the identifier of the type of prescription restrictions
JOGOSULT VARCHAR(64), --subscription right
JIDOKORLAT INTEGER, --recommended number of months from the date of medicine prescription (if 0 it doesn't matter)
SZAKV_ID INTEGER, --foreign key for SZAKVKODOK
KIINT_ID INTEGER --foreign key for KIINTOR
);

CREATE TABLE EUPONTOK(
ID INTEGER PRIMARY KEY,
EUTIP VARCHAR(32), --type of aid, (values: Gyógyszer: EÜ50, EÜ70, EÜ90, EÜ100, GYSE: Normatív, EÜ emelt, EÜ Kiemelt)
KODSZAM INTEGER, --first half of the indication code before "/"
PERJEL VARCHAR(32), --second half of the indication code after "/" (ISO code)
IND_TIP VARCHAR(4000) --indication type: 'G' if medicine, 'S' if GYSE
);

CREATE TABLE GYOGYSZ(
ID INTEGER PRIMARY KEY,
KOZHID INTEGER, --Unique product identifier managed by the OGYÉI (number above 1000000 if an identifier is not assigned yet)
OEP_DAT VARCHAR(8), --Start (effective) date of validity in yyyymmdd form
TIPUS VARCHAR(1), --Category of type of product (G: medicine, I: immune, T: nutritional product, R: radiopharmaceutical, H: homeopathic medicine, A: raw material, F: FoNo, C: packaging material, K: manufacturing fee, S: medical device)
OEP_TTT VARCHAR(9), --Code used by NEAK (National Health Insurance Fund Management) to identify the product (TTT code)
OEP_EAN VARCHAR(32), --EAN (European Article Numbering) code of product
OEP_TK VARCHAR(64), --Registration number of the product issued by the OGYÉI
OEP_NEV VARCHAR(255), --Name of product
OEP_KSZ VARCHAR(255), --Packaging of product/unit of measure
OEP_ATC VARCHAR(7), --ATC code managed by NEAK
HATOANYAG VARCHAR(128), --Name of the main active substance of the product
ADAGMOD VARCHAR(32), --Dosage method identifier
ID_GYFORMA INTEGER, --ID assigned to the pharmaceutical form
GYFORMA VARCHAR(100), --Text description of the full pharmaceutical form
RENDELHET VARCHAR(3), --Identifier for the prescription of the product (VN: Medicinal product available without a prescription, V: Medicinal product available only on prescription, J: Medicinal product for outpatient use following a specialist/hospital diagnosis, S or M: I: Medicinal product for use under conditions provided by providers of outpatient specialised outpatient or inpatient specialised inpatient care)
EGYENID INTEGER, --Equivalence group identification number established by the OGYÉI. If it is not in an equivalence group, it is -1
POTENCIA VARCHAR(64), --Potency (homeopathic products)
OHATO_MENNY INTEGER, --Total active substance content
HATO_MENNY INTEGER, --Active substance content per unit pack
HATO_EGYS VARCHAR(50), --OHATO_MENNY, HATO_MENNY fields unit of quantity (e.g. mg)
KISZ_MENNY INTEGER, --Number of packing units in the product
KISZ_EGYS VARCHAR(50), --Unit name of the unit of packaging of the product (e.g. pcs)
DDD_MENNY INTEGER, --DDD (average daily dose)
DDD_EGYS VARCHAR(50), --DDD_MENNY unit of quantity (e.g. mg)
DDD_FAKTOR INTEGER, --Conversion number between HATO_EGYS and DDD_EGYS (e.g. 1000 for g and mg)
DOT INTEGER, --How many days' supply according to WHO
ADAG_MENNY INTEGER, --Quantities of ADAG_EGYS are contained in the package
ADAG_EGYS VARCHAR(50), --Unit of a quantity usually prescribed by the doctor, e.g. tablet, drop, scoop, ml, pea-size (for creams), ..., etc.
OEP_TAR INTEGER, --Production price
OEP_NKAR INTEGER, --Wholesale price
OEP_FAN INTEGER, --Net consumer price
OEP_FAB INTEGER, --Gross consumer price
NTK INTEGER, --Daily therapy costs
OEP_ITM VARCHAR(3), --Old aid designation of the product: 0NT: not subsidised XXX: aid % if nominally subsidised, e.g. 025, FIX: fixed group based aid, TFX: therapeutic fixed group based aid, KOM: combination review based aid, EMT: individual fairness based aid.
OEP_JC1 VARCHAR(1), --I: if the preparation can be prescribed with a national defence authorisation
OEP_JC2 VARCHAR(1), --I: if the product is ready to be prescribed to patients receiving medical treatment
OEP_JC3 VARCHAR(1), --I: if the product can be prescribed in the event of an industrial accident
OEP_JC4 VARCHAR(1), --I: if the product can be prescribed with EÜ privileges
OEP_JC5 VARCHAR(1), --I: if the product EÜ can be prescribed with increased privileges
KGYKERET INTEGER, --1: may be taken into account for the determination of the medical allowance, 2: may not be taken into account for the determination of the medical allowance
EGYSEGAR INTEGER, --Price per active substance HATO_EGYS
NORM_TIP VARCHAR(16), --Indication of aid, NT: non-assisted, C<number>: article code of the external aid. Techniques of normative support: NOMIN: nominally (percentage) supported, HFIX: supported by a fixed technique for active substances, TFX: supported by a fixed therapeutic technique,FIX: supported by a fixed technique for GYSE,KOMBI: the combination review has established the support for GYSE can be NON-NOMIN, which means that although there is normative support, it cannot be replaced, only by a public medicine.
NORM_SZAZ INTEGER, --Aid amount in % for normative aid (e.g. 0, 25, 55, 80)
NORM_FIXID INTEGER, --Normative fixed group identifier
NORM_REFNTK INTEGER, --Reference NFC of normative fixed group
OEP_INN INTEGER, --Normative support net
OEP_INB INTEGER, --Normative support gross
NORM_TERDIJ INTEGER, --Fee to be paid by the patient
NTK_TD INTEGER, --A Daily therapy cost calculated on the basis of the fee to be paid by the patient (in case of normative support)
EUEM_TIP VARCHAR(16), --Normative title is the delivery time (only used for GYSE) Normative title is the quantity that can be written (only used for GYSE). EÜ uplift technique: (null) : not subsidised NOMIN: nominally (percentage) subsidised, HFIX: subsidised by the active substance fixed technique, TFX: subsidised by the therapeutic fixed technique, KOMBI: subsidy established by the Combination Review, BIOL: subsidised under the rules for biological products, LFX: subsidised under the rules for small molecule heparins.
EUEM_SZAZ INTEGER, --Aid amount in % in case of EÜ increased aid (e.g. 50, 70, 90)
EUEM_FIXID INTEGER, --EÜ raised fixed group identifier
EUEM_REFNTK INTEGER, --Reference NFCs for the EÜ elevated fixed group
OEP_EUN INTEGER, --EÜ increased aid net 
OEP_EUB INTEGER, --EÜ increased aid gross
EUEM_TERDIJ INTEGER, --Fee to be paid by the patient (in the case of EÜ increased aid)
NTK_EETD INTEGER, --Daily therapy cost calculated on the basis of the fee payable by the patient (in the case of EÜ increased aid)
EUEM_PONTOK VARCHAR(128), --EÜ points to which the product can be attributed EC increased aid
EUKIEM_TIP VARCHAR(16), --EÜ priority support technique: (null) : not supported, NOMIN: nominally (percentage) supported, HFIX: supported by the active substance fix technique, TFX: supported by the therapeutic fix technique, KOMBI: supported by the combination review, BIOL: supported under the rules for biologicals, LFX: supported under the rules for small molecule heparins.
EUKIEM_SZAZ INTEGER, --Rate of EÜ priority aid % for EÜ priority aid (e.g. 100)
EUKIEM_FIXID INTEGER, --EÜ priority group identifier
EUKIEM_REFNTK INTEGER, --EÜ priority fixed group reference NFCs
OEP_EU100N INTEGER, --EÜ priority aid net
OEP_EU100B INTEGER, --EÜ priority aid gross
EUKIEM_TERDIJ INTEGER, --Fee to be paid by the patient (in case of EÜ priority support)
NTK_EKTD INTEGER, --Daily therapy costs calculated on the basis of the fee to be paid by the patient (in the case of EÜ priority support)
EUKIEM_PONTOK VARCHAR(128), --EÜ points for which the product is eligible for EÜ priority support
FORGALOMBAN INTEGER, --0 = Not in circulation, 1 = In circulation. Classification based on the following information: In circulation according to OWL (declared in OWL and submitted a copy of the first wholesale invoice), listed in P@NKA Wholesale Purchasing/Stock data (based on data 2 months prior to the current PUPHA validity), Included in P@NKA Wholesaler Delivery data (based on data 2 months earlier than the current PUPHA validity), Included in BÉVER Turnover data (based on data 2 months earlier than the current PUPHA validity), Temporary shortage of supply reported by distributor
BESOROLAS INTEGER, --Cost-effectiveness category code by title
PATIKA VARCHAR(1), --K = drug available over-the-counter, I = drug available over-the-counter but not on ePrescription, E = drug available over-the-counter but on ePrescription, (null) = if drug: not available over-the-counter, if drug: not available over-the-counter and therefore not on ePrescription
FORGENGT VARCHAR(128), --Medicinal product: marketing authorisation holder / GYSE: manufacturer
FORGENGT_ID INTEGER, --Medicinal product: FMedicine: Marketing Authorisation Holder Identifier / GYSE: Manufacturer Identifier
FORGALMAZ VARCHAR(128), --Medical Distributor
FORGALMAZ_ID INTEGER, --Medical Distributor identifier
BRANDNEV VARCHAR(128), --Brand name of medicine
BRAND_ID INTEGER, --Brand name identifier of the medicine
KERESZTJELZES VARCHAR(32), --Indication of the potency (poison class), e.g. +, ++
REGI_NEV VARCHAR(255), --The expiry date, if not yet closed, is 31.12.2099
PRAS_TERMEK INTEGER, --The product in the PReferred Price Range is a 3-digit number: the first digit refers to the normative, the second to the EÜ increased and the third to the EÜ priority. If 1 is the corresponding digit, the product is in the preferred price band for that title, if 2, it is outside, if 3, it is not in the pras group or cannot be interpreted.
NICHE_ID INTEGER, --Foreign key for NICHE. (To which element of the active substance prescription the product belongs. If not classified: null)
KEST_TERM INTEGER, --Beneficiary status product:1, otherwise 0
);

CREATE TABLE KIINTOR(
ID INTEGER PRIMARY KEY,
JAROFEKVO VARCHAR(20), --J: out-patient facility, F: in-patient facility, M: other workplace constraints
MEGYE VARCHAR(100), --region
INTKOD VARCHAR(20), --institution code
INTEZET VARCHAR(250), --institution name
GYFKOD VARCHAR(20), --GYF code
EGYSEG VARCHAR(250)
);


CREATE TABLE ORVOSOK(
PECSETKOD VARCHAR(6),-- doctor's seal code
SZAKV_ID INTEGER --Identifier of the qualification
);

CREATE TABLE SZAKVKODOK(
ID INTEGER PRIMARY KEY,
KOD INTEGER, --qualification code
LEIRAS VARCHAR(250), --qualification name
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
# CREATE TABLE NICHE(
# ID INTEGER PRIMARY KEY,
# EGYEN_ID INTEGER, --Equivalence group identification number
# LEIRAS VARCHAR(250) --The text to be printed on the prescription identifying the medicine ordered is the name of the equivalence group given by the OGYÉI
# );
