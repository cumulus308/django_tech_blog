from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

CustomUser = get_user_model()


class IndexViewTest(TestCase):
    def test_index_view(self):
        response = self.client.get(
            reverse("index")
        )  # 'index'는 urls.py에서 설정한 이름이어야 합니다.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "layout/layouts.html")


class SignUpViewTest(TestCase):
    def test_signup_view_get(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_signup_view_post(self):
        form_data = {
            "username": "testuser",
            "nickname": "testnickname",
            "last_name": "Test",
            "email": "testuser@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        response = self.client.post(reverse("accounts:signup"), data=form_data)
        self.assertEqual(response.status_code, 302)  # 성공 시 리디렉션
        self.assertTrue(CustomUser.objects.filter(username="testuser").exists())


class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123"
        )

    def test_login_view_get(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_view_post(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "password123"},
        )
        self.assertEqual(response.status_code, 302)  # 로그인 성공 후 리디렉션


CustomUser = get_user_model()


class CustomUserUpdateViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            nickname="testnickname",
        )
        # Use get_or_create to avoid creating duplicate profiles
        self.profile, created = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                "hobbies": "Reading",
                "specialties": "Programming",
                "interests": "Music",
                "bio": "This is a bio",
            },
        )
        self.client.login(username="testuser", password="password123")

    def test_user_update_view_get(self):
        response = self.client.get(
            reverse("accounts:profile_edit", kwargs={"user_id": self.user.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/personal_info.html")

    def test_user_update_view_post(self):
        form_data = {
            "email": "newemail@example.com",
            "nickname": "newnickname",
            "hobbies": "Writing",
            "specialties": "Design",
            "interests": "Art",
            "bio": "Updated bio",
        }
        response = self.client.post(
            reverse("accounts:profile_edit", kwargs={"user_id": self.user.pk}),
            data=form_data,
        )
        self.assertEqual(response.status_code, 302)  # 성공 시 리디렉션
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")
        self.assertEqual(self.user.nickname, "newnickname")
        self.assertEqual(self.profile.hobbies, "Writing")
        self.assertEqual(self.profile.specialties, "Design")
        self.assertEqual(self.profile.interests, "Art")
        self.assertEqual(self.profile.bio, "Updated bio")


class CustomPasswordChangeViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="oldpassword"
        )
        self.client.login(username="testuser", password="oldpassword")

    def test_password_change_view_get(self):
        response = self.client.get(reverse("accounts:password_change"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/personal_info.html")

    def test_password_change_view_post(self):
        form_data = {
            "old_password": "oldpassword",
            "new_password1": "newstrongpassword123",
            "new_password2": "newstrongpassword123",
        }
        response = self.client.post(reverse("accounts:password_change"), data=form_data)
        self.assertEqual(response.status_code, 302)  # 성공 시 리디렉션
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newstrongpassword123"))
