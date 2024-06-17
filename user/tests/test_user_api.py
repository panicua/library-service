from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail
from django.contrib.auth import get_user_model
from django.urls import reverse


class UserManagerTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@mail.com", password="password"
        )
        self.superuser = get_user_model().objects.create_superuser(
            email="testsuperuser@mail.com", password="password"
        )
        self.client.force_authenticate(user=self.superuser)

    def test_create_user(self):
        self.assertEqual(self.user.email, "testuser@mail.com")
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_create_superuser(self):
        self.assertEqual(self.superuser.email, "testsuperuser@mail.com")
        self.assertTrue(self.superuser.is_active)
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)

    def test_user_str(self):
        self.assertEqual(str(self.user), "testuser@mail.com")


class UnauthorizedUserApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_manage_no_access(self):
        res = self.client.get(path=reverse("user:manage"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UserAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@api.com", password="password"
        )
        self.superuser = get_user_model().objects.create_superuser(
            email="testsuperuser@api.com", password="password"
        )
        self.client.force_authenticate(user=self.superuser)

    def test_create_user_via_api(self):
        url = reverse("user:create")
        data = {"email": "test@api.com", "password": "password", "first_name": "Test", "last_name": "User"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(get_user_model().objects.count(), 3)

    def test_retrieve_user_via_api(self):
        url = reverse("user:manage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.superuser.email)

    def test_token_obtain(self):
        url = reverse("user:token_obtain_pair")
        data = {"email": self.superuser.email, "password": "password"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_password_validation(self):
        payload = {"email": "register@test.com", "password": "shrt"}
        url = reverse("user:create")
        res = self.client.post(path=url, data=payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            res.data.get("password"),
            [ErrorDetail(string="Ensure this field has at least 5 characters.", code="min_length")]
        )

    def test_register_user(self):
        payload = {"email": "register@test.com", "password": "test_password"}
        url = reverse("user:create")
        res = self.client.post(path=url, data=payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            res.data.get("email"),
            get_user_model().objects.last().email
        )

    def test_user_manage_access(self):
        self.client.force_authenticate(self.user)

        res = self.client.get(path=reverse("user:manage"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, res.data.get("email"))
