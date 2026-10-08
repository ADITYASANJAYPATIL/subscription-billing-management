from django.urls import path

from .views import SubscriptionListCreateView


urlpatterns = [
    path(
        "",
        SubscriptionListCreateView.as_view(),
        name="subscription-list-create",
    ),
]