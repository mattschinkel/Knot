# Phase 3 Spec — Effects / Capabilities / Contracts

> Owner: R1 Architect (decides autonomously). Implementation: R2 Kernel Engineer. Verification: R4 Verifier. Human observes via the dashboard (non-blocking); R1 makes all decisions.  
> Status: DECIDED by R1 (autonomous) — implemented; tests green.

Phase 3 introduces **effects**, **capabilities**, and **contracts** as structural features of the Knot kernel. These are not runtime semantics but **first-class type-level constructs** that shape how functions behave, what permissions they require, and what guarantees they provide. The design is grounded in the deterministic kernel's need for composable, sandboxable, and verifiable AI execution.

The key innovation is that **prohibitions become structural constraints**: if a function is forbidden from using a capability, that restriction is encoded in the type system and prevents any path that would violate it — even at runtime.

---

## 1. Scope

### In Phase 3
- Effect sets (pure, fs.read, fs.write, fs.delete, net.request, db.read, db.write, io.stdout, io.stderr, time.now, random, ai)
- Capability granting (capability fs.read, capability net.request, etc.)
- Function contracts: requires, guarantees, ensures
- Runtime effect checking (effect validation at graph-level)
- Effect propagation through function composition
- Capability constraints on function calls (runtime enforcement)
- Effect/contract representation in the kernel's value and type models
- Property tests for all effect/contract logic

### Explicitly OUT of Phase 3
- Holes (PARTIAL/VALID/INVALID) — Phase 4
- Structured errors and repairs — Phase 5
- Edit operations — Phase 6
- AI tool FFI — Phase 10
- Concurrency / memory regions — Phase 11

---

## 2. Design decisions (DECIDED by R1)

These are the final, autonomous decisions. Each is recorded with rationale and is **FINAL**.

### D1 — Effects as first-class type-level features

**DECISION:** Effects are **first-class type-level constructs** encoded in function types via `EffectSet` and `EffectMap`.  
**Rationale:** Effects must be composable and checkable at type level to enable static analysis. They are not runtime flags but part of the function signature. A function's type includes its effect set (e.g., `T -> U@net`), and the kernel enforces that every call must have matching capabilities.

> Example: `DEF[send_email,FN[[to:string,body:string],?]]` → effect set = `{network, email}`

---

### D2 — Capabilities as runtime-grantable permissions

**DECISION:** Capabilities are **runtime-grantable permissions** (not type-level). A function may declare `requires capability net.request`, but the runtime decides whether to grant it.  
**Rationale:** This enables sandboxing: an AI agent can request a capability, but cannot seize it. The runtime enforces capability constraints as structural checks — if a function requires `net.request` and the agent has no such capability, the call fails with a structured error.

> Example: `DEF[get_weather,FN[[city:string],?]]` → runtime may reject if `net.request` not granted

---

### D3 — Contracts as type-level annotations

**DECISION:** Contracts (`requires`, `guarantees`, `ensures`) are **type-level annotations** that become part of the function's type signature. They are not runtime-checked by default but are used to generate **partial type errors** when violated.  
**Rationale:** Contracts enable static verification of program behavior. The kernel records them in the function type and uses them to infer or validate partial types. Violations are reported as `PARTIAL` with a contract error.

> Example: `DEF[sqrt,FN[[x:f64@money],sqrt[x]]]` → `requires: GE[x,0:f64@money]`

---

### D4 — Effect propagation via composition

**DECISION:** Effect sets **compose via union** when functions are composed.  
**Rationale:** If `f: A -> B@net` and `g: B -> C@io`, then `f.g: A -> C@(net|io)`. This ensures that the combined effect is the union of individual effects — no hidden leakage.

> Example: `f.g` has effect set = `f.effects ∪ g.effects`

---

### D5 — Capability constraints as structural checks

**DECISION:** Capability constraints are **structural checks** on function calls. A function with `requires capability net.request` can only be called if the runtime has granted that capability.  
**Rationale:** This prevents runtime violations. The kernel enforces that every call site must have matching capabilities — even if the function is defined in a module with different capabilities, the call must be authorized.

> Example: `DEF[get_weather,FN[[city:string],?]]` → runtime must have `net.request` to call

---

### D6 — Effects and capabilities in function types

**DECISION:** Function types include both **effect set** and **capability set**. The type is:  
`T -> U@E<caps>` where `E` is the effect set and `<caps>` is the granted capabilities.  
**Rationale:** This allows the kernel to track both what effects a function has and what capabilities are available at runtime — enabling fine-grained authorization.

> Example: `i32 -> i32@{pure} <net.request>` — function has no effects, but requires net.request capability

---

### D7 — Contracts as optional annotations

**DECISION:** Contracts are **optional** and only appear in the function definition. They do not affect the function's type unless used in inference.  
**Rationale:** This avoids bloating the type system. Contracts are used for documentation and verification, not type inference.

> Example: `DEF[sqrt,FN[[x:f64@money],sqrt[x]]]` — no `requires` or `guarantees` → optional

---

### D8 — Effect validation at graph-level

**DECISION:** Effect validation happens at **graph-level** — before any function body executes. The kernel checks that all effects are granted and all capabilities are authorized.  
**Rationale:** This ensures that effects are checked before any computation begins — preventing runtime violations. The check is part of the deterministic kernel's validation pass.

> Example: `f: A -> B@net` → runtime must have `net` capability before `f` runs

---

## 3. Value representation (`src/knot/values.py`)

Add the following to `Value`:

```
Value (abstract)
├─ IntVal        (bits: 32|64, signed, value)
├─ FloatVal      (bits: 32|64, value)
├─ BoolVal
├─ StringVal
├─ BytesVal
├─ UnitVal       (the single () value)
├─ ListVal       (items: tuple[Value,...], elem_t: Type)
├─ SetVal        (items: frozenset[Value], elem_t: Type)
├─ MapVal        (items: frozendict[Value,Value], k_t, v_t)
├─ TupleVal      (items: tuple[Value,...], types: tuple[Type,...])
├─ SumVal        (tag: str, payload: Value, sum_t: SumType)
├─ RecordVal     (fields: frozendict[str,Value], rec_t: RecordType)
├─ HoleVal       (expected: Type | None)        # D3
└─ ErrorVal      (err: StructuredError)          # D4
```

**Add to `Value` subclasses:**

- `EffectSetVal` — a frozenset of effect categories (e.g., `{network, io}`)
- `CapabilitySetVal` — a frozenset of granted capabilities (e.g., `{net.request, fs.read}`)
- `ContractVal` — a frozendict of contract annotations: `{requires: ..., guarantees: ..., ensures: ...}`

> Example: `EffectSetVal({network, io})` — function has these effects

---

## 4. Type algebra (`src/knot/types.py`)

Add the following to `Type`:

```
Type (abstract)
├─ BaseType        (name: "i32"|"i64"|"f32"|"f64"|"bool"|"string"
│                         |"bytes"|"unit"|"never")
├─ NominalType     (name: str, def: Type)        # type Distance = f64@meters
├─ OptionType      (inner: Type)                 # T?
├─ ListType        (elem: Type)                  # [T]
├─ SetType         (elem: Type)                  # {T}
├─ MapType         (key: Type, val: Type)         # K->V
├─ TupleType       (elems: tuple[Type,...])      # (T,U,V)
├─ SumType         (variants: frozendict[str, RecordType])  # T|U
├─ CapIntersect    (caps: tuple[Type,...])       # T&U (capability intersection)
├─ UnitType        (base: Type, dim: Dimension)   # T@dim   (D2)
└─ RegionType      (inner: Type, region: str)    # T<region R> (Phase 0: shape only)
```

**Add new type constructors:**

- `EffectType` — `T@E` where `E` is an effect set  
  Example: `i32@{pure}` or `string@{fs.read}`

- `CapabilityType` — `T<C>` where `C` is a capability set  
  Example: `i32 <net.request>`

- `ContractType` — `T[requires:R, guarantees:G, ensures:E]`  
  Example: `i32[sqrt, requires: GE[x,0], guarantees: GE[result,0]]`

> Example: `DEF[sqrt,FN[[x:f64@money],sqrt[x]]]` → type = `f64@{pure}[sqrt, requires: GE[x,0], guarantees: GE[result,0]]`

---

## 5. Units / dimensions (`src/knot/units.py`)

Units remain as exponent maps (D2). Add:

- `Dimension` — base dimension → exponent (e.g., `{m: 2}` for meters²)
- `UnitType` — `T@dim` where `dim` is a dimension

> Example: `Distance = f64@meters` → `f64@{m: 1}`

---

## 6. Effect and capability data structures

### `src/knot/effects.py`

```
EffectCategory = Literal[
    "pure",
    "fs.read",
    "fs.write",
    "fs.delete",
    "net.request",
    "db.read",
    "db.write",
    "io.stdout",
    "io.stderr",
    "time.now",
    "random",
    "ai"
]

EffectSet = frozenset[EffectCategory]

Capability = Literal[
    "fs.read",
    "fs.write",
    "fs.delete",
    "net.request",
    "db.read",
    "db.write",
    "io.stdout",
    "io.stderr",
    "time.now",
    "random",
    "ai"
]

CapabilitySet = frozenset[Capability]
```

### `src/knot/contracts.py`

```
ContractAnnotation = Dict[str, Any]

Contract = Dict[
    "requires": ContractAnnotation,
    "guarantees": ContractAnnotation,
    "ensures": ContractAnnotation
]

# Example: requires: {x: "f64@money", y: "i32"}, guarantees: {result: "f64@money"}
```

---

## 7. File layout

```
src/knot/
├── values.py          # Value representation (extends Value)
├── types.py           # Type algebra (adds EffectType, CapabilityType, ContractType)
├── effects.py        # Effect categories and sets
├── contracts.py      # Contract annotations
├── effects_check.py  # Runtime effect validation
├── contracts_check.py # Contract violation detection
├── tests/
│   ├── effects/
│   │   ├── test_effects.py
│   │   └── test_composition.py
│   ├── contracts/
│   │   ├── test_requires.py
│   │   ├── test_guarantees.py
│   │   └── test_ensures.py
│   └── integration/
│       └── test_function_types.py
└── grammar/
    └── effects.gbnf   # GBNF grammar for effects/contracts
```

---

## 8. Definition of done

- All effect and capability types are defined and tested
- Function types include `EffectType` and `CapabilityType`
- Runtime effect validation passes for all function calls
- Contracts are parsed and stored in function types
- Effect composition via union is implemented
- Capability constraints are enforced at runtime
- All property tests pass (coverage >90%)
- GBNF grammar for effects/contracts is complete
- All tests pass in `tests/effect`, `tests/contract`, `tests/integration`

---

## 9. Resolved sub-questions (DECIDED by R1)

### Q1 — Should effects be runtime or type-level?

**DECISION:** Effects are **type-level**. They are part of the function signature and checked at graph-level.  
**Rationale:** Type-level effects enable static analysis and composable type inference.

---

### Q2 — Should capabilities be type-level or runtime?

**DECISION:** Capabilities are **runtime-grantable**. They are not part of the function type but are checked at runtime.  
**Rationale:** This enables sandboxing — an agent can request a capability, but cannot seize it.

---

### Q3 — Should contracts be optional or mandatory?

**DECISION:** Contracts are **optional**. They are only used for documentation and verification.  
**Rationale:** Avoids bloating the type system. Contracts are used to generate partial types when inferred.

---

### Q4 — Should effects compose via union or intersection?

**DECISION:** Effects compose via **union**.  
**Rationale:** If `f: A -> B@net` and `g: B -> C@io`, then `f.g: A -> C@(net|io)`. This ensures no hidden leakage.

---

### Q5 — Should capability constraints be enforced at runtime?

**DECISION:** Yes. Capability constraints are **enforced at runtime**.  
**Rationale:** Prevents runtime violations. The runtime checks that every call has matching capabilities.

---

### Q6 — Should contracts be part of the function type?

**DECISION:** Yes. Contracts are **part of the function type** as optional annotations.  
**Rationale:** Enables static verification and partial typing.

---

### Q7 — Should effects be first-class or second-class?

**DECISION:** Effects are **first-class**. They are part of the function type and can be passed as arguments.  
**Rationale:** Enables composable effect handling and type-level reasoning.

---

### Q8 — Should capabilities be passed as arguments?

**DECISION:** No. Capabilities are **runtime-grantable** and not passed as arguments.  
**Rationale:** Capabilities are permissions granted by the runtime — not passed between functions.

---

### Q9 — Should contracts be checked at runtime?

**DECISION:** Yes. Contracts are **checked at runtime** to detect violations.  
**Rationale:** Enables detection of contract violations during execution.

---

### Q10 — Should effects be tracked per-call?

**DECISION:** Yes. Effects are **tracked per-call** via `EffectSetVal`.  
**Rationale:** Enables fine-grained effect tracking and validation.

---