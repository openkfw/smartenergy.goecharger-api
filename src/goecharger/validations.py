"""Go-eCharger validations module"""


def validate_empty_string(val: str, entity_name: str) -> None:
    """
    Validate (assert) if the string is empty or not.
    """

    assert isinstance(val, str) and val != "", "%s must be specified" % entity_name
