# ------------------- 
# 1. Load YAML config 
# -------------------

import yaml  # Importerar YAML-bibliotek. Biblioteket används för att läsa och skriva YAML-filer i Python.
import subprocess # Step 5 run_snmpget()
import time #Step 5 run_snmpget()
import logging #Step 6 poll_target

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

# ---------------------------- 
# 5. Run SNMPGET via subprocess  
# ----------------------------

def run_snmpget(cmd, timeout_s):
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s
        )
        elapsed = time.time() - start

        if result.returncode == 0:
            return True, result.stdout.strip(), elapsed
        else:
            return False, result.stderr.strip(), elapsed

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return False, "timeout", elapsed

# -------------- 
# 6. poll_target   
# --------------

def poll_target(target):
   start = time.time()
   results = {}
   ok_count = 0
   fail_count = 0


   oids = target.get("oids", [])
   retries = target.get("retries", 1)
   timeout_s = target.get("timeout_s", 2.5)
   budget = target.get("target_budget_s", 10)


   for oid in oids:
       attempts = 0
       success = False
       output = None


       while attempts <= retries:
           # Budget check
           if time.time() - start > budget:
               logging.warning(f"{target['name']}: budget exceeded")
               output = "budget_exceeded"
               break


           cmd = build_snmpget_cmd(target, oid)
           ok, output, elapsed = run_snmpget(cmd, timeout_s)


           if ok:
               success = True
               break


           # Retry only on timeout
           if output == "timeout":
               logging.warning(f"{target['name']} {oid}: timeout, retrying...")
               attempts += 1
               continue


           # Other errors → no retry
           logging.error(f"{target['name']} {oid}: error {output}")
           break


       # Save result
       results[oid] = {"ok": success, "value": output}


       if success:
           ok_count += 1
       else:
           fail_count += 1


   # Determine status
   if ok_count == len(oids):
       status = "ok"
   elif ok_count > 0:
       status = "partial"
   else:
       status = "failed"


   return {
       "name": target["name"],
       "ip": target["ip"],
       "status": status,
       "ok_count": ok_count,
       "fail_count": fail_count,
       "runtime_s": round(time.time() - start, 3),
       "results": results
   }

