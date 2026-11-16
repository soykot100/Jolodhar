# JOLODHAR - VS Code Setup Guide (Bengali)

## VS Code Terminal-এ venv দিয়ে কীভাবে চালাবেন — Step by Step

### Step 1: ZIP extract করুন
ZIP file টি extract করে `jolodhar` folder খুলুন।

### Step 2: VS Code-এ project খুলুন
- VS Code খুলুন
- `File` → `Open Folder` → `jolodhar` folder select করুন

### Step 3: Terminal খুলুন
- VS Code-এ `Ctrl + ` (backtick) চাপুন অথবা
- Menu: `Terminal` → `New Terminal`

### Step 4: Virtual Environment তৈরি করুন
Terminal-এ এই command লিখুন:

**Linux / macOS:**
```bash
python3 -m venv venv
```

**Windows:**
```cmd
python -m venv venv
```

### Step 5: venv Activate করুন

**Linux / macOS (VS Code terminal - bash/zsh):**
```bash
source venv/bin/activate
```

**Windows (VS Code terminal - Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (VS Code terminal - PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

যদি PowerShell-এ error আসে (execution policy), তাহলে প্রথমে এটা রান করুন:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
তারপর আবার `venv\Scripts\Activate.ps1` রান করুন।

Activate হলে terminal-এ `(venv)` লেখা দেখাবে এভাবে:
```
(venv) user@machine:~/jolodhar$
```

### Step 6: Dependencies Install করুন
venv activate করা অবস্থায়:
```bash
pip install -r requirements.txt
```

### Step 7: ML Model Train করুন (প্রথমবার দরকার)
```bash
python ml/train_model.py
```
এতে `ml/model.pkl`, `ml/metrics.json` ইত্যাদি তৈরি হবে।

### Step 8: Server চালান
```bash
python app.py
```

### Step 9: Browser-এ খুলুন
- **Public View:** http://localhost:5000/public
- **Control Panel Login:** http://localhost:5000/login
  - Username: `admin`
  - Password: `jolodhar2025`

---

## One-Command Setup (Alternative)

আরো সহজে চাইলে `start.sh` (Linux/Mac) বা `start.bat` (Windows) রান করুন — এটা সব স্টেপ অটোমেটিক করবে:

**Linux / macOS:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

---

## VS Code এর Debug Feature ব্যবহার করুন

`.vscode/launch.json` আগেই configure করা আছে। VS Code-এ:
1. `Run` → `Start Debugging` (বা `F5`)
2. Configuration select করুন:
   - **"JOLODHAR Server (SocketIO)"** — main app run করতে
   - **"Train ML Model"** — model train করতে
   - **"JOLODHAR (Windows venv)"** — Windows-এর জন্য

---

## সমস্যা হলে (Troubleshooting)

### 1. `python` / `python3` command পাওয়া যাচ্ছে না
Python install করুন: https://www.python.org/downloads/
VS Code-এ `Python` extension install করুন।

### 2. `pip install` এ error
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Port 5000 already in use
`.env` file খুলে PORT পরিবর্তন করুন:
```
PORT=5001
```

### 4. Module not found error
venv activate করা আছে কিনা দেখুন — terminal-এ `(venv)` লেখা থাকা দরকার।

### 5. NASA POWER API error
ইন্টারনেট কানেকশন চেক করুন। API rate limit হলে কয়েক মিনিট পর আবার চেষ্টা করুন। Weather forecast ততক্ষণ Open-Meteo থেকে কাজ করবে।

### 6. Database reset করতে চাইলে
```bash
rm data/jolodhar.db
python app.py
```
Database আবার auto-create হবে demo data সহ।

---

## Quick Commands Summary

| Command | কাজ |
|---------|------|
| `python3 -m venv venv` | venv তৈরি (Linux/Mac) |
| `python -m venv venv` | venv তৈরি (Windows) |
| `source venv/bin/activate` | venv activate (Linux/Mac) |
| `venv\Scripts\activate` | venv activate (Windows) |
| `pip install -r requirements.txt` | dependencies install |
| `python ml/train_model.py` | ML model train |
| `python app.py` | server চালান |
| `deactivate` | venv থেকে বের হন |
