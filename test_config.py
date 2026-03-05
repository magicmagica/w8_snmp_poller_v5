# This is a unit test that ensures validate_config() raises an error if targets are missing from the configuration.

#-----------------------------------------
# Missing targets key → ska ge ValueError:
#-----------------------------------------

import unittest  # Importerar testbibliotek
from poller import validate_config  # Importerar funktionen som ska testas

class TestConfig(unittest.TestCase):  # Testklass för config-tester

    def test_missing_targets(self):  # Test: saknade targets
        cfg = {  # Skapar test-config
            "defaults": {  # Standardinställningar
                "timeout_s": 2.5,  # Timeout i sekunder
                "retries": 1,  # Antal försök
                "target_budget_s": 10,  # Tidsbudget
                "oids": ["sysUpTime.0"]  # SNMP OID-lista
            }
        }
        with self.assertRaises(ValueError):  # Förväntar ValueError
            validate_config(cfg)  # Kör funktionen med fel config


#--------------------------------------
#Target missing ip → ska ge ValueError:
#--------------------------------------

    def test_target_missing_ip(self):  # Test: target saknar ip
        cfg = {  # Test-config
            "defaults": {  # Standardinställningar
                "timeout_s": 2.5,  # Timeout
                "retries": 1,  # Retries
                "target_budget_s": 10,  # Budget
                "oids": ["sysUpTime.0"]  # OID
            },
            "targets": [  # Lista med targets
                {"name": "router1"}  # ip saknas
            ]
        }
        with self.assertRaises(ValueError):  # Ska ge fel
            validate_config(cfg)  # Kör validering

#------------------------------------------
#Non-numeric timeout_s → ska ge ValueError:
#------------------------------------------

    def test_timeout_not_numeric(self):  # Test: timeout fel datatyp
        cfg = {  # Test-config
            "defaults": {  # Standardinställningar
                "timeout_s": "abc",  # Fel typ (ska vara nummer)
                "retries": 1,  # Retries
                "target_budget_s": 10,  # Budget
                "oids": ["sysUpTime.0"]  # OID
            },
            "targets": []  # Tom lista med targets
        }
        with self.assertRaises(ValueError):  # Förväntar fel
            validate_config(cfg)  # Kör funktionen

if __name__ == "__main__":  # Körs bara om filen startas direkt
    unittest.main()  # Startar alla tester

#Runs with:
#python -m unittest -v
