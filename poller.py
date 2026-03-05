import argparse #Step 7 main()
import json #Step 7 main()
import sys #Step 7 main()
import time #Step 5 run_snmpget() # Allows to measure how long things take
import logging #Step 6 poll_target import logging allowsto write warnings and errors to the log
import subprocess #Step 5 run_snmpget() # Allows to run external commands lika "snmpget"
import yaml #Importerar YAML-bibliotek. Biblioteket används för att läsa och skriva YAML-filer i Python.

# -------------------
# 1. Load YAML config
# -------------------

def load_config(path):  # Function (load_config) that reads a configuration file. "path" is the path to the configuration file.
    with open(path, "r") as f:  # Opens the file at the specified path for reading. "r" = read mode. "with" ensures the file is automatically closed when the block finishes. "f" is the file object.
        return yaml.safe_load(f)  # Reads the contents of the YAML file. safe_load converts the YAML data into Python data structures (dict, list, etc.). Returns the data from the function.
# Example usage:
# cfg = load_config("config.yml")
# print(cfg)

# ---------------------------- 
# 2. Validate config structure  
# ----------------------------

# The validate function goes through the config file and checks for all the essential parts and that they are correct type( list, dic, number). Important, or else the script crashes later.
# If something is wrong the function stops immediately and tells exactly what is wrong. Every target should have a name, IP and community (if v2c is used)

def validate_config(cfg): # Function to control that the configuration data is correct and complete. Takes config created by: cfg = load_config(...) cfg is a dictionary.
    if "targets" not in cfg:  # Checks if the key 'targets' exists in the config
        raise ValueError("Config missing required key: targets")  # Stops the program if targets is missing.

    if not isinstance(cfg["targets"], list):  # Checks that 'targets' is a list
        raise ValueError("targets must be a list")  # Stops if targets is not a list.

    if not isinstance(cfg["defaults"], dict):  # Checks that 'defaults' is a dictionary (keys and values)
        raise ValueError("defaults must be a dict")  # Stops if defaults is not a dictionary

    defaults = cfg.get("defaults")  # Saves the defaults section for easier access. .get(). Safer to use. If key is missing = None returns instead of a crash.
# Get ‘defaults’ from the configuration file and save it in a variable so cfg['defaults'] dosent have to be written all the time.

    for key in ["timeout_s", "retries", "target_budget_s"]:  # Loops through each setting that is required to be a number.
        if key in defaults and not isinstance(defaults[key], (int, float)):  # Checks if the value is a number
            raise ValueError(f"default {key} must be numeric")  # Stops if it's not a number

    for t in cfg["targets"]:  # Loops through each target in the list.
        if "name" not in t:  # Checks that each target has a name
            raise ValueError("Target missing name")  # Stops if name is missing
        if "ip" not in t:  # Checks that each target has an IP address
            raise ValueError(f"Target {t.get('name','?')} missing ip")  # Stops if IP is missing
        if "community" not in t and defaults.get("snmp_version", "v2c") == "v2c":  # Checks if community is in target and if SNMP version is v2c.
            raise ValueError(f"Target {t['name']} missing community for v2c")  # Stops if community is missing and tell that the community string is required.

# Example usage:
# cfg = load_config("config.yml")
# validate_config(cfg)

# ----------------------------- 
# 3. Merge defaults with target 
# -----------------------------

# Applicera standardvärden från config.
# Combine defaults and target and return one merged config. 
def merge_defaults(defaults, target):  # Function that combines default settings with a specific target's settings, defaults and targets are parameters.
   merged = defaults.copy()            # Creates a copy of the default settings so the original don't change
   merged.update(target)               # Adds the target's own settings, replacing defaults where needed
   return merged                       # Returns the final combined result whitch is used by the rest of the program.

# Example usage:
# defaults = cfg["defaults"]
# t0 = cfg["targets"][0]
# merged = merge_defaults(defaults, t0)
# print(merged)

# ----------------------------
# 4. Build SNMPGET command (SNMPv2c)
# ----------------------------

# build_snmpget_cmd takes all info about a target (IP, community‑string, SNMP‑version, timeout, retries) and builds a complete SNMPGET command whitch can runs in the terminal.
# This function translates the python-data to a real snmpget command.
def build_snmpget_cmd(target, oid):                 # This creates a function that builds the command needed to run an SNMPGET
   version = target.get("snmp_version", "v2c")      # Gets the SNMP version, or uses "v2c" if none is provided
   if version.startswith("v"):                      # Checks if the version starts with the letter "v"
        version = version[1:]                       # Removes the "v" so "v2c" becomes "2c"

   community = target.get("community", "public")    # Gets the community string, or uses "public" if missing
   ip = target["ip"]                                # Gets the target's IP address
   timeout_s = str(target.get("timeout_s", 2.5))    # Gets the timeout value, or uses 2.5 seconds if missing
   retries = str(target.get("retries", 1))          # Gets the retry count, or uses 1 if missing

   return [
       "snmpget",                                   # The command that will be run
       "-v", version,                               # Tells SNMP which version to use
       "-c", community,                             # Provides the community string (password-like)
       "-t", timeout_s,                             # Sets how long to wait before giving up
       "-r", retries,                               # Sets how many times to retry
       ip,                                          # The device to contact
       oid                                          # The specific SNMP value to read
   ]

# Example usage:
# cmd = build_snmpget_cmd(merged, "sysName.0")
# print(cmd)

# ---------------------------- 
# 5. Run SNMPGET via subprocess  
# ----------------------------

def run_snmpget(cmd, timeout_s):                            # Function that runs an SNMPGET command with a timeout
    start = time.time()                                     # Records the current time so  it is possible to measure how long the command takes
    try:
        result = subprocess.run(                            # Runs the command in the operating system
            cmd,                                            # Command list that was earlier built
            capture_output=True,                            # Tells Python to capture the output instead of printing it
            text=True,                                      # Makes the output text instead of bytes
            timeout=timeout_s                               # Stops the command if it takes too long
        )
        elapsed = time.time() - start                       # Calculates how long the command took

        if result.returncode == 0:                          # Checks if the command succeeded (return code 0 means success)
            return True, result.stdout.strip(), elapsed     # Returns success, the output, and the time used
        else:
            return False, result.stderr.strip(), elapsed    # Returns failure, the error message, and the time used

    except subprocess.TimeoutExpired:                       # This happens if the command took longer than the allowed timeout
        elapsed = time.time() - start                       # Calculates how long we waited before timing out
        return False, "timeout", elapsed                    # This returns failure with the message "timeout"

# Example usage:
# ok, out, elapsed = run_snmpget(cmd, 2.5)
# print(ok, out, elapsed)

# -------------- 
# 6. poll_target   
# --------------

def poll_target(target):                                    # Defines a function that polls one device (target)
   start = time.time()                                      # Records when the polling started
   results = {}                                             # This will store the results for each OID
   ok_count = 0                                             # Counts how many OIDs succeeded
   fail_count = 0                                           # Counts how many OIDs failed

   oids = target.get("oids", [])                            # Gets the list of OIDs to poll (or an empty list if missing)
   retries = target.get("retries", 1)                       # Gets how many times we may retry on timeout
   timeout_s = target.get("timeout_s", 2.5)                 # Gets the timeout for each SNMP request
   budget = target.get("target_budget_s", 10)               # Gets the total time allowed for this target

   for oid in oids:                                         # Loops through each OID we want to poll
       attempts = 0                                         # Counts how many attempts are made
       success = False                                      # Tracks eventually succeed
       output = None                                        # Store the output or error message
     
       while attempts <= retries:                          # Keeps trying until there is no more retries
           if time.time() - start > budget:                 # Checks if the total allowed time is used
                logging.warning(                                                                        #ADDED     
                    f"event=budget_exceeded device={target['name']} ip={target['ip']} subnet={subnet} " #ADDED
                    f"budget_s={budget} timeout_s={timeout_s} retries={retries} snmp_id={snmp_id}"      #ADDED
                )                                                                                       #ADDED
               #logging.warning(f"{target['name']}: budget exceeded")  # This logs a warning            #OLD

               output = "budget_exceeded"                   # Marks the result as budget exceeded
               break                                        # Stops trying this OID

           cmd = build_snmpget_cmd(target, oid)             # Builds the SNMPGET command for this OID
           ok, output, elapsed = run_snmpget(cmd, timeout_s)  # This runs the command and gets the result


           if ok:                                           # Checks if the SNMPGET succeeded
               success = True                               # Marks the OID as successful
               break                                        # Stops retrying
           
           # Retry only on timeout
           if output == "timeout":                          # Checks if the failure was a timeout
               logging.warning(                                                                                 #ADDED
                    f"event=timeout device={target['name']} ip={target['ip']} subnet={subnet} oid={oid} "       #ADDED
                    f"attempt={attempts+1}/{retries+1} timeout_s={timeout_s} snmp_id={snmp_id} action=retrying" #ADDED
                )                                                                                               #ADDED
               #logging.warning(f"{target['name']} {oid}: timeout, retrying...")  # Logs a retry message        #OLD
               attempts += 1                                # Increases the retry counter
               continue                                     # Tries again

           # Other errors → no retry
           logging.error(f"{target['name']} {oid}: error {output}")  # This logs other errors
           break                                            # Stops retrying for non-timeout errors

       # Save result
       results[oid] = {"ok": success, "value": output}      # Saves the result for this OID

       if success:
           ok_count += 1                                    # Increases the success counter
       else:
           fail_count += 1                                  # Increases the failure counter

   # Determine status
   if ok_count == len(oids):                                # Checks if all OIDs succeeded
       status = "ok"                                        # Everything worked
   elif ok_count > 0:                                       # Checks if some succeeded
       status = "partial"                                   # Some worked, some failed
   else:
       status = "failed"                                    # Nothing worked

   return {                                                 # Returns a summary of the polling
       "name": target["name"],                              # The target's name
       "ip": target["ip"],                                  # The target's IP address
       "status": status,                                    # The overall status
       "ok_count": ok_count,                                # Number of successful OIDs
       "fail_count": fail_count,                            # Number of failed OIDs
       "runtime_s": round(time.time() - start, 3),          # Total time spent polling
       "results": results                                   # Detailed results for each OID
   }

# Example usage:
# cfg = load_config("config.yml")
# validate_config(cfg)
# merged = merge_defaults(cfg["defaults"], cfg["targets"][0])
# logging.basicConfig(level=logging.INFO)
# print(poll_target(merged))

# ---------
# 7. main() 
# ---------

def main():                                                     # Startar huvudprogrammet

    parser = argparse.ArgumentParser()                          # (argparse) skapar parser för CLI-argument
    parser.add_argument("--config", required=True)              # (1) configfilen som ska läsas av load_config()
    parser.add_argument("--out", required=True)                 # (main/output) fil där JSON-resultatet ska skrivas
    parser.add_argument("--log-level", default="INFO")          # (6) styr hur mycket logging poll_target visar
    args = parser.parse_args()                                  # (argparse) läser argument från terminalen

    logging.basicConfig(                                        # (6) logging används i poll_target()
        level=getattr(logging, args.log_level.upper(), logging.INFO),  # (6) sätter loggnivå
        #level=args.log_level,
        format="%(asctime)s %(levelname)s %(message)s"          # (6) format på loggmeddelanden
    )

    # Load + validate config
    try:
        cfg = load_config(args.config)                          # (1) använder load_config() för att läsa YAML
        validate_config(cfg)                                    # (2) kontrollerar att configen är korrekt
    except Exception as e:                                      # (1-2) fångar fel från load_config/validate_config
        logging.error(f"Invalid config: {e}")                   # (6) loggar felet
        sys.exit(2)                                             # (main) stoppar programmet med exitkod

    defaults = cfg.get("defaults", {})                          # (3) defaults används av merge_defaults()
    targets = cfg["targets"]                                    # (2) targets verifierades i validate_config()

    logging.info(f"Starting poller, {len(targets)} targets")    # (6) loggar hur många targets som ska pollas

    run_start = time.time()                                     # (main) mäter total körtid
    results = []                                                # (main) lista där poll_resultat sparas

    for t in targets:                                           # (2) loopar igenom alla targets från config
        merged = merge_defaults(defaults, t)                    # (3) kombinerar defaults + target
        logging.info(f"Polling {merged['name']} ({merged['ip']})")  # (6) loggar vilken enhet som pollas
        results.append(poll_target(merged))                     # (6) poll_target kör SNMP polling

    duration = round(time.time() - run_start, 3)                # (main) beräknar total runtime

    output = {                                                  # (main) bygger JSON-resultatet
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),        # (main) tidpunkt för körningen
        "config": args.config,                                  # (1) vilken configfil som användes
        "duration_s": duration,                                 # (main) total körtid
        "targets": results                                      # (6) resultat från poll_target()
    }

    # Write JSON
    if args.out == "-":                                         # (main) "-" betyder skriv till terminal
        print(json.dumps(output, indent=2))                     # (main) skriver JSON till stdout
    else:
        with open(args.out, "w") as f:                          # (main) öppnar outputfil
            json.dump(output, f, indent=2)                      # (main) skriver JSON till fil

    # Exit code logic
    statuses = [t.get("status", "failed") for t in results]     # (6) läser status från poll_target-resultat
    # Exit code logic
    # statuses = [t["status"] for t in results]

    if all(s == "failed" for s in statuses):                    # (6) alla polling misslyckades
        sys.exit(2)                                             # exitkod 2
    if any(s != "ok" for s in statuses):                        # (6) minst en partial eller fail
        sys.exit(1)                                             # exitkod 1

    sys.exit(0)                                                 # (main) allt lyckades

if __name__ == "__main__":
   main()

