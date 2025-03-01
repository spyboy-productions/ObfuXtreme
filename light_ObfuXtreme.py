import ast
import base64
import marshal
import random
import string
import zlib
import sys
import time
import platform
import os
from datetime import datetime

class StealthObfuscator:
    def __init__(self, filename):
        self.filename = filename
        self.code = self._read_file()
        self.var_map = {}
        self._valid_identifiers = self._generate_valid_identifiers()
        
    def _read_file(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            return f.read()

    def _generate_valid_identifiers(self):
        common_prefixes = ['utils', 'helper', 'data', 'core', 'base', 'main']
        common_suffixes = ['manager', 'handler', 'processor', 'controller']
        
        valid_names = []
        for _ in range(500):
            prefix = random.choice(common_prefixes)
            suffix = random.choice(common_suffixes)
            random_part = ''.join(random.choices(string.ascii_lowercase, k=4))
            name = f"_{prefix}_{random_part}_{suffix}"
            valid_names.append(name)
        return valid_names

    def _generate_junk_code(self):
        junk_code = []
        int_vars = []
        list_vars = []

        # Create integer variables
        for _ in range(3):
            var_name = f"_{''.join(random.choices(string.ascii_lowercase, k=2))}{random.randint(1000, 9999)}"
            var_value = random.randint(1, 1000)
            int_vars.append(var_name)
            junk_code.append(f"{var_name} = {var_value}")

        # Create list variables
        for _ in range(2):
            var_name = f"_{''.join(random.choices(string.ascii_lowercase, k=2))}{random.randint(1000, 9999)}"
            junk_code.append(f"{var_name} = [i for i in range({random.randint(5, 10)})]")
            list_vars.append(var_name)

        # Integer operations
        int_operations = [
            "{var} = {var} + {value}",
            "{var} = {var} * {value} // {divisor}",
            "if {var} > {value}: {var} = {value}"
        ]

        # List operations
        list_operations = [
            "{var}.append({value})",
            "{var}.extend([{value}, {other}])",
            "del {var}[{index}]"
        ]

        # Generate type-safe operations
        for _ in range(3):
            # Integer operation
            if int_vars:
                var = random.choice(int_vars)
                value = random.randint(1, 100)
                divisor = random.randint(2, 5)
                junk_code.append(random.choice(int_operations).format(
                    var=var, value=value, divisor=divisor
                ))

            # List operation
            if list_vars:
                var = random.choice(list_vars)
                value = random.randint(1, 10)
                other = random.randint(1, 10)
                index = random.randint(0, 4)
                junk_code.append(random.choice(list_operations).format(
                    var=var, value=value, other=other, index=index
                ))

        return '\n'.join(junk_code)

    def _add_anti_analysis(self):
        return """
def _system_check():
    try:
        _start = time.time()
        
        _env_vars = os.environ.keys()
        if any(x in _env_vars for x in ['DEBUGGER', 'PYTHONINSPECT']):
            return False
            
        # Adjusted timing check to be more realistic
        _temp = sum(i * i for i in range(100000))  # Increased loop size
        elapsed = time.time() - _start
        if elapsed < 0.001:  # Adjusted threshold
            return False
            
        _sys_info = platform.system().lower()
        _check_paths = [os.path.expanduser('~'), os.getcwd(), sys.prefix]
        _check_terms = ['sandbox', 'virtual', 'analysis']
        
        if any(x in _sys_info for x in _check_terms):
            return False
            
        if any(any(term in path.lower() for term in _check_terms) for path in _check_paths):
            return False
            
        return True
    except:
        return False

def _validate_environment():
    if not _system_check():
        sys.exit(0)
    time.sleep(random.uniform(0.1, 0.3))
"""

    def obfuscate(self):
        tree = ast.parse(self.code)
        tree = RenameVars(self).visit(tree)
        tree = ControlFlowObfuscator().visit(tree)
        
        obfuscated_source = compile(ast.unparse(tree), "<string>", "exec")
        encoded = marshal.dumps(obfuscated_source)
        encoded = zlib.compress(encoded)
        encoded = base64.b85encode(encoded).decode()
        
        loader_code = f"""import base64, marshal, zlib, sys, time, platform, os, random
from datetime import datetime

{self._generate_junk_code()}

{self._add_anti_analysis()}

{self._generate_junk_code()}

def _execute_code():
    try:
        _validate_environment()
        _code = marshal.loads(zlib.decompress(base64.b85decode('{encoded}')))
        exec(_code, globals())
    except Exception as e:
        print(f"Error: {{e}}")  # Added error logging for debugging

if __name__ == "__main__":
    _execute_code()
"""
        
        with open("obfuscated.py", "w", encoding="utf-8") as f:
            f.write(loader_code)
            
        print("[+] File obfuscated successfully")

class ControlFlowObfuscator(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        wrapped_body = node.body
        for _ in range(2):
            wrapped_body = [
                ast.Try(
                    body=wrapped_body,
                    handlers=[
                        ast.ExceptHandler(
                            type=ast.Name(id='Exception', ctx=ast.Load()),
                            name=None,
                            body=[ast.Raise()]
                        )
                    ],
                    orelse=[],
                    finalbody=[]
                )
            ]
        node.body = wrapped_body
        return node

class RenameVars(ast.NodeTransformer):
    def __init__(self, obfuscator):
        self.obfuscator = obfuscator
        self.scope_vars = set()
        
    def _generate_random_name(self, name):
        if (name.startswith('__') or 
            name in ('self', 'cls', 'print', 'exec', 'eval', 'globals')):
            return name
            
        if name not in self.obfuscator.var_map:
            if self.obfuscator._valid_identifiers:
                self.obfuscator.var_map[name] = self.obfuscator._valid_identifiers.pop()
            else:
                new_name = f"_{random.choice(string.ascii_lowercase)}{random.randint(1000, 9999)}"
                self.obfuscator.var_map[name] = new_name
                
        return self.obfuscator.var_map[name]

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)):
            if isinstance(node.ctx, ast.Store):
                self.scope_vars.add(node.id)
            node.id = self._generate_random_name(node.id)
        return node

    def visit_FunctionDef(self, node):
        old_scope = self.scope_vars.copy()
        self.scope_vars = set()
        
        if not node.name.startswith('__'):
            node.name = self._generate_random_name(node.name)
            
        for arg in node.args.args:
            if not arg.arg.startswith('__'):
                arg.arg = self._generate_random_name(arg.arg)
                
        self.generic_visit(node)
        self.scope_vars = old_scope
        return node

    def visit_ClassDef(self, node):
        if not node.name.startswith('__'):
            node.name = self._generate_random_name(node.name)
        self.generic_visit(node)
        return node

def main():
    if len(sys.argv) != 2:
        print("Usage: python light_ObfuXtreme.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    obfuscator = StealthObfuscator(filename)
    obfuscator.obfuscate()

if __name__ == "__main__":
    main()