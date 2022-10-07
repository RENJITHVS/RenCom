import sys

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from django.conf import settings


class PayPalClient:
    def __init__(self):
        self.environment = SandboxEnvironment(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET)
        self.client = PayPalHttpClient(self.environment)
