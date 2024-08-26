import pytest
from django.core.exceptions import ValidationError

from django_finance.apps.common.validators import CustomPasswordValidator


class TestCustomPasswordValidator:
    @pytest.mark.parametrize(
        "password",
        [
            "short",  # Less than 8 characters
            "alllowercase",  # Only lowercase letters
            "ALLUPPERCASE",  # Only uppercase letters
            "123456789",  # Only digits
            "NoSpecial123",  # No special character
        ],
    )
    def test_invalid_passwords(self, password):
        validator = CustomPasswordValidator()
        with pytest.raises(ValidationError):
            validator.validate(password)

    @pytest.mark.parametrize("password", ["ValidPass123!"])
    def test_valid_passwords(self, password):
        validator = CustomPasswordValidator()
        validator.validate(password)

    @pytest.mark.parametrize(
        "password",
        [
            "lowercase1!",  # Lowercase but no uppercase
            "UPPERCASE1!",  # Uppercase but no lowercase
        ],
    )
    def test_no_mixed_case_passwords(self, password):
        validator = CustomPasswordValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(password)

        error_message = exc_info.value.messages[0]

        assert exc_info.value.code == "password_no_mixed_case"
        assert error_message == "Password must contain both uppercase and lowercase characters."

    def test_get_help_text(self):
        validator = CustomPasswordValidator()
        expected_help_text = (
            "Your password must be at least 8 characters long and contain at least one number,"
            " one uppercase letter, and one special character."
        )
        assert validator.get_help_text() == expected_help_text
