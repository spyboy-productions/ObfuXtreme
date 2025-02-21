[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

ObfuXtreme is a cutting-edge Python obfuscation tool designed to protect intellectual property by making reverse engineering extremely difficult. It combines multiple layers of security:

- **AES-256 Encryption** with CBC mode
- **Abstract Syntax Tree (AST)** manipulation
- **Anti-Debugging** techniques
- **Polymorphic Code Generation**
- **Zlib Compression** + **Marshal Serialization**

Perfect for protecting sensitive algorithms, API keys, and proprietary business logic.

---

## ✨ Features

- **Military-Grade Encryption**  
  AES-256-CBC with per-build random keys
- **AST-Level Transformations**  
  Variable renaming, Control flow flattening, String encryption
- **Anti-Analysis Protections**  
  Debugger detection, Memory bombardment, Environment checks
- **Self-Destruct Mechanism**  
  Tamper detection with SHA-3 integrity checks
- **Stealth Operation**  
  Silent failure modes, Clean exception handling
- **Cross-Platform**  
  Works on Windows/Linux/macOS

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/ObfuXtreme.git
cd ObfuXtreme
pip install -r requirements.txt
