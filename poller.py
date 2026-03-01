# ------------------- 
# 1. Load YAML config 
# -------------------

import yaml  # Importerar YAML-bibliotek. Biblioteket används för att läsa och skriva YAML-filer i Python.

def load_config(path):  # Funktion (load_config) som läser en config-fil, path är sökvägen till konfigurationsfilen. 
    with open(path, "r") as f:  # Open file to read på den angivna sökvägen. "r" = read mode. with = close file automatiskt när blocket är klart. f = fileobject.
        return yaml.safe_load(f)  # Läser innehållet i YAML-filen. safe_load konverterar YAML till Python-data (dict, list osv.). Returnerar datan från funktionen.


# ---------------------------- 
# 2. Validate config structure  
# ----------------------------

def validate_config(cfg):  # Funktion som kontrollerar config-data
    if "targets" not in cfg:  # Kontrollera att "targets" finns
        raise ValueError("Config missing required key: targets")  # Fel om den saknas

    if not isinstance(cfg["targets"], list):  # Kontrollera att targets är en lista
        raise ValueError("targets must be a list")  # Fel annars

    if not isinstance(cfg["defaults"], dict):  # Kontrollera att defaults är en dictionary
        raise ValueError("defaults must be a dict")  # Fel annars

    defaults = cfg.get("defaults")  # Hämta defaults från config

    for key in ["timeout_s", "retries", "target_budget_s"]:  # Loopa över vissa inställningar
        if key in defaults and not isinstance(defaults[key], (int, float)):  # Måste vara nummer
            raise ValueError(f"default {key} must be numeric")  # Fel om inte numeriskt

    for t in cfg["targets"]:  # Loopa över alla targets
        if "name" not in t:  # Kontrollera att name finns
            raise ValueError("Target missing name")  # Fel om saknas
        if "ip" not in t:  # Kontrollera att ip finns
            raise ValueError(f"Target {t.get('name','?')} missing ip")  # Fel om saknas
        if "community" not in t and defaults.get("snmp_version", "v2c") == "v2c":  # Krävs för SNMP v2c
            raise ValueError(f"Target {t['name']} missing community for v2c")  # Fel om saknas

# ----------------------------- 
# 3. Merge defaults with target 
# -----------------------------

def merge_defaults(defaults, target):
   merged = defaults.copy()
   merged.update(target)
   return merged

# ----------------------------
# 4. Build SNMPGET command (SNMPv2c)
# ----------------------------


def build_snmpget_cmd(target, oid):
   version = target.get("snmp_version", "v2c")
   community = target.get("community", "public")
   ip = target["ip"]
   timeout_s = str(target.get("timeout_s", 2.5))
   retries = str(target.get("retries", 1))


   return [
       "snmpget",
       "-v", version,
       "-c", community,
       "-t", timeout_s,
       "-r", retries,
       ip,
       oid
   ]

