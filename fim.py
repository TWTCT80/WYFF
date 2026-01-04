#!/usr/bin/env python3

import argparse             #Läsa från kommandoraden.
import hashlib              #skapar hash-object -> hashobject kan ta emot data -> ger ett hashvärde
import json                 #Läser och skriver i json.
import os                   #Ge tillgång till operativsystemets funktioner.
from pathlib import Path    #Bättre sätt att arbeta med filer o foldrar.

baseline_file = "fim_base.json" 

#Funktion som beräknar SHA-256-hashen

def sha256_fil(path: Path) -> str:              
    h = hashlib.sha256()                            #skapar ett SHA-256-hash-object
    with path.open("rb") as f:                      # rb = read binary
        while True:
            chunk = f.read(1024 * 1024)             #Läs filen i block om 1 mb
            if chunk == b"":                        #När man når slutet av filen så skickar read() en tom byte-sträng(b"")
                break
            h.update(chunk)                         #chunken läggs till i h (hash-objectet)
    return h.hexdigest()                            #slutliga hashvärdet


def skapa_snapshot(root: Path) -> dict:             #Skapar en ögonblicksbild av alla filer i en mapp
                                                    # root = startkatalog där övervakningen börjar.
    snapshot = {}                                   #Dictionary som kommer fyllas med hashvärden
    for dirpath, _, filenames in os.walk(root):     #Går igenom mapparna rekursivt och kollar filnamn
        for name in filenames:                      
            p = Path(dirpath) / name                # P = path och filnamn
            if p.name == baseline_file:             # Om filen är baseline-filen, gå vidare
                continue
            try:
                rel = str(p.relative_to(root))      #relative_to() är en metod i pathlib som används för att beräkna filens sökväg relativt till den övervakade katalogen, vilket gör baselinen portabel.
                snapshot[rel] = sha256_fil(p)       #Den relativa sökvägen används som nyckel och hashvärdet av filens innehåll är value i snapshot dicten.
            except (PermissionError, OSError):      
                continue
        
    return snapshot                                 # ex output av func: {'test.txt': '66d2d11753be2f4216fdce2502dae77fd9e1963a98f62623afa4b2d0e79967fe'}



#Funktion som ändrar dictionaryn till en sträng så den kan skrivas som json, därefter sparas den som en fil.
def spara_baseline(root: Path, baseline_save_file: Path) -> None:           
    snap = skapa_snapshot(root)                                             # En dict med keys: relativa sökvägar, values: hashvärden
    data = {"root": str(root.resolve()), "files": snap}                     # ex root.resolve() = /home/tom/Documents -> gör det till en sträng så json kan spara den.
    baseline_save_file.write_text(json.dumps(data, indent=2), encoding="utf-8")                   #Skriver baseline-filen
    print(f"\n[OK] - Baseline skapad @ {baseline_save_file} --- Innehåller {len(snap)} filer")

def load_baseline(baseline_save_file: Path) -> dict:
    json_file =  json.loads(baseline_save_file.read_text(encoding="utf-8"))       # read_text läser hela filen som en sträng. json.loads gör om den till ett python-ojekt.
    #print(json_file)        #test-utskrift
    return json_file

def integrity_check(root: Path, baseline_save_file: Path) -> None:          # Funktion som kontrollerar root (mappen du vill kontrollera) mot baseline_save_file (json-filen)
    base = load_baseline(baseline_save_file)                                # Läser json-filen och sparar som en dict (base)
    baseline_files = base["files"]                                                     # plocka ut filerna ur dicten, se nedan: 
    current_files = skapa_snapshot(root)                                              #"root": "/home/tom/Documents",
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
    print(f"\nMapp för övervakning: {root.resolve()}")
    print(f"Baseline: {baseline_save_file.resolve()}")
    print("-" * 40)

    #Nya filer
    print(f"\nNya filer: {len(added)}")
    for f in added:
        print(f" + {f}")
    
    #Borttagna filer
    print(f"Borttagna filer: {len(removed)}")
    for f in removed:
        print(f" - {f}")

    #Ändrade filer
    print(f"Ändrade filer: {len(changed)}")
    for f in changed:
        print(f" * {f}")

    if not (added or removed or changed):
        print("[OK] - Inga förändringar har hittats")
    else:
        print("[VARNING] - Förändringar har hittats!")


if __name__ == "__main__":
    #print(skapa_snapshot(Path("/home/kali/temp/"))) #Test
    
    #spara_baseline(Path("/home/kali/temp/"), Path("/home/kali/Desktop/test.json"))
    integrity_check(Path("/home/kali/temp/"), Path("/home/kali/Desktop/test.json"))
    #load_baseline(Path("/home/kali/Desktop/test.json"))