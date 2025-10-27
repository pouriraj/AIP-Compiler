
import argparse, sys, re, csv, fnmatch, datetime, io, os
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# GUI
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
except Exception:
    tk = None

# PDF
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject, BooleanObject, DictionaryObject

VERSION = "Version 1"
APP_TITLE = f"Iran AIP Compiler (Single-file {VERSION})"

# --- Embedded TSV defaults (from user) ---
GEN_TSV_DEFAULT = r"""Order	Level	Code	Title	Pattern	Family	Enabled	Notes
1	1	GEN 0.1	Preface	GEN 0.1*.pdf	GEN 0 — Introduction	TRUE	
2	1	GEN 0.2	Record of AIP Amendment	GEN 0.2*.pdf	GEN 0 — Introduction	TRUE	
3	1	GEN 0.3	Record of AIP Supplements	GEN 0.3*.pdf	GEN 0 — Introduction	TRUE	
4	1	GEN 0.4	Checklist of AIP Pages	GEN 0.4*.pdf	GEN 0 — Introduction	TRUE	
5	1	GEN 0.5	List of Hand Amendments to the AIP	GEN 0.5*.pdf	GEN 0 — Introduction	TRUE	
6	1	GEN 0.6	Table of Contents to Part 1	GEN 0.6*.pdf	GEN 0 — Introduction	TRUE	
7	1	GEN 1.1	Designated authorities	GEN 1.1*.pdf	GEN 1 — National regulations & requirements	TRUE	
8	1	GEN 1.2	Entry, Transit and Departure of Aircraft	GEN 1.2*.pdf	GEN 1 — National regulations & requirements	TRUE	
9	1	GEN 1.3	Entry, Transit and Departure of Passengers and Crew	GEN 1.3*.pdf	GEN 1 — National regulations & requirements	TRUE	
10	1	GEN 1.4	Entry, Transit and Departure of Cargo	GEN 1.4*.pdf	GEN 1 — National regulations & requirements	TRUE	
11	1	GEN 1.7	Differences from ICAO Standards, Recommended Practices and Procedures	GEN 1.7*.pdf	GEN 1 — National regulations & requirements	TRUE	
12	1	GEN 2.1	Measuring System, Aircraft Markings, Holidays	GEN 2.1*.pdf	GEN 2 — Tables and codes	TRUE	
13	1	GEN 2.2	Abbreviations Used in AIS Publications	GEN 2.2*.pdf	GEN 2 — Tables and codes	TRUE	
14	1	GEN 2.3	Chart Symbols	GEN 2.3*.pdf	GEN 2 — Tables and codes	TRUE	
15	1	GEN 2.4	Location Indicators	GEN 2.4*.pdf	GEN 2 — Tables and codes	TRUE	
16	1	GEN 2.5	List of Radio Navigation Aids	GEN 2.5*.pdf	GEN 2 — Tables and codes	TRUE	
17	1	GEN 2.6	Conversion Tables	GEN 2.6*.pdf	GEN 2 — Tables and codes	TRUE	
18	1	GEN 2.7	Sunrise/Sunset Tables	GEN 2.7*.pdf	GEN 2 — Tables and codes	TRUE	
19	1	GEN 3.1	Aeronautical Information Services	GEN 3.1*.pdf	GEN 3 — Services	TRUE	
20	1	GEN 3.2	Aeronautical Charts	GEN 3.2*.pdf	GEN 3 — Services	TRUE	
21	1	GEN 3.3	Air Traffic Services	GEN 3.3*.pdf	GEN 3 — Services	TRUE	
22	1	GEN 3.4	Communication Services	GEN 3.4*.pdf	GEN 3 — Services	TRUE	
23	1	GEN 3.5	Meteorological Services	GEN 3.5*.pdf	GEN 3 — Services	TRUE	
24	1	GEN 3.6	Search and Rescue	GEN 3.6*.pdf	GEN 3 — Services	TRUE	
25	1	GEN 4.1	Aerodrome/Heliport Charges	GEN 4.1*.pdf	GEN 4 — Charges for aerodromes & ANS	TRUE	
26	1	GEN 4.2	Air Navigation Services Charges	GEN 4.2*.pdf	GEN 4 — Charges for aerodromes & ANS	TRUE"""
ENR_TSV_DEFAULT = r"""Order	Level	Code	Title	Pattern	Family	Enabled	Notes
1	1	ENR 0.6	Table of Contents to Part 2	ENR 0.6*.pdf	ENR 0 — Introduction	TRUE	
2	1	ENR 1.1	General Rules	ENR 1.1*.pdf	ENR 1 — General rules & procedures	TRUE	
3	1	ENR 1.2	Visual Flight Rules	ENR 1.2*.pdf	ENR 1 — General rules & procedures	TRUE	
4	1	ENR 1.3	Instrument Flight Rules	ENR 1.3*.pdf	ENR 1 — General rules & procedures	TRUE	
5	1	ENR 1.4	ATS Airspace Classification	ENR 1.4*.pdf	ENR 1 — General rules & procedures	TRUE	
6	1	ENR 1.5	Holding, Approach and Departure Procedures	ENR 1.5*.pdf	ENR 1 — General rules & procedures	TRUE	
7	1	ENR 1.6	ATC Surveillance Services and Procedures	ENR 1.6*.pdf	ENR 1 — General rules & procedures	TRUE	
8	1	ENR 1.7	Altimeter Setting Procedures	ENR 1.7*.pdf	ENR 1 — General rules & procedures	TRUE	
9	1	ENR 1.8	Regional Supplementary Procedures	ENR 1.8*.pdf	ENR 1 — General rules & procedures	TRUE	
10	1	ENR 1.9	Air Traffic Flow Management (ATFM)	ENR 1.9*.pdf	ENR 1 — General rules & procedures	TRUE	
11	1	ENR 1.10	Flight Planning	ENR 1.10*.pdf	ENR 1 — General rules & procedures	TRUE	
12	1	ENR 1.11	Addressing of Flight Plan Messages	ENR 1.11*.pdf	ENR 1 — General rules & procedures	TRUE	
13	1	ENR 1.12	Interception of Civil Aircraft	ENR 1.12*.pdf	ENR 1 — General rules & procedures	TRUE	
14	1	ENR 1.13	Unlawful Interference	ENR 1.13*.pdf	ENR 1 — General rules & procedures	TRUE	
15	1	ENR 1.14	Air Traffic Incidents	ENR 1.14*.pdf	ENR 1 — General rules & procedures	TRUE	
16	1	ENR 2.1	FIR, UIR, TMA	ENR 2.1*.pdf	ENR 2 — ATS airspace	TRUE	
17	1	ENR 3.1	ATS routes	ENR 3.1*.pdf	ENR 3 — ATS routes	TRUE	
18	1	ENR 3.3	RNAV routes	ENR 3.3*.pdf	ENR 3 — ATS routes	TRUE	
19	1	ENR 3.5	Other routes	ENR 3.5*.pdf	ENR 3 — ATS routes	TRUE	
20	1	ENR 3.6	En-route holding	ENR 3.6*.pdf	ENR 3 — ATS routes	TRUE	
21	1	ENR 4.1	Navaids — en-route	ENR 4.1*.pdf	ENR 4 — Navaids & points	TRUE	
22	1	ENR 4.4	Name-code designators	ENR 4.4*.pdf	ENR 4 — Navaids & points	TRUE	
23	1	ENR 5.1	Prohibited, Restricted, Danger, Caution	ENR 5.1*.pdf	ENR 5 — Navigation warnings	TRUE	
24	2	ENR 5.1.1	Prohibited areas	ENR 5.1.1*.pdf	ENR 5 — Navigation warnings	TRUE	
25	2	ENR 5.1.2	Restricted areas	ENR 5.1.2*.pdf	ENR 5 — Navigation warnings	TRUE	
26	2	ENR 5.1.3	Danger areas	ENR 5.1.3*.pdf	ENR 5 — Navigation warnings	TRUE	
27	2	ENR 5.1.4	Caution areas	ENR 5.1.4*.pdf	ENR 5 — Navigation warnings	TRUE	
28	1	ENR 5.5	Aerial sporting & recreational	ENR 5.5*.pdf	ENR 5 — Navigation warnings	TRUE	
29	1	ENR 6.1	En-Route Chart	ENR 6.1*.pdf	ENR 6 — En-route charts	TRUE"""
AD_TSV_DEFAULT  = r"""Order	Level	Code	Title	Pattern	Family	Enabled	Notes
1	1	AD 0.6	Table of Contents to Part 3	AD 0.6*.pdf	AD 0 — Preface	TRUE	
2	1	AD 1.1	Aerodromes/Heliport Availability	AD 1.1*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
3	2	AD 1.1.1	General Conditions Under Which Aerodromes/Heliports and Associated Facilities are Available for Use	AD 1.1.1*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
4	2	AD 1.1.2	Applicable ICAO Documents	AD 1.1.2*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
5	2	AD 1.1.3	Civil Use of Military Aerodromes/Heliports	AD 1.1.3*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
6	2	AD 1.1.4	Aerodrome Operating Minima	AD 1.1.4*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
7	2	AD 1.1.5	Low Visibility Procedures (LVP)	AD 1.1.5*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
8	2	AD 1.1.6	Determination of Aerodrome Traffic Zone (ATZ) and Aerodrome Traffic Pattern Altitude in Tehran FIR	AD 1.1.6*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
9	1	AD 1.2	Rescue and Firefighting Services and Snow Plan	AD 1.2*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
10	2	AD 1.2.1	Rescue and Firefighting Services	AD 1.2.1*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
11	2	AD 1.2.2	Snow Plan	AD 1.2.2*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
12	1	AD 1.3	Index to Aerodromes and Heliports	AD 1.3*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
13	1	AD 1.4	Grouping of Aerodromes/Heliports	AD 1.4*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE	
14	1	AD 1.5	Status of Certification of Aerodromes	AD 1.5*.pdf	AD 1 — Aerodrome/Heliport Introduction	TRUE"""
AD_ICAO_TSV_DEFAULT = r"""Code	Name	Type	Enabled	Notes
OIAA	Abadan	Aerodrome	TRUE		
OIAD	Dezful	Aerodrome	TRUE		
OIAG	Aghajari	Aerodrome	TRUE		
OIAH	Gachsaran	Aerodrome	TRUE		
OIAJ	Omidiyeh	Aerodrome	TRUE		
OIAM	Bandar Mahshahr / Mahshahr	Aerodrome	TRUE		
OIAI	Masjed Soleiman / Shahid Asyaee	Aerodrome	TRUE		
OIAW	Ahwaz	Aerodrome	TRUE		
OIBA	Abumusa Island	Aerodrome	TRUE		
OIBB	Bushehr	Aerodrome	TRUE		
OIBH	Bahregan	Aerodrome	TRUE		
OIBJ	Jam	Aerodrome	TRUE		
OIBK	Kish Island / Kish	Aerodrome	TRUE
OIBL	Bandar Lengeh	Aerodrome	TRUE
OIBP	Pars Special Energy Economy Zone (PSEEZ) / Persian Gulf (Khalij-e-Fars)	Aerodrome	TRUE	
OIBQ	Khark Island / Khark	Aerodrome	TRUE
OIBS	Sirri Island	Aerodrome	TRUE
OIBV	Lavan Island / Lavan	Aerodrome	TRUE
OIBX	Tunb-e- Bozorg Island/ TUNB-E- BOZORG	Aerodrome	TRUE
OICC	Kermanshah / Shahid Ashrafi Esfahani	Aerodrome	TRUE	
OICI	Ilam	Aerodrome	TRUE	
OICK	Khoram Abad	Aerodrome	TRUE	
OICS	Sanandaj	Aerodrome	TRUE	
OIFE	Esfahan / HESA	Aerodrome	TRUE	
OIFH	Esfahan / Shahid Vatan Pour AIR BASE	Aerodrome	TRUE	
OIFK	Kashan	Aerodrome	TRUE	
OIFM	Esfahan / Shahid Beheshti	Aerodrome	TRUE	
OIFP	Esfahan / Badr Air Base	Aerodrome	TRUE	
OIFS	Shahre Kord	Aerodrome	TRUE	
OIGG	Rasht / Sardar Jangal	Aerodrome	TRUE	
OIHH	Hamadan	Aerodrome	TRUE	
OIHR	Aeak	Aerodrome	TRUE	
OIHS	Hamadan / Nogeh	Aerodrome	TRUE	
OIIB	Eyvanakei / Boland Parvaz	Aerodrome	TRUE	
OIID	Tehran / Doshan Tappeh	Aerodrome	TRUE	
OIIE	Tehran / Imam Khomeini	Aerodrome	TRUE	
OIIF	Karaj / Fath	Aerodrome	TRUE	
OIII	Tehran / Mehrabad	Aerodrome	TRUE	
OIIK	Ghazvin	Aerodrome	TRUE	
OIIM	Karaj / Naja	Aerodrome	TRUE	
OIIP	Karaj / Payam	Aerodrome	TRUE	
OIIS	Semnan	Aerodrome	TRUE	
OIKB	Bandar Abbas	Aerodrome	TRUE
OIKJ	Jiroft	Aerodrome	TRUE	
OIKK	Kerman	Aerodrome	TRUE	
OIKM	Bam	Aerodrome	TRUE	
OIKP	Bandar Abbas / HavaDarya	Aerodrome	TRUE	
OIKQ	Gheshm Island / Gheshm	Aerodrome	TRUE	
OIKR	Rafsanjan	Aerodrome	TRUE	
OIKY	Sirjan	Aerodrome	TRUE	
OIMB	Birjand	Aerodrome	TRUE	
OIMC	Sarakhs	Aerodrome	TRUE	
OIMG	Mashhad / Golbahar	Aerodrome	TRUE	
OIMJ	Shahroud	Aerodrome	TRUE	
OIMM	Mashhad	Aerodrome	TRUE	
OIMN	Bojnord	Aerodrome	TRUE	
OIMQ	Kashmar	Aerodrome	TRUE	
OIMS	Sabzevar	Aerodrome	TRUE	
OIMT	Tabas	Aerodrome	TRUE	
OINE	Kalaleh	Aerodrome	TRUE	
OING	Gorgan	Aerodrome	TRUE	
OINJ	Bishe Kola	Aerodrome	TRUE	
OINN	Nowshahr	Aerodrome	TRUE	
OINR	Ramsar	Aerodrome	TRUE	
OINZ	Sari / Dasht-e Naz	Aerodrome	TRUE	
OISF	Fasa	Aerodrome	TRUE	
OISJ	Jahrom	Aerodrome	TRUE	
OISL	Lar	Aerodrome	TRUE	
OISO	Zarghan	Aerodrome	TRUE	
OISR	Lamerd	Aerodrome	TRUE	
OISS	Shiraz / Shahid Dastgheib	Aerodrome	TRUE	
OISY	Yasouj	Aerodrome	TRUE	
OITK	Khoy	Aerodrome	TRUE	
OITL	Ardabil	Aerodrome	TRUE	
OITM	Sahand	Aerodrome	TRUE	
OITP	Parsabade Moghan	Aerodrome	TRUE	
OITR	Urmia	Aerodrome	TRUE	
OITT	Tabriz	Aerodrome	TRUE	
OITU	Maku	Aerodrome	TRUE	
OITZ	Zanjan	Aerodrome	TRUE	
OIYP	Yazd / Pardis Yazd	Aerodrome	TRUE	
OIYR	Mehriz / Imam Reza	Aerodrome	TRUE	
OIYY	Yazd / Shahid Ayatollah Sadoughi	Aerodrome	TRUE	
OIZB	Zabol	Aerodrome	TRUE	
OIZC	Chah Bahar - Konarak	Aerodrome	TRUE	
OIZH	Zahedan	Aerodrome	TRUE	
OIZI	Iranshahr	Aerodrome	TRUE	
OIZS	Saravan	Aerodrome	TRUE	
OIIO	Tehran / Panha	Heliport	TRUE"""
REQUIRED_TSV = ("GEN.tsv","ENR.tsv","AD.tsv","AD_ICAO.tsv")

# --- Logging ---
_gui_log = None
def set_gui_log(w):  # Text widget
    global _gui_log; _gui_log = w
def log(msg: str):
    line = f"[{datetime.datetime.now():%H:%M:%S}] {msg}"
    try:
        if _gui_log is not None:
            _gui_log.insert("end", line + "\n"); _gui_log.see("end"); _gui_log.update()
        else:
            print(line)
    except Exception:
        print(line)

# --- Helpers ---
def packaged_maps_dir() -> Path:
    try:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent
        d = base/"maps"
        return d if d.exists() else base
    except Exception:
        return Path(__file__).resolve().parent

def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def list_all_pdfs(root: Optional[Path]) -> List[Path]:
    if not root or not root.exists(): return []
    return sorted([p for p in root.rglob("*.pdf") if p.is_file()], key=lambda p: natural_key(p.as_posix()))

def first_existing_dir(parent: Path, name: str) -> Optional[Path]:
    n = name.lower()
    for c in parent.iterdir():
        if c.is_dir() and c.name.lower()==n:
            return c
    return None

def parse_autorun_wef(root: Path) -> Optional[str]:
    f = root/"AUTORUN.INF"
    if not f.exists(): return None
    for line in f.read_text(errors="ignore").splitlines():
        if line.strip().lower().startswith("date="):
            val = line.split("=",1)[1].strip()
            m = re.search(r"WEF.*", val, flags=re.I)
            return m.group(0).strip() if m else val
    return None

def extract_airac_cycle(amdt_dir: Optional[Path]) -> Optional[str]:
    if not amdt_dir or not amdt_dir.exists(): return None
    for p in amdt_dir.rglob("*.pdf"):
        m = re.search(r"\bAIRAC\s*(\d{4})\.(\d+)\b", p.stem.upper())
        if m:
            year, num = int(m.group(1)), int(m.group(2))
            return f"{int(num)}-{year%100:02d}"
    return None

def parse_aic_year(stem: str) -> Optional[int]:
    s = stem.upper().replace("_"," ")
    m = re.search(r"AIC\s*\d+\s*-\s*(\d{2})", s) or re.search(r"AIC\s*\d+[-/](\d{2})", s) or re.search(r"AIC\s*(\d{4})\.\d+", s)
    if m:
        yy = m.group(1)
        if len(yy)==2: return 2000 + int(yy)
        return int(yy)
    m4 = re.search(r"(20\d{2}|19\d{2})", s)
    return int(m4.group(1)) if m4 else None

def parse_sup_year(stem: str) -> Optional[int]:
    s = stem.upper().replace("_"," ")
    m = re.search(r"(20\d{2}|19\d{2})\s*[-/.]\s*\d+", s) or re.search(r"(20\d{2}|19\d{2})", s)
    return int(m.group(1)) if m else None

# --- TSV loading with fallback ---
def _load_tsv_from_path_or_default(path: Optional[Path], default_text: str) -> list[dict]:
    if path and path.exists():
        f = open(path, "r", encoding="utf-8", newline="")
    else:
        f = io.StringIO(default_text)
    out=[]; 
    with f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if not row: continue
            if (row.get("Enabled","TRUE") or "TRUE").strip().upper() not in ("TRUE","1","YES","Y"): 
                continue
            out.append({k:(row.get(k) or "").strip() for k in r.fieldnames})
    return out

def resolve_maps_dir(maps_dir: Optional[Path]):
    pkg = packaged_maps_dir()
    if maps_dir and all((maps_dir/name).exists() for name in REQUIRED_TSV):
        base = maps_dir; source = "user"
    elif all((pkg/name).exists() for name in REQUIRED_TSV):
        base = pkg; source = "packaged"
    else:
        base = None; source = "embedded"
    if source != "user":
        log(f"[INFO] TSV maps not found in the selected folder; using {source} defaults.")
    tsvs = {
        "GEN": _load_tsv_from_path_or_default((base/"GEN.tsv") if base else None, GEN_TSV_DEFAULT),
        "ENR": _load_tsv_from_path_or_default((base/"ENR.tsv") if base else None, ENR_TSV_DEFAULT),
        "AD":  _load_tsv_from_path_or_default((base/"AD.tsv")  if base else None, AD_TSV_DEFAULT),
        "ICAO": _load_tsv_from_path_or_default((base/"AD_ICAO.tsv") if base else None, AD_ICAO_TSV_DEFAULT),
    }
    return base, tsvs

# --- Matching helpers ---
def _alts(pat: str) -> List[str]:
    pats = [pat]
    if " " in pat:
        pats += [pat.replace(" ",""), pat.replace(" ","_"), pat.replace(" ","-")]
    if "_" in pat:
        pats += [pat.replace("_"," "), pat.replace("_","-")]
    if "-" in pat:
        pats += [pat.replace("-"," "), pat.replace("-","_")]
    seen=set(); out=[]
    for x in pats:
        xl = x.lower()
        if xl not in seen:
            out.append(xl); seen.add(xl)
    return out

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())

def choose_file_for_pattern(search_root: Path, pattern: str, code: Optional[str]=None) -> Optional[Path]:
    files = list_all_pdfs(search_root)
    pats = [p.strip() for p in (pattern or "").split("|") if p.strip()]
    pats = [p.replace("\\","/") for p in pats]
    # direct match with alts
    alts = []
    for p in pats: alts += _alts(p)
    for p in files:
        rel = p.relative_to(search_root).as_posix().lower()
        name= p.name.lower()
        for pat in alts:
            if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(name, pat):
                return p
    # normalized prefix (also try Code)
    anchors = []
    for p in pats:
        core = p[:-4] if p.lower().endswith(".pdf") else p
        core = core.replace("*","").strip()
        if core: anchors.append(_norm(core))
    if code: anchors.append(_norm(code))
    for p in files:
        if any(_norm(p.stem).startswith(a) for a in anchors if a):
            return p
    return None

def group_by_family(rows: List[Dict[str,str]], prefix: str):
    groups: Dict[str, List[Dict[str,str]]] = {}; order: Dict[str,int] = {}
    for r in rows:
        code = r.get("Code",""); fam = r.get("Family") or ""
        if not fam:
            m = re.match(rf"^\s*{re.escape(prefix)}\s+(\d+)", code, re.I)
            fam = f"{prefix} {m.group(1)}" if m else prefix
        groups.setdefault(fam, []).append(r)
        try:
            o = int(float(r.get("Order") or "999999")); order[fam] = min(order.get(fam,o), o)
        except Exception: pass
    return sorted(groups.items(), key=lambda kv: (order.get(kv[0], 999999), natural_key(kv[0])))

def icao_of(p: Path) -> Optional[str]:
    s = p.stem.upper()
    m = re.search(r"\b([A-Z]{4})\b", s)
    if m: return m.group(1)
    for part in p.parts:
        m = re.search(r"\b([A-Z]{4})\b", str(part).upper())
        if m: return m.group(1)
    return None

def add_bm(writer: PdfWriter, title: str, page_index: int, parent=None):
    try:
        return writer.add_outline_item(title, page_index, parent=parent)
    except Exception:
        try:
            return writer.addBookmark(title, page_index, parent=parent)
        except Exception:
            return None

def compile_pdf(root: Path, out_path: Path, maps_dir: Optional[Path]):
    writer = PdfWriter(); page_cursor=0
    def append_pdf(path: Path, parent, label: Optional[str]=None):
        nonlocal page_cursor
        try:
            reader = PdfReader(str(path))
        except Exception as e:
            log(f"[WARN] Skipping unreadable PDF: {path} ({e})"); return 0
        n = len(reader.pages)
        if n==0: log(f"[WARN] Zero-page PDF: {path}"); return 0
        start = page_cursor
        for pg in reader.pages: writer.add_page(pg)
        add_bm(writer, label or path.stem, start, parent=parent)
        page_cursor += n
        log(f"Added {n:>3} pages: {path.relative_to(root) if path.is_relative_to(root) else path.name}")
        return n

    # TSVs
    base, tsvs = resolve_maps_dir(maps_dir)

    # locate dirs
    sup_dir = first_existing_dir(root, "SUP") or (root/"AIP"/"SUP" if (root/"AIP"/"SUP").exists() else None)
    aic_dir = first_existing_dir(root, "AIC") or (root/"AIP"/"AIC" if (root/"AIP"/"AIC").exists() else None)
    aip_dir = first_existing_dir(root, "AIP")
    amdt_dir= first_existing_dir(root, "AMDT")

    # Preamble only top-level PDFs
    root_pdfs = sorted([p for p in root.glob("*.pdf")], key=lambda p: natural_key(p.name))
    if root_pdfs:
        pre = add_bm(writer, "Preamble", page_cursor, parent=None)
        for p in root_pdfs: append_pdf(p, pre)

    # SUP
    if sup_dir:
        sup_parent = add_bm(writer, "SUP — Supplements", page_cursor, parent=None)
        buckets: Dict[int,List[Path]] = {}
        for p in list_all_pdfs(sup_dir):
            yy = parse_sup_year(p.stem) or 0
            buckets.setdefault(yy, []).append(p)
        for y in sorted(buckets.keys()):
            ybm = add_bm(writer, str(y if y else "Unknown"), page_cursor, parent=sup_parent)
            for p in sorted(buckets[y], key=lambda p: natural_key(p.name)):
                append_pdf(p, ybm)

    # AIC
    if aic_dir:
        aic_parent = add_bm(writer, "AIC — Aeronautical Information Circulars", page_cursor, parent=None)
        buckets: Dict[int,List[Path]] = {}
        for p in list_all_pdfs(aic_dir):
            yy = parse_aic_year(p.stem) or 0
            buckets.setdefault(yy, []).append(p)
        for y in sorted(buckets.keys()):
            ybm = add_bm(writer, str(y if y else "Unknown"), page_cursor, parent=aic_parent)
            for p in sorted(buckets[y], key=lambda p: natural_key(p.name)):
                append_pdf(p, ybm)

    # AIP
    if aip_dir:
        aip_parent = add_bm(writer, "AIP", page_cursor, parent=None)

        # AMDT first inside AIP
        amdt_files = list_all_pdfs(amdt_dir)
        if amdt_files:
            amdt_bm = add_bm(writer, "AMDT", page_cursor, parent=aip_parent)
            for p in amdt_files: append_pdf(p, amdt_bm)

        # PART 1 — GEN
        part1 = add_bm(writer, "PART 1 — GENERAL (GEN)", page_cursor, parent=aip_parent)
        for fam, rows in group_by_family(tsvs["GEN"], "GEN"):
            fam_bm = add_bm(writer, fam, page_cursor, parent=part1)
            for r in rows:
                file = choose_file_for_pattern(aip_dir, r.get("Pattern") or "", code=r.get("Code"))
                if file:
                    label = f"{r['Code']} — {r['Title']}" if r.get("Title") else r["Code"]
                    append_pdf(file, fam_bm, label=label)
                else:
                    log(f"[HARDSET] Missing GEN: {r.get('Code')} pattern='{r.get('Pattern')}'")

        # PART 2 — ENR
        part2 = add_bm(writer, "PART 2 — En-route (ENR)", page_cursor, parent=aip_parent)
        for fam, rows in group_by_family(tsvs["ENR"], "ENR"):
            fam_bm = add_bm(writer, fam, page_cursor, parent=part2)
            for r in rows:
                file = choose_file_for_pattern(aip_dir, r.get("Pattern") or "", code=r.get("Code"))
                if file:
                    label = f"{r['Code']} — {r['Title']}" if r.get("Title") else r["Code"]
                    append_pdf(file, fam_bm, label=label)
                else:
                    log(f"[HARDSET] Missing ENR: {r.get('Code')} pattern='{r.get('Pattern')}'")

        # PART 3 — AD
        part3 = add_bm(writer, "PART 3 — Aerodromes (AD)", page_cursor, parent=aip_parent)

        # AD 0 / AD 1 via TSV
        ad0 = add_bm(writer, "AD 0 — Preface", page_cursor, parent=part3)
        ad1 = add_bm(writer, "AD 1 — Aerodrome/Heliport Introduction", page_cursor, parent=part3)
        for fam, rows in group_by_family(tsvs["AD"], "AD"):
            uf = fam.upper().strip()
            parent = ad0 if uf.startswith("AD 0") else (ad1 if uf.startswith("AD 1") else None)
            if not parent: continue
            for r in rows:
                file = choose_file_for_pattern(aip_dir, r.get("Pattern") or "", code=r.get("Code"))
                if file:
                    label = f"{r['Code']} — {r['Title']}" if r.get("Title") else r["Code"]
                    append_pdf(file, parent, label=label)
                else:
                    log(f"[HARDSET] Missing {uf.split()[0]}: {r.get('Code')} pattern='{r.get('Pattern')}'")

        # AD 2 / AD 3 grouped by ICAO
        def icao_groups(folder_name: str) -> Dict[str, List[Path]]:
            sub = None
            for d in aip_dir.rglob("*"):
                if d.is_dir() and d.name.replace("_"," ").replace("-"," ").strip().lower()==folder_name.lower():
                    sub = d; break
            pdfs = list_all_pdfs(sub) if sub else []
            buckets: Dict[str, List[Path]] = {}
            for p in pdfs:
                code = icao_of(p) or "UNKNOWN"
                buckets.setdefault(code, []).append(p)
            return buckets

        # ICAO names
        icao_names = {}
        for row in tsvs["ICAO"]:
            code = (row.get("Code") or "").upper().strip()
            nm = (row.get("Name") or "").strip()
            if code: icao_names[code] = nm

        for subgroup, parent_title, base_label in (("AD 2","AD 2 — Aerodromes","Aerodrome Data"),
                                                   ("AD 3","AD 3 — Heliports","Heliport Data")):
            parent_bm = add_bm(writer, parent_title, page_cursor, parent=part3)
            for code, files in sorted(icao_groups(subgroup).items()):
                disp = f"{code} — {icao_names.get(code,'')}" if icao_names.get(code) else code
                ic_bm = add_bm(writer, disp, page_cursor, parent=parent_bm)
                files = sorted(files, key=lambda x: natural_key(x.name))
                base = [p for p in files if p.stem.upper()==code.upper()]
                rest = [p for p in files if p.stem.upper()!=code.upper()]
                if base: append_pdf(base[0], ic_bm, label=base_label)
                for p in rest: append_pdf(p, ic_bm)

    # Metadata
    wef = parse_autorun_wef(root) or ""
    airac = extract_airac_cycle(first_existing_dir(root, "AMDT")) or ""
    if airac and wef: title = f"Iran AIP AIRAC {airac} ({wef})"
    elif airac:       title = f"Iran AIP AIRAC {airac}"
    elif wef:         title = f"Iran AIP ({wef})"
    else:             title = "Iran AIP"

    try:
        writer.add_metadata({
            "/Title": title,
            "/Author": 'Iran Airports & Air Navigation Company (IAC) (compiled with AIP Compiler by "Ali Pouriraj").',
            "/Subject": "Iran's Civil Aviation Aeronautical Information Publication(AIP)",
            "/Creator": 'AIP Compiler "https://github.com/pouriraj/AIP-Compiler" by "Ali Pouriraj"',
            "/Producer": 'AIP Compiler "https://github.com/pouriraj/AIP-Compiler" by "Ali Pouriraj"',
            "/Language": "English",
            "/PageCount": str(len(writer.pages)),
            "/CreationDate": datetime.datetime.now().strftime("D:%Y%m%d%H%M%S%z"),
            "/ModDate": datetime.datetime.now().strftime("D:%Y%m%d%H%M%S%z"),
            "/Keywords": "AIP, Iran, GEN, ENR, AD, AIC, SUP, AMDT, AIRAC",
        })
        writer.page_mode = "/UseOutlines"
        writer._root_object.update({NameObject("/ViewerPreferences"): DictionaryObject({NameObject("/DisplayDocTitle"): BooleanObject(True)})})
        writer._root_object.update({NameObject("/Lang"): TextStringObject("en")})
    except Exception:
        pass

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f: writer.write(f)
    log(f"Total pages: {len(writer.pages)}")
    log(f"Written: {out_path}")

# --- GUI ---
def run_gui():
    if tk is None:
        print("tkinter not available"); return
    win = tk.Tk(); win.title(APP_TITLE); win.geometry("980x640")
    frm = tk.Frame(win, padx=12, pady=12); frm.pack(fill="both", expand=True)

    root_var = tk.StringVar()
    out_var  = tk.StringVar(value=str(Path.cwd()/f"Iran AIP ({VERSION}).pdf"))
    maps_var = tk.StringVar(value="")  # leave empty by default

    def browse_root():
        p = filedialog.askdirectory(title="Select AIP root (contains AIP, AIC, SUP, AMDT ...)")
        if p: root_var.set(p); compute_default_out()

    def browse_out():
        p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")])
        if p: out_var.set(p)

    def browse_maps():
        p = filedialog.askdirectory(title="Select TSV maps folder (leave empty to use defaults)")
        if p: maps_var.set(p)

    def export_tsvs():
        d = filedialog.askdirectory(title="Choose folder to export TSV templates")
        if not d: return
        tgt = Path(d); tgt.mkdir(parents=True, exist_ok=True)
        (tgt/"GEN.tsv").write_text(GEN_TSV_DEFAULT, encoding="utf-8")
        (tgt/"ENR.tsv").write_text(ENR_TSV_DEFAULT, encoding="utf-8")
        (tgt/"AD.tsv").write_text(AD_TSV_DEFAULT, encoding="utf-8")
        (tgt/"AD_ICAO.tsv").write_text(AD_ICAO_TSV_DEFAULT, encoding="utf-8")
        messagebox.showinfo("Exported", f"Templates written to:\\n{d}")

    def compute_default_out():
        try:
            rp = Path(root_var.get())
            wef = parse_autorun_wef(rp) or ""
            airac = extract_airac_cycle(first_existing_dir(rp, "AMDT")) or ""
            if airac and wef: title=f"Iran AIP AIRAC {airac} ({wef})"
            elif airac: title=f"Iran AIP AIRAC {airac}"
            elif wef: title=f"Iran AIP ({wef})"
            else: title="Iran AIP"
            out_var.set(str(rp/f"{title}.pdf"))
        except Exception: pass

    tk.Label(frm, text="AIP Root:").grid(row=0, column=0, sticky="w"); tk.Entry(frm, textvariable=root_var, width=80).grid(row=0, column=1, sticky="ew")
    tk.Button(frm, text="Browse…", command=browse_root).grid(row=0, column=2, padx=6)

    tk.Label(frm, text="Output PDF:").grid(row=1, column=0, sticky="w", pady=(6,0)); tk.Entry(frm, textvariable=out_var, width=80).grid(row=1, column=1, sticky="ew", pady=(6,0))
    tk.Button(frm, text="Browse…", command=browse_out).grid(row=1, column=2, padx=6, pady=(6,0))

    tk.Label(frm, text="TSV Maps Dir (optional):").grid(row=2, column=0, sticky="w", pady=(6,0)); tk.Entry(frm, textvariable=maps_var, width=80).grid(row=2, column=1, sticky="ew", pady=(6,0))
    tk.Button(frm, text="Select…", command=browse_maps).grid(row=2, column=2, padx=6, pady=(6,0))

    logbox = scrolledtext.ScrolledText(frm, height=20); logbox.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(10,0))
    frm.columnconfigure(1, weight=1); frm.rowconfigure(4, weight=1)
    set_gui_log(logbox)

    def run_now():
        rp = Path(root_var.get().strip())
        op = Path(out_var.get().strip())
        mp = Path(maps_var.get().strip()) if maps_var.get().strip() else None
        if not rp.exists():
            messagebox.showerror("Error","Please select a valid AIP root"); return
        try:
            log("=== Compile started ===")
            compile_pdf(rp, op, mp)
            messagebox.showinfo("Done", f"Wrote:\\n{op}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(frm, text="Export TSV templates", command=export_tsvs).grid(row=3, column=0, columnspan=3, pady=(6,6))
    tk.Button(frm, text="Compile", command=run_now).grid(row=5, column=0, columnspan=3, pady=10)

    win.mainloop()

# --- CLI ---
def main():
    ap = argparse.ArgumentParser(description=f"Iran AIP Compiler {VERSION}")
    ap.add_argument("root", nargs="?", type=Path, help="Path to the extracted AIP root folder")
    ap.add_argument("--root", dest="root_opt", type=Path, help="Path to the extracted AIP root folder (same as positional)")
    ap.add_argument("-o","--output", type=Path, default=None, help="Output PDF (default computed from AIRAC/WEF)")
    ap.add_argument("--maps-dir", type=Path, help="TSV folder (leave empty to use defaults)")
    ap.add_argument("--gui", action="store_true", help="Launch GUI")
    args = ap.parse_args()

    if getattr(args, "root_opt", None) is not None and args.root is None:
        args.root = args.root_opt

    if args.gui or args.root is None:
        return run_gui()

    if args.output is None:
        wef = parse_autorun_wef(args.root) or ""
        airac = extract_airac_cycle(first_existing_dir(args.root,"AMDT")) or ""
        if airac and wef: title=f"Iran AIP AIRAC {airac} ({wef})"
        elif airac: title=f"Iran AIP AIRAC {airac}"
        elif wef: title=f"Iran AIP ({wef})"
        else: title="Iran AIP"
        args.output = args.root/f"{title}.pdf"

    compile_pdf(args.root, args.output, args.maps_dir)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as ex:
        print("ERROR:", ex, file=sys.stderr)
