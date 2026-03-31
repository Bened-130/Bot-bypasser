import random
import json
import os
from datetime import datetime


class DataGenerator:
    def __init__(self, storage_file='used_data.json'):
        self.storage_file = storage_file
        self.used_emails = set()
        self.used_phones = set()
        self.used_names = set()  # Track used full names
        self.used_name_combinations = set()  # Track first+last combinations
        
        self.load_used_data()
        
        # Kenyan first names
        self.first_names = [
            'John', 'Mary', 'Peter', 'Grace', 'James', 'Esther', 'Michael', 'Jane',
            'Daniel', 'Lucy', 'David', 'Sarah', 'Joseph', 'Elizabeth', 'Paul', 'Ann',
            'Stephen', 'Margaret', 'George', 'Catherine', 'Patrick', 'Ruth', 'Francis',
            'Christine', 'Samuel', 'Joyce', 'Robert', 'Nancy', 'Benjamin', 'Lydia',
            'Emmanuel', 'Martha', 'Simon', 'Betty', 'Thomas', 'Veronica', 'Andrew',
            'Regina', 'Moses', 'Dorothy', 'Joshua', 'Rebecca', 'Abraham', 'Phyllis',
            'Isaac', 'Rachel', 'Jacob', 'Hannah', 'Gabriel', 'Deborah', 'Jonathan',
            'Beatrice', 'Timothy', 'Gladys', 'Philip', 'Agnes', 'Nicholas', 'Julia',
            'White', 'Lizadro', 'Cliffod', 'Alex', 'Jackline', 'Shalon', 'Ireen',
            'Kevin', 'Brian', 'Anthony', 'Charles', 'Dennis', 'Edward', 'Fredrick',
            'Gerald', 'Henry', 'Ian', 'Jared', 'Kennedy', 'Leonard', 'Martin',
            'Allan', 'Benson', 'Cyrus', 'Dominic', 'Eric', 'Felix', 'Geoffrey',
            'Harrison', 'Ivan', 'Jamie', 'Kelvin', 'Lawrence', 'Morris', 'Nelson',
            'Oliver', 'Patrick', 'Quincy', 'Ryan', 'Stanley', 'Trevor', 'Ulysses',
            'Victor', 'Wallace', 'Xavier', 'Yvonne', 'Zachary', 'Adrian', 'Bruce',
            'Caleb', 'Derek', 'Eugene', 'Frank', 'Gideon', 'Harvey', 'Irene',
            'Janet', 'Karen', 'Laura', 'Monica', 'Naomi', 'Olivia', 'Priscilla',
            'Queen', 'Rose', 'Susan', 'Teresa', 'Unice', 'Vivian', 'Wendy',
            'Abigail', 'Bridget', 'Caroline', 'Diana', 'Emily', 'Faith', 'Gladys',
            'Helen', 'Ivy', 'Jackie', 'Kate', 'Lilian', 'Mildred', 'Nina',
            'Ophelia', 'Patricia', 'Quinter', 'Rita', 'Stella', 'Tracy', 'Ursula',
            'Vanessa', 'Winnie', 'Xena', 'Yolanda', 'Zara', 'Aaron', 'Bob',
            'Colin', 'Duncan', 'Ellis', 'Finn', 'Graham', 'Howard', 'Irving'
        ]
        
        # Kenyan last names
        self.last_names = [
            'Mwangi', 'Wanjiku', 'Otieno', 'Wambui', 'Kamau', 'Njeri', 'Ochieng',
            'Wangari', 'Njoroge', 'Wairimu', 'Omondi', 'Wanjiru', 'Kariuki', 'Wangechi',
            'Kipchirchir', 'Jepchirchir', 'Mutua', 'Kyalo', 'Muli', 'Waweru',
            'Githinji', 'Waithaka', 'Mbugua', 'Ndungu', 'Wanjala', 'Oduor', 'Akinyi',
            'Okoth', 'Auma', 'Onyango', 'Oloo', 'Adhiambo', 'Were', 'Ouma',
            'Muriithi', 'Macharia', 'Kinyua', 'Gachanja', 'Muchiri', 'Mweteri',
            'Kathuri', 'Mukami', 'Kathurima', 'Mbiti', 'Nkirote',
            'Gaichiumia', 'Mwongela', 'Kinya', 'Mwiti', 'Murithi', 'Kirimi',
            'Muthomi', 'Mukangu', 'Thuranira', 'Karema', 'Mbogori', 'Muketha',
            'Kathambi', 'Muroki', 'Kiogora', 'Mwitari', 'Kinyua', 'Muriuki',
            'Mwangangi', 'Mutegi', 'Mukundi', 'Muthuri', 'Muriithi', 'Mwangi',
            'Kamande', 'Muchemi', 'Mukiibi', 'Mugambi', 'Muriuki', 'Mwaniki',
            'Mutuku', 'Musyoka', 'Muthama', 'Munyao', 'Mutiso', 'Mulei',
            'Muthoka', 'Muli', 'Munyoki', 'Musembi', 'Mutua', 'Muthui',
            'Mwendwa', 'Mwikya', 'Mwinzi', 'Mwalili', 'Muthangya', 'Mutie',
            'Musinga', 'Muthoka', 'Mwakazi', 'Muthama', 'Mwanzia', 'Muthoka'
        ]
        
        self.domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'mail.com', 'protonmail.com', 'yandex.com',
            'zoho.com', 'aol.com', 'gmx.com', 'fastmail.com'
        ]
        
    def load_used_data(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.used_emails = set(data.get('emails', []))
                    self.used_phones = set(data.get('phones', []))
                    self.used_names = set(data.get('names', []))
                    self.used_name_combinations = set(data.get('name_combinations', []))
                print(f"Loaded {len(self.used_names)} used names, {len(self.used_emails)} emails")
            except Exception as e:
                print(f"Could not load: {e}")
    
    def save_used_data(self):
        data = {
            'emails': list(self.used_emails),
            'phones': list(self.used_phones),
            'names': list(self.used_names),
            'name_combinations': list(self.used_name_combinations),
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save: {e}")
    
    def generate_unique_name(self):
        """
        Generate truly unique name that has NEVER been used before
        Tries 10,000 combinations before adding numbers
        """
        max_attempts = 10000
        
        for attempt in range(max_attempts):
            first = random.choice(self.first_names)
            last = random.choice(self.last_names)
            
            full_name = f"{first} {last}"
            name_combo = f"{first}|{last}"  # Track combinations separately
            
            # Check if this exact name OR this first+last combo was used
            if full_name not in self.used_names and name_combo not in self.used_name_combinations:
                self.used_names.add(full_name)
                self.used_name_combinations.add(name_combo)
                self.save_used_data()
                return {
                    'full_name': full_name,
                    'first_name': first,
                    'last_name': last
                }
        
        # If all combinations exhausted, add middle initial or number
        print(f"Adding suffix to ensure uniqueness (attempt {max_attempts})")
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        middle = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        full_name = f"{first} {middle}. {last}"
        
        # Ensure even this is unique
        counter = 1
        original_full = full_name
        while full_name in self.used_names:
            full_name = f"{original_full} {counter}"
            counter += 1
        
        self.used_names.add(full_name)
        self.save_used_data()
        
        return {
            'full_name': full_name,
            'first_name': first,
            'last_name': last
        }
    
    def generate_email_with_name(self, name):
        """
        Generate email that CONTAINS the actual name (not random numbers)
        Format: firstname.lastname@domain or firstnamelastname@domain
        """
        first = name['first_name'].lower()
        last = name['last_name'].lower()
        
        # Clean names (remove special chars)
        first_clean = ''.join(c for c in first if c.isalnum())
        last_clean = ''.join(c for c in last if c.isalnum())
        
        max_attempts = 1000
        
        for _ in range(max_attempts):
            # Real name-based formats (NO random numbers as username)
            formats = [
                f"{first_clean}.{last_clean}",           # john.mwangi
                f"{first_clean}{last_clean}",              # johnmwangi
                f"{first_clean[0]}{last_clean}",           # jmwangi
                f"{first_clean}{last_clean[0]}",           # johnm
                f"{first_clean}_{last_clean}",             # john_mwangi
                f"{first_clean}.{last_clean[0]}",          # john.m
                f"{first_clean[0]}.{last_clean}",          # j.mwangi
                f"{last_clean}.{first_clean}",             # mwangi.john
                f"{first_clean}{last_clean[:3]}",          # johnmwa
                f"{first_clean[:3]}{last_clean}",          # johmwangi
            ]
            
            # Occasionally add a small number if needed for uniqueness
            if random.random() < 0.3:  # 30% chance to add year/number
                year = random.choice([1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003])
                formats.append(f"{first_clean}.{last_clean}{year}")  # john.mwangi1998
                formats.append(f"{first_clean}{last_clean}{random.randint(1,99)}")
            
            username = random.choice(formats)
            domain = random.choice(self.domains)
            email = f"{username}@{domain}"
            
            # Validate
            if len(email) > 60 or '..' in email or email.startswith('.') or email.endswith('.'):
                continue
            
            if email not in self.used_emails:
                self.used_emails.add(email)
                self.save_used_data()
                return email
        
        # Fallback with guaranteed unique timestamp
        timestamp = datetime.now().strftime('%S%f')[-6:]  # Last 6 digits of microseconds
        email = f"{first_clean}.{last_clean}.{timestamp}@{random.choice(self.domains)}"
        self.used_emails.add(email)
        self.save_used_data()
        return email
    
    def generate_phone(self):
        """Generate unique Kenyan phone"""
        max_attempts = 10000
        
        for _ in range(max_attempts):
            safaricom = ['070', '071', '072', '0740', '0741', '0742', '0743', '0745', '0746', '0748', '011']
            airtel = ['073', '075', '078', '010']
            telkom = ['077', '076']
            
            all_prefixes = safaricom + airtel + telkom
            prefix = random.choice(all_prefixes)
            
            remaining = 9 - len(prefix)
            suffix = ''.join(random.choices('0123456789', k=remaining))
            
            phone = f"{prefix}{suffix}"
            
            if len(phone) != 10 or not phone.startswith(('07', '01')):
                continue
            
            if phone not in self.used_phones:
                self.used_phones.add(phone)
                self.save_used_data()
                return phone
        
        raise Exception("Could not generate unique phone")
    
    def generate_whatsapp(self):
        """WhatsApp in local format"""
        return self.generate_phone()
    
    def generate_age_bracket(self):
        """Age bracket from form: 18-24, 25-30, 31-35"""
        brackets = ['18-24', '25-30', '31-35']
        weights = [0.4, 0.35, 0.25]
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
        """FIXED: No contact"""
        return "No, I do not wish to be contacted"
    
    def generate_complete_profile(self):
        """Generate complete unique profile"""
        # CRITICAL: Always get a NEW unique name
        name = self.generate_unique_name()
        
        # Email based on that name (not random)
        email = self.generate_email_with_name(name)
        
        phone = self.generate_phone()
        whatsapp = self.generate_whatsapp()
        
        profile = {
            'full_name': name['full_name'],
            'first_name': name['first_name'],
            'last_name': name['last_name'],
            'email': email,  # Contains real name: john.mwangi@gmail.com
            'phone': phone,
            'whatsapp': whatsapp,
            'age_bracket': self.generate_age_bracket(),
            'county': self.generate_county(),
            'youth_senator': self.generate_youth_senator(),
            'youth_woman_rep': self.generate_youth_woman_rep(),
            'contact_preference': self.generate_contact_preference(),
            'timestamp': datetime.now().isoformat()
        }
        
        return profile
    
    def get_stats(self):
        return {
            'total_unique_names': len(self.used_names),
            'total_emails': len(self.used_emails),
            'total_phones': len(self.used_phones),
            'storage_file': self.storage_file
        }


# Test
if __name__ == '__main__':
    gen = DataGenerator()
    
    print("Testing - 10 Unique Profiles")
    print("=" * 60)
    
    for i in range(10):
        profile = gen.generate_complete_profile()
        print(f"\n{i+1}. Name: {profile['full_name']}")
        print(f"   Email: {profile['email']}")
        print(f"   Phone: {profile['phone']}")
        
        # Verify email contains name parts
        first = profile['first_name'].lower()
        last = profile['last_name'].lower()
        email_user = profile['email'].split('@')[0]
        
        if first[:3] in email_user or last[:3] in email_user:
            print(f"Email contains name")
        else:
            print(f"Email may not contain name")
    
    print("\n" + "=" * 60)
    stats = gen.get_stats()
    print(f"Total unique names generated: {stats['total_unique_names']}")
    print(f"Total unique emails: {stats['total_emails']}")