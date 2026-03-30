#!/usr/bin/env python3
"""
Google Form Vote Bot - 13 Page Complete Handler
- Page 1: Name, Email, WhatsApp (local format), Age
- Page 2: County = Meru
- Page 7: Lizadro Peter (Senator), Nancy Gaichiumia Mwongela (Woman Rep)
- Page 13: No contact + Submit
- NO international numbers
"""

import time
import random
import argparse
import sys
from datetime import datetime, timedelta

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.action_chains import ActionChains
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("❌ Install: pip install selenium webdriver-manager")
    sys.exit(1)

from data_generator import DataGenerator


class GoogleFormVoteBot:
    def __init__(self, form_url):
        self.form_url = form_url
        self.data_gen = DataGenerator()
        
        # Statistics
        self.success_count = 0
        self.fail_count = 0
        self.start_time = None
        
        # FIXED SELECTIONS from screenshots
        self.YOUTH_SENATOR = 'Lizadro Peter'
        self.WOMAN_REP = 'Nancy Gaichiumia Mwongela'
        self.COUNTY = 'Meru'
        self.CONTACT = 'No, I do not wish to be contacted'
        
        print("\n" + "="*70)
        print("🗳️  GOOGLE FORM BOT - 13 PAGE COMPLETE")
        print("="*70)
        print("FIXED SELECTIONS:")
        print(f"  Youth Senator: {self.YOUTH_SENATOR}")
        print(f"  Woman Rep: {self.WOMAN_REP}")
        print(f"  County: {self.COUNTY}")
        print(f"  Contact: {self.CONTACT}")
        print(f"  Phone Format: Local Kenyan (07XX XXX XXX)")
        print("="*70 + "\n")
    
    def create_driver(self):
        """Create stealth Chrome driver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def fill_text_input(self, driver, placeholder_contains, value):
        """Fill text input by placeholder or label"""
        try:
            # Try by placeholder
            xpath = f'//input[contains(@placeholder, "{placeholder_contains}") or contains(@aria-label, "{placeholder_contains}")]'
            inputs = driver.find_elements(By.XPATH, xpath)
            
            for inp in inputs:
                if inp.is_displayed():
                    inp.clear()
                    inp.send_keys(value)
                    time.sleep(random.uniform(0.2, 0.5))
                    return True
            
            # Try by parent label
            labels = driver.find_elements(By.XPATH, f'//span[contains(text(), "{placeholder_contains}")]')
            for label in labels:
                try:
                    parent = label.find_element(By.XPATH, '../../..')
                    inp = parent.find_element(By.TAG_NAME, 'input')
                    inp.clear()
                    inp.send_keys(value)
                    time.sleep(random.uniform(0.2, 0.5))
                    return True
                except:
                    pass
            
            return False
        except:
            return False
    
    def select_radio(self, driver, option_text):
        """Select radio button by option text"""
        try:
            # Find label with text, click it
            labels = driver.find_elements(By.XPATH, 
                f'//span[contains(text(), "{option_text}") or text()="{option_text}"]')
            
            for label in labels:
                if label.is_displayed():
                    try:
                        # Click the div/span that acts as radio
                        parent = label.find_element(By.XPATH, '../..')
                        parent.click()
                        time.sleep(random.uniform(0.3, 0.6))
                        return True
                    except:
                        # Try clicking label directly
                        label.click()
                        time.sleep(random.uniform(0.3, 0.6))
                        return True
            
            return False
        except:
            return False
    
    def select_dropdown(self, driver, option_text):
        """Select from dropdown"""
        try:
            # Click dropdown to open
            dropdowns = driver.find_elements(By.XPATH, 
                '//div[@role="listbox"] | //div[contains(@class, "MocG8c")] | //div[contains(@class, "quantumWizMenuPaperselectOption")]')
            
            for dd in dropdowns:
                if dd.is_displayed():
                    dd.click()
                    time.sleep(random.uniform(0.5, 1))
                    
                    # Find and click option
                    options = driver.find_elements(By.XPATH, 
                        f'//span[contains(text(), "{option_text}") or text()="{option_text}"]')
                    
                    for opt in options:
                        if opt.is_displayed():
                            opt.click()
                            time.sleep(random.uniform(0.3, 0.6))
                            return True
            
            return False
        except:
            return False
    
    def click_next(self, driver):
        """Click Next button"""
        try:
            buttons = driver.find_elements(By.XPATH, 
                '//span[text()="Next"]/ancestor::div[@role="button"] | //div[@role="button"]//span[text()="Next"]')
            
            for btn in buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(random.uniform(2, 4))
                    return True
            
            return False
        except:
            return False
    
    def click_submit(self, driver):
        """Click Submit button"""
        try:
            buttons = driver.find_elements(By.XPATH, 
                '//span[text()="Submit"]/ancestor::div[@role="button"] | //div[@role="button"]//span[text()="Submit"]')
            
            for btn in buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(random.uniform(3, 5))
                    return True
            
            return False
        except:
            return False
    
    def submit_one_vote(self, profile):
        """Submit complete 13-page form"""
        driver = None
        try:
            driver = self.create_driver()
            
            print(f"\n📝 Vote: {profile['email']}")
            
            # Load form
            driver.get(self.form_url)
            time.sleep(random.uniform(3, 5))
            
            # ===== PAGE 1: Personal Info =====
            print("  Page 1: Personal info")
            
            # Full Name
            if not self.fill_text_input(driver, "Full Name", profile['full_name']):
                print("    ⚠️ Could not fill name")
            
            # Email
            if not self.fill_text_input(driver, "Email", profile['email']):
                print("    ⚠️ Could not fill email")
            
            # WhatsApp (local format 07XX XXX XXX)
            if not self.fill_text_input(driver, "WhatsApp", profile['whatsapp']):
                print("    ⚠️ Could not fill WhatsApp")
            
            # Age Bracket
            if not self.select_radio(driver, profile['age_bracket']):
                print("    ⚠️ Could not select age")
            
            # Next
            if not self.click_next(driver):
                print("    ❌ Could not advance from Page 1")
                return False, "Stuck on Page 1"
            
            # ===== PAGE 2: County =====
            print("  Page 2: County")
            
            # Select Meru from dropdown
            if not self.select_dropdown(driver, self.COUNTY):
                # Try radio if dropdown fails
                if not self.select_radio(driver, self.COUNTY):
                    print("    ⚠️ Could not select Meru")
            
            # Next
            if not self.click_next(driver):
                print("    ❌ Could not advance from Page 2")
            
            # ===== PAGES 3-6: Unknown (fast forward) =====
            for page_num in range(3, 7):
                print(f"  Page {page_num}: Skipping/Next")
                
                # Try to fill any visible text fields with name
                try:
                    inputs = driver.find_elements(By.TAG_NAME, 'input')
                    for inp in inputs:
                        if inp.is_displayed() and inp.get_attribute('type') == 'text':
                            inp.send_keys(profile['full_name'])
                except:
                    pass
                
                if not self.click_next(driver):
                    print(f"    ⚠️ Could not advance from Page {page_num}")
            
            # ===== PAGE 7: VOTING (CRITICAL) =====
            print("  Page 7: VOTING")
            
            # Youth Senator: Lizadro Peter
            senator_selected = self.select_radio(driver, self.YOUTH_SENATOR)
            if senator_selected:
                print(f"    ✅ Senator: {self.YOUTH_SENATOR}")
            else:
                # Try partial
                senator_selected = self.select_radio(driver, "Lizadro")
                if senator_selected:
                    print(f"    ✅ Senator: Lizadro (partial match)")
                else:
                    print(f"    ❌ Could not select {self.YOUTH_SENATOR}")
            
            # Youth Woman Rep: Nancy Gaichiumia Mwongela
            woman_selected = self.select_radio(driver, self.WOMAN_REP)
            if woman_selected:
                print(f"    ✅ Woman Rep: {self.WOMAN_REP}")
            else:
                # Try partial
                woman_selected = self.select_radio(driver, "Nancy")
                if not woman_selected:
                    woman_selected = self.select_radio(driver, "Mwongela")
                if woman_selected:
                    print(f"    ✅ Woman Rep: Nancy/Mwongela (partial)")
                else:
                    print(f"    ❌ Could not select {self.WOMAN_REP}")
            
            # Next
            if not self.click_next(driver):
                print("    ❌ Could not advance from Page 7")
            
            # ===== PAGES 8-12: Unknown =====
            for page_num in range(8, 13):
                print(f"  Page {page_num}: Skipping/Next")
                
                # Fill any text fields
                try:
                    inputs = driver.find_elements(By.TAG_NAME, 'input')
                    for inp in inputs:
                        if inp.is_displayed() and inp.get_attribute('type') == 'text':
                            inp.send_keys(profile['full_name'])
                except:
                    pass
                
                if not self.click_next(driver):
                    print(f"    ⚠️ Could not advance from Page {page_num}")
            
            # ===== PAGE 13: Contact + Submit =====
            print("  Page 13: Final")
            
            # Select "No, I do not wish to be contacted"
            no_contact = self.select_radio(driver, "No, I do not wish")
            if not no_contact:
                no_contact = self.select_radio(driver, "not wish to be contacted")
            if no_contact:
                print("    ✅ Selected: No contact")
            else:
                print("    ⚠️ Could not select no contact")
            
            # Submit
            if self.click_submit(driver):
                print("  ✅ SUBMITTED")
                time.sleep(random.uniform(2, 4))
                
                # Verify submission
                current_url = driver.current_url
                if 'formResponse' in current_url or 'submit' in current_url.lower():
                    return True, "Success"
                else:
                    return True, "Likely success"
            else:
                print("  ❌ Submit failed")
                return False, "Submit button not found"
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)[:100]}")
            return False, str(e)
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def run(self, total_votes=5000, duration_seconds=3600):
        """Execute voting campaign"""
        
        print(f"\n{'='*70}")
        print(f"🚀 CAMPAIGN: {total_votes} VOTES")
        print(f"{'='*70}")
        print(f"Target: {self.form_url}")
        print(f"Duration: {duration_seconds}s ({duration_seconds/3600:.2f} hours)")
        print(f"Rate: 1 vote every {duration_seconds/total_votes:.3f}s")
        print(f"{'='*70}\n")
        
        stats = self.data_gen.get_stats()
        print(f"📊 Data pool: {stats['total_emails_generated']} previous")
        print(f"🆕 Generating {total_votes} new unique profiles\n")
        
        input("⚠️  Press ENTER to start (Ctrl+C to stop)... ")
        
        delay = duration_seconds / total_votes
        print(f"\n⏱️  Delay: {delay:.3f}s between votes")
        print(f"🚀 Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Expected finish: {(datetime.now() + timedelta(seconds=duration_seconds)).strftime('%H:%M:%S')}\n")
        
        self.start_time = time.time()
        
        try:
            for vote_num in range(1, total_votes + 1):
                elapsed = time.time() - self.start_time
                if elapsed >= duration_seconds:
                    print(f"\n⏰ Time limit at vote {vote_num-1}")
                    break
                
                # Generate profile
                profile = self.data_gen.generate_complete_profile()
                
                # Verify FIXED selections
                assert profile['youth_senator'] == self.YOUTH_SENATOR
                assert profile['youth_woman_rep'] == self.WOMAN_REP
                assert profile['county'] == self.COUNTY
                
                # Submit
                success, msg = self.submit_one_vote(profile)
                
                if success:
                    self.success_count += 1
                    status = "✅"
                else:
                    self.fail_count += 1
                    status = "❌"
                
                # Progress every 10 votes
                if vote_num % 10 == 0 or vote_num == 1:
                    current_rate = vote_num / elapsed * 3600 if elapsed > 0 else 0
                    eta = (datetime.now() + timedelta(seconds=(total_votes-vote_num) * delay)).strftime('%H:%M:%S')
                    
                    print(f"\n[{vote_num:4d}/{total_votes}] {status} | "
                          f"Success: {self.success_count} | Fail: {self.fail_count} | "
                          f"Rate: {current_rate:.0f}/hr | ETA: {eta}")
                    print(f"  Latest: {profile['email'][:35]} | {profile['whatsapp']}")
                
                # Delay
                next_vote = self.start_time + (vote_num * delay)
                sleep_time = next_vote - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopped by user")
        
        # Final report
        self._print_report()
        return self.fail_count == 0
    
    def _print_report(self):
        """Print final results"""
        total_time = time.time() - self.start_time
        total = self.success_count + self.fail_count
        
        print(f"\n{'='*70}")
        print(f"📊 FINAL REPORT")
        print(f"{'='*70}")
        print(f"⏱️  Duration: {total_time:.1f}s ({total_time/60:.1f}min)")
        print(f"✅ Successful: {self.success_count:,}")
        print(f"❌ Failed: {self.fail_count:,}")
        print(f"📈 Success rate: {self.success_count/total*100:.2f}%" if total > 0 else "N/A")
        
        print(f"\n🎯 FIXED SELECTIONS DELIVERED:")
        print(f"   Senator: {self.YOUTH_SENATOR} - {self.success_count} votes")
        print(f"   Woman Rep: {self.WOMAN_REP} - {self.success_count} votes")
        print(f"   County: {self.COUNTY}")
        
        stats = self.data_gen.get_stats()
        print(f"\n📧 Unique data: {len(self.data_gen.used_emails)} emails, {len(self.data_gen.used_phones)} phones")
        print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(
        description='Google Form Bot - Lizadro Peter & Nancy Gaichiumia Mwongela',
        epilog="""
EXAMPLES:
  python google_form_bot.py --url "https://docs.google.com/forms/d/e/.../viewform" --votes 5000
  python google_form_bot.py --url "YOUR_FORM_URL" --votes 100 --duration 600
        """
    )
    
    parser.add_argument('--url', '-u', required=True, help='Google Form URL')
    parser.add_argument('--votes', '-n', type=int, default=5000, help='Total votes')
    parser.add_argument('--duration', '-d', type=int, default=3600, help='Duration seconds')
    
    args = parser.parse_args()
    
    bot = GoogleFormVoteBot(form_url=args.url)
    success = bot.run(total_votes=args.votes, duration_seconds=args.duration)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()