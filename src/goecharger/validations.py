"""Go-eCharger validations module"""


def validate_empty_string(val: str, entity_name: str) -> None:
    """
    Validate (assert) if the string is empty or not.
    """

    assert isinstance(val, str) and val != "", f"{entity_name} must be specified"
