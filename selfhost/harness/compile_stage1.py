"""Load Stage-1 .gol sources and drive lex/parse/codegen via Stage 0."""

from __future__ import annotations

from pathlib import Path

from golem.errors import StructuredError
from golem.parser import parse_program
from golem.values import ErrorVal, IntVal, ListVal, StringVal, SumVal, Value
from golem.vm.chunk import Chunk
from golem.vm.compiler import FuncInfo, ProgramImage
from golem.vm.machine import VM

ROOT = Path(__file__).resolve().parents[1]
STAGE1 = ROOT / "stage1"
FIXTURES = ROOT / "fixtures"


def _strip_rem(text: str) -> str:
    return "\n".join(
        ln
        for ln in text.splitlines()
        if ln.strip() and not ln.strip().upper().startswith("REM")
    )


def resolve_stage1_imports(root_name: str = "root.gol") -> list[str]:
    """Resolve IMPORT['name'] from root.gol into ordered .gol file basenames."""
    from golem.ast import OpExpr
    from golem.parser import parse_program
    from golem.values import StringVal

    root_path = STAGE1 / root_name
    if not root_path.is_file():
        return [
            "lexer.gol",
            "parser.gol",
            "ast.gol",
            "codegen.gol",
            "check.gol",
            "main.gol",
        ]
    nodes = parse_program(_strip_rem(root_path.read_text(encoding="utf-8")))
    files: list[str] = []
    for n in nodes:
        from golem.ast import ImportDecl, OpExpr, IdentExpr, LitExpr

        if isinstance(n, ImportDecl):
            files.append(str(n.module) + ".gol")
        elif isinstance(n, OpExpr) and str(n.op).upper() == "IMPORT":
            kids = list(n.children or [])
            if not kids:
                continue
            k0 = kids[0]
            if isinstance(k0, IdentExpr):
                name = str(k0.id)
            elif isinstance(k0, LitExpr):
                name = str(k0.value)
            else:
                name = str(k0)
            files.append(name + ".gol" if not name.endswith(".gol") else name)
    return files or [
        "lexer.gol",
        "parser.gol",
        "ast.gol",
        "codegen.gol",
        "check.gol",
        "main.gol",
    ]


def load_stage1_program() -> list:
    """Load Stage-1 sources via root.gol IMPORT graph (not a hard-coded list)."""
    nodes: list = []
    for name in resolve_stage1_imports():
        path = STAGE1 / name
        text = _strip_rem(path.read_text(encoding="utf-8"))
        nodes.extend(parse_program(text))
    return nodes


def _call_def_values(prog, name, args, *, granted_caps=None):
    """Call DEF with Value args (not AST)."""
    from golem.ast import DefNode, FnExpr
    from golem.partial import evaluate

    defs = {}
    for item in prog:
        if isinstance(item, DefNode):
            defs[str(item.name)] = item
    d = defs.get(name)
    if d is None:
        return ErrorVal(StructuredError(kind="eval", message="unknown " + name))
    body = d.body
    if not isinstance(body, FnExpr):
        return evaluate(body, program=prog, granted_caps=granted_caps)
    if len(args) != len(body.params):
        return ErrorVal(StructuredError(kind="eval", message="arity"))
    binds = {str(p[0]): args[i] for i, p in enumerate(body.params)}
    return evaluate(
        body.body, program=prog, bindings=binds, granted_caps=granted_caps
    )


def compile_air_source(prog: list, src: str) -> SumVal | ErrorVal | Value:
    return _call_def_values(prog, "compile_source", [StringVal(src)])


def program_from_sum(result: Value) -> ProgramImage | ErrorVal:
    if isinstance(result, ErrorVal):
        return result
    if not isinstance(result, SumVal) or result.tag != "Program":
        return ErrorVal(
            StructuredError(kind="harness", message="expected Program, got " + repr(result))
        )
    funcs = result.payload
    if not isinstance(funcs, ListVal):
        return ErrorVal(StructuredError(kind="harness", message="bad program payload"))
    image = ProgramImage()
    for item in funcs.items:
        if not isinstance(item, SumVal) or item.tag != "Func":
            return ErrorVal(StructuredError(kind="harness", message="bad Func"))
        pack = item.payload
        if not isinstance(pack, ListVal) or len(pack.items) != 4:
            return ErrorVal(StructuredError(kind="harness", message="bad Func pack"))
        name_v, arity_v, code_v, consts_v = pack.items
        name = str(name_v.value) if isinstance(name_v, StringVal) else str(name_v)
        if not isinstance(arity_v, IntVal):
            return ErrorVal(StructuredError(kind="harness", message="arity"))
        if not isinstance(code_v, ListVal) or not isinstance(consts_v, ListVal):
            return ErrorVal(StructuredError(kind="harness", message="code/consts"))
        code = []
        for c in code_v.items:
            if not isinstance(c, IntVal):
                return ErrorVal(StructuredError(kind="harness", message="code not int"))
            code.append(c.value)
        ch = Chunk(code=code, constants=list(consts_v.items))
        nlocals = max(arity_v.value, _max_local_slots(code))
        image.functions[name] = FuncInfo(
            name, arity_v.value, ch, (), nlocals=nlocals
        )
        if name == "__main":
            image.main = ch
    return image


def _max_local_slots(code: list[int]) -> int:
    """Highest LOAD_LOCAL/STORE_LOCAL index + 1 (0 if none)."""
    from golem.vm.opcode import Op

    i = 0
    hi = -1
    while i < len(code):
        op = code[i]
        i += 1
        if op in (Op.LOAD_CONST, Op.LOAD_LOCAL, Op.STORE_LOCAL, Op.JUMP, Op.JUMP_IF_FALSE):
            if i >= len(code):
                break
            if op in (Op.LOAD_LOCAL, Op.STORE_LOCAL):
                hi = max(hi, code[i])
            i += 1
        elif op in (Op.CALL, Op.NATIVE):
            i += 2
    return hi + 1


def chunk_from_sum(result: Value) -> Chunk | ErrorVal:
    """Back-compat: Program → __main chunk, or legacy Chunk sum."""
    if isinstance(result, ErrorVal):
        return result
    if isinstance(result, SumVal) and result.tag == "Program":
        img = program_from_sum(result)
        if isinstance(img, ErrorVal):
            return img
        if img.main is None:
            return ErrorVal(StructuredError(kind="harness", message="no __main"))
        return img.main
    if not isinstance(result, SumVal) or result.tag != "Chunk":
        return ErrorVal(StructuredError(kind="harness", message="expected Chunk/Program"))
    pack = result.payload
    if not isinstance(pack, ListVal) or len(pack.items) != 2:
        return ErrorVal(StructuredError(kind="harness", message="bad chunk pack"))
    code_v, consts_v = pack.items[0], pack.items[1]
    if not isinstance(code_v, ListVal) or not isinstance(consts_v, ListVal):
        return ErrorVal(StructuredError(kind="harness", message="code/consts"))
    code = []
    for c in code_v.items:
        if not isinstance(c, IntVal):
            return ErrorVal(StructuredError(kind="harness", message="code not int"))
        code.append(c.value)
    return Chunk(code=code, constants=list(consts_v.items))


def run_chunk(ch: Chunk, image: ProgramImage | None = None) -> Value:
    nlocals = _max_local_slots(ch.code)
    return VM(image or ProgramImage()).run_chunk(ch, arity_locals=nlocals)


def run_func(image: ProgramImage, name: str, args: list[Value] | None = None) -> Value:
    return VM(image).call(name, list(args or []))
