from django.contrib.auth import get_user_model
from django.test import TestCase
from model_bakery import baker

User = get_user_model()


# Create your tests here.
class UserProfileTests(TestCase):

    def test_str_is_id_and_ein(self):
        """String representation of UserProfile is associated user's email instance"""
        user = baker.make(User)
        self.assertEqual(str(user.profile), user.email)
