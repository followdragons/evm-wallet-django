from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Chat, ChatWallet, ChatTokenBalance, ChatActivity
from wallet.models import EVMChain, Token
from decimal import Decimal

User = get_user_model()


class ChatModelTest(TestCase):
    def setUp(self):
        self.chat = Chat.objects.create(
            chat_id=-1001234567890,
            title="Test Chat",
            username="testchat",
            description="A test chat"
        )

    def test_chat_creation(self):
        self.assertEqual(self.chat.title, "Test Chat")
        self.assertEqual(self.chat.username, "testchat")
        self.assertEqual(self.chat.get_display_name(), "@testchat")

    def test_chat_without_username(self):
        chat = Chat.objects.create(
            chat_id=-1001234567891,
            title="Test Chat 2",
            description="A test chat without username"
        )
        self.assertEqual(chat.get_display_name(), "Test Chat 2")


class ChatAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            telegram_id=123456789,
            username_tg="testuser"
        )
        self.chat = Chat.objects.create(
            chat_id=-1001234567890,
            title="Test Chat",
            username="testchat"
        )

    def test_list_chats(self):
        url = reverse('chat:chat_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('chats', response.data)

    def test_get_chat_detail(self):
        url = reverse('chat:chat_detail', kwargs={'chat_id': self.chat.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Chat")

    def test_create_chat_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('chat:chat_create')
        data = {
            'chat_id': -1001234567892,
            'title': 'New Test Chat',
            'username': 'newtestchat',
            'description': 'A new test chat'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['chat']['title'], 'New Test Chat')

    def test_create_chat_unauthenticated(self):
        url = reverse('chat:chat_create')
        data = {
            'chat_id': -1001234567893,
            'title': 'Unauthorized Chat'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
