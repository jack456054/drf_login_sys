from rest_framework.test import APIClient, APITestCase
from basic_app.models import UserProfileInfo
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status
from django.contrib.auth.models import User

# Create your tests here.


# Test user's permission
class AdminUserAccessTest(APITestCase):
    def setUp(self):
        print('Setting up...')

        # Initialize the APIClient app
        self.client = APIClient()

        # Create a test admin user
        password = make_password("admin")
        admin_info = {"username": "admin", "password": password,
                      "email": "admin@email.com", }
        admin = User(**admin_info)
        admin.is_staff = True
        admin.save()

        # Create test user
        password = make_password("test")
        user_info = {"username": "test", "password": password,
                     "email": "test@email.com", }
        user = User(**user_info)
        user.save()
        user_with_portfolio = UserProfileInfo.objects.create(
            user=user, portfolio_site="http://test.com")
        user_with_portfolio.save()

        # Create test1 user
        password = make_password("test1")
        user_info = {"username": "test1", "password": password,
                     "email": "test1@email.com", }
        user = User(**user_info)
        user.save()
        user_with_portfolio = UserProfileInfo.objects.create(
            user=user, portfolio_site="http://test1.com")
        user_with_portfolio.save()

    # List test
    def test_list(self):
        print("List action testing...")
        url = '/api/basic_app/'

        # Non user test
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin test
        profiles = UserProfileInfo.objects.values()
        people = User.objects.values('username', 'password', 'email')
        self.client.login(username='admin', password='admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(len(response.data)):
            self.assertEqual(response.data[i]['user'], people[i+1])
            self.assertEqual(
                response.data[i]['portfolio_site'], profiles[i]['portfolio_site'])
        self.client.logout()

        # User test
        self.client.login(username='test', password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        print('passed!')

    # Create test
    def test_create(self):
        print("Create action testing...")
        url = '/api/basic_app/'

        # Non user test
        password = make_password("test2")
        data = {"user": {"username": "test2", "password": password,
                         "email": "test2@email.com", }, "portfolio_site": "http://test2.com", }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(UserProfileInfo.objects.count(), 3)
        self.assertEqual(User.objects.last().username, 'test2')
        self.assertEqual(UserProfileInfo.objects.last(
        ).portfolio_site, 'http://test2.com')

        # Admin test
        self.client.login(username='admin', password='admin')
        password = make_password("test3")
        data = {"user": {"username": "test3", "password": password,
                         "email": "test3@email.com", }, "portfolio_site": "http://test3.com", }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 5)
        self.assertEqual(UserProfileInfo.objects.count(), 4)
        self.assertEqual(User.objects.last().username, 'test3')
        self.assertEqual(UserProfileInfo.objects.last(
        ).portfolio_site, 'http://test3.com')
        self.client.logout()

        # User test
        self.client.login(username='test1', password='test1')
        password = make_password("test4")
        data = {"user": {"username": "test4", "password": password,
                         "email": "test4@email.com", }, "portfolio_site": "http://test4.com", }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 6)
        self.assertEqual(UserProfileInfo.objects.count(), 5)
        self.assertEqual(User.objects.last().username, 'test4')
        self.assertEqual(UserProfileInfo.objects.last(
        ).portfolio_site, 'http://test4.com')
        self.client.logout()

        print('passed!')

    # Retrieve test
    def test_retrieve(self):
        print("Retrieve action testing...")
        url = '/api/basic_app/{}/'

        # Non user test
        response = self.client.get(url.format(
            UserProfileInfo.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin test
        self.client.login(username='admin', password='admin')
        response = self.client.get(url.format(
            UserProfileInfo.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'],
                         User.objects.values().last()['username'])
        self.client.logout()

        # User test
        # Not allowed to access other's info
        self.client.login(username='test', password='test')
        response = self.client.get(url.format(
            UserProfileInfo.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        # Allowed to access self info
        self.client.login(username='test1', password='test1')
        response = self.client.get(url.format(
            UserProfileInfo.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'],
                         User.objects.values().last()['username'])
        self.client.logout()

        print('passed!')

    # Destroy test
    def test_destroy(self):
        print("Destroy action testing...")
        url = '/api/basic_app/{}/'

        # Non user test
        response = self.client.delete(url.format(
            UserProfileInfo.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # User test
        # Not allowed to access other's info
        self.client.login(username='test', password='test')
        response = self.client.delete(url.format(
            UserProfileInfo.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        # Allowed to access self info
        self.client.login(username='test1', password='test1')
        response = self.client.delete(url.format(
            UserProfileInfo.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.last().is_active, False)
        self.client.logout()

        print('passed!')

    # Update test
    def test_update(self):
        print("Update action testing...")
        url = '/api/basic_app/{}/'

        # Non user test
        data = {"user": {"username": "test2", "password": "test2",
                         "email": "test2@email.com", }, "portfolio_site": "http://test2.com", }
        response = self.client.put(url.format(
            UserProfileInfo.objects.last().id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        # Admin test
        self.client.login(username='admin', password='admin')
        response = self.client.put(url.format(
            UserProfileInfo.objects.last().id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['user']['username'],
                         User.objects.values().last()['username'])
        self.assertEqual(response.data['user']
                         ['username'], data['user']['username'])
        self.client.logout()

        # User test
        # Not allowed to access other's info
        self.client.login(username='test', password='test')
        response = self.client.put(url.format(
            UserProfileInfo.objects.last().id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        # Allowed to access self info
        data = {"user": {"username": "test1", "password": "test1",
                         "email": "test1@email.com", }, "portfolio_site": "http://test1.com", }
        self.client.login(username='test2', password='test2')
        response = self.client.put(url.format(
            UserProfileInfo.objects.last().id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['user']['username'],
                         User.objects.values().last()['username'])
        self.assertEqual(response.data['user']
                         ['username'], data['user']['username'])
        self.client.logout()

        print('passed!')

    # Partial update test
    def test_partial_update(self):
        print("Partial update action testing...")
        url = '/api/basic_app/{}/'

        # Non user test
        data = {"user": {"username": "test2", "password": "test2"},
                "portfolio_site": "http://test2.com", }
        response = self.client.patch(url.format(
            UserProfileInfo.objects.last().id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        # Admin test
        self.client.login(username='admin', password='admin')
        response = self.client.put(url.format(
            UserProfileInfo.objects.last().id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['user']['username'],
                         User.objects.values().last()['username'])
        self.assertEqual(response.data['user']
                         ['username'], data['user']['username'])
        self.assertEqual(data['portfolio_site'],
                         UserProfileInfo.objects.values().last()['portfolio_site'])
        self.assertEqual(
            response.data['portfolio_site'], data['portfolio_site'])
        user = User.objects.get(username='test2')
        self.assertTrue(user.check_password('test2'))
        self.client.logout()

        # User test
        # Not allowed to access other's info
        self.client.login(username='test', password='test')
        response = self.client.patch(url.format(
            UserProfileInfo.objects.last().id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        # Allowed to access self info
        data = {"user": {"username": "test1", "password": "test1"},
                "portfolio_site": "http://test1.com", }
        self.client.login(username='test2', password='test2')
        response = self.client.patch(url.format(
            UserProfileInfo.objects.last().id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['user']['username'],
                         User.objects.values().last()['username'])
        self.assertEqual(response.data['user']
                         ['username'], data['user']['username'])
        self.assertEqual(data['portfolio_site'],
                         UserProfileInfo.objects.values().last()['portfolio_site'])
        self.assertEqual(
            response.data['portfolio_site'], data['portfolio_site'])
        user = User.objects.get(username='test1')
        self.assertTrue(user.check_password('test1'))
        self.client.logout()

        print('passed!')
