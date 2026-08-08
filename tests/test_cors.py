from backend.app import is_origin_allowed


def test_vercel_origin_is_allowed() -> None:
    assert is_origin_allowed("https://gym-for-us.vercel.app") is True
