# Stage 0.5 Spec — Self-host language gaps

> Owner: Cursor. Implements `axiom_design.md` §22.5 gaps so Stage 1 knotc can be written in Knot.  
> Status: DECIDED — implementing.

Stage 0 (Python) already parses/checks/runs arith+IF+DEF. Stage 0.5 adds **runtime**
parity for strings, lists, maps, records, MATCH, and capability-gated IO — in both
`evaluate` and the bytecode VM.

---

## 1. Scope

### In
- String ops: `LEN`, `AT`, `SLICE`, `CONCAT`, `CODEPOINT`, `FROM_CODEPOINT`
- List: `LIST[...]`, `LEN`, `AT`, `APPEND`, `CONCAT`
- Map: `MAP_NEW[]`, `MAP_GET[m,k]`, `MAP_SET[m,k,v]`
- Record: `RECORD[name,FIELD[k,v],...]`, `GET[rec,field]`
- Sum/MATCH: `SUM[tag,payload]`, `TAG[v]`, `PAYLOAD[v]`, `MATCH[e,CASE[tag,body],...]`
- IO: `FS_READ[path]`, `FS_WRITE[path,data]`, `PRINT[v]` (caps: fs.read / fs.write / io.stdout)
- VM: `NATIVE` opcode (name + arity) dispatching to the same runtime
- Recursion regression tests (`fact`)

### Out
- MAP/FILTER higher-order (needs first-class closures in VM)
- Pretty sugar, LLVM, AI front-end in Knot

---

## 2. Decisions

### D1 — One runtime module
**DECISION:** `src/knot/runtime_ops.py` implements `eval_op(op, args, *, granted)`. Both `evaluate` and VM call it.

### D2 — NATIVE opcode
**DECISION:** `Op.NATIVE` with const name + arity; args on stack L→R.

### D3 — MATCH shape
**DECISION:** `MATCH[scrutinee,CASE[Tag,body],...]`. Scrutinee must be `SumVal`. First matching tag wins. Optional `CASE[Tag,name,body]` binds payload in body bindings.

### D4 — Strings are code-point sequences
**DECISION:** `AT`/`SLICE`/`LEN`/`CODEPOINT` operate on Unicode code points (Python str).

### D5 — IO never raises across evaluate
**DECISION:** Missing file / denied cap → `ErrorVal`.

---

## 3. DoD

- [x] Spec decided
- [x] runtime_ops + evaluate wired
- [x] VM NATIVE
- [x] MATCH parse/canonical/eval
- [x] IO with caps
- [x] Tests green
