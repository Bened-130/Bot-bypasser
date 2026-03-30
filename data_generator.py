import random
import string
import json
import os
from datetime import datetime


class DataGenerator:
    def __init__(self, storage_file='used_data.json'):
        self.storage_file = storage_file
        self.used_emails = set()
        self.used_phones = set()
        self.used_names = set()
        self.load_used_data()
        
        # Kenyan names
        self.first_names = [
            'John', 'Mary', 'Peter', 'Grace', 'James', 'Esther', 'Michael', 'Jane',
            'Daniel', 'Lucy', 'David', 'Sarah', 'Joseph', 'Elizabeth', 'Paul', 'Ann',
            'Stephen', 'Margaret', 'George', 'Catherine', 'Patrick', 'Ruth', 'Francis',
            'Christine', 'Samuel', 'Joyce', 'Robert', 'Nancy', 'Benjamin', 'Lydia',
            'Emmanuel', 'Martha', 'Simon', 'Betty', 'Thomas', 'Veronica', 'Andrew',
            'Regina', 'Moses', 'Dorothy', 'Joshua', 'Rebecca', 'Abraham', 'Phyllis',
            'Isaac', 'Rachel', 'Jacob', 'Hannah', 'Gabriel', 'Deborah', 'Jonathan',
            'Beatrice', 'Timothy', 'Gladys', 'Philip', 'Agnes', 'Nicholas', 'Julia',
            'Lizadro', 'Cliffod', 'Alex', 'Jackline', 'Shalon', 'Ireen', 'Mwongela'
        ]
        
        self.last_names = [
            'Mwangi', 'Wanjiku', 'Otieno', 'Wambui', 'Kamau', 'Njeri', 'Ochieng',
            'Wangari', 'Njoroge', 'Wairimu', 'Omondi', 'Wanjiru', 'Kariuki', 'Wangechi',
            'Kipchirchir', 'Jepchirchir', 'Mutua', 'Kyalo', 'Muli', 'Waweru',
            'Githinji', 'Waithaka', 'Mbugua', 'Ndungu', 'Wanjala', 'Oduor', 'Akinyi',
            'Okoth', 'Auma', 'Onyango', 'Oloo', 'Adhiambo', 'Were', 'Ouma',
            'Muriithi', 'Macharia', 'Kinyua', 'Gachanja', 'Muchiri', 'Mweteri',
            'Kathuri', 'Mukami', 'Mukami', 'Kathurima', 'Mbiti', 'Nkirote',
            'Gaichiumia', 'Mwongela', 'Kinya', 'Mwiti', 'Peter', 'Lizadro'
        ]
        
        self.domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'mail.com', 'protonmail.com', 'yandex.com'
        ]
        
    def load_used_data(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.used_emails = set(data.get('emails', []))
                    self.used_phones = set(data.get('phones', []))
                    self.used_names = set(data.get('names', []))
            except:
                pass
    
    def save_used_data(self):
        data = {
            'emails': list(self.used_emails),
            'phones': list(self.used_phones),
            'names': list(self.used_names),
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def generate_name(self):
        max_attempts = 1000
        for _ in range(max_attempts):
            first = random.choice(self.first_names)
            last = random.choice(self.last_names)
            full_name = f"{first} {last}"
            
            if full_name not in self.used_names:
                self.used_names.add(full_name)
                return {
                    'full_name': full_name,
                    'first_name': first,
                    'last_name': last
                }
        
        # Fallback
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        full_name = f"{first} {last} {random.randint(1, 999)}"
        self.used_names.add(full_name)
        return {
            'full_name': full_name,
            'first_name': first,
            'last_name': last
        }
    
    def generate_email(self, name=None):
        max_attempts = 10000
        
        for _ in range(max_attempts):
            if name:
                first = name['first_name'].lower()
                last = name['last_name'].lower()
            else:
                first = random.choice(self.first_names).lower()
                last = random.choice(self.last_names).lower()
            
            formats = [
                f"{first}.{last}{random.randint(1,9999)}",
                f"{first}{last}{random.randint(1,999)}",
                f"{first[0]}{last}{random.randint(10,99999)}",
                f"{first}_{last}{random.randint(1,9999)}",
                f"{first}{random.randint(100,99999)}",
                f"{last}.{first}{random.randint(1,999)}",
                f"{first}{last[0]}{random.randint(100,99999)}",
                f"{first}{random.randint(1975,2005)}",
            ]
            
            username = random.choice(formats).replace(' ', '')
            domain = random.choice(self.domains)
            email = f"{username}@{domain}"
            
            if len(email) > 60 or '..' in email or email.startswith('.') or email.endswith('.'):
                continue
            
            if email not in self.used_emails:
                self.used_emails.add(email)
                self.save_used_data()
                return email
        
        raise Exception("Could not generate unique email")
    
    def generate_phone(self):
        max_attempts = 10000
        
        for _ in range(max_attempts):
            safaricom = ['070', '071', '072', '0740', '0741', '0742', '0743', '0745', '0746', '0748', '011']
            airtel = ['073', '075', '078', '010']
            telkom = ['077', '076']
            
            all_prefixes = safaricom + airtel + telkom
            prefix = random.choice(all_prefixes)
            
            remaining_length = 9 - len(prefix)
            suffix = ''.join(random.choices(string.digits, k=remaining_length))
            
            phone = f"{prefix}{suffix}"
            
            if len(phone) != 10 or not phone.startswith(('07', '01')):
                continue
            
            phone_variants = [phone, f"+254{phone[1:]}", f"254{phone[1:]}", f"0{phone}"]
            
            if not any(var in self.used_phones for var in phone_variants):
                self.used_phones.update(phone_variants)
                self.save_used_data()
                return {
                    'local': phone,
                    'international': f"+254{phone[1:]}",
                    'plain': f"254{phone[1:]}"
                }
        
        raise Exception("Could not generate unique phone")
    
    def generate_whatsapp(self, phone_data=None):
        if phone_data:
            return phone_data['international']
        return self.generate_phone()['international']
    
    def generate_age_bracket(self):
        brackets = ['18-24', '25-30', '21-35', '18-25', '26-35']
        weights = [0.35, 0.30, 0.20, 0.10, 0.05]
        return random.choices(brackets, weights=weights)[0]
    
    def generate_county(self):
        """Always Meru County"""
        return 'Meru County'
    
    def generate_youth_senator(self):
        """
        FIXED per user requirement: Lizadro Peter
        (From screenshot: Jackline Mukami, Lizadro Peter, Cliffod Kathurima, Peter Mweteri, Alex Muigai Mbiti)
        """
        return 'Lizadro Peter'
    
    def generate_youth_woman_rep(self):
        """
        FIXED per user requirement: Nancy Gaichiumia Mwongela
        (From screenshot: Jackline Nkirote, Nancy Gaichiumia Mwongela, Shalon Kinya, Ireen Kinya mwiti)
        """
        return 'Nancy Gaichiumia Mwongela'
    
    def generate_contact_preference(self):
        return "No, I don't wish to be contacted"
    
    def generate_complete_profile(self):
        name = self.generate_name()
        email = self.generate_email(name)
        phone = self.generate_phone()
        whatsapp = self.generate_whatsapp(phone)
        
        profile = {
            'full_name': name['full_name'],
            'first_name': name['first_name'],
            'last_name': name['last_name'],
            'email': email,
            'phone': phone['local'],
            'phone_international': phone['international'],
            'whatsapp': whatsapp,
            'age_bracket': self.generate_age_bracket(),
            'county': self.generate_county(),
            'youth_senator': self.generate_youth_senator(),  # FIXED: Lizadro Peter
            'youth_woman_rep': self.generate_youth_woman_rep(),  # FIXED: Nancy Gaichiumia Mwongela
            'contact_preference': self.generate_contact_preference(),
            'timestamp': datetime.now().isoformat()
        }
        
        return profile
    
    def get_stats(self):
        return {
            'total_emails_generated': len(self.used_emails),
            'total_phones_generated': len([p for p in self.used_phones if p.startswith('07')]),
            'total_names_generated': len(self.used_names),
            'storage_file': self.storage_file
        }