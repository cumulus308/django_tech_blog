from django.test import TestCase
from accounts.forms import (
    CustomUserCreationForm,
    CustomUserUpdateForm,
    UserProfileUpdateForm,
)
from accounts.models import CustomUser, UserProfile


class CustomUserCreationFormTest(TestCase):
    def test_form_valid_data(self):
        form_data = {
            "username": "testuser",
            "nickname": "testnickname",
            "last_name": "Test",
            "email": "testuser@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("strongpassword123"))

    def test_form_invalid_data(self):
        # Passwords do not match
        form_data = {
            "username": "testuser",
            "nickname": "testnickname",
            "last_name": "Test",
            "email": "testuser@example.com",
            "password1": "strongpassword123",
            "password2": "weakpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_email_required(self):
        form_data = {
            "username": "testuser",
            "nickname": "testnickname",
            "last_name": "Test",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class CustomUserUpdateFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            nickname="testnickname",
        )

    def test_form_valid_data(self):
        form_data = {
            "email": "newemail@example.com",
            "nickname": "newnickname",
        }
        form = CustomUserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.email, "newemail@example.com")
        self.assertEqual(updated_user.nickname, "newnickname")

    def test_form_invalid_email(self):
        form_data = {
            "email": "",
            "nickname": "newnickname",
        }
        form = CustomUserUpdateForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class UserProfileUpdateFormTest(TestCase):
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

    def test_form_valid_data(self):
        form_data = {
            "hobbies": "Writing",
            "specialties": "Design",
            "interests": "Art",
            "bio": "This is an updated bio",
        }
        form = UserProfileUpdateForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
        updated_profile = form.save()
        self.assertEqual(updated_profile.hobbies, "Writing")
        self.assertEqual(updated_profile.specialties, "Design")
        self.assertEqual(updated_profile.interests, "Art")
        self.assertEqual(updated_profile.bio, "This is an updated bio")

    def test_form_empty_bio(self):
        form_data = {
            "hobbies": "Writing",
            "specialties": "Design",
            "interests": "Art",
            "bio": "",
        }
        form = UserProfileUpdateForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
        updated_profile = form.save()
        self.assertEqual(updated_profile.bio, "")
