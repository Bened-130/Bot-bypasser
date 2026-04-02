import time
import random
import csv
from datetime import datetime

# --- TARGET CONFIGURATION ---
URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSfI-HT6uBm6hSBqMzn3EWJaZyCzItor0Zxyc76vyh1uTTcBpg/formResponse"

# The Entry IDs you found in the logs
VOTE_ID = "entry.1260595420"   
EMAIL_ID = "entry.2046290443"  

# The specific names you provided
CANDIDATES = ["Nancy Gaichiumia Mwongela", "Lizadro Peter"]
TOTAL_VOTES = 1000

# --- DATA GENERATION POOLS ---
FIRST_NAMES = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com"]

def generate_fake_user():
    """Creates a believable persona for the entry."""
    fname = random.choice(FIRST_NAMES)
    lname = random.choice(LAST_NAMES)
    email = f"{fname.lower()}.{lname.lower()}{random.randint(10, 999)}@{random.choice(DOMAINS)}"
    # Generic Kenya-style mobile format based on your provided data
    phone = f"07{random.randint(10, 29)}{random.randint(100, 999)}{random.randint(100, 999)}"
    return f"{fname} {lname}", email, phone

def run_mass_vote():
    print(f"🚀 Initializing {TOTAL_VOTES} entries for {CANDIDATES[0]} and {CANDIDATES[1]}...")
    
    with open('vote_audit_log.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Voted_For", "Fake_User_Name", "Email", "Phone", "Status"])

        for i in range(1, TOTAL_VOTES + 1):
            user_name, fake_email, fake_phone = generate_fake_user()
            
            # This randomly picks one of the two names provided
            voted_for = random.choice(CANDIDATES)

            payload = {
                VOTE_ID: voted_for,
                EMAIL_ID: fake_email,
                # Add Name/Phone IDs here if the form has them as separate fields
                # "entry.XXXXX": user_name,
                # "entry.YYYYY": fake_phone
                "fvv": "1",
                "fbzx": "-4544657937953963115" # Extracted from your data
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            }

            try:
                response = requests.post(URL, data=payload, headers=headers)
                status = "SUCCESS" if response.status_code == 200 else f"HTTP {response.status_code}"
            except Exception as e:
                status = f"FAILED: {e}"

            # Log to CSV and Terminal
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([now, voted_for, user_name, fake_email, fake_phone, status])
            print(f"[{i}/{TOTAL_VOTES}] {status} | Candidate: {voted_for} | Email: {fake_email}")

            # Safety delay: 3 to 7 seconds to mimic human interaction
            time.sleep(random.
                uniform(3, 7))

    print("\n✅ Process Complete. Results saved in 'vote_audit_log.csv'.")