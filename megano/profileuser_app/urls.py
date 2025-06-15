from django.urls import path


from .views import (
    SignInApiView,
    ProfileDetailUpdateApiView,
    AvatarUserCreateOrUpdateApiView,
    ProfileUserLogoutView,
    UserSignUpApiView,
    ChangePasswordUserApiView,
)


app_name = "profileuser_app"


urlpatterns = [
    path("api/sign-in", SignInApiView.as_view(), name="sign-in"),
    path("api/sign-up", UserSignUpApiView.as_view(), name="sign-up"),
    path("api/sign-out", ProfileUserLogoutView.as_view(), name="sign-out"),
    path("api/profile", ProfileDetailUpdateApiView.as_view(), name="profile"),
    path(
        "api/profile/password", ChangePasswordUserApiView.as_view(), name="change-psw"
    ),
    path(
        "api/profile/avatar", AvatarUserCreateOrUpdateApiView.as_view(), name="avatar"
    ),
]
