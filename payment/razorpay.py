import razorpay
from django.conf import settings


def initate_refund_razorpay(payment_id, amount):
    razorpay_client = razorpay.Client(
        auth=(str(settings.RAZOR_PAY_KEY_ID), str(settings.KEY_SECRET))
    )

    res = razorpay_client.payment.refund(
        payment_id,
        {
            "amount": int(amount) * 100,
            "speed": "normal",
            "notes": {"notes_key_1": "Sorry for the delay", "notes_key_2": "Done"},
            "receipt": payment_id + "0001",
        },
    )
    print(res)
    return res
