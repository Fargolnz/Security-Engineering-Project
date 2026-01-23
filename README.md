# 🎭 Anonymous Messaging Bot – Secure vs Insecure Cryptography Demo

This project is an educational **Telegram bot** developed for a *Secure Computing / Computer Security* course.  
It demonstrates how **incorrect and incomplete use of cryptography** can silently break anonymity and lead to **identity disclosure**.

The repository contains **two Telegram bots with identical functionality but different security models**:

- 🔴 **Insecure Bot** — `bot_insecure.py`
- 🟢 **Secure Bot** — `bot_secure.py`

---

## 🧠 Project Motivation

Anonymous messaging systems are widely used in real-world applications.  
However, anonymity is **not guaranteed by intention**, but by **correct security design**.

This project demonstrates:

- Why **Base64 is NOT encryption**
- How **client-controlled tokens** can be abused
- How **tampering** leads to identity leakage
- How proper cryptographic design prevents these attacks

---

## ⚙️ Features

- Anonymous message sending via **unique personal links**
- Inline keyboard with **Reply** button
- **Continuous / threaded anonymous replies**
- Fully functional Telegram bot (real environment)
- Side-by-side comparison of secure vs insecure logic

---

## 🗂 Project Structure

```text
.
├── bot_insecure.py
├── bot_secure.py
├── .env.example
├── requirements.txt
└── README.md
```

---

 ## 👥 Developers

| Name | Role / Responsibility |
|------|----------|
| Seyyedeh Fargol Nazemzadeh | **Bot implementation and attack demonstration** – Gathered project requirements, implemented both insecure and secure Telegram bots, and demonstrated the bots in practice. |
| Seyyed Ali Faghih Mousavi | **Project Designer & Cryptography Analyst** – Defined the project scope and analyzed different encryption methods for insecure and secure implementation. |
| Saeed Razzaghi | **Documentation Specialist & Security Explainer** – Worked on detailed documentation, focusing on cryptography explanations and security concepts. |

---

## 🔴 Insecure Bot (`bot_insecure.py`)

### ❌ Security Issues

- Uses **Base64 encoding instead of real encryption**
- Reply tokens are:
  - Reversible
  - Trusted without validation
  - Stored directly in memory
- Callback data can be **tampered with**
- Sender identity can be recovered from reply tokens

### ⚠️ Impact

A user replying to an anonymous message can decode or manipulate the token and **reveal the real sender identity**, breaking anonymity.

### Vulnerabilities Demonstrated

- Information Disclosure
- Tampering
- Broken Cryptography
- Trusting Client-Side Data

---

## 🟢 Secure Bot (`bot_secure.py`)

### ✅ Security Improvements

- Uses **proper encryption with a secret key and IV**
- Tokens are:
  - Cryptographically protected
  - Validated before use
  - Never stored in raw form
- Manipulated or forged tokens are detected
- Only verified sender IDs are used internally

### 🛡️ Result

Anonymous messaging remains anonymous even during multi-step reply chains.

---

## 🔐 Security Concepts Covered

- Encoding vs Encryption
- Token Tampering
- Information Disclosure
- STRIDE Threat Model (T – Tampering)
- Secure token lifecycle management
- Server-side trust vs client-side data

---

## 🧪 Attack Scenario (Insecure Version)

1. User A sends an anonymous message to User B
2. Bot generates a Base64-based reply token
3. User B clicks **Reply**
4. The token is decoded or manipulated
5. Sender identity is revealed or forged

---

## 🛠️ Technologies Used

- Python 3.10+
- python-telegram-bot v20.6
- Telegram Bot API
- Cryptography primitives
- python-dotenv

---

## 🚀 How to Run

### 1️⃣ Clone the repository

```bash
git clone https://github.com/fargolnz/anonymous-messaging-bot.git
cd your-repo
```

### 2️⃣ Create `.env` file

```ini
BOT_TOKEN=your_telegram_bot_token
AES_KEY=your_secret_key
STATIC_IV=your_static_iv
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the bot

```bash
python bot_insecure.py
# or
python bot_secure.py
```

---

## 🎓 Educational Purpose

This project is **strictly for educational use**.

It demonstrates real-world security design mistakes and shows how small cryptographic errors can completely break system guarantees.

**Do NOT use the insecure version in production.**

---

## 📌 Disclaimer

This project does not promote misuse of Telegram or privacy violations.  
All vulnerabilities are demonstrated in a controlled academic environment.

---

## ⭐ Final Note

**Anonymity is not a feature — it is a security guarantee.**  
And guarantees only exist when cryptography is used correctly.
