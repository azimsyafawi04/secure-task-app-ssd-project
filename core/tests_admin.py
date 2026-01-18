from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import InventoryItem

class AdminFunctionalityTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='password123', email='admin@example.com')
        self.regular_user = User.objects.create_user(username='user', password='password123')
        self.client = Client()

    def test_admin_dashboard_access_staff(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        # Verify total_users, active_users, and inactive_users
        self.assertIn('total_users', response.context)
        self.assertIn('active_users', response.context)
        self.assertIn('inactive_users', response.context)
        self.assertEqual(response.context['total_users'], 2)
        self.assertEqual(response.context['active_users'], 2)
        self.assertEqual(response.context['inactive_users'], 0)
        self.assertLessEqual(len(response.context['audit_logs']), 10)

    def test_admin_user_management_access_staff(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('admin_user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.context)

    def test_audit_logs_all_access_staff(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('audit_logs_all'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('audit_logs', response.context)

    def test_admin_dashboard_access_denied_regular(self):
        self.client.login(username='user', password='password123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_user_soft_delete(self):
        self.client.login(username='admin', password='password123')
        response = self.client.post(reverse('admin_user_delete', args=[self.regular_user.id]))
        # Should redirect back to management page now
        self.assertEqual(response.status_code, 302)
        
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)

    def test_admin_password_change(self):
        self.client.login(username='admin', password='password123')
        # SetPasswordForm uses new_password1 and new_password2 (usually, let's check field names)
        # Actually in Django SetPasswordForm, the fields are 'new_password1' and 'new_password2'
        response = self.client.post(reverse('admin_user_edit_password', args=[self.regular_user.id]), {
            'new_password1': 'newpassword123!',
            'new_password2': 'newpassword123!'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify login with new password
        self.client.logout()
        success = self.client.login(username='user', password='newpassword123!')
        self.assertTrue(success)
