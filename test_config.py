# Koden är ett unit test som kontrollerar att validate_config() kastar ett fel när targets saknas i konfigurationen.

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

if __name__ == "__main__":  # Körs bara om filen startas direkt
    unittest.main()  # Startar alla tester

#Runs with:
python -m unittest -v
