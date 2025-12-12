import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from contacts.models import Contact, SpamReport

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=50, help='Number of users to create')
        parser.add_argument('--contacts', type=int, default=200, help='Number of contacts to create')
        parser.add_argument('--spam_reports', type=int, default=30, help='Number of spam reports to create')

    def handle(self, *args, **options):
        num_users = options['users']
        num_contacts = options['contacts']
        num_spam_reports = options['spam_reports']
        
        self.stdout.write(self.style.SUCCESS(f'Creating {num_users} users...'))
        
        phone_numbers = set()
        while len(phone_numbers) < num_users:
            phone_numbers.add(f"+1{random.randint(1000000000, 9999999999)}")
        
        users = []
        for i, phone_number in enumerate(phone_numbers):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}{last_name.lower()}{i}"
            user = User.objects.create_user(
                username=username,
                password='password123',
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                email=fake.email() if random.random() > 0.2 else None
            )
            users.append(user)
            self.stdout.write(f'Created user: {user.get_full_name()} ({user.phone_number})')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(users)} users'))
        
        self.stdout.write(self.style.SUCCESS(f'Creating {num_contacts} contacts...'))
        
        non_user_phone_numbers = set()
        while len(non_user_phone_numbers) < num_contacts // 2:
            phone = f"+1{random.randint(1000000000, 9999999999)}"
            if phone not in phone_numbers:
                non_user_phone_numbers.add(phone)
        
        contacts_created = 0
        
        for user in users:
            other_users = random.sample([u for u in users if u != user], k=min(5, len(users) - 1))
            
            for other_user in other_users:
                contact = Contact.objects.create(
                    owner=user,
                    name=f"{other_user.first_name} {other_user.last_name}",
                    phone_number=other_user.phone_number,
                    email=other_user.email
                )
                contacts_created += 1
                
                if contacts_created >= num_contacts:
                    break
            
            if contacts_created >= num_contacts:
                break
                
            for _ in range(min(3, len(non_user_phone_numbers))):
                if not non_user_phone_numbers:
                    break
                    
                phone = non_user_phone_numbers.pop()
                contact = Contact.objects.create(
                    owner=user,
                    name=f"{fake.first_name()} {fake.last_name()}",
                    phone_number=phone,
                    email=fake.email() if random.random() > 0.3 else None
                )
                contacts_created += 1
                
                if contacts_created >= num_contacts:
                    break
                    
            if contacts_created >= num_contacts:
                break
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {contacts_created} contacts'))
        
        self.stdout.write(self.style.SUCCESS(f'Creating {num_spam_reports} spam reports...'))
        
        all_phones = list(phone_numbers) + list(non_user_phone_numbers)
        spam_phones = random.sample(all_phones, min(num_spam_reports // 2, len(all_phones)))
        
        reports_created = 0
        
        for phone in spam_phones:
            reporters = random.sample(users, min(3, len(users)))
            for reporter in reporters:
                if reporter.phone_number == phone:
                    continue
                    
                SpamReport.objects.create(
                    reporter=reporter,
                    phone_number=phone
                )
                reports_created += 1
                
                if reports_created >= num_spam_reports:
                    break
                    
            if reports_created >= num_spam_reports:
                break
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {reports_created} spam reports')) 