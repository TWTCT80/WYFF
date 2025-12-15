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
        
    return snapshot





if __name__ == "__main__":
    print(skapa_snapshot(Path("/home/kali/temp/")))
    
