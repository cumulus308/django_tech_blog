from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import UserProfile, Follow

CustomUser = get_user_model()


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            nickname="testnickname",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.nickname, "testnickname")
        self.assertTrue(self.user.check_password("password123"))

    def test_user_str_method(self):
        self.assertEqual(str(self.user), "testuser")


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            nickname="testnickname",
        )
        self.profile, created = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                "hobbies": "Reading",
                "specialties": "Programming",
                "interests": "Music",
                "bio": "This is a bio",
            },
        )

        if not created:
            self.profile.hobbies = "Reading"
            self.profile.specialties = "Programming"
            self.profile.interests = "Music"
            self.profile.bio = "This is a bio"
            self.profile.save()

    def test_userprofile_creation(self):
        self.assertEqual(self.profile.hobbies, "Reading")
        self.assertEqual(self.profile.specialties, "Programming")
        self.assertEqual(self.profile.interests, "Music")
        self.assertEqual(self.profile.bio, "This is a bio")

    def test_userprofile_str_method(self):
        self.assertEqual(str(self.profile), "testuser의 프로필")


class FollowModelTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password123",
            nickname="nickname1",
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password123",
            nickname="nickname2",
        )
        self.follow = Follow.objects.create(follower=self.user1, following=self.user2)

    def test_follow_creation(self):
        self.assertEqual(self.follow.follower.username, "user1")
        self.assertEqual(self.follow.following.username, "user2")
        self.assertIsNotNone(self.follow.created_at)

    def test_user_following_relationship(self):
        self.assertEqual(self.user1.follower.count(), 1)
        self.assertEqual(self.user2.following.count(), 1)

        self.assertEqual(self.user1.follower.first(), self.follow)
        self.assertEqual(self.user2.following.first(), self.follow)
