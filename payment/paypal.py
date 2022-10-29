import sys

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from django.conf import settings

import razorpay


class PayPalClient:
    def __init__(self):
        self.environment = SandboxEnvironment(
            client_id=str(settings.CLIENT_ID), client_secret=str(settings.CLIENT_SECRET)
        )
        self.client = PayPalHttpClient(self.environment)
