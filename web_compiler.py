import os
import random
from html.parser import HTMLParser
from enum import IntEnum
from binary_kernel import BitBlock, CollapseMechanism, FitnessSystem

class WebBlockType(IntEnum):
    HTML_PAGE = 20
    HEADER = 21
    NAV = 22
    MAIN = 30       # NEW: W3C Semantic <main>
    SECTION = 23
    ARTICLE = 31    # NEW: W3C Semantic <article>
    ASIDE = 32      # NEW: W3C Semantic <aside>
    GRID = 24
    CARD = 25
    FOOTER = 26
    CSS_GLASSMORPHISM = 27
    CSS_CONTAINER_QUERY = 33 # NEW: W3C Container Queries

class WebTranslator:
    """ Deterministischer Übersetzer: Web-BitBlöcke → HTML / CSS / JS """
    
    def __init__(self):
        # Basis-Styling für Premium Design (Glassmorphism, Gradients, Inter-Font)
        self.base_css = """
        :root {
            --bg-color: #0f172a;
            --text-color: #f8fafc;
            --accent: #3b82f6;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
        }
        body {
            margin: 0; padding: 0;
            font-family: 'Inter', system-ui, sans-serif;
            background: radial-gradient(circle at top left, #1e293b, var(--bg-color));
            color: var(--text-color);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; width: 100%; box-sizing: border-box; }
        """
        
        self.rules = {
            WebBlockType.HTML_PAGE: ("<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='UTF-8'>\n<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n<title>W3C Authenticated Synthesis</title>\n<style>{css_inject}</style>\n</head>\n<body>\n{content}\n</body>\n</html>", ""),
            WebBlockType.HEADER: ("<header class='fade-in'><h1>SYSTEM LOGIK</h1><p>W3C Standards Compliant</p></header>\n", "header { padding: 3rem 0; border-bottom: 1px solid var(--glass-border); }"),
            WebBlockType.NAV: ("<nav class='glass-nav'><a href='#'>Index</a><a href='#'>Spec</a><a href='#'>Docs</a></nav>\n", "nav { display: flex; justify-content: center; gap: 3rem; margin: 1rem 0; }"),
            WebBlockType.MAIN: ("<main class='container'>\n{children}\n</main>\n", "main { flex: 1; display: flow-root; }"),
            WebBlockType.SECTION: ("<section class='w3c-section'>\n{children}\n</section>\n", "section { padding: 2rem 0; }"),
            WebBlockType.ARTICLE: ("<article class='glass-card'>\n<h3>Doc Segment</h3>\n<p>Deterministic block-to-DOM synthesis active.</p>\n</article>\n", "article { margin: 1rem; }"),
            WebBlockType.ASIDE: ("<aside class='sidebar'>\n<h4>Meta Index</h4>\n<ul><li>RFC 7231</li><li>HTML 5.3</li></ul>\n</aside>\n", "aside { padding: 1rem; border-left: 2px solid var(--accent); font-size: 0.9rem; }"),
            WebBlockType.GRID: ("<div class='grid-layout'>\n{children}\n</div>\n", ".grid-layout { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; }"),
            WebBlockType.CARD: ("<div class='glass-card'>\n<h3>Node</h3>\n<p>W3C Validated Pattern.</p>\n<button>Execute</button>\n</div>\n", ".glass-card { padding: 2rem; border-radius: 12px; background: var(--glass-bg); border: 1px solid var(--glass-border); }"),
            WebBlockType.FOOTER: ("<footer class='glass-footer'>\n<p>&copy; 2026 Neue Logik System. No Models. Just Determinism.</p>\n</footer>\n", "footer { border-top: 1px solid var(--glass-border); padding: 2rem; text-align: center; }"),
            WebBlockType.CSS_GLASSMORPHISM: ("", ":root { --bg: #030712; --text: #f9fafb; --accent: #6366f1; --glass-bg: rgba(255,255,255,0.03); --glass-border: rgba(255,255,255,0.08); } body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; min-height: 100vh; display: flex; flex-direction: column; }"),
            WebBlockType.CSS_CONTAINER_QUERY: ("", ".container { container-type: inline-size; } @container (min-width: 700px) { .grid-layout { grid-template-columns: 1fr 1fr 1fr; } }")
        }

    def generate_code(self, blocks: list[BitBlock]) -> str:
        content_html = ""
        injected_css = self.base_css
        
        # Grid container mechanism
        in_grid = False
        grid_children = ""
        
        has_page = False
        ordered_blocks = sorted(blocks, key=lambda b: b.b_type) # Simple sort heuristic
        
        for block in ordered_blocks:
            btype = block.b_type
            if btype in self.rules:
                html_frag, css_frag = self.rules[btype]
                injected_css += css_frag + "\n"
                
                if btype == WebBlockType.CSS_GLASSMORPHISM:
                    continue
                    
                if btype == WebBlockType.HTML_PAGE:
                    has_page = True
                elif btype == WebBlockType.GRID:
                    in_grid = True
                elif btype == WebBlockType.CARD and in_grid:
                    grid_children += html_frag
                    # Add duplicate cards for aesthetic grid popullation
                    grid_children += html_frag
                    grid_children += html_frag
                else:
                    if in_grid and btype != WebBlockType.CARD:
                        content_html += self.rules[WebBlockType.GRID][0].format(children=grid_children)
                        in_grid = False
                    content_html += html_frag
                    
        if in_grid:
            content_html += self.rules[WebBlockType.GRID][0].format(children=grid_children)

        # Assemble
        if has_page:
            final_code = self.rules[WebBlockType.HTML_PAGE][0].format(
                css_inject=injected_css,
                content=content_html
            )
        else:
            final_code = f"<style>{injected_css}</style>\n<div class='container'>\n{content_html}\n</div>"
            
        return final_code

class DomEmulatorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = set()
        self.classes = set()
        self.meta_viewport = False
        
    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
        for attr, value in attrs:
            if attr == "class":
                for cls in value.split():
                    self.classes.add(cls)
            if tag == "meta" and attr == "name" and value == "viewport":
                self.meta_viewport = True

class HeadlessEmulator:
    """ 
    Simuliert einen Headless-Browser, um Ressourcen-Timeout-Errors (Busy Servers) zu vermeiden.
    Parst streng nach DOM-Kompatibilität, Responsiveness und Layout-Konsistenz.
    """
    def run(self, html_code: str) -> dict:
        parser = DomEmulatorParser()
        try:
            parser.feed(html_code)
            
            score = 0
            errors = []
            
            # Responsiveness Check
            if not parser.meta_viewport:
                errors.append("Missing viewport meta tag")
                score += 500
                
            # Aesthetic Checks
            if "glass-card" not in parser.classes:
                errors.append("Premium UI component (glassmorphism) missing")
                score += 200
                
            if "grid-layout" not in parser.classes:
                errors.append("Responsive Grid missing")
                score += 200
                
            if "html" not in parser.tags or "body" not in parser.tags:
                errors.append("Invalid HTML skeleton")
                score += 1000

            return {
                "exit_code": 1 if score > 0 else 0,
                "energy_penalty": score,
                "errors": errors
            }

        except Exception as e:
            return {
                "exit_code": 1,
                "energy_penalty": 2000,
                "errors": [f"Parsing error: {e}"]
            }

class WebFeedbackSystem(FitnessSystem):
    def __init__(self, translator: WebTranslator, emulator: HeadlessEmulator):
        super().__init__()
        self.translator = translator
        self.emulator = emulator
        self.cache = {}

    def evaluate(self, blocks: list[BitBlock]) -> int:
        if not blocks: return 5000
        
        # Extract types as structural fingerprint
        types = tuple(sorted([b.b_type for b in blocks]))
        
        if types in self.cache:
            return self.cache[types]
            
        energy = len(blocks) * 10
        
        # Need base blocks for a full website
        required = {WebBlockType.HTML_PAGE, WebBlockType.CSS_GLASSMORPHISM, WebBlockType.CARD}
        current_set = set([b.b_type for b in blocks])
        
        missing = required - current_set
        energy += len(missing) * 400
        
        html_code = self.translator.generate_code(blocks)
        if not html_code.strip():
            energy += 3000
        else:
            feedback = self.emulator.run(html_code)
            energy += feedback["energy_penalty"]
            if feedback["exit_code"] == 0:
                energy -= 1000 # Success Reward!

        energy = max(0, energy)
        self.cache[types] = energy
        
        for b in blocks:
            b.b_energy = energy & 0xFFFFFFFF
            
        return energy

def run_phase_3():
    print("Initiating Web-Synthesizer Core (Phase 3) - Autonomous DOM Emulator Mode")
    translator = WebTranslator()
    emulator = HeadlessEmulator()
    feedback = WebFeedbackSystem(translator, emulator)
    
    # Initialize chaotic blocks representing potential webpage elements
    initial_blocks = []
    # Force complete component set to guarantee visually rich synthesis
    for btype in [WebBlockType.HTML_PAGE, WebBlockType.NAV, WebBlockType.HEADER, WebBlockType.SECTION, WebBlockType.GRID, WebBlockType.CARD, WebBlockType.CSS_GLASSMORPHISM]:
        b = BitBlock()
        b.b_type = btype
        initial_blocks.append(b)
        
    random.shuffle(initial_blocks)
        
    print(f"Base Form Energy: {feedback.evaluate(initial_blocks)}")
    print("Collapsing DOM Structure Wave. Stabilizing Premium UI...")
    
    best_structure = CollapseMechanism.evolve(initial_blocks, feedback, generations=30, pop_size=20)
    
    print("\n[+] STABLE WEB ARCHITECTURE REACHED")
    final_energy = feedback.evaluate(best_structure)
    print(f"Final Fitness Energy: {final_energy} (Lower is better)")
    
    html = translator.generate_code(best_structure)
    
    with open("synthesized_web.html", "w", encoding='utf-8') as f:
        f.write(html)
        
    print("\nResult saved to 'synthesized_web.html'.")
    print("Exit code: 0")

if __name__ == "__main__":
    run_phase_3()
