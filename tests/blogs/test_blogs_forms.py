from django.test import TestCase
from django.contrib.auth import get_user_model
from blogs.models import Category, Post, Comment, Bookmark, Like
from django.utils import timezone
import datetime

CustomUser = get_user_model()


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Django")
        self.assertEqual(str(category), "Django")


class PostModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="password"
        )
        self.category = Category.objects.create(name="Django")

    def test_post_creation(self):
        post = Post.objects.create(
            title="Test Post",
            writer=self.user,
            content="This is a test post.",
            category=self.category,
        )
        self.assertEqual(str(post), "Test Post")
        self.assertEqual(post.writer, self.user)
        self.assertEqual(post.category, self.category)

    def test_post_ordering(self):
        post1 = Post.objects.create(
            title="Post 1",
            writer=self.user,
            content="This is post 1.",
            category=self.category,
            created_at=timezone.now() - datetime.timedelta(seconds=10),
        )
        post2 = Post.objects.create(
            title="Post 2",
            writer=self.user,
            content="This is post 2.",
            category=self.category,
            created_at=timezone.now(),
        )

        posts = Post.objects.all()

        self.assertEqual(posts.first(), post2)
        self.assertEqual(posts.last(), post1)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="password"
        )
        self.category = Category.objects.create(name="Django")
        self.post = Post.objects.create(
            title="Test Post",
            writer=self.user,
            content="This is a test post.",
            category=self.category,
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            post=self.post, writer=self.user, content="This is a comment."
        )
        self.assertEqual(str(comment), "testuser comment This is a comment.")
        self.assertEqual(comment.post, self.post)

    def test_comment_hierarchy(self):
        parent_comment = Comment.objects.create(
            post=self.post, writer=self.user, content="This is a parent comment."
        )
        child_comment = Comment.objects.create(
            post=self.post,
            writer=self.user,
            content="This is a child comment.",
            parent=parent_comment,
        )
        self.assertTrue(child_comment.is_parent is False)
        self.assertEqual(parent_comment.children.count(), 1)
        self.assertEqual(parent_comment.children.first(), child_comment)


class BookmarkModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="password"
        )
        self.category = Category.objects.create(name="Django")
        self.post = Post.objects.create(
            title="Test Post",
            writer=self.user,
            content="This is a test post.",
            category=self.category,
        )

    def test_bookmark_creation(self):
        bookmark = Bookmark.objects.create(user=self.user, post=self.post)
        self.assertEqual(str(bookmark), "testuser bookmarked Test Post")

    def test_unique_bookmark(self):
        Bookmark.objects.create(user=self.user, post=self.post)
        with self.assertRaises(Exception):
            Bookmark.objects.create(user=self.user, post=self.post)


class LikeModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="password"
        )
        self.category = Category.objects.create(name="Django")
        self.post = Post.objects.create(
            title="Test Post",
            writer=self.user,
            content="This is a test post.",
            category=self.category,
        )

    def test_like_creation(self):
        like = Like.objects.create(user=self.user, post=self.post)
        self.assertEqual(str(like), "testuser likes Test Post")

    def test_unique_like(self):
        Like.objects.create(user=self.user, post=self.post)
        with self.assertRaises(Exception):
            Like.objects.create(user=self.user, post=self.post)
