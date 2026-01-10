#!/usr/bin/env python3

import argparse             #Läsa från kommandoraden.
import hashlib              #skapar hash-object -> hashobject kan ta emot data -> ger ett hashvärde
import json                 #Läser och skriver i json.
import os                   #Ge tillgång till operativsystemets funktioner.
from pathlib import Path    #Bättre sätt att arbeta med filer o foldrar.
import platform


BASELINE_FILE = "wyff_baseline.json" 
line = "*" * 65
header = """
          
   █████   ███   █████ █████ █████ ███████████ ███████████
   ░░███   ░███  ░░███ ░░███ ░░███ ░░███░░░░░░█░░███░░░░░░█
    ░███   ░███   ░███  ░░███ ███   ░███   █ ░  ░███   █ ░ 
    ░███   ░███   ░███   ░░█████    ░███████    ░███████   
    ░░███  █████  ███     ░░███     ░███░░░█    ░███░░░█   
     ░░░█████░█████░       ░███     ░███  ░     ░███  ░    
       ░░███ ░░███         █████    █████       █████      
        ░░░   ░░░         ░░░░░    ░░░░░       ░░░░░           
             
               ** Watch Your Files Fool **
               
                          RESULT"""


def sha256_file(path: Path) -> str:                  #Funktion som beräknar SHA-256-hashen
    h = hashlib.sha256()                            #skapar ett SHA-256-hash-object
    with path.open("rb") as f:                      # rb = read binary
        while True:
            chunk = f.read(1024 * 1024)             #Läs filen i block om 1 mb
            if chunk == b"":                        #När man når slutet av filen så skickar read() en tom byte-sträng(b"")
                break
            h.update(chunk)                         #chunken läggs till i h (hash-objectet)
    return h.hexdigest()                            #slutliga hashvärdet


def build_snapshot(root: Path) -> dict:             #Skapar en ögonblicksbild av alla filer i en mapp
                                                    # root = startkatalog där övervakningen börjar.
    snapshot = {}                                   #Dictionary som kommer fyllas med hashvärden
    for dirpath, _, filenames in os.walk(root):     #Går igenom mapparna rekursivt och kollar filnamn
        for name in filenames:                      
            p = Path(dirpath) / name                # P = path och filnamn
            if p.name == BASELINE_FILE:             # Om filen är baseline-filen, gå vidare
                continue
            try:
                rel = str(p.relative_to(root))      #relative_to() är en metod i pathlib som används för att beräkna filens sökväg relativt till den övervakade katalogen, vilket gör baselinen portabel.
                snapshot[rel] = sha256_file(p)       #Den relativa sökvägen används som nyckel och hashvärdet av filens innehåll är value i snapshot dicten.
            except (PermissionError, OSError):      
                continue
        
    return snapshot                                 # ex output av func: {'test.txt': '66d2d11753be2f4216fdce2502dae77fd9e1963a98f62623afa4b2d0e79967fe'}



#Funktion som ändrar dictionaryn till en sträng så den kan skrivas som json, därefter sparas den som en fil.
def save_baseline(root: Path, baseline_save_file: Path) -> None:           
    snap = build_snapshot(root)                                             # En dict med keys: relativa sökvägar, values: hashvärden
    data = {"root": str(root.resolve()), "files": snap}                     # ex root.resolve() = /home/tom/Documents -> gör det till en sträng så json kan spara den.
    baseline_save_file.write_text(json.dumps(data, indent=2), encoding="utf-8")                   #Skriver baseline-filen
    print(f"\n[OK] - Baseline built @ {baseline_save_file} --- Contains {len(snap)} files")

def load_baseline(baseline_save_file: Path) -> dict:
    json_file =  json.loads(baseline_save_file.read_text(encoding="utf-8"))       # read_text läser hela filen som en sträng. json.loads gör om den till ett python-ojekt.
    #print(json_file)        #test-utskrift
    return json_file

def check_integrity(root: Path, baseline_save_file: Path) -> None:          # Funktion som kontrollerar root (mappen du vill kontrollera) mot baseline_save_file (json-filen)
    
    base = load_baseline(baseline_save_file)                                # Läser json-filen och sparar som en dict (base)
    baseline_files = base["files"]                                                     # plocka ut filerna ur dicten, se nedan: 
    current_files = build_snapshot(root)                                              #"root": "/home/tom/Documents",
                                                                            #"files": {
                                                                            #  "text1.txt": "hash1",
                                                                            #  "text2.txt": "hash2"

    baseline_paths = set(baseline_files.keys())       #Skapar sets för att göra jämförelsen enkel
    current_paths = set(current_files.keys())

    added = sorted(current_paths - baseline_paths)
    removed = sorted(baseline_paths - current_paths)
    
    changed = []
    for f in (baseline_paths & current_paths):       # jämför de gamla och nya setsen
        if baseline_files[f] != current_files[f]:
            changed.append(f)
    changed = sorted(changed)

    #Rubrik
    print(header)
    print(line)
    print(f"\nTarget directory: {root.resolve()}")
    print(line)
    print(f"\nBaseline path: {baseline_save_file.resolve()}")
    print(line)

    #Nya filer
    print(f"\nNew files: {len(added)}")
    for f in added:
        print(f" + {f}")
    
    #Borttagna filer
    print(f"Deleted files: {len(removed)}")
    for f in removed:
        print(f" - {f}")

    #Ändrade filer
    print(f"Changed files: {len(changed)}")
    for f in changed:
        print(f" * {f}")
        

    if not (added or removed or changed):
        print(line)
        print("\n[OK] - No changes have been found !\n")
        print(line)
    else:
        print(line)
        print("\n[WARNING] - CHANGES HAVE BEEN DETECTED !!\n")
        print(line)

def main():
    ap = argparse.ArgumentParser(
        description="WYFF: Monitor directories for integrity changes",
        epilog="""
Examples:

  Create a baseline for a directory:
    wyff baseline ~/Pictures

  Create a baseline and choose where to save it:
    wyff baseline ~/Pictures --baseline-file ~/baselines/pictures.json

  Check a directory against its baseline:
    wyff check ~/Pictures

  Check using a specific baseline file:
    wyff check ~/Pictures --baseline-file ~/baselines/pictures.json

Notes:
  • A baseline represents the file state at a specific point in time.
  • The same baseline file must be used when running 'check'.
  • If no --baseline-file is specified, the default file is used.

  
""",
    formatter_class=argparse.RawTextHelpFormatter,
    )
    ap.add_argument("mode", choices=["baseline", "check"], help="Create baseline or check for changes")
    ap.add_argument("path", help="Target directory")
    ap.add_argument("--baseline-file", default=BASELINE_FILE, help="Baseline json-file (default = wyff_baseline.json)" )
    args = ap.parse_args()

    root = Path(args.path).expanduser().resolve()
    baseline_path = Path(args.baseline_file).expanduser().resolve()

    if platform.system() != "Linux":
        raise SystemExit("Error: WYFF is intended to run on Linux systems only.")
    
    if not os.access(root, os.R_OK):
        raise SystemExit("Error: No read permission for target directory.")

    
    if not root.is_dir():
        raise SystemExit(f"\n{line}\nError: {root} is not a directory.\n{line}\n")

    if args.mode == "baseline":
        save_baseline(root, baseline_path)
    else:
        if not baseline_path.exists():
            raise SystemExit(f"\n{line}\nError: baseline file doesn't exist: {baseline_path}\nRun 'baseline' first\n{line}\n")
        check_integrity(root, baseline_path)

if __name__ == "__main__":
    main()

