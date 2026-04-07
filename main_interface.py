import sys
import json
from system import FrontendKI, BitEncoder, CoreOrchestrator
from learning_module import NightlyLearner

def run_interactive_system():
    frontend = FrontendKI()
    encoder = BitEncoder()
    orchestrator = CoreOrchestrator()
    learner = NightlyLearner(orchestrator.macro_registry)
    
    print("\n" + "="*60)
    print(" NEUE LOGIK - INTERAKTIVES KONTROLLZENTRUM (V5.2) ")
    print("="*60)
    print("[INFO] Keine neuronale Netze. Rein binäre Operator-Logik.")
    print("[INFO] Sicherheits-Gateway: Aktiv.")
    print("[INFO] Lern-Modul: Bereit.\n")
    
    while True:
        try:
            print("-" * 40)
            user_input = input("WAS SOLL DAS SYSTEM SYNTHETISIEREN? (oder 'exit' / 'nightly'):\n> ")
            
            if user_input.lower() == 'exit':
                print("[BYE] System wird heruntergefahren.")
                break
                
            if user_input.lower() == 'nightly':
                learner.perform_nightly_loop()
                continue

            if not user_input.strip():
                continue

            # 1. FRONTEND: SEMANTISCHE INTERPRETATION
            task_json = frontend.parse_intent(user_input)
            
            if task_json["task"] == "blocked":
                print("\n[STOP] Sicherheits-Gateway hat den Zugriff verweigert.")
                continue
            
            if task_json["task"] == "unknown" or task_json["type"] == "none":
                print("\n[FEHLER] Intention konnte nicht in binäre Blöcke gemappt werden.")
                print("Versuchen Sie: 'Erstelle Website' oder 'Filtere CSV Datei'.")
                continue

            # 2. ENCODER & KERN: ZUSTANDSKOLLAPS
            print(f"\n[KERN] Starte binäre Synthese für Typ: {task_json['type'].upper()}...")
            initial_blocks = encoder.encode(task_json)
            
            # 3. ORCHESTRATOR: CODE GENERIERUNG & SANDBOX TEST
            final_code = orchestrator.process(initial_blocks, task_json["type"])
            
            print("\n[ERFOLG] Die Synthese war erfolgreich.")
            print(f"Ergebnis gespeichert in: {'final_output.html' if task_json['type'] == 'web' else 'final_output.py'}")
            
        except KeyboardInterrupt:
            print("\n[BYE] Systemabbruch durch User.")
            break
        except Exception as e:
            print(f"\n[SYSTEM-FEHLER] Kritischer Abbruch: {e}")

if __name__ == "__main__":
    run_interactive_system()
