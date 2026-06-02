from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Review, Service

class ServicesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reviewer", password="pass12345")
        self.provider = User.objects.create_user(username="provider", password="pass12345")
        self.service = Service.objects.create(
            provider=self.provider,
            title="Test Service",
            description="Test description",
            price="100.00",
            availability_type="online",
        )

    def test_user_can_update_existing_review(self):
        review = Review.objects.create(service=self.service, reviewer=self.user, rating=2, comment="Old")

        self.client.login(username="reviewer", password="pass12345")
        response = self.client.post(
            reverse("add_review", args=[self.service.id]),
            data={"rating": "5", "comment": "New"},
        )

        self.assertEqual(response.status_code, 302)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "New")
