# ------------------- 
# 1. Load YAML config 
# -------------------

import yaml  # Importerar YAML-bibliotek. Biblioteket används för att läsa och skriva YAML-filer i Python.

def load_config(path):  # Funktion (load_config) som läser en config-fil, path är sökvägen till konfigurationsfilen. 
    with open(path, "r") as f:  # Open file to read på den angivna sökvägen. "r" = read mode. with = close file automatiskt när blocket är klart. f = fileobject.
        return yaml.safe_load(f)  # Läser innehållet i YAML-filen. safe_load konverterar YAML till Python-data (dict, list osv.). Returnerar datan från funktionen.
