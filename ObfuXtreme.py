import ast
import base64
import hashlib
import marshal
import os
import random
import sys
import zlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


# ======================================================
# Build-time Python version (AUTO-REBUILD)
# ======================================================
PY_VERSION = sys.version_info[:2]  # e.g. (3, 12)


# ======================================================
# Utilities
# ======================================================
def _rand_ident(prefix="_", length=8):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return prefix + "".join(random.choice(alphabet) for _ in range(length))


# ======================================================
# Variable collection
# ======================================================
class VariableCollector(ast.NodeVisitor):
    def __init__(self):
        self.assigned = set()
        self.globals = set()
        self.args = set()

    def visit_Global(self, node):
        self.globals.update(node.names)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.assigned.add(node.id)

    def visit_arg(self, node):
        self.args.add(node.arg)
        self.assigned.add(node.arg)


# ======================================================
# Variable renaming (locals only)
# ======================================================
class VariableRenamer(ast.NodeTransformer):
    def __init__(self, assigned, args, globals_):
        self.rename = set(assigned) - set(args) - set(globals_)
        self.map = {}

    def _new(self, name):
        return "v_" + hashlib.shake_128(name.encode()).hexdigest(8)

    def visit_Name(self, node):
        if node.id in self.rename:
            if node.id not in self.map:
                self.map[node.id] = self._new(node.id)
            node.id = self.map[node.id]
        return node


# ======================================================
# Control-flow flattening (SAFE MODE)
# ======================================================
class ControlFlowFlattener(ast.NodeTransformer):
    SAFE_INIT_LOCALS = False

    BLOCKED = (
        ast.Return,
        ast.Yield,
        ast.YieldFrom,
        ast.Try,
        ast.With,
        ast.Break,
        ast.Continue,
        ast.AsyncFunctionDef,
        ast.Global,
        ast.Nonlocal,
    )

    def visit_FunctionDef(self, node):
        self.generic_visit(node)

        # Skip unsafe functions
        if any(isinstance(n, self.BLOCKED) for n in ast.walk(node)):
            return node

        # Skip closures / nested defs
        if any(isinstance(n, ast.FunctionDef) for n in node.body):
            return node

        original = list(node.body)
        if not original:
            return node

        new_body = []
        state = f"_st_{random.randint(1000, 9999)}"

        new_body.append(
            ast.Assign(
                targets=[ast.Name(state, ast.Store())],
                value=ast.Constant(0),
            )
        )

        while_body = []
        for i, stmt in enumerate(original):
            while_body.append(
                ast.If(
                    test=ast.Compare(
                        ast.Name(state, ast.Load()),
                        [ast.Eq()],
                        [ast.Constant(i)],
                    ),
                    body=[
                        stmt,
                        ast.AugAssign(
                            ast.Name(state, ast.Store()),
                            ast.Add(),
                            ast.Constant(1),
                        ),
                    ],
                    orelse=[],
                )
            )

        new_body.append(
            ast.While(
                test=ast.Compare(
                    ast.Name(state, ast.Load()),
                    [ast.Lt()],
                    [ast.Constant(len(original))],
                ),
                body=while_body,
                orelse=[],
            )
        )

        # Preserve implicit return
        new_body.append(ast.Return(ast.Constant(None)))

        node.body = new_body
        return node


# ======================================================
# String encryption (per-string IV)
# ======================================================
class StringEncryptor(ast.NodeTransformer):
    def __init__(self, key):
        self.key = key
        self.in_fstring = False

    def visit_JoinedStr(self, node):
        self.in_fstring = True
        self.generic_visit(node)
        self.in_fstring = False
        return node

    def _encrypt(self, data: bytes):
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(pad(data, 16))

    def visit_Constant(self, node):
        if self.in_fstring:
            return node

        if isinstance(node.value, str):
            enc = self._encrypt(node.value.encode())
            return ast.Call(
                ast.Name("_decrypt_str", ast.Load()),
                [ast.Constant(enc)],
                [],
            )

        if isinstance(node.value, (bytes, bytearray)):
            enc = self._encrypt(bytes(node.value))
            return ast.Call(
                ast.Name("_decrypt_bytes", ast.Load()),
                [ast.Constant(enc)],
                [],
            )

        return node


# ======================================================
# Obfuscator core
# ======================================================
class UltimateObfuscator:
    def __init__(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            self.code = f.read()

        self.key = os.urandom(32)
        self.iv = os.urandom(16)

    def _split(self, data, parts):
        out = [os.urandom(len(data)) for _ in range(parts - 1)]
        last = bytearray(data)
        for p in out:
            last = bytearray(a ^ b for a, b in zip(last, p))
        out.append(bytes(last))
        return out

    def transform(self):
        tree = ast.parse(self.code)

        vc = VariableCollector()
        vc.visit(tree)

        for t in (
            ControlFlowFlattener(),
            VariableRenamer(vc.assigned, vc.args, vc.globals),
            StringEncryptor(self.key),
        ):
            tree = t.visit(tree)
            ast.fix_missing_locations(tree)

        return marshal.dumps(compile(tree, "<obf>", "exec"))

    def build(self, output):
        payload = zlib.compress(self.transform(), 9)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted = cipher.encrypt(pad(payload, 16))
        payload_b85 = base64.b85encode(encrypted).decode("ascii")

        k_parts = self._split(self.key, 3)
        iv_parts = self._split(self.iv, 2)

        loader = f'''
# ==========================
# ObfuXtreme v4 Loader
# ==========================

import sys
import base64
import marshal
import zlib

# ---- Dependency guard ----
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
except ModuleNotFoundError:
    print("[FATAL] Missing dependency: pycryptodome")
    print("Install with: python -m pip install pycryptodome")
    sys.exit(1)

# ---- Python version guard (AUTO) ----
EXPECTED_PY = {PY_VERSION}

if sys.version_info[:2] != EXPECTED_PY:
    print("[FATAL] Unsupported Python version")
    print(f"Expected: {{EXPECTED_PY[0]}}.{{EXPECTED_PY[1]}}")
    print(f"Found:    {{sys.version_info[0]}}.{{sys.version_info[1]}}")
    sys.exit(1)

def _xor(parts):
    from functools import reduce
    return reduce(lambda a,b: bytes(x^y for x,y in zip(a,b)), parts)

_KEY = _xor({k_parts!r})
_IV  = _xor({iv_parts!r})

def _decrypt_str(d):
    iv, p = d[:16], d[16:]
    return unpad(AES.new(_KEY, AES.MODE_CBC, iv).decrypt(p), 16).decode("utf-8", "ignore")

def _decrypt_bytes(d):
    iv, p = d[:16], d[16:]
    return unpad(AES.new(_KEY, AES.MODE_CBC, iv).decrypt(p), 16)

_enc = base64.b85decode({payload_b85!r})
plain = unpad(AES.new(_KEY, AES.MODE_CBC, _IV).decrypt(_enc), 16)

exec(
    marshal.loads(zlib.decompress(plain)),
    {{
        "__name__": "__main__",
        "__builtins__": __builtins__,
        "_decrypt_str": _decrypt_str,
        "_decrypt_bytes": _decrypt_bytes,
    }}
)
'''
        with open(output, "w", encoding="utf-8") as f:
            f.write(loader)

        print("[OK] Obfuscated ->", output)


# ======================================================
# CLI
# ======================================================
def main():
    if len(sys.argv) < 2:
        print("Usage: python ObfuXtreme.py input.py [output.py]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "obfuscated.py"

    if not os.path.isfile(inp):
        print("File not found:", inp)
        sys.exit(1)

    UltimateObfuscator(inp).build(out)


if __name__ == "__main__":
    main()
