import random

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# django.setup()


from accounts.models import CustomUser
from blogs.models import Category, Post
from model_bakery import seq, baker
import itertools

user = baker.make(
    CustomUser,
    _quantity=20,
    password="qwer1234!!",
    last_name=seq("ormstrudy"),
)
print("user 생성 완료")
categories = baker.make(
    Category,
    _quantity=12,
    name=itertools.cycle(
        [
            "Python",
            "Django",
            "Machine Learning",
            "Artificial Intelligence",
            "Data Science",
            "Web Development",
            "JavaScript",
            "React",
            "DevOps",
            "Cloud Computing",
            "Cybersecurity",
            "APIs",
        ]
    ),
)
print("category 생성 완료")
post = baker.make(
    Post,
    _quantity=500,
    title=seq("post_num_"),
    thumbnail="blog/files/2024/08/29/돌체_콜드브루_9R7vAmL.jpg",
    category=lambda: random.choice(categories),
    writer=lambda: random.choice(user),
)
