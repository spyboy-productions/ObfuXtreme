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


ObfuXtreme is an advanced Python obfuscation tool designed to bypass antivirus detection and remain undetectable on VirusTotal.

- **AES-256 Encryption** with CBC mode
- **Abstract Syntax Tree (AST)** manipulation
- **Polymorphic Code Generation**
- **Zlib Compression** + **Marshal Serialization**

---

> [!CAUTION] 
> **Please use this responsibly and ethically.**
> <h4> DISCLAIMER </h4> 
> ObfuXtreme is a Proof of Concept (PoC) Tool created strictly for educational and research purposes. It is designed to demonstrate advanced Python obfuscation techniques.  
While this tool showcases its effectiveness by being undetectable on VirusTotal, it is NOT intended for malicious use. Using ObfuXtreme to obfuscate malware, bypass security measures, or engage in any unethical activities is strictly prohibited.  

#### **Responsibility & Ethics**  
- Cybersecurity professionals and developers can use this tool to **understand, analyze, and defend against** similar obfuscation techniques used by attackers.  
- The **developer does not condone** nor take responsibility for any misuse of this tool. Users are solely accountable for how they apply it.  
- **Always comply with local laws and ethical guidelines** when using this tool.  

By using ObfuXtreme, `you acknowledge that you understand these terms and accept full responsibility for your actions`.  

### ✨ Feature 

| Feature | Found? | Notes |
|---------|--------|-------|
| **Military-Grade Encryption** | ✅ | Uses **AES-256-CBC** for encryption. |
| **AES-256-CBC with per-build random keys** | ✅ | Generates a new **32-byte key** (`self.aes_key = os.urandom(32)`) and **16-byte IV** (`self.iv = os.urandom(16)`) per build. |
| **AST-Level Transformations** | ✅ | Implements **Variable Renaming, Control Flow Flattening, and String Encryption** using `ast.NodeTransformer`. |
| **Variable Renaming** | ✅ | Uses a hashing method (`shake_128`) to obfuscate variable names. |
| **Control Flow Flattening** | ✅ | Implements state-based execution in `ControlFlowFlattener`. |
| **String Encryption** | ✅ | Encrypts string literals with AES before execution. |
| **Anti-Analysis Protections** | ✅ | Includes **Debugger Detection, Memory Bombardment, and Environment Checks**. |
| **Debugger Detection** | ✅ | `_anti_debug()` exits if a debugger is detected (`sys.gettrace()` or `IsDebuggerPresent`). |
| **Memory Bombardment** | ❌ | No evidence of excessive memory usage or process exhaustion techniques. |
| **Environment Checks** | ✅ | Uses OS-based debugger detection. |
| **Self-Destruct Mechanism** | ✅ | Implements **Tamper detection with SHA-3 integrity checks** (used in `_decrypt_str` with exception handling). |
| **Stealth Operation** | ✅ | Uses **silent failure modes** (returns empty string if decryption fails) and **exception handling**. |
| **Cross-Platform** | ✅ | Designed for **Windows, Linux, and macOS** using standard Python and PyCryptodome. |

---

## VirusTotal Scans

<p align="center"> <strong>Without ObfuXtreme</strong><br> <img width="90%" src="https://github.com/spyboy-productions/ObfuXtreme/blob/main/Image/without_ObfuXtreme.png" alt="VirusTotal scan without ObfuXtreme" /> </p> 
<p align="center"> <strong>With ObfuXtreme</strong><br> <img width="90%" src="https://github.com/spyboy-productions/ObfuXtreme/blob/main/Image/with_ObfuXtreme.png" alt="VirusTotal scan with ObfuXtreme" /> </p>


## 📖 Installation
```bash
git clone https://github.com/spyboy-productions/ObfuXtreme.git
```
```
cd ObfuXtreme
```
```
pip install -r requirements.txt
```
```
python ObfuXtreme.py <your_script.py>
```
`To Run Light version With No External requirements:`
```
python light_ObfuXtreme.py <your_script.py>
```
## 🔥 Usage

To obfuscate a Python script, run:

Example:

`python ObfuXtreme.py test.py`

This will generate an obfuscated file named obfuscated.py that contains the encrypted and protected version of your script.

🛠️ Running the Obfuscated Script

Simply run:

`python obfuscated.py`

### To do:
1. add new module that Works only on the original machine.
2. add new module that ask for password.
3. add option to convert to .exe file after obfuscation.

<h4 align="center"> If you find this GitHub repo useful, please consider giving it a star! ⭐️ </h4> 
