"""Stage 0.5 runtime ops: strings, lists, maps, records, sums, IO.

Shared by evaluate() and the VM NATIVE opcode. Errors-as-values; never raise
for kernel diagnostics (IO OSError → ErrorVal).
"""

from __future__ import annotations

from pathlib import Path

from .effects import Capability, CapabilitySet, check_capabilities
from .errors import StructuredError
from .types import (
    BaseType,
    ListType,
    MapType,
    RecordType,
    SumType,
    STRING,
    I32,
    BYTES,
)
from .values import (
    BoolVal,
    BytesVal,
    ErrorVal,
    FloatVal,
    IntVal,
    ListVal,
    MapVal,
    RecordVal,
    StringVal,
    SumVal,
    UnitVal,
    Value,
)


def _err(kind: str, op: str, message: str) -> ErrorVal:
    return ErrorVal(StructuredError(kind=kind, op=op, message=message))


def _need_caps(names: list[str], granted: CapabilitySet | None) -> ErrorVal | None:
    granted = granted or CapabilitySet()
    needed: list[Capability] = []
    for n in names:
        try:
            needed.append(Capability(n))
        except ValueError:
            return _err("capability", "IO", "unknown capability " + n)
    if not check_capabilities(CapabilitySet(needed), granted):
        return _err("capability", "IO", "missing capabilities: " + ",".join(names))
    return None


def eval_op(
    op: str,
    args: list[Value],
    *,
    granted: CapabilitySet | None = None,
) -> Value:
    """Dispatch a Stage 0.5 / collection / IO op."""
    op = str(op).upper()
    if op == "LIST":
        if not args:
            return ListVal((), I32)
        # Heterogeneous lists allowed for bootstrap packs (Stage 0.5 / self-host).
        elem_t = args[0].type
        return ListVal(tuple(args), elem_t)

    if op == "LEN":
        if len(args) != 1:
            return _err("arity", "LEN", "expected 1")
        a = args[0]
        if isinstance(a, StringVal):
            return IntVal(32, len(a.value))
        if isinstance(a, ListVal):
            return IntVal(32, len(a.items))
        if isinstance(a, BytesVal):
            return IntVal(32, len(a.value))
        if isinstance(a, MapVal):
            return IntVal(32, len(a.items))
        return _err("type", "LEN", "LEN requires string|list|bytes|map")

    if op == "AT":
        if len(args) != 2:
            return _err("arity", "AT", "expected 2")
        coll, idx = args[0], args[1]
        if not isinstance(idx, IntVal):
            return _err("type", "AT", "index must be i32")
        i = idx.value
        if isinstance(coll, StringVal):
            if i < 0 or i >= len(coll.value):
                return _err("bounds", "AT", "string index out of range")
            return StringVal(coll.value[i])
        if isinstance(coll, ListVal):
            if i < 0 or i >= len(coll.items):
                return _err("bounds", "AT", "list index out of range")
            return coll.items[i]
        if isinstance(coll, BytesVal):
            if i < 0 or i >= len(coll.value):
                return _err("bounds", "AT", "bytes index out of range")
            return IntVal(32, coll.value[i])
        return _err("type", "AT", "AT requires string|list|bytes")

    if op == "SLICE":
        if len(args) != 3:
            return _err("arity", "SLICE", "expected 3")
        coll, start, end = args[0], args[1], args[2]
        if not isinstance(start, IntVal) or not isinstance(end, IntVal):
            return _err("type", "SLICE", "start/end must be i32")
        s, e = start.value, end.value
        if isinstance(coll, StringVal):
            return StringVal(coll.value[s:e])
        if isinstance(coll, ListVal):
            return ListVal(coll.items[s:e], coll.elem_t)
        if isinstance(coll, BytesVal):
            return BytesVal(coll.value[s:e])
        return _err("type", "SLICE", "SLICE requires string|list|bytes")

    if op == "CONCAT":
        if len(args) != 2:
            return _err("arity", "CONCAT", "expected 2")
        a, b = args[0], args[1]
        if isinstance(a, StringVal) and isinstance(b, StringVal):
            return StringVal(a.value + b.value)
        if isinstance(a, ListVal) and isinstance(b, ListVal):
            return ListVal(a.items + b.items, a.elem_t if a.items else b.elem_t)
        if isinstance(a, BytesVal) and isinstance(b, BytesVal):
            return BytesVal(a.value + b.value)
        return _err("type", "CONCAT", "CONCAT type mismatch")

    if op == "APPEND":
        if len(args) != 2:
            return _err("arity", "APPEND", "expected 2")
        lst, elem = args[0], args[1]
        if not isinstance(lst, ListVal):
            return _err("type", "APPEND", "APPEND requires list")
        return ListVal(lst.items + (elem,), lst.elem_t)

    if op == "CODEPOINT":
        if len(args) != 1:
            return _err("arity", "CODEPOINT", "expected 1")
        a = args[0]
        if not isinstance(a, StringVal) or len(a.value) != 1:
            return _err("type", "CODEPOINT", "expected single-char string")
        return IntVal(32, ord(a.value))

    if op == "FROM_CODEPOINT":
        if len(args) != 1:
            return _err("arity", "FROM_CODEPOINT", "expected 1")
        a = args[0]
        if not isinstance(a, IntVal):
            return _err("type", "FROM_CODEPOINT", "expected i32")
        try:
            return StringVal(chr(a.value))
        except ValueError:
            return _err("bounds", "FROM_CODEPOINT", "invalid code point")

    if op == "MAP_NEW":
        if args:
            return _err("arity", "MAP_NEW", "expected 0")
        return MapVal(frozenset(), STRING, I32)

    if op == "MAP_GET":
        if len(args) != 2:
            return _err("arity", "MAP_GET", "expected 2")
        m, k = args[0], args[1]
        if not isinstance(m, MapVal):
            return _err("type", "MAP_GET", "expected map")
        for kk, vv in m.items:
            if kk == k:
                return vv
        return _err("key", "MAP_GET", "missing key")

    if op == "MAP_SET":
        if len(args) != 3:
            return _err("arity", "MAP_SET", "expected 3")
        m, k, v = args[0], args[1], args[2]
        if not isinstance(m, MapVal):
            return _err("type", "MAP_SET", "expected map")
        items = {kk: vv for kk, vv in m.items}
        items[k] = v
        return MapVal(
            frozenset(items.items()),
            m.key_t if m.items else k.type,
            m.val_t if m.items else v.type,
        )

    if op == "RECORD":
        # RECORD[name:string, FIELD pairs already flattened as name, k1, v1, k2, v2...]
        # Callers pass: [StringVal(name), StringVal(k), val, ...]
        if len(args) < 1 or not isinstance(args[0], StringVal):
            return _err("arity", "RECORD", "RECORD[name, k,v, ...]")
        name = args[0].value
        rest = args[1:]
        if len(rest) % 2 != 0:
            return _err("arity", "RECORD", "fields must be k,v pairs")
        fields: list[tuple[str, Value]] = []
        type_fields: list[tuple[str, object]] = []
        for i in range(0, len(rest), 2):
            k, v = rest[i], rest[i + 1]
            if not isinstance(k, StringVal):
                return _err("type", "RECORD", "field name must be string")
            fields.append((k.value, v))
            type_fields.append((k.value, v.type))
        type_fields.sort(key=lambda x: x[0])
        rec_t = RecordType(name, tuple((n, t) for n, t in type_fields))  # type: ignore
        return RecordVal(frozenset(fields), rec_t)

    if op == "GET":
        if len(args) != 2:
            return _err("arity", "GET", "expected 2")
        base, field = args[0], args[1]
        fname = None
        if isinstance(field, StringVal):
            fname = field.value
        elif isinstance(field, IntVal) and isinstance(base, ListVal):
            return eval_op("AT", [base, field], granted=granted)
        else:
            # Ident lowered to string by caller; accept StringVal only here
            return _err("type", "GET", "field must be string")
        if isinstance(base, RecordVal):
            for k, v in base.fields:
                if k == fname:
                    return v
            return _err("key", "GET", "missing field " + fname)
        return _err("type", "GET", "GET requires record")

    if op == "SUM":
        if len(args) != 2:
            return _err("arity", "SUM", "expected 2")
        tag_v, payload = args[0], args[1]
        if not isinstance(tag_v, StringVal):
            return _err("type", "SUM", "tag must be string")
        tag = tag_v.value
        # Open sum for bootstrap: single-variant SumType
        rec = RecordType(tag, (("payload", payload.type),))
        return SumVal(tag, payload, SumType(((tag, rec),)))

    if op == "TAG":
        if len(args) != 1:
            return _err("arity", "TAG", "expected 1")
        a = args[0]
        if not isinstance(a, SumVal):
            return _err("type", "TAG", "expected sum")
        return StringVal(a.tag)

    if op == "PAYLOAD":
        if len(args) != 1:
            return _err("arity", "PAYLOAD", "expected 1")
        a = args[0]
        if not isinstance(a, SumVal):
            return _err("type", "PAYLOAD", "expected sum")
        return a.payload

    if op == "FS_READ":
        miss = _need_caps(["fs.read"], granted)
        if miss:
            return miss
        if len(args) != 1 or not isinstance(args[0], StringVal):
            return _err("arity", "FS_READ", "expected path string")
        try:
            data = Path(args[0].value).read_bytes()
        except OSError as e:
            return _err("io", "FS_READ", str(e))
        return BytesVal(data)

    if op == "FS_WRITE":
        miss = _need_caps(["fs.write"], granted)
        if miss:
            return miss
        if len(args) != 2 or not isinstance(args[0], StringVal):
            return _err("arity", "FS_WRITE", "expected path, data")
        path = args[0].value
        data = args[1]
        if isinstance(data, BytesVal):
            raw = data.value
        elif isinstance(data, StringVal):
            raw = data.value.encode("utf-8")
        else:
            return _err("type", "FS_WRITE", "data must be bytes|string")
        try:
            Path(path).write_bytes(raw)
        except OSError as e:
            return _err("io", "FS_WRITE", str(e))
        return UnitVal()

    if op == "PRINT":
        miss = _need_caps(["io.stdout"], granted)
        if miss:
            return miss
        if len(args) != 1:
            return _err("arity", "PRINT", "expected 1")
        v = args[0]
        if isinstance(v, StringVal):
            text = v.value
        elif isinstance(v, IntVal):
            text = str(v.value)
        elif isinstance(v, BoolVal):
            text = "true" if v.value else "false"
        else:
            text = repr(v)
        print(text)
        return UnitVal()

    if op == "BYTES_FROM_STRING":
        if len(args) != 1 or not isinstance(args[0], StringVal):
            return _err("arity", "BYTES_FROM_STRING", "expected string")
        return BytesVal(args[0].value.encode("utf-8"))

    if op == "STRING_FROM_BYTES":
        if len(args) != 1 or not isinstance(args[0], BytesVal):
            return _err("arity", "STRING_FROM_BYTES", "expected bytes")
        try:
            return StringVal(args[0].value.decode("utf-8"))
        except UnicodeDecodeError as e:
            return _err("io", "STRING_FROM_BYTES", str(e))

    if op == "FLOAT_FROM_STRING":
        if len(args) != 1 or not isinstance(args[0], StringVal):
            return _err("arity", "FLOAT_FROM_STRING", "expected string")
        try:
            return FloatVal(64, float(args[0].value))
        except ValueError as e:
            return _err("type", "FLOAT_FROM_STRING", str(e))

    if op == "ERR_MAKE":
        if len(args) < 1 or not isinstance(args[0], StringVal):
            return _err("arity", "ERR_MAKE", "expected code string")
        msg = args[1].value if len(args) > 1 and isinstance(args[1], StringVal) else args[0].value
        return ErrorVal(StructuredError(kind="err", message=msg, op=args[0].value))

    if op == "UNIT":
        return UnitVal()

    if op == "REF":
        if len(args) != 2 or not isinstance(args[0], StringVal):
            return _err("arity", "REF", "expected region string, value")
        from .values import RegionVal

        return RegionVal(args[1], args[0].value)

    if op == "DEREF":
        if len(args) != 1:
            return _err("arity", "DEREF", "expected 1")
        from .values import RegionVal

        a = args[0]
        if isinstance(a, RegionVal):
            return a.value
        return _err("type", "DEREF", "expected RegionVal")

    return _err("eval", op, "op not implemented")


# Ops handled by eval_op (not user DEF calls).
RUNTIME_OPS = frozenset(
    {
        "LIST",
        "LEN",
        "AT",
        "SLICE",
        "CONCAT",
        "APPEND",
        "CODEPOINT",
        "FROM_CODEPOINT",
        "MAP_NEW",
        "MAP_GET",
        "MAP_SET",
        "RECORD",
        "GET",
        "SUM",
        "TAG",
        "PAYLOAD",
        "FS_READ",
        "FS_WRITE",
        "PRINT",
        "BYTES_FROM_STRING",
        "STRING_FROM_BYTES",
        "FLOAT_FROM_STRING",
        "ERR_MAKE",
        "UNIT",
        "REF",
        "DEREF",
    }
)
