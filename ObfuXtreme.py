import ast
import base64
import hashlib
import marshal
import os
import random
import sys
import traceback
import zlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def _rand_ident(prefix: str = "_", length: int = 8) -> str:
    """Generate a random identifier name."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return prefix + "".join(random.choice(alphabet) for _ in range(length))


class VariableCollector(ast.NodeVisitor):
    """
    Collects variable names that are assigned in the code.
    Also tracks global variables and function argument names.
    """
    def __init__(self):
        self.assigned_vars = set()
        self.global_vars = set()
        self.arg_names = set()

    def visit_Global(self, node):
        self.global_vars.update(node.names)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.assigned_vars.add(node.id)
        self.generic_visit(node)

    def visit_arg(self, node):
        # We track arg names separately so we can avoid renaming them later.
        self.arg_names.add(node.arg)
        self.assigned_vars.add(node.arg)
        self.generic_visit(node)


class VariableRenamer(ast.NodeTransformer):
    """
    Renames *local variables only*.
    Function arguments are NOT renamed to avoid breaking keyword calls.
    """
    def __init__(self, assigned_vars, arg_names):
        self.assigned_vars = set(assigned_vars)
        self.arg_names = set(arg_names)
        self.var_map = {}

        # Remove argument names from the set of variables to rename
        for a in self.arg_names:
            self.assigned_vars.discard(a)

    def _obf_name(self, original: str) -> str:
        return f"var_{hashlib.shake_128(original.encode()).hexdigest(8)}"

    def visit_Name(self, node):
        if node.id in self.assigned_vars:
            if node.id not in self.var_map:
                self.var_map[node.id] = self._obf_name(node.id)
            node.id = self.var_map[node.id]
        return node

    def visit_arg(self, node):
        # Do not rename arguments at all.
        return node


class ControlFlowFlattener(ast.NodeTransformer):
    """
    Flattens *simple* functions into a while+if state machine.
    Adds local initializers to avoid UnboundLocalError.
    Skips complex functions with constructs that are hard to safely transform.
    """

    COMPLEX_NODES = (
        ast.Return,
        ast.Yield,
        ast.YieldFrom,
        ast.AsyncFunctionDef,
        ast.Try,
        ast.With,
        ast.Break,
        ast.Continue,
    )

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # First, transform inner nodes
        self.generic_visit(node)

        # Skip complex functions – safer & avoids semantic breakage
        if any(isinstance(n, self.COMPLEX_NODES) for n in ast.walk(node)):
            return node

        original_body = list(node.body)
        if not original_body:
            return node

        # Collect locals assigned in this function
        assigned_in_func = set()
        arg_names = set()
        globals_in_func = set()
        nonlocals_in_func = set()

        for n in ast.walk(node):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                assigned_in_func.add(n.id)
            elif isinstance(n, ast.arg):
                arg_names.add(n.arg)
            elif isinstance(n, ast.Global):
                globals_in_func.update(n.names)
            elif isinstance(n, ast.Nonlocal):
                nonlocals_in_func.update(n.names)

        # Only initialize *true locals* (not args, not globals/nonlocals)
        assigned_locals = {
            name
            for name in assigned_in_func
            if name not in globals_in_func
            and name not in nonlocals_in_func
            and name not in arg_names
        }

        # Local initializers: name = None (helps avoid UnboundLocalError)
        initializers = []
        for name in sorted(assigned_locals):
            # Avoid messing with magic dunders
            if name.startswith("__") and name.endswith("__"):
                continue
            init = ast.Assign(
                targets=[ast.Name(id=name, ctx=ast.Store())],
                value=ast.Constant(value=None)
            )
            initializers.append(init)

        state_var = f"state_{random.randint(1000, 9999)}"

        new_body = [
            ast.Assign(
                targets=[ast.Name(id=state_var, ctx=ast.Store())],
                value=ast.Constant(value=0)
            )
        ]

        new_body.extend(initializers)

        while_body = []
        for i, stmt in enumerate(original_body):
            # Dispatch for each original statement
            dispatch_if = ast.If(
                test=ast.Compare(
                    left=ast.Name(id=state_var, ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=i)]
                ),
                body=[
                    stmt,
                    ast.AugAssign(
                        target=ast.Name(id=state_var, ctx=ast.Store()),
                        op=ast.Add(),
                        value=ast.Constant(value=1)
                    )
                ],
                orelse=[]
            )
            while_body.append(dispatch_if)

            # Simple opaque-predicate junk block (always false)
            opaque_if = ast.If(
                test=ast.Compare(
                    left=ast.BinOp(
                        left=ast.Constant(123),
                        op=ast.Mult(),
                        right=ast.Constant(456),
                    ),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(789)],  # 123*456 = 56088, never 789
                ),
                body=[ast.Expr(value=ast.Constant(value=None))],
                orelse=[]
            )
            while_body.append(opaque_if)

        new_body.append(
            ast.While(
                test=ast.Compare(
                    left=ast.Name(id=state_var, ctx=ast.Load()),
                    ops=[ast.Lt()],
                    comparators=[ast.Constant(value=len(original_body))]
                ),
                body=while_body,
                orelse=[]
            )
        )

        node.body = new_body
        return node


class StringEncryptor(ast.NodeTransformer):
    """
    Encrypts string and bytes literals (excluding f-string components)
    using AES-CBC. Replaces them with _decrypt_str(b"...") or
    _decrypt_bytes(b"...").
    """
    def __init__(self, key: bytes, iv: bytes):
        self.key = key
        self.iv = iv
        self.in_fstring = False

    def _encrypt(self, data: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return cipher.encrypt(pad(data, AES.block_size))

    def visit_JoinedStr(self, node: ast.JoinedStr):
        # Don't encrypt constants inside f-strings
        self.in_fstring = True
        self.generic_visit(node)
        self.in_fstring = False
        return node

    def visit_Constant(self, node: ast.Constant):
        if self.in_fstring:
            return node

        # Plain Python strings
        if isinstance(node.value, str):
            encrypted = self._encrypt(node.value.encode("utf-8"))
            return ast.Call(
                func=ast.Name(id="_decrypt_str", ctx=ast.Load()),
                args=[ast.Constant(value=encrypted)],
                keywords=[]
            )

        # Bytes / bytearray literals
        if isinstance(node.value, (bytes, bytearray)):
            encrypted = self._encrypt(bytes(node.value))
            return ast.Call(
                func=ast.Name(id="_decrypt_bytes", ctx=ast.Load()),
                args=[ast.Constant(value=encrypted)],
                keywords=[]
            )

        return node


class UltimateObfuscator:
    """
    Orchestrates AST transformation, encryption, and loader generation.
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.code = self._read_file()
        self.aes_key = os.urandom(32)  # AES-256
        self.iv = os.urandom(16)       # AES block size

        # Prepare obfuscated key/iv parts for the loader
        self.k_parts = self._split_key(self.aes_key, 3)
        self.iv_parts = self._split_key(self.iv, 2)

    def _read_file(self) -> str:
        with open(self.filename, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _split_key(key: bytes, parts: int):
        """
        Split a key into N XOR-combined parts.
        Store all parts, reconstruct by XOR of all.
        """
        if parts < 2:
            return [key]

        length = len(key)
        rand_parts = [os.urandom(length) for _ in range(parts - 1)]

        # last part = key xor all previous
        last = bytearray(key)
        for rp in rand_parts:
            last = bytearray(a ^ b for a, b in zip(last, rp))
        rand_parts.append(bytes(last))
        return rand_parts

    def _transform_ast(self) -> bytes:
        tree = ast.parse(self.code)

        # 1) Collect variables
        collector = VariableCollector()
        collector.visit(tree)
        assigned_vars = collector.assigned_vars - collector.global_vars
        arg_names = collector.arg_names

        # 2) Apply transformers
        transformers = [
            VariableRenamer(assigned_vars, arg_names),
            ControlFlowFlattener(),
            StringEncryptor(self.aes_key, self.iv),
        ]

        for tr in transformers:
            tree = tr.visit(tree)
            ast.fix_missing_locations(tree)

        code_obj = compile(tree, "<obfuscated>", "exec")
        return marshal.dumps(code_obj)

    def _build_loader(self, encrypted_data: str) -> str:
        """
        Builds the loader stub with:
        - obfuscated key/iv reconstruction
        - anti-debug
        - decrypt helpers
        - execution harness
        """
        anti_debug_name = _rand_ident("_ad_")
        main_func_name = _rand_ident("_m_")
        dec_str_name = _rand_ident("_ds_")
        dec_bytes_name = _rand_ident("_db_")

        # Prepare key/iv parts repr for embedding
        k_parts_repr = ", ".join(repr(p) for p in self.k_parts)
        iv_parts_repr = ", ".join(repr(p) for p in self.iv_parts)

        loader = f"""import sys
import os
import base64
import marshal
import zlib
import traceback

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def {anti_debug_name}():
    try:
        if sys.gettrace():
            raise SystemExit

        if os.name == "nt":
            try:
                import ctypes
                if ctypes.windll.kernel32.IsDebuggerPresent():
                    raise SystemExit
            except Exception:
                pass
    except Exception:
        pass


{anti_debug_name}()


def _reconstruct_key(parts):
    # XOR all parts together
    from functools import reduce
    return reduce(lambda a, b: bytes(x ^ y for x, y in zip(a, b)), parts)


_KEY_PARTS = [{k_parts_repr}]
_IV_PARTS = [{iv_parts_repr}]

_KEY = _reconstruct_key(_KEY_PARTS)
_IV = _reconstruct_key(_IV_PARTS)


def {dec_str_name}(data: bytes) -> str:
    try:
        cipher = AES.new(_KEY, AES.MODE_CBC, _IV)
        return unpad(cipher.decrypt(data), 16).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def {dec_bytes_name}(data: bytes) -> bytes:
    try:
        cipher = AES.new(_KEY, AES.MODE_CBC, _IV)
        return unpad(cipher.decrypt(data), 16)
    except Exception:
        return b""


# Stable names used inside obfuscated payload
_decrypt_str = {dec_str_name}
_decrypt_bytes = {dec_bytes_name}


def {main_func_name}():
    try:
        _encrypted = {encrypted_data!r}

        cipher = AES.new(_KEY, AES.MODE_CBC, _IV)
        encrypted_data = base64.b85decode(_encrypted)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), 16)
        decompressed_data = zlib.decompress(decrypted_data)

        ns = {{
            "__name__": "__main__",
            "__builtins__": __builtins__,
            "_decrypt_str": _decrypt_str,
            "_decrypt_bytes": _decrypt_bytes,
        }}

        exec(marshal.loads(decompressed_data), ns)
    except Exception:
        print("Execution failed:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    {main_func_name}()
"""
        return loader

    def obfuscate(self, output_file: str = "obfuscated.py"):
        transformed = self._transform_ast()
        compressed = zlib.compress(transformed, level=9)

        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.iv)
        encrypted_bytes = cipher.encrypt(pad(compressed, AES.block_size))
        encrypted_b85 = base64.b85encode(encrypted_bytes).decode("ascii")

        loader = self._build_loader(encrypted_b85)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(loader)

        print(f"[SUCCESS] Obfuscated → {output_file}")
        # Key/IV are no longer printed to avoid trivial extraction


def main():
    if len(sys.argv) < 2:
        print("Usage: python ObfuXtreme_v3.py <file.py> [output.py]")
        sys.exit(1)

    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print(f"File not found: {filename}")
        sys.exit(1)

    output_file = "obfuscated.py"
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]

    obf = UltimateObfuscator(filename)
    obf.obfuscate(output_file=output_file)


if __name__ == "__main__":
    main()
