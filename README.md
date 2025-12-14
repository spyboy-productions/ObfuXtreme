<h4 align="center"> If you find this GitHub repo useful, please consider giving it a star! ⭐️ </h4> 
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

### ⚡ ObfuXtreme — Advanced Python Obfuscation Engine

ObfuXtreme is an advanced Python obfuscation tool designed to bypass antivirus detection and remain undetectable on VirusTotal.

✔ Produces highly obfuscated Python code

✔ Evades static detection

✔ Built using safe AST transformations

✔ Ideal for security research, analysis, reverse-engineering studies

---

### ⚠️ Disclaimer & Ethics

> [!CAUTION]
> **Use responsibly and ethically.**
> ObfuXtreme is a Proof-of-Concept (PoC) tool created strictly for education, research, and defensive cybersecurity purposes.

### **You must NOT use this for:**

* Obfuscating malware
* Bypassing security products
* Evading detection for malicious purposes
* Any illegal or unethical activity

The developers take **no responsibility** for misuse.
By using ObfuXtreme, **you accept full responsibility** for your actions and agree to comply with all applicable laws.

---

### ✨ ObfuXtreme v3 – Major Features

| Feature                           | Status | Notes                                                                                |
| --------------------------------- | ------ | ------------------------------------------------------------------------------------ |
| **AES-256-CBC Encryption**        | ✅      | Encrypts strings + bytes using per-build random key and IV                           |
| **Key Splitting (XOR)**           | ✅      | Keys are split into multiple XOR parts to avoid static extraction                    |
| **AST-Level Obfuscation**         | ✅      | Safe transformations using Python `ast` module                                       |
| **Variable Renaming**             | ✅      | Renames *locals only* to avoid breaking keyword arguments                            |
| **Safe Control Flow Flattening**  | ✅      | Only flattens simple functions (no return, break, continue, with, try, yield, async) |
| **Opaque Predicates**             | ✅      | Inserts junk conditional blocks to disrupt static analysis                           |
| **String & Bytes Encryption**     | ✅      | All string and bytes literals are AES-encrypted                                      |
| **Per-Build Random Polymorphism** | ✅      | Different output every time                                                          |
| **Anti-Debugging**                | ✅      | Detects sys.gettrace() & Windows debugger                                            |
| **Cross-Platform**                | ✅      | Works on Windows, Linux, macOS                                                       |
| **Silent Failure Handling**       | ✅      | Decrypt functions fail silently to avoid leaking details                             |
| **VT Friendly (Research Only!)**  | ⚠️     | Obfuscated scripts are harder for static AV engines to classify                      |

---

### 🔥 What’s NEW in v3?

### 🆕 Safe, stable, real-world obfuscation

* No more broken functions
* No more argument name renaming (fixes keyword calls)
* No more `UnboundLocalError`
* Handles *complex codebases* reliably

### 🆕 New Control Flow Flattener (Safe Mode)

* Flattens only pure sequential functions
* Skips anything that may break semantic behavior
* Auto-initializes real locals
* Never touches arguments (`self`, `request`, etc.)

### 🆕 XOR Split AES Key & IV

```
_KEY_PARTS = [random1, random2, final_xor]
_KEY = XOR(all_parts)
```

Makes static extraction significantly harder.

### 🆕 Encrypted Bytes + Strings

String & bytes constants both get AES-encrypted.

### 🆕 Randomized Loader & Function Names

Every build uses unique random identifiers.

---

### 🧪 VirusTotal Demonstration (Educational)

<p align="center"> <strong>Without ObfuXtreme</strong><br> <img width="90%" src="https://github.com/spyboy-productions/ObfuXtreme/blob/main/Image/without_ObfuXtreme.png" /> </p> 
<p align="center"> <strong>With ObfuXtreme</strong><br> <img width="90%" src="https://github.com/spyboy-productions/ObfuXtreme/blob/main/Image/with_ObfuXtreme.png" /> </p>

These results highlight the effectiveness of structural obfuscation for **research and analysis**, NOT for malicious intent.

---

### 📦 Installation

```bash
git clone https://github.com/spyboy-productions/ObfuXtreme.git
cd ObfuXtreme
pip install -r requirements.txt
```

---

### 🚀 Usage

### Obfuscate a script:

```bash
python ObfuXtreme.py your_script.py
```
OR
```
python ObfuXtreme.py your_script.py obfuscated.py
```

### Output:

A file named:

```
obfuscated.py
```

### Run the obfuscated script:

```bash
python obfuscated.py
```

### Light Version (No External Libraries)

```bash
python light_ObfuXtreme.py your_script.py
```

---

### 🛠️ Development Roadmap

* [ ] Machine-bound execution module (“run only on this PC”)
* [ ] Obfuscated password-protected decryption
* [ ] Auto .exe generation after obfuscation
* [ ] Junk code generation levels (Low/Medium/Hard/Extreme)
* [ ] Add optional metamorphic transformations

---

<h4 align="center">If this project helps you, please give it a ⭐ — it motivates future improvements!</h4>
