# Phase 9 Spec — Compiler / Bytecode VM

> Owner: Cursor. Decisions follow `ai_docs/axiom_design.md` §16 Phase 9 and §22.  
> Status: DECIDED — done.

Phase 9 delivers the **deterministic lowering half**: AST → bytecode → stack VM.
The AI front-end (judgment) stays out of this phase. Sub-200ms feedback is a
hard product constraint; drift metric **M5** measures compile+run latency.

---

## 1. Scope

### In Phase 9
- Bytecode opcodes + `Chunk` (code, constants, names)
- `compile(expr) -> Chunk` for literals, arith, compare, IF, holes
- `compile_program(defs) -> ProgramImage` (named functions from DEF/FN)
- Stack `VM.run(chunk | call)` returning `Value` / `ErrorVal`
- `knot.vm.run(source_or_ast, ...)` convenience
- M5: median compile+execute latency (ms) on a fixed suite; lower better
- Drift baseline phase 9 includes M5

### Explicitly OUT of Phase 9
- AI front-end / repairs during compile — Phase 5/10
- LLVM/native backend
- Full optimizer passes (peephole optional later)
- Concurrency opcodes (PAR) — Phase 11

---

## 2. Design decisions (DECIDED)

### D1 — Stack VM
**DECISION:** Single stack + locals frame. CALL pushes a frame; RETURN pops.

### D2 — Opcodes (v1)
**DECISION:** LOAD_CONST, LOAD_LOCAL, STORE_LOCAL, ADD/SUB/MUL/DIV/MOD/NEG,
EQ/NE/LT/LE/GT/GE, NOT/AND/OR, JUMP, JUMP_IF_FALSE, CALL, RETURN, POP, HOLE_TRAP.

### D3 — Deterministic lowering only
**DECISION:** Compiler never guesses; invalid AST shapes → ErrorVal at compile time.

### D4 — Holes
**DECISION:** Compiling a HoleExpr emits HOLE_TRAP; VM returns ErrorVal(kind=hole_trap).

### D5 — M5 measurement
**DECISION:** M5 = median milliseconds of (compile_program + run entry) over fixed suite,
N=21 warm runs after 3 warmup. Target product bar <200ms; baseline records measured value.

### D6 — Drift
**DECISION:** Phase 9 baseline includes M1–M5.

---

## 3. File layout

```
src/knot/vm/
  __init__.py
  opcode.py
  chunk.py
  compiler.py
  machine.py
tests/vm/
  test_compile.py
  test_vm_arith.py
  test_vm_call.py
  test_vm_hole.py
  test_m5.py
  test_vm_prop.py
```

---

## 4. Definition of done

- [x] Spec decided
- [x] compile + VM run for arith/IF/DEF calls
- [x] hole trap in VM
- [x] M5 measured + baseline
- [x] Full pytest green

---

## 5. Tasks

| ID | Goal | File | Symbol | Test |
|----|------|------|--------|------|
| T1 | Opcodes + Chunk | `vm/` | `Chunk` | `test_compile.py` |
| T2 | compile expr/program | `compiler.py` | `compile` | `test_compile.py` |
| T3 | VM arith/IF | `machine.py` | `VM` | `test_vm_arith.py` |
| T4 | DEF/FN CALL | `compiler.py` | `compile_program` | `test_vm_call.py` |
| T5 | hole + props + M5 drift | `machine`/drift | `measure_m5` | `test_m5.py` |
