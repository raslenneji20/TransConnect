from datetime import date, timedelta
from decimal import Decimal
import re

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from EntreprisesApp.models import Entreprise, Utilisateur
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule


class TransConnectTestCase(TestCase):
    def create_user(self, username, role):
        return Utilisateur.objects.create_user(
            username=username,
            email=f'{username}@gmail.com',
            password='Secure-Unique-Password-2026!',
            role=role,
        )

    def test_new_user_with_empty_id_gets_a_generated_id(self):
        user = Utilisateur.objects.create_user(
            username='empty-id-user',
            email='empty-id-user@gmail.com',
            password='Secure-Unique-Password-2026!',
            user_id='',
        )

        self.assertTrue(user.user_id)

    def create_company(self, user, name, company_type='transporteur', suffix='1'):
        return Entreprise.objects.create(
            raison_sociale=name,
            matricule_fiscale=f'123456{suffix}/A/B/C/123',
            adresse='12 rue du Transport, Tunis, Tunisie',
            type_entreprise=company_type,
            gerant=user,
        )


class EntrepriseCreateViewTests(TransConnectTestCase):
    def test_create_redirects_to_company_list_for_admin(self):
        manager = self.create_user('company-manager', Utilisateur.Role.GERANT)
        admin = self.create_user('company-admin', Utilisateur.Role.ADMIN)
        self.client.force_login(admin)

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


class DefaultLanguageTests(TransConnectTestCase):
    def setUp(self):
        self.admin = self.create_user('language-admin', Utilisateur.Role.ADMIN)
        self.client.force_login(self.admin)

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


class RegistrationAndProfileTests(TransConnectTestCase):
    def registration_data(
        self,
        username='new-user',
        role=Utilisateur.Role.CHARGEUR,
        matricule='1234567/A/B/C/123',
    ):
        return {
            'username': username,
            'email': f'{username}@gmail.com',
            'telephone': '21620000000',
            'role': role,
            'raison_sociale': f'Entreprise {username}',
            'matricule_fiscale': matricule,
            'adresse': '12 rue du Transport, Tunis, Tunisie',
            'password1': 'Secure-Unique-Password-2026!',
            'password2': 'Secure-Unique-Password-2026!',
        }

    def test_register_creates_role_scoped_company_and_logs_user_in(self):
        response = self.client.post(
            reverse('entreprises:register'),
            self.registration_data(),
        )

        self.assertRedirects(response, reverse('home'))
        user = Utilisateur.objects.get(username='new-user')
        self.assertEqual(user.role, Utilisateur.Role.CHARGEUR)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        self.assertEqual(user.entreprise.type_entreprise, 'chargeur')
        self.assertTrue(user.is_active)

    def test_registration_creates_transporteur_for_gerant(self):
        response = self.client.post(
            reverse('entreprises:register'),
            self.registration_data(
                username='new-gerant',
                role=Utilisateur.Role.GERANT,
                matricule='1234568/A/B/C/123',
            ),
        )

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(
            Entreprise.objects.get(gerant__username='new-gerant').type_entreprise,
            'transporteur',
        )

    def test_public_registration_cannot_assign_admin_role(self):
        response = self.client.post(
            reverse('entreprises:register'),
            self.registration_data(username='public-admin', role=Utilisateur.Role.ADMIN),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Utilisateur.objects.filter(username='public-admin').exists())

    def test_registration_rejects_non_gmail_address(self):
        data = self.registration_data(username='other-email')
        data['email'] = 'other-email@yahoo.com'

        response = self.client.post(reverse('entreprises:register'), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gmail.com")
        self.assertFalse(Utilisateur.objects.filter(username='other-email').exists())

    def test_registration_rejects_telephone_with_non_numeric_characters(self):
        data = self.registration_data(username='invalid-phone')
        data['telephone'] = '+216 20 000 000'

        response = self.client.post(reverse('entreprises:register'), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ne doit contenir que des chiffres")
        self.assertFalse(Utilisateur.objects.filter(username='invalid-phone').exists())

    def test_profile_updates_contact_fields_but_not_role(self):
        user = self.create_user('profile-user', Utilisateur.Role.CHARGEUR)
        self.create_company(user, 'Profile Company')
        self.client.force_login(user)

        response = self.client.post(
            reverse('entreprises:profile'),
            {
                'username': 'updated-profile-user',
                'email': 'updated-profile@gmail.com',
                'telephone': '21621111111',
                'role': Utilisateur.Role.ADMIN,
            },
        )

        self.assertRedirects(response, reverse('entreprises:profile'))
        user.refresh_from_db()
        self.assertEqual(user.username, 'updated-profile-user')
        self.assertEqual(user.email, 'updated-profile@gmail.com')
        self.assertEqual(user.telephone, '21621111111')
        self.assertEqual(user.role, Utilisateur.Role.CHARGEUR)
        self.assertFalse(user.is_staff)

    def test_account_deactivation_preserves_company_and_business_records(self):
        user = self.create_user('deactivate-user', Utilisateur.Role.CHARGEUR)
        company = self.create_company(user, 'Preserved Company', 'chargeur')
        shipment = self.create_shipment(company, 'EXP-DEACT')
        self.client.force_login(user)

        response = self.client.post(
            reverse('entreprises:deactivate_account'),
            {'password': 'Secure-Unique-Password-2026!'},
        )

        self.assertRedirects(response, reverse('entreprises:login'))
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertTrue(Entreprise.objects.filter(pk=company.pk).exists())
        self.assertTrue(Expedition.objects.filter(pk=shipment.pk).exists())
        self.assertFalse(user.has_usable_password())

    def test_account_deactivation_requires_current_password(self):
        user = self.create_user('wrong-password-user', Utilisateur.Role.CHARGEUR)
        self.create_company(user, 'Password Company', 'chargeur')
        self.client.force_login(user)

        response = self.client.post(
            reverse('entreprises:deactivate_account'),
            {'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_sends_email_and_accepts_new_password(self):
        user = self.create_user('password-reset-user', Utilisateur.Role.CHARGEUR)

        response = self.client.post(
            reverse('entreprises:password_reset'),
            {'email': user.email},
        )

        self.assertRedirects(
            response,
            reverse('entreprises:password_reset_done'),
        )
        self.assertEqual(len(mail.outbox), 1)
        reset_url = re.search(
            r'http://testserver(/entreprises/reset/\S+)',
            mail.outbox[0].body,
        ).group(1)
        confirm_response = self.client.get(reset_url, follow=True)
        self.assertEqual(confirm_response.status_code, 200)

        new_password = 'K7!vQ2#nL9@x'
        response = self.client.post(
            confirm_response.request['PATH_INFO'],
            {
                'new_password1': new_password,
                'new_password2': new_password,
            },
        )

        self.assertRedirects(
            response,
            reverse('entreprises:password_reset_complete'),
        )
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    def create_shipment(self, company, suffix='EXP-TEST'):
        return Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrive='Sousse',
            poids_kg=Decimal('500'),
            date_souhaitee=date.today() + timedelta(days=5),
            description=f'Livraison {suffix}',
            entreprise=company,
        )


class RoleAccessTests(TransConnectTestCase):
    def test_anonymous_users_are_redirected_to_login(self):
        response = self.client.get(reverse('vehicules:liste'))

        self.assertRedirects(
            response,
            f'{reverse("entreprises:login")}?next={reverse("vehicules:liste")}',
        )

    def test_gerant_only_sees_own_company_and_cannot_create_shipments(self):
        gerant = self.create_user('gerant-one', Utilisateur.Role.GERANT)
        other_gerant = self.create_user('gerant-two', Utilisateur.Role.GERANT)
        self.create_company(gerant, 'Own Transport Company', suffix='1')
        self.create_company(other_gerant, 'Other Transport Company', suffix='2')
        self.client.force_login(gerant)

        response = self.client.get(reverse('entreprises:liste'))

        self.assertContains(response, 'Own Transport Company')
        self.assertNotContains(response, 'Other Transport Company')
        self.assertEqual(
            self.client.get(reverse('expeditions:create')).status_code,
            403,
        )

    def test_gerant_can_update_only_its_own_company_details(self):
        gerant = self.create_user('company-editor', Utilisateur.Role.GERANT)
        other_gerant = self.create_user('other-company-editor', Utilisateur.Role.GERANT)
        company = self.create_company(gerant, 'Editable Company', suffix='2')
        other_company = self.create_company(other_gerant, 'Protected Company', suffix='3')
        self.client.force_login(gerant)

        response = self.client.post(
            reverse('entreprises:update', args=[company.pk]),
            {
                'raison_sociale': 'Updated Company',
                'matricule_fiscale': company.matricule_fiscale,
                'adresse': '15 rue du Transport, Tunis, Tunisie',
                'type_entreprise': 'chargeur',
                'gerant': other_gerant.pk,
            },
        )

        self.assertRedirects(
            response,
            reverse('entreprises:detail_entreprise', args=[company.pk]),
        )
        company.refresh_from_db()
        self.assertEqual(company.raison_sociale, 'Updated Company')
        self.assertEqual(company.type_entreprise, 'transporteur')
        self.assertEqual(company.gerant_id, gerant.pk)
        self.assertEqual(
            self.client.get(
                reverse('entreprises:update', args=[other_company.pk])
            ).status_code,
            404,
        )

    def test_chargeur_only_sees_own_shipments_and_cannot_access_vehicles(self):
        chargeur = self.create_user('chargeur-one', Utilisateur.Role.CHARGEUR)
        other_chargeur = self.create_user('chargeur-two', Utilisateur.Role.CHARGEUR)
        own_company = self.create_company(
            chargeur,
            'Own Cargo Company',
            company_type='chargeur',
            suffix='3',
        )
        other_company = self.create_company(
            other_chargeur,
            'Other Cargo Company',
            company_type='chargeur',
            suffix='4',
        )
        own_shipment = self.create_shipment(own_company, 'OWN')
        self.create_shipment(other_company, 'OTHER')
        self.client.force_login(chargeur)

        response = self.client.get(reverse('expeditions:liste'))

        self.assertContains(response, own_shipment.reference)
        self.assertEqual(
            self.client.get(reverse('vehicules:liste')).status_code,
            403,
        )

    def test_admin_can_view_all_companies(self):
        admin = self.create_user('global-admin', Utilisateur.Role.ADMIN)
        gerant_one = self.create_user('admin-gerant-one', Utilisateur.Role.GERANT)
        gerant_two = self.create_user('admin-gerant-two', Utilisateur.Role.GERANT)
        self.create_company(gerant_one, 'First Company', suffix='5')
        self.create_company(gerant_two, 'Second Company', suffix='6')
        self.client.force_login(admin)

        response = self.client.get(reverse('entreprises:liste'))

        self.assertContains(response, 'First Company')
        self.assertContains(response, 'Second Company')

    def test_home_shows_account_deletion_but_not_administration_link_for_all_roles(self):
        admin = self.create_user('home-admin', Utilisateur.Role.ADMIN)
        self.client.force_login(admin)

        response = self.client.get(reverse('home'))

        self.assertNotContains(response, 'Administration')
        self.assertContains(response, 'Supprimer mon compte')

        self.client.logout()
        chargeur = self.create_user('home-chargeur', Utilisateur.Role.CHARGEUR)
        self.create_company(
            chargeur,
            'Home Cargo Company',
            company_type='chargeur',
            suffix='4',
        )
        self.client.force_login(chargeur)
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Supprimer mon compte')
        self.assertNotContains(response, 'Administration')

    def test_admin_can_deactivate_account_when_another_admin_remains(self):
        admin = self.create_user('deactivate-admin', Utilisateur.Role.ADMIN)
        other_admin = self.create_user('remaining-admin', Utilisateur.Role.ADMIN)
        self.client.force_login(admin)

        response = self.client.post(
            reverse('entreprises:deactivate_account'),
            {'password': 'Secure-Unique-Password-2026!'},
        )

        self.assertRedirects(response, reverse('entreprises:login'))
        admin.refresh_from_db()
        other_admin.refresh_from_db()
        self.assertFalse(admin.is_active)
        self.assertTrue(other_admin.is_active)

    def test_last_admin_sees_account_deletion_is_blocked(self):
        admin = self.create_user('last-admin', Utilisateur.Role.ADMIN)
        self.client.force_login(admin)

        response = self.client.get(reverse('entreprises:deactivate_account'))

        self.assertContains(response, 'Le dernier compte administrateur actif')
        self.assertNotContains(response, 'Confirmer la suppression du compte')

    def test_staff_user_without_admin_role_cannot_access_admin_site(self):
        gerant = self.create_user('staff-gerant', Utilisateur.Role.GERANT)
        Utilisateur.objects.filter(pk=gerant.pk).update(is_staff=True)
        self.client.force_login(gerant)

        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 403)

    def test_admin_role_can_access_admin_site(self):
        admin = self.create_user('site-admin', Utilisateur.Role.ADMIN)
        self.client.force_login(admin)

        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 200)

    def test_gerant_sees_only_its_own_offers(self):
        gerant = self.create_user('offer-owner', Utilisateur.Role.GERANT)
        other_gerant = self.create_user('other-offer-owner', Utilisateur.Role.GERANT)
        cargo_user = self.create_user('offer-cargo', Utilisateur.Role.CHARGEUR)
        own_company = self.create_company(
            gerant,
            'Carrier One',
            company_type='transporteur',
            suffix='9',
        )
        other_company = self.create_company(
            other_gerant,
            'Carrier Two',
            company_type='transporteur',
            suffix='0',
        )
        cargo_company = self.create_company(
            cargo_user,
            'Offer Cargo',
            company_type='chargeur',
            suffix='1',
        )
        shipment = self.create_shipment(cargo_company, 'SCOPE')
        own_offer = self.create_offer(own_company, shipment, 'OWN-VEHICLE')
        other_offer = self.create_offer(other_company, shipment, 'OTHER-VEHICLE')
        self.client.force_login(gerant)

        response = self.client.get(reverse('offres:liste'))

        self.assertContains(response, f'#{own_offer.pk}')
        self.assertNotContains(response, f'#{other_offer.pk}')

    def create_offer(self, company, shipment, registration):
        vehicle = Vehicule.objects.create(
            immatriculation=registration,
            capacite_kg=1000,
            type_vehicule='camionnette',
            entreprise=company,
        )
        return Offre.objects.create(
            prix=Decimal('120.00'),
            delai_jours=3,
            statut='proposee',
            date_proposition=date.today(),
            expedition=shipment,
            entreprise=company,
            vehicule=vehicle,
        )

    def test_chargeur_can_accept_an_offer_on_own_shipment(self):
        chargeur = self.create_user('offer-chargeur', Utilisateur.Role.CHARGEUR)
        manager = self.create_user('offer-manager', Utilisateur.Role.GERANT)
        cargo_company = self.create_company(
            chargeur,
            'Offer Cargo Company',
            company_type='chargeur',
            suffix='7',
        )
        carrier_company = self.create_company(
            manager,
            'Offer Carrier Company',
            company_type='transporteur',
            suffix='8',
        )
        shipment = self.create_shipment(cargo_company, 'OFFER')
        vehicle = Vehicule.objects.create(
            immatriculation='TEST-001',
            capacite_kg=1000,
            type_vehicule='camionnette',
            entreprise=carrier_company,
        )
        offer = Offre.objects.create(
            prix=Decimal('120.00'),
            delai_jours=3,
            statut='proposee',
            date_proposition=date.today(),
            expedition=shipment,
            entreprise=carrier_company,
            vehicule=vehicle,
        )
        self.client.force_login(chargeur)

        response = self.client.post(
            reverse('offres:respond', args=[offer.pk]),
            {'action': 'acceptee'},
        )

        offer.refresh_from_db()
        shipment.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(offer.statut, 'acceptee')
        self.assertEqual(shipment.statut, 'attribuee')

    def create_shipment(self, company, suffix='EXP-TEST'):
        return Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrive='Sousse',
            poids_kg=Decimal('500'),
            date_souhaitee=date.today() + timedelta(days=5),
            description=f'Livraison {suffix}',
            entreprise=company,
        )
