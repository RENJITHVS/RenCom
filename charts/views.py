from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, F, Sum, Avg
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from orders.models import OrderItem
from .utils import (
    months,
    colorPrimary,
    colorSuccess,
    colorDanger,
    generate_color_palette,
    get_year_dict,
)


def test_admin(user):
    return user.role == "ADMIN"


@user_passes_test(test_admin, login_url="/admin/")
def get_filter_options(request):
    grouped_purchases = (
        OrderItem.objects.annotate(year=ExtractYear("order__created"))
        .values("year")
        .order_by("-year")
        .distinct()
    )
    options = [purchase["year"] for purchase in grouped_purchases]

    return JsonResponse(
        {
            "options": options,
        }
    )


@user_passes_test(test_admin, login_url="/admin/")
def get_sales_chart(request, year):
    purchases = OrderItem.objects.filter(order__created__year=year)
    grouped_purchases = (
        purchases.annotate(month=ExtractMonth("order__created"))
        .values("month")
        .annotate(average=Sum("price"))
        .values("month", "average")
        .order_by("month")
    )

    sales_dict = get_year_dict()

    for group in grouped_purchases:
        sales_dict[months[group["month"] - 1]] = round(group["average"], 2)

    return JsonResponse(
        {
            "title": f"Sales in {year}",
            "data": {
                "labels": list(sales_dict.keys()),
                "datasets": [
                    {
                        "label": "Amount (Rs)",
                        "backgroundColor": colorPrimary,
                        "borderColor": colorPrimary,
                        "data": list(sales_dict.values()),
                    }
                ],
            },
        }
    )


@user_passes_test(test_admin, login_url="/admin/")
def spend_per_customer_chart(request, year):
    purchases = OrderItem.objects.filter(order__created__year=year)
    grouped_purchases = (
        purchases.annotate(month=ExtractMonth("order__created"))
        .values("month")
        .annotate(average=Avg("price"))
        .values("month", "average")
        .order_by("month")
    )

    spend_per_customer_dict = get_year_dict()

    for group in grouped_purchases:
        spend_per_customer_dict[months[group["month"] - 1]] = round(group["average"], 2)

    return JsonResponse(
        {
            "title": f"Spend per customer in {year}",
            "data": {
                "labels": list(spend_per_customer_dict.keys()),
                "datasets": [
                    {
                        "label": "Amount (Rs)",
                        "backgroundColor": colorPrimary,
                        "borderColor": colorPrimary,
                        "data": list(spend_per_customer_dict.values()),
                    }
                ],
            },
        }
    )


@user_passes_test(test_admin, login_url="/admin/")
def payment_success_chart(request, year):
    purchases = OrderItem.objects.filter(order__created__year=year)

    return JsonResponse(
        {
            "title": f"Payment success rate in {year}",
            "data": {
                "labels": ["Payed", "Pending"],
                "datasets": [
                    {
                        "label": "Amount (Rs)",
                        "backgroundColor": [colorSuccess, colorDanger],
                        "borderColor": [colorSuccess, colorDanger],
                        "data": [
                            purchases.filter(order__billing_status=True).count(),
                            purchases.filter(order__billing_status=False).count(),
                        ],
                    }
                ],
            },
        }
    )
