from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from blogs.models import Post, Category, Like
from django.utils import timezone
from unittest.mock import patch, mock_open
import uuid

CustomUser = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Test Category")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password",
            nickname=f"testuser_{uuid.uuid4()}",
        )
        self.other_user = CustomUser.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="password",
            nickname=f"otheruser_{uuid.uuid4()}",
        )
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            writer=self.user,
            category=self.category,
            created_at=timezone.now(),
        )


class PostListViewTest(BaseTestCase):
    def test_post_list_view(self):
        response = self.client.get(reverse("blogs:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_list_view_with_search(self):
        response = self.client.get(reverse("blogs:post_list"), {"q": "test"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_list_view_with_ordering(self):
        response = self.client.get(reverse("blogs:post_list"), {"order_by": "-hit"})
        self.assertEqual(response.status_code, 200)


class PostDetailViewTest(BaseTestCase):
    def test_post_detail_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(
            reverse("blogs:post_detail", kwargs={"pk": self.post.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_detail_view_increase_hit(self):
        self.client.login(username="otheruser", password="password")
        initial_hit = self.post.hit
        response = self.client.get(
            reverse("blogs:post_detail", kwargs={"pk": self.post.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.hit, initial_hit + 1)


class PostCreateViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="testuser", password="password")

    @patch("blogs.forms.open", new_callable=mock_open, read_data="banned_word")
    def test_post_create_view(self, mock_file):
        response = self.client.post(
            reverse("blogs:post_create"),
            {
                "title": "New Post",
                "content": "Content of the new post",
                "category": self.category.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title="New Post").exists())


class PostUpdateViewTest(BaseTestCase):
    def test_post_update_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            reverse("blogs:post_update", kwargs={"pk": self.post.pk}),
            {
                "title": "Updated Post",
                "content": "Updated content of the post",
                "category": self.category.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Post")


class PostDeleteViewTest(BaseTestCase):
    def test_post_delete_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            reverse("blogs:post_delete", kwargs={"pk": self.post.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())


class ToggleLikeViewTest(BaseTestCase):
    def test_toggle_like_view(self):
        self.client.login(username="otheruser", password="password")
        response = self.client.post(
            reverse("blogs:toggle_like", kwargs={"post_id": self.post.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Like.objects.filter(user=self.other_user, post=self.post).exists()
        )

        response = self.client.post(
            reverse("blogs:toggle_like", kwargs={"post_id": self.post.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Like.objects.filter(user=self.other_user, post=self.post).exists()
        )
