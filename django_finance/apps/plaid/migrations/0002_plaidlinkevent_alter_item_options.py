# Generated by Django 5.1 on 2024-09-06 14:11

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plaid", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlaidLinkEvent",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Used for soft deleting records.",
                    ),
                ),
                (
                    "user_id",
                    models.CharField(help_text="The ID of the user.", max_length=250),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[("SUCCESS", "Success"), ("EXIT", "Exit")],
                        help_text="Displayed as `Success` or `Exit` based on response from onSuccess or onExit callbacks.",
                        max_length=20,
                    ),
                ),
                (
                    "link_session_id",
                    models.TextField(
                        help_text="A unique identifier associated with a user's actions and events through the Link flow."
                    ),
                ),
                (
                    "request_id",
                    models.TextField(
                        blank=True,
                        help_text="A unique identifier for the request, which can be used for troubleshooting.",
                    ),
                ),
                (
                    "error_type",
                    models.TextField(
                        blank=True, help_text="A broad categorization of the error."
                    ),
                ),
                (
                    "error_code",
                    models.TextField(
                        blank=True,
                        help_text="The particular error code. Each error_type has a specific set of error_codes.",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.AlterModelOptions(
            name="item",
            options={"ordering": ("-created_at",)},
        ),
    ]
