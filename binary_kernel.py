import random
from enum import IntEnum
import hashlib

class BlockType(IntEnum):
    ACTION = 1
    DATA_FLOW = 2
    CONSTRAINT = 3
    IO = 4

class Ops(IntEnum):
    ADD_BLOCK = 1
    REMOVE_BLOCK = 2
    SWAP_BLOCKS = 3
    MUTATE_FLAGS = 4
    REWIRE_IO = 5
    MERGE_BLOCKS = 6
    SPLIT_BLOCK = 7
    SHIFT_BITS = 8
    XOR_PATTERN = 9

class BitBlock:
    """
    256-bit Memory Layout:
    0-7     (8 bit): Type (BlockType / ID)
    8-31   (24 bit): Flags (IO, ErrorHandling, Parallel)
    32-95  (64 bit): Parameters (Hash, Index)
    96-159 (64 bit): Input connections
    160-223(64 bit): Output connections
    224-255(32 bit): Energy/Meta
    """
    def __init__(self, value: int = 0):
        self.value = value & ((1 << 256) - 1) # Force 256-bit constraint

    def _get_bits(self, shift: int, bits: int) -> int:
        mask = (1 << bits) - 1
        return (self.value >> shift) & mask

    def _set_bits(self, shift: int, bits: int, val: int):
        mask = (1 << bits) - 1
        val = val & mask
        clear_mask = ~(mask << shift)
        self.value = (self.value & clear_mask) | (val << shift)

    @property
    def b_type(self) -> int: return self._get_bits(0, 8)
    @b_type.setter
    def b_type(self, val: int): self._set_bits(0, 8, val)

    @property
    def b_flags(self) -> int: return self._get_bits(8, 24)
    @b_flags.setter
    def b_flags(self, val: int): self._set_bits(8, 24, val)

    @property
    def b_params(self) -> int: return self._get_bits(32, 64)
    @b_params.setter
    def b_params(self, val: int): self._set_bits(32, 64, val)

    @property
    def b_inputs(self) -> int: return self._get_bits(96, 64)
    @b_inputs.setter
    def b_inputs(self, val: int): self._set_bits(96, 64, val)

    @property
    def b_outputs(self) -> int: return self._get_bits(160, 64)
    @b_outputs.setter
    def b_outputs(self, val: int): self._set_bits(160, 64, val)

    @property
    def b_energy(self) -> int: return self._get_bits(224, 32)
    @b_energy.setter
    def b_energy(self, val: int): self._set_bits(224, 32, val)

    def to_hex(self) -> str:
        return f"{self.value:064x}"

    def __repr__(self) -> str:
        return f"<BitBlock T:{self.b_type} F:{self.b_flags:06x} P:{self.b_params:016x} I:{self.b_inputs:016x} O:{self.b_outputs:016x} E:{self.b_energy}>"

class OperatorEngine:
    """ Applies deterministic, bitwise transformations to block lists. """
    @staticmethod
    def add_block(blocks: list[BitBlock], new_block: BitBlock):
        blocks.append(new_block)
        
    @staticmethod
    def remove_block(blocks: list[BitBlock], idx: int):
        if 0 <= idx < len(blocks):
            blocks.pop(idx)

    @staticmethod
    def swap_blocks(blocks: list[BitBlock], idx1: int, idx2: int):
        if 0 <= idx1 < len(blocks) and 0 <= idx2 < len(blocks):
            blocks[idx1], blocks[idx2] = blocks[idx2], blocks[idx1]

    @staticmethod
    def mutate_flags(block: BitBlock, mask: int):
        block.b_flags ^= mask

    @staticmethod
    def rewire_io(block: BitBlock, new_in: int, new_out: int):
        block.b_inputs = new_in
        block.b_outputs = new_out

    @staticmethod
    def xor_pattern(block: BitBlock, pattern: int):
        block.value ^= (pattern & ((1 << 256) - 1))

class FitnessSystem:
    """ Evaluates stability and structure. """
    def __init__(self, target_type_sequence: list[int] = None):
        self.target_type_sequence = target_type_sequence or []

    def evaluate(self, blocks: list[BitBlock]) -> int:
        """ Returns Energy. Lower is better (more stable). """
        energy = 0
        
        # Base energy
        if not blocks:
            return 9999
            
        # Complexity penalty
        energy += len(blocks) * 10
        
        # Linkage evaluation (are outputs linked?)
        # Simple heuristic: sequence matching target structure
        if self.target_type_sequence:
            for i, target_type in enumerate(self.target_type_sequence):
                if i < len(blocks):
                    if blocks[i].b_type != target_type:
                        energy += 500  # Penalty for wrong type
                    else:
                        energy -= 100  # Reward for correct type
                else:
                    energy += 1000 # Missing block penalty
        
        # Update individual block energy values (meta data)
        for b in blocks:
            b.b_energy = energy
            
        return max(0, energy)

class CollapseMechanism:
    """ Selects optimal structures from competing solutions. """
    @staticmethod
    def evolve(initial_blocks: list[BitBlock], fitness: FitnessSystem, generations=100, pop_size=20) -> list[BitBlock]:
        population = [ [BitBlock(b.value) for b in initial_blocks] for _ in range(pop_size) ]
        
        for _ in range(generations):
            # Evaluate all
            scored = [(fitness.evaluate(p), p) for p in population]
            scored.sort(key=lambda x: x[0])
            
            # Select top
            best = scored[:pop_size//2]
            
            # Collapse/Breed (Mutate)
            new_pop = [p[1] for p in best]
            while len(new_pop) < pop_size:
                parent = random.choice(best)[1]
                child = [BitBlock(b.value) for b in parent]
                
                # Apply random primitive operator
                op = random.choice(list(Ops))
                if op == Ops.ADD_BLOCK:
                    b = BitBlock()
                    b.b_type = random.randint(1, 4)
                    OperatorEngine.add_block(child, b)
                elif op == Ops.REMOVE_BLOCK and len(child) > 1:
                    OperatorEngine.remove_block(child, random.randint(0, len(child)-1))
                elif op == Ops.SWAP_BLOCKS and len(child) > 1:
                    OperatorEngine.swap_blocks(child, random.randint(0, len(child)-1), random.randint(0, len(child)-1))
                elif op == Ops.MUTATE_FLAGS and len(child) > 0:
                    OperatorEngine.mutate_flags(random.choice(child), random.randint(1, 0xFFFFFF))
                elif op == Ops.XOR_PATTERN and len(child) > 0:
                    OperatorEngine.xor_pattern(random.choice(child), random.randint(1, (1<<256)-1))
                    
                new_pop.append(child)
                
            population = new_pop
            
        # Return best collapse
        final_scored = [(fitness.evaluate(p), p) for p in population]
        final_scored.sort(key=lambda x: x[0])
        return final_scored[0][1]

def main():
    print("Initializing Neue Logik System - Binary Core Phase 1")
    engine = OperatorEngine()
    
    # Expected target pipeline: ACTION, DATA_FLOW, ACTION
    fitness = FitnessSystem(target_type_sequence=[
        BlockType.ACTION,
        BlockType.DATA_FLOW,
        BlockType.ACTION
    ])
    
    initial = [BitBlock()]
    initial[0].b_type = BlockType.IO
    
    print(f"Initial Energy: {fitness.evaluate(initial)}")
    
    print("Collapsing wave function...")
    best_structure = CollapseMechanism.evolve(initial, fitness, generations=100)
    
    print(f"Final Energy: {fitness.evaluate(best_structure)}")
    print("Stable Structure Blocks:")
    for b in best_structure:
        print(b)
        
    assert best_structure[0].b_type == BlockType.ACTION
    assert best_structure[1].b_type == BlockType.DATA_FLOW
    assert best_structure[2].b_type == BlockType.ACTION
    print("Test passed. Phase 1 foundation solid.")

if __name__ == '__main__':
    main()
