from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AvatarUser, ProfileUser
from .serializers import (
    AuthUserSerializer,
    ChangePasswordUserSerializer,
    ProfileUserSerializer,
    UserSerializer,
)
from .utils import (
    check_email_user_exists,
    create_new_user,
    create_profile_new_user,
    get_classic_dict,
    get_data_new_user,
    get_update_user_data,
    validate_all_new_user_data,
    validate_file,
    validate_fullname_user,
    validate_phone_user,
)


class ProfileUserLogoutView(LogoutView):
    """
    View - класс для разлогирования пользователя из системы.
    """

    next_page = reverse_lazy("profileuser_app:sign-in")


class SignInApiView(APIView):
    """
    Класс - API-view. Предоставлет возможность пользователю войти в систему.
    """

    def post(self, request: Request) -> Response:
        """
        Метод post, позволяющий отправить данные и аутентифицировать пользователя в системе.
        :param request: запрос
        :return: статус-код 200, если пользователь есть в системе и 400, если нет.
        """
        clear_username_and_psw_dict = get_classic_dict(dict_string=request.data)
        auth_serializer = AuthUserSerializer(data=clear_username_and_psw_dict)
        auth_serializer.is_valid(raise_exception=True)
        user = auth_serializer.validated_data
        login(request, user)
        return Response(status=status.HTTP_200_OK)


class ProfileDetailUpdateApiView(APIView):
    """
    Класс - API-view. Предоставлет возможность получить полную информацию о пользователе и обновить ее.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """
        Метод get, позволяющий получить информацию о пользователе.
        :param request: запрос
        :return: словарь с данными о пользователе.
        """

        return Response(
            ProfileUserSerializer(
                ProfileUser.objects.get(user_id=request.user.pk), many=False
            ).data
        )

    def post(self, request: Request) -> Response:
        """
        Метод post, позволяющий обновить информацию о пользователе.
        Если данные переданы не все, то будут взяты за основу уже имеющаяся информация.
        :param request: запрос
        :return: статус-код 200, если введенные данные корректны, 400, если нет.
        """

        profile_user = ProfileUser.objects.get(user=request.user.pk)
        fullname_user_update, phone_user_update, email_user = get_update_user_data(
            data=request.data, user=profile_user
        )

        validate_fullname_user(fullname=fullname_user_update)
        profile_user.fullName = fullname_user_update

        validate_phone_user(old_phone=profile_user.phone, new_phone=phone_user_update)
        profile_user.phone = phone_user_update

        check_email_user_exists(old_email=profile_user.email, new_email=email_user)
        profile_user.email = email_user

        profile_user.save()
        return Response(status=status.HTTP_200_OK)


class AvatarUserCreateOrUpdateApiView(APIView):
    """
    Класс - API-view. Предоставлет возможность установить или обновить аватар пользователя.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """
        :param request: запрос
        :return: статус-код 200, если файл удовлетворяет требованиям, и 400, если нет.
        """

        new_avatar_user = request.data.get("avatar")

        validate_file(namefile=new_avatar_user.name, size=new_avatar_user.size)

        current_avatar_user, _ = AvatarUser.objects.get_or_create(
            profile_id=request.user.pk
        )

        current_avatar_user.avatar = new_avatar_user
        current_avatar_user.save()
        return Response(status=status.HTTP_200_OK)


class UserSignUpApiView(APIView):
    """
    Класс - API-view. Предоставлет возможность зарегистрироваться в системе и добавить расширенный профиль.
    """

    def post(self, request: Request) -> Response:
        """
        Метод - post. Проверяет введенные данные. Создает пользователя и расширяет информацию о нем.
        :param request: запрос
        :return: статус 201, если пользователь создан и 400, если данные некорректны.
        """
        clear_name_login_psw_dict = get_classic_dict(request.data)
        validate_all_new_user_data(data=clear_name_login_psw_dict)

        user_serializer = UserSerializer(data=clear_name_login_psw_dict)

        if user_serializer.is_valid():
            name, surname, patronymic, login_user, psw_user = get_data_new_user(
                user_serializer.validated_data
            )
            user = create_new_user(
                name=name, surname=surname, login_user=login_user, psw_user=psw_user
            )
            create_profile_new_user(
                new_user=user, name=name, surname=surname, patronymic=patronymic
            )
            current_user = authenticate(username=login_user, password=psw_user)
            if current_user:
                login(request, current_user)
                return Response(status=status.HTTP_201_CREATED)
            return Response(status.HTTP_400_BAD_REQUEST)
        return Response(status.HTTP_400_BAD_REQUEST)


class ChangePasswordUserApiView(APIView):
    """
    Класс - API-view. Предоставлет возможность сменить пользователю пароль.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """
        Метод - post. Изменяет пароль пользователя.
        :param request: запрос
        :return: В случае успешной валидации данных меняет пароль пользователя в БД и возвращет статус 200.
        """
        password_serializer = ChangePasswordUserSerializer(
            data=request.data, context={"request": request}
        )
        password_serializer.is_valid(raise_exception=True)
        password_serializer.save()
        return Response(status.HTTP_200_OK)
