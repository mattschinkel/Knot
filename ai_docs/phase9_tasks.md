# Phase 9 Tasks

| ID | Goal | File | Function/Class | Test |
|---|------|------|----------------|------|
| T1 | Opcodes + Chunk | `src/golem/vm/` | `Chunk` | `tests/vm/test_compile.py` |
| T2 | compile AST → Chunk | `src/golem/vm/compiler.py` | `compile_expr` | `tests/vm/test_compile.py` |
| T3 | VM execute arith/IF | `src/golem/vm/machine.py` | `VM` | `tests/vm/test_vm_arith.py` |
| T4 | compile_program + CALL | `src/golem/vm/compiler.py` | `compile_program` | `tests/vm/test_vm_call.py` |
| T5 | hole trap + M5 + drift phase 9 | `src/golem/vm/` + baseline | `measure_m5` | `tests/vm/test_m5.py` |
