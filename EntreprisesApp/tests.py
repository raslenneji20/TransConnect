from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from EntreprisesApp.models import Entreprise, Utilisateur


class EntrepriseCreateViewTests(TestCase):
    def test_create_redirects_to_company_list(self):
        manager = Utilisateur.objects.create_user(
            username='company-manager',
            email='manager@gmail.com',
            password='test-password',
            role='manager',
        )

        response = self.client.post(
            reverse('entreprises:create'),
            {
                'raison_sociale': 'Entreprise de transport',
                'matricule_fiscale': '1234567/A/B/C/123',
                'adresse': '12 rue du Transport, Tunis, Tunisie',
                'type_entreprise': 'transporteur',
                'gerant': manager.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('entreprises:liste'))
        self.assertTrue(
            Entreprise.objects.filter(matricule_fiscale='1234567/A/B/C/123').exists()
        )


class DefaultLanguageTests(TestCase):
    def test_defaults_to_french_despite_browser_language(self):
        response = self.client.get(
            reverse('entreprises:liste'),
            HTTP_ACCEPT_LANGUAGE='en',
        )

        self.assertEqual(settings.LANGUAGE_CODE, 'fr')
        self.assertContains(response, '<html lang="fr">', html=False)
        self.assertContains(response, 'Entreprises')

    def test_respects_explicit_english_language_cookie(self):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = 'en'

        response = self.client.get(reverse('entreprises:liste'))

        self.assertContains(response, '<html lang="en">', html=False)
        self.assertContains(response, 'Companies')
