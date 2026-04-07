import random
import hashlib
from binary_kernel import BitBlock, CollapseMechanism, OperatorEngine, Ops
from web_compiler import WebBlockType, WebFeedbackSystem, WebTranslator, HeadlessEmulator

# 255 represents a compressed/learned sequence of blocks
MACRO_BLOCK_TYPE = 255

class MacroRegistry:
    """ Musterverdichtung: Speichert erfolgreiche Substrukturen als einzelne Makro-Blöcke """
    def __init__(self, persistence_path="macros.json"):
        self.persistence_path = persistence_path
        self.macros = {}  # { hash_id: list_of_values }
        self.load()
        
    def load(self):
        import os, json
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r") as f:
                    data = json.load(f)
                    self.macros = {int(k): v for k, v in data.items()}
            except: pass

    def save(self):
        import json
        with open(self.persistence_path, "w") as f:
            json.dump({str(k): [b if isinstance(b, int) else b.value for b in v] for k, v in self.macros.items()}, f)

    def register_macro(self, blocks: list[BitBlock]) -> int:
        # Create a unique 64-bit fingerprint for the block sequence
        types_str = "-".join(str(b.b_type) for b in blocks)
        hash_id = int(hashlib.md5(types_str.encode()).hexdigest(), 16) & 0xFFFFFFFFFFFFFFFF
        
        # Save values for persistence
        self.macros[hash_id] = [b.value for b in blocks]
        self.save()
        return hash_id
        
    def get_macro(self, hash_id: int) -> list[BitBlock]:
        if hash_id not in self.macros:
            return []
        return [BitBlock(v) for v in self.macros[hash_id]]

class MetaTranslator(WebTranslator):
    """ Erweitert den Übersetzer um die Fähigkeit, Makro-Blöcke zu entpacken """
    def __init__(self, registry: MacroRegistry):
        super().__init__()
        self.registry = registry
        
    def generate_code(self, blocks: list[BitBlock]) -> str:
        # 1. Unroll Macros
        unrolled_blocks = []
        for b in blocks:
            if b.b_type == MACRO_BLOCK_TYPE:
                macro_blocks = self.registry.get_macro(b.b_params)
                unrolled_blocks.extend(macro_blocks)
            else:
                unrolled_blocks.append(b)
                
        # 2. Delegate to parent logic
        return super().generate_code(unrolled_blocks)

class MetaOperatorEngine:
    """ Erweitert die Basis-Operatoren um Operator-Evolution """
    @staticmethod
    def inject_macro(blocks: list[BitBlock], registry: MacroRegistry):
        if not registry.macros:
            return
        
        # Pick a random macro ID
        macro_id = random.choice(list(registry.macros.keys()))
        
        # Create macro block
        b = BitBlock()
        b.b_type = MACRO_BLOCK_TYPE
        b.b_params = macro_id
        
        blocks.append(b)

class AdvancedCollapseMechanism(CollapseMechanism):
    """ Der fortgeschrittene Kollaps-Mechanismus nutzt verdichtete Muster """
    @staticmethod
    def evolve_with_meta(initial_blocks: list[BitBlock], fitness, registry: MacroRegistry, generations=50, pop_size=20) -> list[BitBlock]:
        population = [ [BitBlock(b.value) for b in initial_blocks] for _ in range(pop_size) ]
        
        for _ in range(generations):
            scored = [(fitness.evaluate(p), p) for p in population]
            scored.sort(key=lambda x: x[0])
            
            best = scored[:pop_size//2]
            new_pop = [p[1] for p in best]
            
            while len(new_pop) < pop_size:
                parent = random.choice(best)[1]
                child = [BitBlock(b.value) for b in parent]
                
                # Meta-Mutation vs Standard-Mutation
                op = random.choice(list(Ops) + ["META_INJECT"])
                
                if op == "META_INJECT":
                    MetaOperatorEngine.inject_macro(child, registry)
                elif op == Ops.ADD_BLOCK:
                    b = BitBlock()
                    b.b_type = random.choice(list(WebBlockType))
                    OperatorEngine.add_block(child, b)
                elif op == Ops.REMOVE_BLOCK and len(child) > 1:
                    OperatorEngine.remove_block(child, random.randint(0, len(child)-1))
                elif op == Ops.SWAP_BLOCKS and len(child) > 1:
                    OperatorEngine.swap_blocks(child, random.randint(0, len(child)-1), random.randint(0, len(child)-1))
                    
                new_pop.append(child)
                
            population = new_pop
            
        final_scored = [(fitness.evaluate(p), p) for p in population]
        final_scored.sort(key=lambda x: x[0])
        return final_scored[0][1]


def run_phase_4():
    print("Initiating Phase 4: Optimization, Emergence & Pattern Density")
    registry = MacroRegistry()
    
    print("[1] Learning Baseline Structure (Musterverdichtung)...")
    # Manually teaching the system a recurring pattern: "A Responsive Grid Section with Cards"
    grid_pattern = []
    for btype in [WebBlockType.GRID, WebBlockType.CARD, WebBlockType.CARD]:
        b = BitBlock()
        b.b_type = btype
        grid_pattern.append(b)
        
    macro_ui_hash = registry.register_macro(grid_pattern)
    print(f"-> UI Macro (Grid + Cards) learned. Hash signature: {macro_ui_hash:x}")
    
    print("\n[2] Firing Meta-Evolution with Learned Macros...")
    translator = MetaTranslator(registry)
    emulator = HeadlessEmulator()
    feedback = WebFeedbackSystem(translator, emulator)
    
    # We start sparsely. The AI has to fill in the rest using the Macro!
    initial = []
    # Force essentials except Grid and Card (The AI should use the macro!)
    for btype in [WebBlockType.HTML_PAGE, WebBlockType.CSS_GLASSMORPHISM]:
        b = BitBlock()
        b.b_type = btype
        initial.append(b)
        
    best_structure = AdvancedCollapseMechanism.evolve_with_meta(
        initial, feedback, registry, generations=40, pop_size=20
    )
    
    print("\n[+] META-COLLAPSE SUCCESSFUL")
    energy = feedback.evaluate(best_structure)
    print(f"Final Fitness Energy: {energy}")
    
    macro_count = sum(1 for b in best_structure if b.b_type == MACRO_BLOCK_TYPE)
    print(f"System utilized {macro_count} Meta-Operator(s) to optimize the build path!")
    
    html = translator.generate_code(best_structure)
    with open("emergent_web.html", "w", encoding='utf-8') as f:
        f.write(html)
        
    print("Emergent UI saved to 'emergent_web.html'.")
    print("Exit code: 0")

if __name__ == "__main__":
    run_phase_4()
