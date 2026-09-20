from datetime import date, timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from gymapp.models import Admin, DietPlan, Member, Payment, Progress, Trainer, User, WorkoutPlan
from gymapp.services import create_admin, create_member, create_trainer
from gymapp.utils import calculate_bmi

PASSWORD = 'GymPass123!'


class FitFocusTests(TestCase):
    def setUp(self):
        self.admin = create_admin(
            email='admin@test.com',
            password=PASSWORD,
            username='test_admin',
        )
        self.trainer = create_trainer(
            password=PASSWORD,
            email='trainer@test.com',
            fullname='Test Trainer',
            phone='5551110001',
            specialization='Strength',
            qualification='CPT',
        )
        self.other_trainer = create_trainer(
            password=PASSWORD,
            email='trainer2@test.com',
            fullname='Second Trainer',
            phone='5551110002',
            specialization='Cardio',
            qualification='ACE',
        )
        self.member = create_member(
            password=PASSWORD,
            email='member@test.com',
            fullname='Test Member',
            dob=date(1995, 5, 5),
            age=30,
            gender='Male',
            phone='5552220001',
            address='1 Test Street',
            height=180,
            weight=80,
            goal='Muscle Gain',
        )
        self.other_member = create_member(
            password=PASSWORD,
            email='member2@test.com',
            fullname='Other Member',
            dob=date(1998, 1, 1),
            age=27,
            gender='Female',
            phone='5552220002',
            address='2 Test Street',
            height=165,
            weight=60,
            goal='Weight Loss',
        )
        self.member.trainer = self.trainer
        self.member.save(update_fields=['trainer'])

    def login(self, email, role):
        return self.client.post(
            reverse('login'),
            {'email': email, 'password': PASSWORD, 'role': role},
        )

    def test_member_registration(self):
        response = self.client.post(
            reverse('register'),
            {
                'fullname': 'New Member',
                'dob': '2000-02-02',
                'age': 24,
                'gender': 'Other',
                'phone': '5552220099',
                'email': 'new.member@test.com',
                'height': '170.00',
                'weight': '70.00',
                'address': '9 New Road',
                'goal': 'General Fitness',
                'password': PASSWORD,
                'confirm_password': PASSWORD,
            },
        )
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(email='new.member@test.com')
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(Member.objects.filter(user=user, phone='5552220099').exists())

    def test_registration_rejects_duplicate_email(self):
        response = self.client.post(
            reverse('register'),
            {
                'fullname': 'Copy Member',
                'dob': '2000-02-02',
                'age': 24,
                'gender': 'Male',
                'phone': '5552220100',
                'email': 'member@test.com',
                'height': '170.00',
                'weight': '70.00',
                'address': '9 New Road',
                'goal': 'General Fitness',
                'password': PASSWORD,
                'confirm_password': PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already registered')

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse('register'),
            {
                'fullname': 'Copy Member',
                'dob': '2000-02-02',
                'age': 24,
                'gender': 'Male',
                'phone': '5552220101',
                'email': 'mismatch@test.com',
                'height': '170.00',
                'weight': '70.00',
                'address': '9 New Road',
                'goal': 'General Fitness',
                'password': PASSWORD,
                'confirm_password': 'Different123!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'must match')

    def test_successful_login(self):
        response = self.login('member@test.com', User.Role.MEMBER)
        self.assertRedirects(response, reverse('member_dashboard'))
        self.client.logout()

        response = self.login('trainer@test.com', User.Role.TRAINER)
        self.assertRedirects(response, reverse('trainer_dashboard'))
        self.client.logout()

        response = self.login('admin@test.com', User.Role.ADMIN)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_invalid_login(self):
        response = self.client.post(
            reverse('login'),
            {'email': 'member@test.com', 'password': 'WrongPass123!', 'role': User.Role.MEMBER},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email, password, or role.')

    def test_login_rejects_wrong_role(self):
        response = self.client.post(
            reverse('login'),
            {'email': 'member@test.com', 'password': PASSWORD, 'role': User.Role.ADMIN},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email, password, or role.')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_unauthorized_users_cannot_access_protected_dashboards(self):
        for url_name in ('admin_dashboard', 'trainer_dashboard', 'member_dashboard'):
            response = self.client.get(reverse(url_name))
            self.assertRedirects(response, reverse('login'))

    def test_role_based_access(self):
        self.login('member@test.com', User.Role.MEMBER)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('member_dashboard'))
        response = self.client.get(reverse('admin_members'))
        self.assertRedirects(response, reverse('member_dashboard'))
        response = self.client.get(reverse('trainer_members'))
        self.assertRedirects(response, reverse('member_dashboard'))

        self.client.logout()
        self.login('trainer@test.com', User.Role.TRAINER)
        response = self.client.get(reverse('trainer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trainer Profile')
        self.assertContains(response, 'Assigned Members')
        self.assertContains(response, 'Assign Workout Plan')
        self.assertContains(response, 'Assign Diet Plan')
        self.assertContains(response, 'View Member Progress')
        response = self.client.get(reverse('admin_trainers_manage'))
        self.assertRedirects(response, reverse('trainer_dashboard'))
        response = self.client.get(reverse('member_dashboard'))
        self.assertRedirects(response, reverse('trainer_dashboard'))

        self.client.logout()
        self.login('admin@test.com', User.Role.ADMIN)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Members')
        self.assertContains(response, 'View Members')
        self.assertContains(response, 'Add Trainers')
        self.assertContains(response, 'Manage Trainers')
        self.assertContains(response, 'Assign Trainers')
        self.assertContains(response, 'View Payments')

    def test_trainer_creation(self):
        self.login('admin@test.com', User.Role.ADMIN)
        response = self.client.post(
            reverse('admin_trainer_add'),
            {
                'fullname': 'Added Trainer',
                'phone': '5551110099',
                'email': 'added.trainer@test.com',
                'specialization': 'Yoga',
                'qualification': 'RYT-200',
                'password': PASSWORD,
            },
        )
        self.assertRedirects(response, reverse('admin_trainers_manage'))
        trainer = Trainer.objects.get(user__email='added.trainer@test.com')
        self.assertEqual(trainer.fullname, 'Added Trainer')
        self.assertTrue(trainer.user.check_password(PASSWORD))

    def test_trainer_assignment(self):
        self.login('admin@test.com', User.Role.ADMIN)
        response = self.client.post(
            reverse('admin_assign_trainer'),
            {'member': self.other_member.member_id, 'trainer': self.other_trainer.trainer_id},
        )
        self.assertRedirects(response, reverse('admin_assign_trainer'))
        self.other_member.refresh_from_db()
        self.assertEqual(self.other_member.trainer, self.other_trainer)

    def test_workout_assignment(self):
        self.login('trainer@test.com', User.Role.TRAINER)
        response = self.client.post(
            reverse('trainer_workout_add'),
            {
                'member': self.member.member_id,
                'workout_name': 'Push Day',
                'exercise_type': 'Strength',
                'duration': '45 minutes',
                'sets': 4,
                'repetitions': 10,
                'instructions': 'Keep elbows tucked.',
            },
        )
        self.assertRedirects(response, reverse('trainer_workout_add'))
        plan = WorkoutPlan.objects.get(workout_name='Push Day')
        self.assertEqual(plan.member, self.member)
        self.assertEqual(plan.trainer, self.trainer)

        self.client.logout()
        self.login('member@test.com', User.Role.MEMBER)
        response = self.client.get(reverse('member_workout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Push Day')
        self.assertContains(response, 'Test Trainer')

    def test_diet_assignment(self):
        self.login('trainer@test.com', User.Role.TRAINER)
        response = self.client.post(
            reverse('trainer_diet_add'),
            {
                'member': self.member.member_id,
                'breakfast': 'Eggs and toast',
                'lunch': 'Chicken salad',
                'dinner': 'Fish and vegetables',
                'snacks': 'Protein shake',
                'instructions': 'Drink plenty of water.',
            },
        )
        self.assertRedirects(response, reverse('trainer_diet_add'))
        plan = DietPlan.objects.get(member=self.member)
        self.assertEqual(plan.trainer, self.trainer)
        self.assertEqual(plan.breakfast, 'Eggs and toast')

        self.client.logout()
        self.login('member@test.com', User.Role.MEMBER)
        response = self.client.get(reverse('member_diet'))
        self.assertContains(response, 'Eggs and toast')
        self.assertContains(response, 'Protein shake')

    def test_progress_update(self):
        self.login('trainer@test.com', User.Role.TRAINER)
        response = self.client.post(
            reverse('trainer_progress'),
            {
                'member': self.member.member_id,
                'weight': '78.50',
                'remarks': 'Leaner after four weeks.',
                'updated_date': date.today().isoformat(),
            },
        )
        self.assertRedirects(response, reverse('trainer_progress'))
        record = Progress.objects.get(member=self.member)
        self.assertEqual(float(record.weight), 78.5)
        self.assertEqual(record.bmi, calculate_bmi(78.5, 180))
        self.member.refresh_from_db()
        self.assertEqual(float(self.member.weight), 78.5)

    def test_trainer_cannot_update_unassigned_member(self):
        self.login('trainer@test.com', User.Role.TRAINER)
        response = self.client.post(
            reverse('trainer_progress'),
            {
                'member': self.other_member.member_id,
                'weight': '61.00',
                'remarks': 'Should not save.',
                'updated_date': date.today().isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Progress.objects.filter(member=self.other_member).exists())

    def test_payment_record(self):
        self.login('admin@test.com', User.Role.ADMIN)
        response = self.client.post(
            reverse('admin_payments'),
            {
                'member': self.member.member_id,
                'amount': '49.99',
                'payment_date': date.today().isoformat(),
                'payment_method': Payment.Method.CARD,
                'payment_status': Payment.Status.PAID,
            },
        )
        self.assertRedirects(response, reverse('admin_payments'))
        payment = Payment.objects.get(member=self.member)
        self.assertEqual(str(payment.amount), '49.99')

        response = self.client.get(reverse('admin_payments'))
        self.assertContains(response, '49.99')

    def test_member_can_view_their_own_data(self):
        Payment.objects.create(
            member=self.member,
            amount=25,
            payment_date=date.today(),
            payment_method=Payment.Method.CASH,
            payment_status=Payment.Status.PAID,
        )
        WorkoutPlan.objects.create(
            member=self.member,
            trainer=self.trainer,
            workout_name='Own Workout',
            exercise_type='Strength',
            duration='30 minutes',
            sets=3,
            repetitions=12,
            instructions='Warm up first.',
        )
        self.login('member@test.com', User.Role.MEMBER)
        self.assertContains(self.client.get(reverse('member_profile')), 'Test Member')
        self.assertContains(self.client.get(reverse('member_workout')), 'Own Workout')
        self.assertContains(self.client.get(reverse('member_payments')), '25')
        self.assertContains(self.client.get(reverse('member_dashboard')), 'Progress Tracking')

    def test_member_cannot_access_another_members_private_data(self):
        Payment.objects.create(
            member=self.other_member,
            amount=999.99,
            payment_date=date.today() - timedelta(days=1),
            payment_method=Payment.Method.CARD,
            payment_status=Payment.Status.PAID,
        )
        WorkoutPlan.objects.create(
            member=self.other_member,
            trainer=self.other_trainer,
            workout_name='Secret Plan',
            exercise_type='HIIT',
            duration='20 minutes',
            sets=5,
            repetitions=20,
            instructions='Private notes.',
        )
        self.login('member@test.com', User.Role.MEMBER)
        payments_page = self.client.get(reverse('member_payments'))
        workout_page = self.client.get(reverse('member_workout'))
        self.assertNotContains(payments_page, '999.99')
        self.assertNotContains(workout_page, 'Secret Plan')
        detail = self.client.get(reverse('admin_member_detail', args=[self.other_member.member_id]))
        self.assertRedirects(detail, reverse('member_dashboard'))

    def test_passwords_are_hashed(self):
        self.assertTrue(self.member.user.check_password(PASSWORD))
        self.assertNotEqual(self.member.user.password, PASSWORD)
        self.assertTrue(self.member.user.password.startswith('pbkdf2_') or self.member.user.has_usable_password())


class InitialAdminCommandTests(TestCase):
    def test_creates_only_the_administrator(self):
        call_command('create_initial_admin', stdout=StringIO())

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Admin.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 0)
        self.assertEqual(Trainer.objects.count(), 0)
        self.assertEqual(WorkoutPlan.objects.count(), 0)
        self.assertEqual(DietPlan.objects.count(), 0)
        self.assertEqual(Progress.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)

        user = User.objects.get(email='admin@gmail.com')
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.check_password('admin123'))
        self.assertNotEqual(user.password, 'admin123')
        self.assertTrue(user.has_usable_password())

    def test_does_not_duplicate_existing_admin(self):
        call_command('create_initial_admin', stdout=StringIO())
        call_command('create_initial_admin', stdout=StringIO())
        self.assertEqual(User.objects.filter(email='admin@gmail.com').count(), 1)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 0)
        self.assertEqual(Trainer.objects.count(), 0)

    def test_initial_admin_can_log_in(self):
        call_command('create_initial_admin', stdout=StringIO())
        response = self.client.post(
            reverse('login'),
            {'email': 'admin@gmail.com', 'password': 'admin123', 'role': User.Role.ADMIN},
        )
        self.assertRedirects(response, reverse('admin_dashboard'))
        dashboard = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, 'Total Members')
        self.assertContains(dashboard, 'No members yet.')
