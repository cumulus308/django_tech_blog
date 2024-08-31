from django.test import TestCase
from django.contrib.auth import get_user_model
from blogs.models import Category, Post, Comment, Bookmark, Like
from datetime import timedelta
from django.utils import timezone

CustomUser = get_user_model()


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Django")
        self.assertEqual(category.name, "Django")
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)

    def test_category_str(self):
        category = Category.objects.create(name="Django")
        self.assertEqual(str(category), "Django")


class PostModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123"
        )
        self.category = Category.objects.create(name="Django")

    def test_post_creation(self):
        post = Post.objects.create(
            title="Test Post",
            writer=self.user,
            content="This is a test post.",
            category=self.category,
        )
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.writer, self.user)
        self.assertEqual(post.content, "This is a test post.")
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.hit, 0)
        self.assertEqual(post.like_count, 0)
        self.assertIsNotNone(post.created_at)
        self.assertIsNotNone(post.updated_at)

    def test_post_str(self):
        post = Post.objects.create(
            title="Test Post", writer=self.user, content="This is a test post."
        )
        self.assertEqual(str(post), "Test Post")


def test_post_ordering(self):
    post1 = Post.objects.create(
        title="Post 1",
        writer=self.user,
        content="First post.",
        created_at=timezone.now() - timedelta(minutes=1),
    )
    post2 = Post.objects.create(
        title="Post 2",
        writer=self.user,
        content="Second post.",
        created_at=timezone.now(),
    )
    posts = Post.objects.all()
    self.assertEqual(posts.first(), post2)
    self.assertEqual(posts.last(), post1)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123"
        )
        self.post = Post.objects.create(
            title="Test Post", writer=self.user, content="This is a test post."
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            post=self.post, writer=self.user, content="This is a comment."
        )
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.writer, self.user)
        self.assertEqual(comment.content, "This is a comment.")
        self.assertIsNone(comment.parent)
        self.assertTrue(comment.is_parent)
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)

    def test_comment_str(self):
        comment = Comment.objects.create(
            post=self.post, writer=self.user, content="This is a comment."
        )
        self.assertEqual(str(comment), f"{self.user} comment This is a comment.")

    def test_comment_replies(self):
        parent_comment = Comment.objects.create(
            post=self.post, writer=self.user, content="Parent comment."
        )
        child_comment = Comment.objects.create(
            post=self.post,
            writer=self.user,
            content="Child comment.",
            parent=parent_comment,
        )
        self.assertEqual(parent_comment.children.count(), 1)
        self.assertEqual(parent_comment.children.first(), child_comment)
        self.assertFalse(child_comment.is_parent)


class BookmarkModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123"
        )
        self.post = Post.objects.create(
            title="Test Post", writer=self.user, content="This is a test post."
        )

    def test_bookmark_creation(self):
        bookmark = Bookmark.objects.create(user=self.user, post=self.post)
        self.assertEqual(bookmark.user, self.user)
        self.assertEqual(bookmark.post, self.post)
        self.assertIsNotNone(bookmark.created_at)

    def test_bookmark_str(self):
        bookmark = Bookmark.objects.create(user=self.user, post=self.post)
        self.assertEqual(
            str(bookmark), f"{self.user.username} bookmarked {self.post.title}"
        )

    def test_bookmark_unique_together(self):
        Bookmark.objects.create(user=self.user, post=self.post)
        with self.assertRaises(Exception):
            Bookmark.objects.create(user=self.user, post=self.post)


class LikeModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123"
        )
        self.post = Post.objects.create(
            title="Test Post", writer=self.user, content="This is a test post."
        )

    def test_like_creation(self):
        like = Like.objects.create(user=self.user, post=self.post)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.post, self.post)
        self.assertIsNotNone(like.created_at)

    def test_like_str(self):
        like = Like.objects.create(user=self.user, post=self.post)
        self.assertEqual(str(like), f"{self.user.username} likes {self.post.title}")

    def test_like_unique_together(self):
        Like.objects.create(user=self.user, post=self.post)
        with self.assertRaises(Exception):
            Like.objects.create(user=self.user, post=self.post)
