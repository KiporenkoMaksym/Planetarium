from django.urls import path

from user.views import CreateUserSerializer, ManageUserView

urlpatterns = [
    path("register/", CreateUserSerializer.as_view(), name="create"),
    path("me/", ManageUserView.as_view(), name="manage"),
]

app_name = "user"
