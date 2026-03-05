README.md (för din labb)
# SNMP Poller

## About the application

This application is a SNMP poller written in Python.

The program reads a YAML configuration file that contains a list of network devices (targets) and SNMP OIDs to poll.

For each target the program performs SNMP GET requests using the `snmpget` command.  
The results are collected and written to a JSON report.

The poller includes features such as:

- configuration validation
- retries and timeout handling
- per-target time budget
- logging
- exit codes for monitoring systems

The poller generates detailed warning logs that include device name, IP address, subnet, OID and retry information to simplify troubleshooting and monitoring.

---

# Files

The project contains the following files:

**poller.py**  
Main application. Contains all methods for loading the configuration, validating it, polling devices and generating the JSON output.

**config.yml**  
Configuration file containing default settings and the list of targets to poll.

**test_config.py**  
Small helper script used to test that the configuration file is valid.

**README.md**  
Documentation describing the application and how to use it.

---

# Methods

### load_config(path)

**Input**

- path (string) – path to YAML configuration file

**Output**

- dictionary containing configuration data

**Description**

Reads the YAML configuration file and converts it into a Python dictionary.

---

### validate_config(cfg)

**Input**

- cfg (dictionary) – configuration loaded from YAML

**Output**

- none (raises error if configuration is invalid)

**Description**

Validates the structure of the configuration file.  
Checks that required keys such as `targets` and `defaults` exist and that the values have correct types.

---

### merge_defaults(defaults, target)

**Input**

- defaults (dictionary)
- target (dictionary)

**Output**

- merged dictionary

**Description**

Combines default configuration values with target specific values.

---

### build_snmpget_cmd(target, oid)

**Input**

- target configuration
- oid (string)

**Output**

- list representing the SNMP command

**Description**

Builds the `snmpget` command that will be executed to poll the device.

Example command:


snmpget -v 2c -c public -t 2 -r 1 192.168.1.1 sysName.0


---

### run_snmpget(cmd, timeout)

**Input**

- cmd (list) – SNMP command
- timeout (float)

**Output**

- success status
- command output
- execution time

**Description**

Runs the SNMP command using Python `subprocess`.

Handles timeout errors.

---

### poll_target(target)

**Input**

- target configuration

**Output**

- dictionary containing polling results

**Description**

Polls all OIDs for a target device.

Handles:

- retries
- timeout
- target budget
- result collection

Returns the status of the target (`ok`, `partial`, `failed`).

---

### Method dependencies

The methods depend on each other in the following way:


main
↓
load_config
↓
validate_config
↓
merge_defaults
↓
poll_target
↓
build_snmpget_cmd
↓
run_snmpget


The `main()` function coordinates the execution of the application.


---

# Installation

The application is tested on Linux (Ubuntu/Kali).

### System dependencies

The SNMP tools must be installed:


sudo apt install snmp


### Python dependencies

Python 3 is required.

Install PyYAML:


pip install pyyaml



---

# Running

Run the application from the command line.


python poller.py --config config.yml --out out.json


### Arguments

**--config**

Path to the YAML configuration file.

**--out**

Output JSON file.  
Use `-` to print the result to the terminal.

**--log-level**

Logging level (optional).  
Default: `INFO`.

Supported values:

- WARNING
- ERROR

### Examples

Write output to a file:


python poller.py --config config.yml --out out.json


Print output to terminal:


python poller.py --config config.yml --out -


Run with debug logging:


python poller.py --config config.yml --out out.json --log-level DEBUG



### Program flow ###
main
 ↓
load_config
 ↓
validate_config
 ↓
for each target
     ↓
     merge_defaults
     ↓
     poll_target
          ↓
          build_snmpget_cmd
          ↓
          run_snmpget
 ↓
write JSON output
Summary

This SNMP poller reads a YAML configuration file, polls network devices using SNMP GET requests, and outputs the results in JSON format.

The modular structure makes it easy to maintain and extend the application.