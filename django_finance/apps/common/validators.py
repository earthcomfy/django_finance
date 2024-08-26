from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """
    Validate that passwords meet complexity requirements:
        - min 8 characters
        - include numbers
        - uppercase, and
        - special characters.
    """

    MIN_PASSWORD_LENGTH = 8

    def validate(self, password, user=None):
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise ValidationError(
                _("Password must be at least 8 characters."),
                code="password_too_short",
            )
        if password.isdigit() or password.isalpha():
            raise ValidationError(
                _("Password must contain at least one number and one letter."),
                code="password_no_number_or_letter",
            )
        if password.islower() or password.isupper():
            raise ValidationError(
                _("Password must contain both uppercase and lowercase characters."),
                code="password_no_mixed_case",
            )
        if password.isalnum():
            raise ValidationError(
                _("Password must contain at least one special character."),
                code="password_no_special_character",
            )

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long and contain at least one number,"
            " one uppercase letter, and one special character."
        )
