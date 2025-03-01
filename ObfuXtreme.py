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

class UltimateObfuscator:
    def __init__(self, filename):
        self.filename = filename
        self.code = self._read_file()
        self.aes_key = os.urandom(32)
        self.iv = os.urandom(16)

    def _read_file(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            return f.read()

    class VariableRenamer(ast.NodeTransformer):
        def __init__(self):
            self.var_map = {}
            
        def _obf_name(self, original):
            return f"var_{hashlib.shake_128(original.encode()).hexdigest(8)}"
            
        def visit_Name(self, node):
            if isinstance(node.ctx, (ast.Store, ast.Load)) and node.id not in ['print']:
                if node.id not in self.var_map:
                    self.var_map[node.id] = self._obf_name(node.id)
                node.id = self.var_map[node.id]
            return node

    class ControlFlowFlattener(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            state_var = f"state_{random.randint(1000, 9999)}"
            new_body = [
                ast.Assign(
                    targets=[ast.Name(id=state_var, ctx=ast.Store())],
                    value=ast.Constant(value=0)
                )
            ]
            
            while_body = []
            for i, stmt in enumerate(node.body):
                while_body.append(
                    ast.If(
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
                )
            
            new_body.append(
                ast.While(
                    test=ast.Compare(
                        left=ast.Name(id=state_var, ctx=ast.Load()),
                        ops=[ast.Lt()],
                        comparators=[ast.Constant(value=len(node.body))]
                    ),
                    body=while_body,
                    orelse=[]
                )
            )
            node.body = new_body
            return node

    class StringEncryptor(ast.NodeTransformer):
        def __init__(self, obfuscator):
            self.obfuscator = obfuscator
            self.in_fstring = False
            
        def visit_JoinedStr(self, node):
            self.in_fstring = True
            self.generic_visit(node)
            self.in_fstring = False
            return node
            
        def visit_Constant(self, node):
            if isinstance(node.value, str) and not self.in_fstring:
                cipher = AES.new(self.obfuscator.aes_key, AES.MODE_CBC, self.obfuscator.iv)
                encrypted = cipher.encrypt(pad(node.value.encode(), 16))
                return ast.Call(
                    func=ast.Name(id='_decrypt_str', ctx=ast.Load()),
                    args=[ast.Constant(value=encrypted)],
                    keywords=[]
                )
            return node

    def _transform_ast(self):
        tree = ast.parse(self.code)
        
        transformers = [
            self.VariableRenamer(),
            self.ControlFlowFlattener(),
            self.StringEncryptor(self),
        ]
        
        for transformer in transformers:
            tree = transformer.visit(tree)
            ast.fix_missing_locations(tree)
            
        return marshal.dumps(compile(tree, "<obfuscated>", "exec"))

    def _build_loader(self, encrypted_data):
        return f"""
import sys
import os
import base64
import hashlib
import marshal
import zlib
import traceback
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def _anti_debug():
    if sys.gettrace() or (os.name == 'nt' and __import__('ctypes').windll.kernel32.IsDebuggerPresent()):
        sys.exit(1)
_anti_debug()

_KEY = {self.aes_key!r}
_IV = {self.iv!r}

def _decrypt_str(data):
    try:
        cipher = AES.new(_KEY, AES.MODE_CBC, _IV)
        return unpad(cipher.decrypt(data), 16).decode()
    except:
        return ""

def _main():
    try:
        #print("Initializing...")
        _encrypted = {encrypted_data!r}
        #print("Decrypting payload...")
        
        # Decryption steps
        cipher = AES.new(_KEY, AES.MODE_CBC, _IV)
        encrypted_data = base64.b85decode(_encrypted)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), 16)
        decompressed_data = zlib.decompress(decrypted_data)
        
        #print("Executing payload...")
        # Pass all needed functions to the execution context
        exec(marshal.loads(decompressed_data), {{
            **globals(),  # Include current global functions
            '__name__': '__main__',
            '__builtins__': __builtins__,
            '_decrypt_str': _decrypt_str  # Explicitly pass the decryption function
        }})
    except Exception as e:
        print("Execution failed:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    _main()
        """

    def obfuscate(self):
        transformed = self._transform_ast()
        compressed = zlib.compress(transformed, level=9)
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.iv)
        encrypted = base64.b85encode(cipher.encrypt(pad(compressed, 16))).decode()
        
        with open("obfuscated.py", "w") as f:
            f.write(self._build_loader(encrypted))
            
        print(f"[SUCCESS] Obfuscated with key: {self.aes_key.hex()}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ObfuXtreme.py <file.py>")
        sys.exit(1)
    UltimateObfuscator(sys.argv[1]).obfuscate()