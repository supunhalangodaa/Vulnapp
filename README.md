# Vulnerable Web App CTF

A deliberately vulnerable web application for CTF challenges. This application contains 6 different vulnerabilities that you need to exploit to find the flags.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database and create a test user:
```bash
python init_db.py
```

4. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:5000

## Challenges

### 1. SQL Injection
Find the hidden user in the database by exploiting the search functionality.
Flag format: `FLAG{sql_1nj3ct10n_1s_d4ng3r0us}`

### 2. Command Injection
Execute a command on the server through the ping functionality.
Flag format: `FLAG{c0mm4nd_1nj3ct10n_br34ks_s3cur1ty}`

### 3. XSS (Cross-Site Scripting)
Inject a script to steal cookies from other users.
Flag format: `FLAG{xss_1s_4_br0ws3r_vuln3r4b1l1ty}`

### 4. Directory Traversal
Access a file outside the intended directory.
Flag format: `FLAG{4_d1r3ct0ry_tr4v3rs4l_1s_n0t_s3cur3}`

### 5. Insecure Deserialization
Exploit the profile update functionality to execute arbitrary code.
Flag format: `FLAG{d3s3r14l1z4t10n_1s_r1sky}`

### 6. Weak Password Reset
Reset a user's password using a weak token generation mechanism.
Flag format: `FLAG{w34k_t0k3ns_4r3_br34k4bl3}`

## Note
This application is intentionally vulnerable and should only be used in a controlled environment for educational purposes. 