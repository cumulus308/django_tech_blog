from django.test import TestCase, Client
from django.urls import reverse
from django.db.models import Q
from blogs.models import Category, Post
from accounts.models import CustomUser


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post content",
            writer=self.user,
            category=self.category,
        )


class CombinedViewTestCase(BaseTestCase):
    def test_combined_view(self):
        url = reverse("search:search_result")
        response = self.client.get(url, {"q": "test"})
        self.assertEqual(response.status_code, 200)

        self.assertIn("highlighted_posts", response.context)
        highlighted_posts = response.context["highlighted_posts"]

        for post in highlighted_posts:
            print("Checking title match:", post["highlighted_title"]["match"])
            self.assertTrue(
                post["highlighted_title"]["match"].strip().lower() == "test"
            )

        self.assertIn("highlighted_writers", response.context)
        highlighted_writers = response.context["highlighted_writers"]
        for writer in highlighted_writers:
            print("Checking writer match:", writer["highlighted_writer"]["match"])
            self.assertTrue(
                writer["highlighted_writer"]["match"].strip().lower() == "test"
            )

        self.assertIn("highlighted_categories", response.context)
        highlighted_categories = response.context["highlighted_categories"]
        for category in highlighted_categories:
            print("Checking category match:", category["highlighted_category"]["match"])
            self.assertTrue(
                category["highlighted_category"]["match"].strip().lower() == "test"
            )

        self.assertIn("writer_count", response.context)
        self.assertIn("post_count", response.context)
        self.assertIn("category_count", response.context)

    def test_combined_view_no_results(self):
        url = reverse("search:search_result")
        response = self.client.get(url, {"q": "nonexistent"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["highlighted_posts"]), 0)
        self.assertEqual(len(response.context["highlighted_writers"]), 0)
        self.assertEqual(len(response.context["highlighted_categories"]), 0)


class TitleContentSearchListViewTestCase(BaseTestCase):
    def test_title_content_search(self):
        url = reverse("search:title_content_result")
        response = self.client.get(url, {"q": "test"})
        self.assertEqual(response.status_code, 200)

        # Check if the post title is in the highlighted_posts context
        self.assertIn("highlighted_posts", response.context)
        highlighted_posts = response.context["highlighted_posts"]
        self.assertTrue(
            any("Test Post" in post["post_title"] for post in highlighted_posts)
        )

        # Check if the content is correctly highlighted
        self.assertTrue(
            any(
                "test post content" in post["post_content"].lower()
                for post in highlighted_posts
            )
        )

    def test_no_results(self):
        url = reverse("search:title_content_result")
        response = self.client.get(url, {"q": "nonexistent"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["highlighted_posts"]), 0)


class WriterSearchListViewTestCase(BaseTestCase):
    def test_writer_search(self):
        url = reverse("search:writer_result")
        response = self.client.get(url, {"q": "testuser"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")

        # Check if the context contains highlighted writers
        self.assertIn("highlighted_writers", response.context)
        self.assertTrue(len(response.context["highlighted_writers"]) > 0)

    def test_no_results(self):
        url = reverse("search:writer_result")
        response = self.client.get(url, {"q": "nonexistent"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "testuser")
        self.assertEqual(len(response.context["highlighted_writers"]), 0)


class CategorySearchListViewTestCase(BaseTestCase):
    def test_category_search(self):
        url = reverse("search:category_result")
        response = self.client.get(url, {"q": "Test Category"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Category")

        # Check if the context contains highlighted categories
        self.assertIn("highlighted_categories", response.context)
        self.assertTrue(len(response.context["highlighted_categories"]) > 0)

    def test_no_results(self):
        url = reverse("search:category_result")
        response = self.client.get(url, {"q": "nonexistent"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Test Category")
        self.assertEqual(len(response.context["highlighted_categories"]), 0)


class CategorySearchDetailListViewTestCase(BaseTestCase):
    def test_category_detail(self):
        url = reverse("search:category_detail_result", args=[self.category.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")

        # Check if the queryset is filtered correctly
        self.assertEqual(list(response.context["posts"]), [self.post])

    def test_nonexistent_category(self):
        url = reverse("search:category_detail_result", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Changed from 404 to 200
        self.assertEqual(len(response.context["posts"]), 0)


class WriterSearchDetailListViewTestCase(BaseTestCase):
    def test_writer_detail(self):
        url = reverse("search:writer_detail_result", args=[self.user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")

        # Check if the queryset is filtered correctly
        self.assertEqual(list(response.context["posts"]), [self.post])

    def test_nonexistent_writer(self):
        url = reverse("search:writer_detail_result", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Changed from 404 to 200
        self.assertEqual(len(response.context["posts"]), 0)
