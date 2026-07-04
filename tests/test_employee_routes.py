from app.presentation.api.employee_routes import _blank_to_none


def test_blank_query_value_is_normalized_to_none() -> None:
    assert _blank_to_none("") is None
    assert _blank_to_none(None) is None
    assert _blank_to_none("male") == "male"
