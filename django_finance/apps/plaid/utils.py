from django.conf import settings

import plaid
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.products import Products


class PlaidConfig:
    """
    Environment configuration and initialization for the Plaid API client.
    """

    def __init__(self):
        self.language = "en"
        self.version = "2020-09-14"
        self.client_name = settings.APP_NAME
        self.client_id = settings.PLAID_CLIENT_ID
        self.secret = settings.PLAID_SECRET
        self.products = self._get_products()
        self.country_codes = self._get_country_codes()
        self.environment = self._get_plaid_environment()
        self.redirect_uri = self._get_redirect_uri()
        self.webhook_uri = self._get_webhook_uri()
        self.client = self._initialize_client()

    def _get_plaid_environment(self) -> plaid.Environment:
        """
        Returns the appropriate Plaid environment based on the Django settings.
        """
        if settings.PLAID_ENV == "production":
            return plaid.Environment.Production
        if settings.PLAID_ENV == "sandbox":
            return plaid.Environment.Sandbox
        return plaid.Environment.Sandbox

    def _initialize_client(self) -> plaid_api.PlaidApi:
        """
        Initializes and returns the Plaid API client with the configured environment.
        """
        configuration = plaid.Configuration(
            host=self.environment,
            api_key={
                "clientId": self.client_id,
                "secret": self.secret,
                "plaidVersion": self.version,
            },
        )
        api_client = plaid.ApiClient(configuration)
        return plaid_api.PlaidApi(api_client)

    def _get_products(self) -> list[Products]:
        """
        Returns a list of Products objects.
        """
        products = settings.PLAID_PRODUCTS.split(",")
        return [Products(product) for product in products]

    def _get_country_codes(self) -> list[CountryCode]:
        """
        Returns a list of CountryCode objects.
        """
        country_codes = settings.PLAID_COUNTRY_CODES.split(",")
        return list(map(lambda x: CountryCode(x), country_codes))

    def _get_redirect_uri(self) -> str:
        """
        Returns the redirect URI.
        """
        return f"{settings.APP_URL}/finance"

    def _get_webhook_uri(self) -> str:
        """
        Returns the webhook URI.
        """
        return f"{settings.APP_URL}/finance/webhook"


plaid_config = PlaidConfig()
