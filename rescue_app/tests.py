from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime, timezone

from rescue_app.auth_helper import (
    create_user,
    authenticate_user,
    update_user_password
)
from rescue_app.food_service import (
    add_food_item,
    claim_food_item,
    mark_food_collected
)


class PublicViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('rescue_app.views.check_db_connection')
    def test_home_page_loads(self, mock_check):
        mock_check.return_value = (False, "DB not connected in test")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Food Rescue")

    @patch('rescue_app.views.check_db_connection')
    def test_login_page_loads(self, mock_check):
        mock_check.return_value = (True, None)
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign In")

    @patch('rescue_app.views.check_db_connection')
    def test_signup_page_loads(self, mock_check):
        mock_check.return_value = (True, None)
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Your Account")

    @patch('rescue_app.food_service.get_food_collection')
    def test_view_food_page_loads(self, mock_food_coll):
        mock_coll = MagicMock()
        mock_coll.find.return_value.sort.return_value = []
        mock_food_coll.return_value = mock_coll

        response = self.client.get(reverse('view_food'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Available Surplus Food")


class ProtectedViewsRedirectTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_add_food_requires_login(self):
        response = self.client.get(reverse('add_food'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_account_settings_requires_login(self):
        response = self.client.get(reverse('account_settings'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))


class AuthAndFoodUnitTestCase(TestCase):
    @patch('rescue_app.auth_helper.get_users_collection')
    def test_create_user_validation(self, mock_users_coll):
        mock_coll = MagicMock()
        mock_coll.find_one.return_value = None
        mock_coll.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_users_coll.return_value = mock_coll

        # Short password
        user, err = create_user("testuser", "test@test.com", "123", "Test User", "1234567890")
        self.assertIsNone(user)
        self.assertIn("at least 6 characters", err)

        # Invalid email
        user, err = create_user("testuser", "bademail", "password123", "Test User", "1234567890")
        self.assertIsNone(user)
        self.assertIn("valid email", err)

        # Valid registration
        user, err = create_user("testuser", "test@test.com", "password123", "Test User", "1234567890")
        self.assertIsNone(err)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')

    @patch('rescue_app.food_service.get_food_collection')
    def test_add_food_validation(self, mock_food_coll):
        mock_coll = MagicMock()
        mock_coll.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_food_coll.return_value = mock_coll

        user = {'id': '64b0f92b7c1234567890abcd', 'username': 'provider1', 'full_name': 'Provider One'}

        # Missing title
        item, err = add_food_item(user, "", "desc", "Cooked Meals", "Vegetarian", "10 plates", "Addr", "City", "Slot", "Exp")
        self.assertIsNone(item)
        self.assertIn("title is required", err)

        # Valid listing
        item, err = add_food_item(user, "Biryani", "desc", "Cooked Meals", "Vegetarian", "10 plates", "Addr", "City", "Slot", "Exp")
        self.assertIsNone(err)
        self.assertEqual(item['title'], "Biryani")

    @patch('rescue_app.food_service.get_food_collection')
    @patch('rescue_app.food_service.get_claims_collection')
    def test_claim_own_food_prohibited(self, mock_claims_coll, mock_food_coll):
        provider_id = '64b0f92b7c1234567890abcd'
        mock_coll = MagicMock()
        mock_coll.find_one.return_value = {
            '_id': ObjectId(provider_id),
            'provider_id': provider_id,
            'title': 'Apples',
            'status': 'available'
        }
        mock_food_coll.return_value = mock_coll

        seeker = {'id': provider_id, 'username': 'same_user', 'full_name': 'Same User'}
        success, msg = claim_food_item(provider_id, seeker)
        self.assertFalse(success)
        self.assertIn("cannot claim food that you listed yourself", msg)

    @patch('rescue_app.food_service.get_food_collection')
    @patch('rescue_app.food_service.get_claims_collection')
    def test_claim_available_food_success(self, mock_claims_coll, mock_food_coll):
        provider_id = '64b0f92b7c1234567890aaaa'
        seeker_id = '64b0f92b7c1234567890bbbb'
        food_id = '64b0f92b7c1234567890cccc'

        mock_food_coll_inst = MagicMock()
        mock_food_coll_inst.find_one.return_value = {
            '_id': ObjectId(food_id),
            'provider_id': provider_id,
            'title': 'Rice Bowls',
            'status': 'available'
        }
        mock_food_coll_inst.find_one_and_update.return_value = {
            '_id': ObjectId(food_id),
            'status': 'claimed'
        }
        mock_food_coll.return_value = mock_food_coll_inst
        mock_claims_coll.return_value = MagicMock()

        seeker = {'id': seeker_id, 'username': 'seeker1', 'full_name': 'Seeker One', 'phone': '9999999999'}
        success, msg = claim_food_item(food_id, seeker, claim_notes="Picking up soon")
        self.assertTrue(success)
        self.assertIn("successfully claimed", msg)

    @patch('rescue_app.food_service.get_food_collection')
    @patch('rescue_app.food_service.get_claims_collection')
    def test_mark_food_collected(self, mock_claims_coll, mock_food_coll):
        user_id = '64b0f92b7c1234567890aaaa'
        food_id = '64b0f92b7c1234567890cccc'

        mock_food = MagicMock()
        mock_food.find_one.return_value = {
            '_id': ObjectId(food_id),
            'provider_id': user_id,
            'status': 'claimed'
        }
        mock_food_coll.return_value = mock_food
        mock_claims_coll.return_value = MagicMock()

        success, msg = mark_food_collected(food_id, user_id)
        self.assertTrue(success)
        self.assertIn("marked as collected", msg)


class AuthenticatedSessionFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['user_id'] = '64b0f92b7c1234567890aaaa'
        session['username'] = 'testprovider'
        session['full_name'] = 'Test Provider'
        session['email'] = 'provider@test.com'
        session['active_mode'] = 'provider'
        session.save()

    @patch('rescue_app.auth_helper.get_user_by_id')
    @patch('rescue_app.views.get_dashboard_stats')
    @patch('rescue_app.views.get_provider_listings')
    def test_dashboard_authenticated_provider(self, mock_listings, mock_stats, mock_user):
        mock_user.return_value = {
            'id': '64b0f92b7c1234567890aaaa',
            'username': 'testprovider',
            'full_name': 'Test Provider',
            'default_role': 'provider'
        }
        mock_stats.return_value = {
            'mode': 'provider',
            'stat_1_label': 'Total Listed', 'stat_1_val': 5,
            'stat_2_label': 'Available', 'stat_2_val': 3,
            'stat_3_label': 'Pending', 'stat_3_val': 1,
            'stat_4_label': 'Rescued', 'stat_4_val': 1,
        }
        mock_listings.return_value = []

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Mode:")
        self.assertContains(response, "Food Provider")

    @patch('rescue_app.auth_helper.get_user_by_id')
    def test_switch_mode(self, mock_user):
        mock_user.return_value = {
            'id': '64b0f92b7c1234567890aaaa',
            'username': 'testprovider',
            'full_name': 'Test Provider'
        }
        response = self.client.get(reverse('switch_mode', kwargs={'mode': 'seeker'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['active_mode'], 'seeker')
