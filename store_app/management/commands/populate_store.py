import random
from faker import Faker
from django.core.management.base import BaseCommand
from store_app.models import User, Category, Product

class Command(BaseCommand):
    help = 'Populates the database with fake data'

    def handle(self, *args, **kwargs):
        faker = Faker()

        # Create Categories
        categories = []
        for _ in range(5):
            category = Category.objects.create(
                name=faker.word(),
                description=faker.text(max_nb_chars=100)
            )
            categories.append(category)

        self.stdout.write(self.style.SUCCESS(f'{len(categories)} categories created.'))

        # Create Products
        products = []
        for _ in range(100):  # Generate 50 products
            category = random.choice(categories)
            manufacture_date = faker.date_this_decade()
            expiry_date = faker.date_between(start_date=manufacture_date, end_date="+1y")

            product = Product.objects.create(
                name=faker.catch_phrase(),
                sku=faker.unique.ean(length=13),
                description=faker.text(max_nb_chars=200),
                category=category,
                quantity=random.randint(0, 100),
                manufacture_date=manufacture_date,
                expiry_date=expiry_date,
                price=faker.random_number(digits=5, fix_len=True) / 100,
                is_in_stock=random.choice([True, False]),
            )
            products.append(product)

        self.stdout.write(self.style.SUCCESS(f'{len(products)} products created.'))

        # Create Users
        roles = ['admin', 'manager', 'cashier']
        users = []
        for _ in range(25):  # Generate 20 users
            user = User.objects.create_user(
                username=faker.unique.user_name(),
                email=faker.unique.email(),
                phone_number=faker.phone_number(),
                password="password123",  # Default password
                role=random.choice(roles),
            )
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f'{len(users)} users created.'))
