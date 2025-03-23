## 👉 Register a User
- **Method**: POST  
- **URL**: `http://127.0.0.1:5000/register`  
- **Headers**:  
  `Content-Type: application/json`  
- **Body (JSON, raw format)**:  
  ```json
  {
    "username": "testuser",
    "password": "testpass"
  }
  ```

## 👉 Login (Step 1)
- **Method**: POST  
- **URL**: `http://127.0.0.1:5000/login`  
- **Headers**:  
  `Content-Type: application/json`  
- **Body (JSON, raw format)**:  
  ```json
  {
    "username": "testuser",
    "password": "testpass"
  }
  ```
- **Expected Response**:  
  ```json
  {
    "message": "Enter 2FA code",
    "username": "testuser"
  }
  ```

## 👉 Generate QR Code (For Google Authenticator)
- **Method**: GET  
- **URL**: `http://127.0.0.1:5000/generate_qr/testuser`  
- **Expected Response**:  
  A QR code image will be returned.  
  Save and scan it using Google Authenticator.

## 👉 Verify 2FA Code (Step 2)
- **Method**: POST  
- **URL**: `http://127.0.0.1:5000/verify_2fa`  
- **Headers**:  
  `Content-Type: application/json`  
- **Body (JSON, raw format)**:  
  ```json
  {
    "username": "testuser",
    "otp": "123456"
  }
  ```
  (Replace "123456" with the actual OTP from Google Authenticator.)
- **Expected Response**:  
  ```json
  {
    "message": "2FA Verified"
  }
  ```

## 👉 Generate JWT Token (Final Step)
- **Method**: POST  
- **URL**: `http://127.0.0.1:5000/generate_token`  
- **Headers**:  
  `Content-Type: application/json`  
- **Body (JSON, raw format)**:  
  ```json
  {
    "username": "testuser",
    "otp": "123456"
  }
  ```
- **Expected Response**:  
  ```json
  {
    "access_token": "your_generated_token"
  }
  ```

## 3️⃣ Use JWT Token for Protected Routes

### 👉 Get All Products
- **Method**: GET  
- **URL**: `http://127.0.0.1:5000/products`  
- **Headers**:  
  ```
  Content-Type: application/json
  Authorization: Bearer your_generated_token
  ```
  (Replace `your_generated_token` with the token you got in the previous step.)
- **Expected Response**:  
  ```json
  [
    {
      "id": 1,
      "name": "Product Name",
      "price": 99.99
    }
  ]
  ```

### 👉 Add a Product
- **Method**: POST  
- **URL**: `http://127.0.0.1:5000/products`  
- **Headers**:  
  ```
  Content-Type: application/json
  Authorization: Bearer your_generated_token
  ```
- **Body (JSON, raw format)**:  
  ```json
  {
    "name": "Laptop",
    "price": 1500
  }
  ```
- **Expected Response**:  
  ```json
  {
    "message": "Product added successfully"
  }
  ```

### 👉 Update a Product
- **Method**: PUT  
- **URL**: `http://127.0.0.1:5000/products/1`  
- **Headers**:  
  ```
  Content-Type: application/json
  Authorization: Bearer your_generated_token
  ```
- **Body (JSON, raw format)**:  
  ```json
  {
    "name": "Updated Laptop",
    "price": 1700
  }
  ```
- **Expected Response**:  
  ```json
  {
    "message": "Product updated"
  }
  ```

### 👉 Delete a Product
- **Method**: DELETE  
- **URL**: `http://127.0.0.1:5000/products/1`  
- **Headers**:  
  ```
  Content-Type: application/json
  Authorization: Bearer your_generated_token
  ```
- **Expected Response**:  
  ```json
  {
    "message": "Product deleted"
  }
  ```

