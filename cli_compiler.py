import ast
import subprocess
import os
import random
from binary_kernel import BitBlock, CollapseMechanism, FitnessSystem, OperatorEngine

class CLIBlockType:
    READ_FILE = 10
    PARSE_CSV = 11
    FILTER = 12
    TO_JSON = 13
    WRITE_FILE = 14

class Translator:
    """ Übersetzt BitBlock-Strukturen deterministisch in ausführbaren Code. """
    def __init__(self):
        self.rules = {
            CLIBlockType.READ_FILE: "with open(path) as f:\n    pass",
            CLIBlockType.PARSE_CSV: "import pandas as pd\ndf = pd.read_csv(path)",
            CLIBlockType.FILTER: "df = df[df['status'] == 'active']",
            CLIBlockType.TO_JSON: "json_data = df.to_json()",
            CLIBlockType.WRITE_FILE: "with open(out, 'w') as f:\n    f.write(json_data)"
        }
        
    def blocks_to_ast(self, blocks: list[BitBlock]) -> ast.Module:
        """ Wandelt die Struktur in einen AST um. """
        body = []
        for block in blocks:
            btype = block.b_type
            if btype in self.rules:
                code_snippet = self.rules[btype]
                parsed_nodes = ast.parse(code_snippet).body
                body.extend(parsed_nodes)
        return ast.Module(body=body, type_ignores=[])

    def generate_code(self, blocks: list[BitBlock]) -> str:
        tree = self.blocks_to_ast(blocks)
        # Formatiere den AST in sauberen Python-Code
        return ast.unparse(tree)

class Executor:
    """ Führt Code isoliert aus und liefert quantifiziertes Feedback (Energie). """
    def __init__(self, sandbox_file="sandbox_exec.py"):
        self.sandbox_file = sandbox_file

    def run(self, code: str) -> dict:
        with open(self.sandbox_file, "w") as f:
            f.write(code)
        
        try:
            # Hier müsste eigentlich isoliert werden (z.B. per Docker/Firecracker), 
            # für den Prototyp reicht subprocess
            result = subprocess.run(
                ["python", self.sandbox_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exception": None
            }
        except subprocess.TimeoutExpired:
            return {"exit_code": 124, "stdout": "", "stderr": "Timeout", "exception": "TimeoutError"}
        except Exception as e:
             return {"exit_code": 1, "stdout": "", "stderr": str(e), "exception": str(e)}

class FeedbackSystem(FitnessSystem):
    """ Erweitertes Fitness-System, das auf Executor-Resultaten basiert. """
    def __init__(self, translator: Translator, executor: Executor):
        super().__init__()
        self.translator = translator
        self.executor = executor
        self.cache = {}
        
        # Test-Daten für Sandbox
        with open("test_data.csv", "w") as f:
            f.write("id,status\n1,active\n2,inactive\n")

    def evaluate(self, blocks: list[BitBlock]) -> int:
        # 1. Strukturelle Vor-Bewertung
        energy = len(blocks) * 10
        if not blocks: return 9999
        
        # Ein valides Pipeline-Konstrukt benötigt meistens Inputs und Outputs
        types = [b.b_type for b in blocks]
        
        # 2. Übesetzung zu Code
        code = self.translator.generate_code(blocks)
        if not code.strip():
            return energy + 2000 # Leerer Code ist extrem schlecht
            
        # Wir fügen noch Initialisierung hinzu, die für den Test unerlässlich ist
        header = "path = 'test_data.csv'\nout = 'out_data.json'\n"
        full_code = header + code
        
        # Lese Cache falls wir den Code schon mal evaluiert haben
        if code in self.cache:
            feedback = self.cache[code]
        else:
            feedback = self.executor.run(full_code)
            self.cache[code] = feedback
        
        if feedback["exit_code"] != 0:
            energy += 1000 # Fehler -> hohe Strafenergie
            if "NameError" in feedback["stderr"]:
                energy += 500 # Unbehandelte Abhängigkeiten
            elif "SyntaxError" in feedback["stderr"]:
                energy += 2000
        else:
            energy -= 500 # Erfolg -> Belohnung
            
            # Überprüfe Business Logic (Wurde JSON geschrieben?)
            if os.path.exists("out_data.json"):
                energy -= 1000 # Großes Ziel erreicht!
                os.remove("out_data.json")
            else:
                energy += 200 # Lief durch, aber kein Output
                
        # Energie beschränken und persistieren
        energy = max(0, energy)
        for b in blocks:
            # Wir speichern die Energie invertiert/limitiert im Blockmasken-Register
            b.b_energy = energy & 0xFFFFFFFF
            
        return energy

def run_phase_2():
    print("Initializing Neue Logik System - Translator & Executor Phase 2")
    translator = Translator()
    executor = Executor()
    feedback = FeedbackSystem(translator, executor)
    
    # Initiale (chaotische) Population an Blöcken
    initial_blocks = []
    for _ in range(3):
        b = BitBlock()
        b.b_type = random.choice([
            CLIBlockType.READ_FILE, 
            CLIBlockType.PARSE_CSV, 
            CLIBlockType.FILTER, 
            CLIBlockType.TO_JSON, 
            CLIBlockType.WRITE_FILE
        ])
        initial_blocks.append(b)
        
    print(f"Initiale Blöcke starten mit Energie: {feedback.evaluate(initial_blocks)}")
    print("Pipeline-Kollaps wird berechnet (Struktur-Code-Evolution)...")
    
    # Evolution nutzen wir aus Phase 1
    best_structure = CollapseMechanism.evolve(initial_blocks, feedback, generations=20, pop_size=15)
    
    print("\n--- STABILE LÖSUNG GEFUNDEN ---")
    print(f"Final Energy: {feedback.evaluate(best_structure)}")
    for b in best_structure:
        print(f"Block Typ: {b.b_type}")
        
    final_code = translator.generate_code(best_structure)
    print("\n--- GENERIERTER CODE ---")
    print(final_code)

if __name__ == "__main__":
    run_phase_2()
