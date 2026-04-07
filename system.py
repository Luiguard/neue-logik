import json
import time
from binary_kernel import BitBlock
from web_compiler import WebBlockType, WebTranslator, HeadlessEmulator, WebFeedbackSystem
from cli_compiler import CLIBlockType, Translator, Executor, FeedbackSystem
from meta_kernel import MacroRegistry, MetaTranslator, AdvancedCollapseMechanism

from learning_module import LearningLog, NightlyLearner, SecurityGateway

class FrontendKI:
    """ SCHICHT 1: FRONTEND-KI (klein, interpretierend) """
    def __init__(self):
        # Mocks a 50M parameter intent extractor doing deterministic JSON parsing
        pass

    def parse_intent(self, text: str) -> dict:
        text = text.lower()
        
        # 1. Vor-Verarbeitung nach Intent
        intent = {"task": "unknown", "type": "none", "pipeline": []}
        
        if "website" in text or "web" in text:
            intent = {
                "task": "create_website",
                "type": "web",
                "pipeline": [
                    {"action": "html_page"},
                    {"action": "header"},
                    {"action": "nav"},
                    {"action": "grid"},
                    {"action": "card"},
                    {"action": "glassmorphism"}
                ]
            }
        elif "csv" in text or "filter" in text:
            intent = {
                "task": "create_program",
                "type": "cli",
                "pipeline": [
                    {"action": "read_file", "format": "csv"},
                    {"action": "filter", "column": "status", "value": "active"},
                    {"action": "to_json"},
                    {"action": "write_file"}
                ]
            }
        elif "lösche" in text or "rm " in text:
            intent = {"task": "system_delete", "type": "danger", "pipeline": []}
            
        # 2. SCHICHT 1: SICHERHEITSREGELN (Frontend blockiert gefährliche Aufgaben)
        if not SecurityGateway.is_safe(intent):
            print("\n[FRONTEND] SICHERHEITSREGEL VERLETZT: Blockiert destruktive Aufgabe.")
            return {"task": "blocked", "type": "none", "pipeline": []}
            
        return intent

class BitEncoder:
    """ Wandelt deterministisch JSON in initiale 256-Bit Blöcke für den Kern """
    @staticmethod
    def encode(task_json: dict) -> list[BitBlock]:
        blocks = []
        if task_json["type"] == "web":
            # Semantic to Bin Mapping
            mapping = {
                "html_page": WebBlockType.HTML_PAGE,
                "header": WebBlockType.HEADER,
                "nav": WebBlockType.NAV,
                "grid": WebBlockType.GRID,
                "card": WebBlockType.CARD,
                "glassmorphism": WebBlockType.CSS_GLASSMORPHISM
            }
            for item in task_json["pipeline"]:
                action = item["action"]
                if action in mapping:
                    b = BitBlock()
                    b.b_type = mapping[action]
                    blocks.append(b)
        elif task_json["type"] == "cli":
            mapping = {
                "read_file": CLIBlockType.READ_FILE,
                "filter": CLIBlockType.FILTER,
                "to_json": CLIBlockType.TO_JSON,
                "write_file": CLIBlockType.WRITE_FILE
            }
            # Adding PARSE_CSV implicitly as an required block for the core to figure out
            b_csv = BitBlock()
            b_csv.b_type = CLIBlockType.PARSE_CSV
            blocks.append(b_csv)
            
            for item in task_json["pipeline"]:
                action = item["action"]
                if action in mapping:
                    b = BitBlock()
                    b.b_type = mapping[action]
                    blocks.append(b)
        return blocks

class CoreOrchestrator:
    """ SCHICHT 2, 3 & 4: Kern, Übersetzer, Executor & Lernmechanismus """
    def __init__(self):
        self.macro_registry = MacroRegistry()
        
        # Web Environment
        self.web_translator = MetaTranslator(self.macro_registry)
        self.web_emulator = HeadlessEmulator()
        self.web_feedback = WebFeedbackSystem(self.web_translator, self.web_emulator)
        
        # CLI Environment
        self.cli_translator = Translator()
        self.cli_executor = Executor()
        self.cli_feedback = FeedbackSystem(self.cli_translator, self.cli_executor)

    def process(self, encoded_blocks: list[BitBlock], task_type: str):
        if not encoded_blocks:
            return "No valid blocks encoded."
            
        print(f"\n[KERN] Übernehme {len(encoded_blocks)} initiale Blöcke ins Register...")
        
        if task_type == "web":
            fitness = self.web_feedback
            translator = self.web_translator
            out_file = "final_output.html"
        else:
            fitness = self.cli_feedback
            translator = self.cli_translator
            out_file = "final_output.py"
            
        print("[KERN] Zustandskollaps läuft (Lerne & Optimiere)...")
        time.sleep(0.5) 
        
        best_structure = AdvancedCollapseMechanism.evolve_with_meta(
            encoded_blocks, fitness, self.macro_registry, generations=20, pop_size=15
        )
        
        final_energy = fitness.evaluate(best_structure)
        print(f"[EXECUTOR] Feedback: Stabilste Struktur gefunden mit Energy = {final_energy}")
        
        # Translate to exact output
        code = translator.generate_code(best_structure)
        
        if task_type == "web":
            with open(out_file, "w", encoding='utf-8') as f:
                f.write(code)
            print(f"[ÜBERSETZER] {out_file} (HTML/CSS) generiert.")
        else:
            with open(out_file, "w", encoding='utf-8') as f:
                f.write(code)
            print(f"[ÜBERSETZER] {out_file} (Python AST) generiert.")
            
        # 2. Loggen für das Wissens- und Lernmodul
        LearningLog.append(
            task_type=task_type,
            energy=final_energy,
            success=(final_energy == 0),
            block_sequence=[b.b_type for b in best_structure]
        )
        
        return code

def start_system():
    frontend = FrontendKI()
    encoder = BitEncoder()
    orchestrator = CoreOrchestrator()
    learner = NightlyLearner(orchestrator.macro_registry)
    
    print("="*50)
    print(" SYSTEM GESAMTABLAUF BEREIT (Security + Learning active) ")
    print("="*50)
    
    # 1. Sicherer Programmlauf
    human_input = "Ich brauche ein CLI tool, das eine CSV einliest, nach status active filtert und als json speichert."
    task_json = frontend.parse_intent(human_input)
    if task_json["task"] != "blocked":
        orchestrator.process(encoder.encode(task_json), task_json["type"])
    
    # 2. Versuch einer destruktiven Aktion (Sicherheits-Check)
    human_input_bad = "Lösche alle Dateien im System rm system."
    print(f"\n[USER] '{human_input_bad}'")
    task_json_bad = frontend.parse_intent(human_input_bad)
    
    # 3. Web-Run
    human_input_web = "Erstelle mir eine Website."
    task_json_web = frontend.parse_intent(human_input_web)
    if task_json_web["task"] != "blocked":
        orchestrator.process(encoder.encode(task_json_web), task_json_web["type"])

    # 4. NIGHTLY LEARNING CYCLE
    learner.perform_nightly_loop()

if __name__ == "__main__":
    start_system()
