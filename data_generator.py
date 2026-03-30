#!/usr/bin/env python3
"""
Data Generator - Google Form Specific
- No international numbers (local Kenyan format only)
- WhatsApp: local format 07XX XXX XXX
- Fixed: Lizadro Peter (Senator), Nancy Gaichiumia Mwongela (Woman Rep)
- County: Meru
- Contact: No
"""

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
            'White', 'Lizadro', 'Cliffod', 'Alex', 'Jackline', 'Shalon', 'Ireen'
        ]
        
        self.last_names = [
            'Mwangi', 'Wanjiku', 'Otieno', 'Wambui', 'Kamau', 'Njeri', 'Ochieng',
            'Wangari', 'Njoroge', 'Wairimu', 'Omondi', 'Wanjiru', 'Kariuki', 'Wangechi',
            'Kipchirchir', 'Jepchirchir', 'Mutua', 'Kyalo', 'Muli', 'Waweru',
            'Githinji', 'Waithaka', 'Mbugua', 'Ndungu', 'Wanjala', 'Oduor', 'Akinyi',
            'Okoth', 'Auma', 'Onyango', 'Oloo', 'Adhiambo', 'Were', 'Ouma',
            'Muriithi', 'Macharia', 'Kinyua', 'Gachanja', 'Muchiri', 'Mweteri',
            'Kathuri', 'Mukami', 'Kathurima', 'Mbiti', 'Nkirote',
            'Gaichiumia', 'Mwongela', 'Kinya', 'Mwiti', 'Murithi'
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
        
        # Fallback with number
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
        """
        Generate Kenyan phone in LOCAL format only (NO international)
        Format: 07XX XXX XXX or 01XX XXX XXX
        """
        max_attempts = 10000
        
        for _ in range(max_attempts):
            # Kenyan prefixes only
            safaricom = ['070', '071', '072', '0740', '0741', '0742', '0743', '0745', '0746', '0748', '011']
            airtel = ['073', '075', '078', '010']
            telkom = ['077', '076']
            
            all_prefixes = safaricom + airtel + telkom
            prefix = random.choice(all_prefixes)
            
            remaining_length = 9 - len(prefix)
            suffix = ''.join(random.choices(string.digits, k=remaining_length))
            
            phone = f"{prefix}{suffix}"
            
            # Validate: must be 10 digits, start with 07 or 01
            if len(phone) != 10 or not phone.startswith(('07', '01')):
                continue
            
            # Check uniqueness (local format only)
            if phone not in self.used_phones:
                self.used_phones.add(phone)
                self.save_used_data()
                return phone  # Return local format only
        
        raise Exception("Could not generate unique phone")
    
    def generate_whatsapp(self):
        """
        WhatsApp number in LOCAL Kenyan format (same as phone)
        NO international format (+254)
        """
        return self.generate_phone()  # Same local format
    
    def generate_age_bracket(self):
        """Age bracket as shown in form: 18-24, 25-30, 31-35"""
        brackets = ['18-24', '25-30', '31-35']
        weights = [0.4, 0.4, 0.2]  # Weight toward younger
        return random.choices(brackets, weights=weights)[0]
    
    def generate_county(self):
        """Always Meru"""
        return 'Meru'
    
    def generate_youth_senator(self):
        """FIXED: Lizadro Peter"""
        return 'Lizadro Peter'
    
    def generate_youth_woman_rep(self):
        """FIXED: Nancy Gaichiumia Mwongela"""
        return 'Nancy Gaichiumia Mwongela'
    
    def generate_contact_preference(self):
        """FIXED: No, I do not wish to be contacted"""
        return "No, I do not wish to be contacted"
    
    def generate_complete_profile(self):
        name = self.generate_name()
        email = self.generate_email(name)
        phone = self.generate_phone()  # Local format only
        whatsapp = self.generate_whatsapp()  # Local format only
        
        profile = {
            'full_name': name['full_name'],
            'first_name': name['first_name'],
            'last_name': name['last_name'],
            'email': email,
            'phone': phone,  # 07XX XXX XXX (local only)
            'whatsapp': whatsapp,  # 07XX XXX XXX (local only)
            'age_bracket': self.generate_age_bracket(),
            'county': self.generate_county(),
            'youth_senator': self.generate_youth_senator(),  # Lizadro Peter
            'youth_woman_rep': self.generate_youth_woman_rep(),  # Nancy Gaichiumia Mwongela
            'contact_preference': self.generate_contact_preference(),  # No contact
            'timestamp': datetime.now().isoformat()
        }
        
        return profile
    
    def get_stats(self):
        return {
            'total_emails_generated': len(self.used_emails),
            'total_phones_generated': len(self.used_phones),
            'total_names_generated': len(self.used_names),
            'storage_file': self.storage_file
        }