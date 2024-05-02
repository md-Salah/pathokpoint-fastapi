import pyotp

def generate_otp() -> str:
    return pyotp.TOTP(pyotp.random_base32()).now()


