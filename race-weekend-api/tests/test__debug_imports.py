def test_debug_security_import():
    import app.core.security as sec
    assert "sha256" in sec._bcrypt_safe_input.__code__.co_names
