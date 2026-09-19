import pytest
import time
from fastapi.testclient import TestClient
from main import app
from core.auth import (
    hash_password,
    verify_password,
    generate_otp,
    hash_otp,
    verify_otp_hash,
    create_access_token,
    decode_access_token
)
from core.memory import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_password,
    save_otp_record,
    get_last_otp_record,
    verify_and_claim_otp,
    consume_verification_token
)

client = TestClient(app)

def test_password_hashing():
    pwd = "SecurePassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_otp_generation_and_hashing():
    otp = generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()
    
    hashed = hash_otp(otp)
    assert verify_otp_hash(otp, hashed) is True
    assert verify_otp_hash("000000", hashed) is False

def test_jwt_token_generation_and_decoding():
    token = create_access_token({"sub": "test@example.com", "user_id": "user-123"})
    payload = decode_access_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["user_id"] == "user-123"
    assert "exp" in payload

def test_full_auth_flow():
    test_email = f"testuser_{int(time.time())}@example.com"
    test_password = "MyStrongPassword2026!"
    
    # 1. Send OTP for registration
    send_res = client.post("/api/auth/send-otp", json={"email": test_email, "purpose": "register"})
    assert send_res.status_code == 200
    assert send_res.json()["status"] == "success"
    
    # 2. Extract the saved OTP directly from DB for test verification
    last_otp = get_last_otp_record(test_email, "register")
    assert last_otp is not None
    
    # For testing, generate and save known OTP
    known_otp = "123456"
    from datetime import datetime, timedelta, timezone
    exp_iso = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    save_otp_record(test_email, hash_otp(known_otp), "register", exp_iso)
    
    # 3. Verify OTP with wrong code
    bad_verify = client.post("/api/auth/verify-otp", json={"email": test_email, "otp": "999999", "purpose": "register"})
    assert bad_verify.status_code == 400
    
    # 4. Verify OTP with correct code
    good_verify = client.post("/api/auth/verify-otp", json={"email": test_email, "otp": known_otp, "purpose": "register"})
    assert good_verify.status_code == 200
    vtoken = good_verify.json()["verification_token"]
    assert vtoken is not None
    
    # 5. Register user
    reg_res = client.post("/api/auth/register", json={
        "email": test_email,
        "password": test_password,
        "verification_token": vtoken
    })
    assert reg_res.status_code == 200
    assert reg_res.json()["status"] == "success"
    
    # 6. Verify cannot re-register with duplicate email
    dup_res = client.post("/api/auth/send-otp", json={"email": test_email, "purpose": "register"})
    assert dup_res.status_code == 400
    
    # 7. Login with invalid password
    bad_login = client.post("/api/auth/login", json={"email": test_email, "password": "WrongPassword"})
    assert bad_login.status_code == 401
    
    # 8. Login with correct password
    login_res = client.post("/api/auth/login", json={"email": test_email, "password": test_password})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    access_token = login_data["access_token"]
    
    # 9. Test protected endpoint /api/auth/me without token -> 401
    unauth_res = client.get("/api/auth/me")
    assert unauth_res.status_code == 401
    
    # 10. Test protected endpoint with valid JWT
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    me_res = client.get("/api/auth/me", headers=auth_headers)
    assert me_res.status_code == 200
    assert me_res.json()["user"]["email"] == test_email
    
    # 11. Test conversation isolation
    create_conv_res = client.post("/api/conversations", json={"title": "My Private Chat"}, headers=auth_headers)
    assert create_conv_res.status_code == 200
    conv_id = create_conv_res.json()["id"]
    
    conv_list_res = client.get("/api/conversations", headers=auth_headers)
    assert conv_list_res.status_code == 200
    convs = conv_list_res.json()
    assert any(c["id"] == conv_id for c in convs)

def test_forgot_password_flow():
    reset_email = f"resetuser_{int(time.time())}@example.com"
    initial_pwd = "OldPassword123!"
    new_pwd = "NewSecurePassword456!"
    
    # Create user first
    create_user(reset_email, hash_password(initial_pwd))
    
    # Request forgot password OTP
    otp_code = "654321"
    from datetime import datetime, timedelta, timezone
    exp_iso = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    save_otp_record(reset_email, hash_otp(otp_code), "forgot_password", exp_iso)
    
    # Verify OTP
    v_res = client.post("/api/auth/verify-otp", json={"email": reset_email, "otp": otp_code, "purpose": "forgot_password"})
    assert v_res.status_code == 200
    vtoken = v_res.json()["verification_token"]
    
    # Reset password
    reset_res = client.post("/api/auth/forgot-password/reset", json={
        "email": reset_email,
        "new_password": new_pwd,
        "verification_token": vtoken
    })
    assert reset_res.status_code == 200
    
    # Login with old password must fail
    old_login = client.post("/api/auth/login", json={"email": reset_email, "password": initial_pwd})
    assert old_login.status_code == 401
    
    # Login with new password must succeed
    new_login = client.post("/api/auth/login", json={"email": reset_email, "password": new_pwd})
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()
