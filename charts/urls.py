from django.urls import path

from . import views

app_name = "charts"

urlpatterns = [
    path("filter-options/", views.get_filter_options, name="chart-filter-options"),
    path("sales/<int:year>/", views.get_sales_chart, name="chart-sales"),
    path(
        "sales/spend-per-customer/<int:year>/",
        views.spend_per_customer_chart,
        name="chart-spend-per-customer",
    ),
    path(
        "sales/payment-success/<int:year>/",
        views.payment_success_chart,
        name="chart-payment-success",
    ),
]
