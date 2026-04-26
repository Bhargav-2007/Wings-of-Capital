def test_mfa_login_flow(test_client, db_session):
    from auth_service.main import app as auth_app
    from auth_service.models.user import User
    from auth_service.models.mfa import MfaSecret
    from auth_service.utils.mfa import (
        generate_mfa_secret,
        encrypt_secret,
        generate_backup_codes,
        generate_backup_salt,
        hash_backup_code,
    )
    from shared.security import hash_password
    import pyotp

    client = test_client(auth_app)

    email = "mfauser@example.com"
    password = "StrongPassw0rd!"

    # Create verified user with MFA enabled and an associated MfaSecret
    user = User(email=email, password_hash=hash_password(password), is_active=True, is_verified=True, mfa_enabled=True)
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)

    secret = generate_mfa_secret()
    secret_encrypted = encrypt_secret(secret)
    backup_codes = generate_backup_codes(2, 8)
    salt = generate_backup_salt()
    hashes = [hash_backup_code(c, salt) for c in backup_codes]

    mfa = MfaSecret(user_id=user.id, secret_encrypted=secret_encrypted, verified=True, backup_codes_salt=salt, backup_codes_hashes=hashes)
    db_session.add(mfa)
    db_session.commit()

    # Generate a current TOTP code and perform login with MFA
    code = pyotp.TOTP(secret).now()
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password, "mfa_code": code})
    assert res.status_code == 200
