import os
import json
import random
from meta_kernel import MacroRegistry

class LearningLog:
    """ Archiv für alle Systemläufe, Erfolge und Fehler """
    PATH = "execution_logs.json"
    
    @staticmethod
    def append(task_type: str, energy: int, success: bool, block_sequence: list[int]):
        logs = []
        if os.path.exists(LearningLog.PATH):
            try:
                with open(LearningLog.PATH, "r") as f:
                    logs = json.load(f)
            except: pass
            
        logs.append({
            "timestamp": os.path.getmtime(LearningLog.PATH) if os.path.exists(LearningLog.PATH) else 0,
            "task_type": task_type,
            "energy": energy,
            "success": success,
            "blocks": block_sequence
        })
        
        with open(LearningLog.PATH, "w") as f:
            json.dump(logs, f)

class NightlyLearner:
    """ SCHICHT 3: WISSENS- UND LERNMODUL (kontrolliert) """
    def __init__(self, registry: MacroRegistry):
        self.registry = registry
        self.whitelist = [
            "developer.mozilla.org",
            "docs.python.org",
            "w3.org",
            "rfc-editor.org"
        ]

    def perform_nightly_loop(self):
        print("\n" + "="*50)
        print(" NIGHTLY LEARNING LOOP - STARTING ")
        print("="*50)
        
        if not os.path.exists(LearningLog.PATH):
            print("[INFO] Keine neuen Logs zum Analysieren.")
            return

        with open(LearningLog.PATH, "r") as f:
            logs = json.load(f)

        # 1. Erfolgreiche Strukturen finden
        successes = [l for l in logs if l["success"]]
        print(f"[1] Analysiere {len(successes)} erfolgreiche Strukturen...")
        
        for s in successes:
            # Wenn eine Sequenz länger als 2 ist, als Makro speichern
            if len(s["blocks"]) >= 2:
                # Wir konvertieren IDs zurück in Dummy-BitBlöcke für die Registry
                from binary_kernel import BitBlock
                blocks = []
                for tid in s["blocks"]:
                    b = BitBlock()
                    b.b_type = tid
                    blocks.append(b)
                
                mid = self.registry.register_macro(blocks)
                print(f" -> Neues Muster verdichtet: {mid:x}")

        # 2. Fehlerquellen (Anti-Patterns) identifizieren
        failures = [l for l in logs if not l["success"]]
        print(f"[2] Analysiere {len(failures)} Fehler-Muster...")
        # (Heuristik: Bestimmte Block-Kombinationen vermeiden)
        
        # 3. Wissens-Update (Read-Only)
        print("[3] Aktualisiere technischen Wissensindex (Read-Only Whitelist)...")
        self.fetch_external_docs()

        print("[4] Lernzyklus abgeschlossen. System-Prioritäten aktualisiert.")

    def fetch_external_docs(self):
        # Simuliert Whitelist-Zugriff auf Dokumentation
        for domain in self.whitelist:
            print(f" -> Fetching {domain} technical updates (Read-Only)... OK")
        
        # Hier könnte man die Translator-Regeln im Speicher erweitern, 
        # wenn neue HTML5 Tags oder Python-Methoden gefunden werden.

class SecurityGateway:
    """ SICHERHEITSREGELN für den Frontend-Interpreter """
    @staticmethod
    def is_safe(intent_json: dict) -> bool:
        forbidden_keywords = ["rm ", "delete ", "drop table", "forkbomb", "overwrite system"]
        
        # Flache Prüfung des Task-Strings
        task_str = json.dumps(intent_json).lower()
        for kw in forbidden_keywords:
            if kw in task_str:
                return False
        return True
