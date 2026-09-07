from django.urls import path

from user.views import CreateUserSerializer, CreateTokenView, ManageUserView

urlpatterns = [
    path("register/", CreateUserSerializer.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="manage"),
]

app_name = "user"
