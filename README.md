<h4 align="center"> If you find this GitHub repo useful, please consider giving it a star! ⭐ </h4> 
<p align="center">
    <a href="https://spyboy.in/twitter">
      <img src="https://img.shields.io/badge/-TWITTER-black?logo=twitter&style=for-the-badge">
    </a>
    &nbsp;
    <a href="https://spyboy.in/">
      <img src="https://img.shields.io/badge/-spyboy.in-black?logo=google&style=for-the-badge">
    </a>
    &nbsp;
    <a href="https://spyboy.blog/">
      <img src="https://img.shields.io/badge/-spyboy.blog-black?logo=wordpress&style=for-the-badge">
    </a>
    &nbsp;
    <a href="https://spyboy.in/Discord">
      <img src="https://img.shields.io/badge/-Discord-black?logo=discord&style=for-the-badge">
    </a>
</p>

<p align="center">
  <img width="20%" src="https://github.com/spyboy-productions/ObfuXtreme/blob/main/Image/logo_ObfuXtreme.jpg" />
</p>

---

## ⚡ ObfuXtreme — Advanced Python Obfuscation Engine

**ObfuXtreme** is an advanced Python obfuscation engine focused on **structural obfuscation**, **AST-level transformations**, and **runtime payload protection**.

It is designed for **security research**, **defensive analysis**, and **reverse-engineering studies** — not for malicious use.

✔ Produces heavily obfuscated Python code  
✔ Breaks static analysis and signature-based detection  
✔ Uses safe AST transformations (no bytecode patching)  
✔ Runtime loader with encrypted payload execution  

---

## ⚠️ Disclaimer & Ethics

> **Use responsibly and ethically.**

ObfuXtreme is a **Proof-of-Concept (PoC)** project intended strictly for:
- education
- research
- defensive cybersecurity testing

### ❌ You must NOT use this tool for:
- malware obfuscation
- bypassing security products
- evading detection for malicious purposes
- any illegal or unethical activity

The authors take **no responsibility for misuse**.  
By using this project, **you accept full responsibility** for how it is used.

---

## ✨ ObfuXtreme v4 — Key Features

| Feature | Status | Notes |
|------|------|------|
| **AES-256-CBC Encryption** | ✅ | Encrypts payload, strings, and bytes |
| **Per-String Random IV** | ✅ | Prevents frequency & pattern analysis |
| **XOR-Split Key Storage** | ✅ | AES key and IV split into multiple XOR parts |
| **AST-Level Obfuscation** | ✅ | Safe transformations using Python `ast` |
| **Local Variable Renaming** | ✅ | Arguments, globals, nonlocals preserved |
| **Safe Control-Flow Flattening** | ✅ | Only applied to simple, linear functions |
| **Encrypted Runtime Loader** | ✅ | Payload decrypted & executed at runtime |
| **Auto-Rebuild per Python Version** | ✅ | Build version enforced at runtime |
| **Cross-Platform** | ✅ | Windows, Linux, macOS |
| **Clean Failure Handling** | ✅ | Clear errors instead of crashes |
| **VT-Friendly (Research)** | ⚠️ | Structural obfuscation only |

---

## 🔁 Auto-Rebuild (Important)

ObfuXtreme **automatically locks the output to the Python version used during obfuscation**.

Example:
```text
Build with Python 3.12 → output runs only on Python 3.12
````

This is intentional and prevents:

* marshal incompatibility
* silent crashes
* undefined behavior

If you change Python versions, **rebuild the script**.

---

## 📦 Dependencies

### Required

* Python **3.10+**
* **pycryptodome**

Install dependency:

```bash
pip install pycryptodome
```

> The obfuscated output also requires `pycryptodome` unless packaged with PyInstaller.

---

## 🚀 Installation

```bash
git clone https://github.com/spyboy-productions/ObfuXtreme.git
cd ObfuXtreme
pip install -r requirements.txt
```

---

## 🧪 Usage

### Obfuscate a script

```bash
python ObfuXtreme.py your_script.py
```

or

```bash
python ObfuXtreme.py your_script.py obfuscated.py
```

### Output

```text
obfuscated.py
```

### Run obfuscated file

```bash
python obfuscated.py
```

---

## 🧪 VirusTotal Demonstration (Educational)

<p align="center">
<strong>Without ObfuXtreme</strong><br>
<img width="90%" src="https://github.com/spyboy-productions/ObfuXtreme/blob/main/Image/without_ObfuXtreme.png" />
</p>

<p align="center">
<strong>With ObfuXtreme</strong><br>
<img width="90%" src="https://github.com/spyboy-productions/ObfuXtreme/blob/main/Image/with_ObfuXtreme.png" />
</p>

These results demonstrate **structural obfuscation effectiveness** for research and analysis only.

---

## 📦 Creating a Standalone `.exe` (No Python Required)

If you want to distribute without requiring Python or pycryptodome:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole obfuscated.py
```

This bundles:

* Python runtime
* Crypto dependencies
* Obfuscated payload

---

## Common misunderstanding (important)

**“ObfuXtreme already obfuscates the code, so why does the OS matter?”**

Because obfuscation and packaging are two different steps:

```
ObfuXtreme outputs Python code
The obfuscated .py file is cross-platform
It still requires Python + pycryptodome
PyInstaller produces native binaries
Native binaries are OS-specific
Obfuscation ≠ packaging
```

<p align="center">
  <img width="90%" alt="Diagram" src="https://github.com/user-attachments/assets/a8ebc30f-15a5-4cc4-8b01-be013ac42229" />
</p>

* ✔ ObfuXtreme can be run on **any OS**
* ✔ The obfuscated `.py` file is **portable**
* ✔ **PyInstaller must run on macOS** to produce macOS binaries
* ✔ This is standard behavior for all Python packagers (PyInstaller, Nuitka, etc.)

---

## 🛠️ Roadmap

* [ ] Optional metamorphic transformations
* [ ] Junk code intensity levels
* [ ] Machine-bound execution
* [ ] Password-protected loader
* [ ] Optional marshal-free mode
* [ ] CI multi-Python build support

---

<h4 align="center">If this project helps you, please give it a ⭐ — it directly supports further development.</h4>
