#!/usr/bin/env python3
"""
Google Form Bot - FIXED VERSION
- Names always change (never duplicate)
- Emails contain real names
- 5000 votes, 1 hour
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
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("❌ Install: pip install selenium webdriver-manager")
    sys.exit(1)

from data_generator import DataGenerator


class GoogleFormVoteBot:
    def __init__(self, form_url):
        self.form_url = form_url
        self.data_gen = DataGenerator()
        
        self.success_count = 0
        self.fail_count = 0
        self.start_time = None
        
        self.YOUTH_SENATOR = 'Lizadro Peter'
        self.WOMAN_REP = 'Nancy Gaichiumia Mwongela'
        self.COUNTY = 'Meru'
        
        print("\n" + "="*70)
        print("🗳️  GOOGLE FORM BOT - FIXED (UNIQUE NAMES)")
        print("="*70)
        print("Features:")
        print(f"  ✓ Names: Always unique, never repeated")
        print(f"  ✓ Emails: Contain real names (john.mwangi@gmail.com)")
        print(f"  ✓ Senator: {self.YOUTH_SENATOR}")
        print(f"  ✓ Woman Rep: {self.WOMAN_REP}")
        print(f"  ✓ County: {self.COUNTY}")
        print("="*70 + "\n")
    
    def create_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def fill_input_by_label(self, driver, label_text, value):
        """Fill input by finding label text"""
        try:
            # Find label containing text
            labels = driver.find_elements(By.XPATH, f'//span[contains(text(), "{label_text}")]')
            
            for label in labels:
                try:
                    # Go up to parent container and find input
                    parent = label.find_element(By.XPATH, '../../../..')
                    inp = parent.find_element(By.TAG_NAME, 'input')
                    if inp.is_displayed():
                        inp.clear()
                        inp.send_keys(value)
                        time.sleep(random.uniform(0.3, 0.6))
                        return True
                except:
                    continue
            
            # Try direct input with aria-label
            inputs = driver.find_elements(By.XPATH, f'//input[contains(@aria-label, "{label_text}")]')
            for inp in inputs:
                if inp.is_displayed():
                    inp.clear()
                    inp.send_keys(value)
                    time.sleep(random.uniform(0.3, 0.6))
                    return True
            
            return False
        except:
            return False
    
    def select_radio(self, driver, text):
        """Select radio option"""
        try:
            # Find span with text, click parent
            spans = driver.find_elements(By.XPATH, f'//span[contains(text(), "{text}")]')
            
            for span in spans:
                if span.is_displayed():
                    try:
                        # Click the radio container (2-3 levels up)
                        parent = span.find_element(By.XPATH, '../..')
                        parent.click()
                        time.sleep(random.uniform(0.3, 0.6))
                        return True
                    except:
                        span.click()
                        time.sleep(random.uniform(0.3, 0.6))
                        return True
            
            return False
        except:
            return False
    
    def select_dropdown(self, driver, option_text):
        """Select from dropdown"""
        try:
            # Click to open dropdown
            dropdowns = driver.find_elements(By.XPATH, 
                '//div[@role="listbox"] | //div[contains(@class, "MocG8c")]')
            
            for dd in dropdowns:
                if dd.is_displayed():
                    dd.click()
                    time.sleep(random.uniform(0.5, 1))
                    
                    # Find option
                    options = driver.find_elements(By.XPATH, f'//span[contains(text(), "{option_text}")]')
                    for opt in options:
                        if opt.is_displayed():
                            opt.click()
                            time.sleep(random.uniform(0.3, 0.6))
                            return True
            
            return False
        except:
            return False
    
    def click_button(self, driver, text):
        """Click button by text"""
        try:
            buttons = driver.find_elements(By.XPATH, 
                f'//span[text()="{text}"]/ancestor::div[@role="button"] | //div[@role="button"]//span[text()="{text}"]')
            
            for btn in buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(random.uniform(2, 4))
                    return True
            
            return False
        except:
            return False
    
    def submit_vote(self, profile):
        """Submit one complete vote"""
        driver = None
        try:
            driver = self.create_driver()
            
            print(f"\n📝 {profile['full_name']} | {profile['email']}")
            
            driver.get(self.form_url)
            time.sleep(random.uniform(4, 6))
            
            # PAGE 1: Personal Info
            print("  Page 1...")
            
            # Full Name
            if not self.fill_input_by_label(driver, "Full Name", profile['full_name']):
                print("    ⚠️ Name field not found, trying generic...")
                # Try any visible text input
                inputs = driver.find_elements(By.TAG_NAME, 'input')
                for inp in inputs:
                    if inp.is_displayed() and inp.get_attribute('type') == 'text':
                        inp.send_keys(profile['full_name'])
                        break
            
            # Email
            self.fill_input_by_label(driver, "Email", profile['email'])
            
            # WhatsApp
            self.fill_input_by_label(driver, "WhatsApp", profile['whatsapp'])
            
            # Age
            self.select_radio(driver, profile['age_bracket'])
            
            # Next
            if not self.click_button(driver, "Next"):
                return False, "No Next button on Page 1"
            
            # PAGE 2: County
            print("  Page 2...")
            self.select_dropdown(driver, self.COUNTY)
            self.click_button(driver, "Next")
            
            # PAGES 3-6: Fast forward
            for p in range(3, 7):
                print(f"  Page {p}...")
                time.sleep(random.uniform(1, 2))
                self.click_button(driver, "Next")
            
            # PAGE 7: VOTING (CRITICAL)
            print("  Page 7: VOTING")
            
            # Senator: Lizadro Peter
            if not self.select_radio(driver, self.YOUTH_SENATOR):
                self.select_radio(driver, "Lizadro")  # Partial
            
            # Woman Rep: Nancy Gaichiumia Mwongela
            if not self.select_radio(driver, self.WOMAN_REP):
                self.select_radio(driver, "Nancy")  # Partial
            
            self.click_button(driver, "Next")
            
            # PAGES 8-12: Continue
            for p in range(8, 13):
                print(f"  Page {p}...")
                time.sleep(random.uniform(1, 2))
                self.click_button(driver, "Next")
            
            # PAGE 13: Submit
            print("  Page 13: Submit")
            self.select_radio(driver, "not wish to be contacted")
            
            if self.click_button(driver, "Submit"):
                print("  ✅ SUBMITTED")
                time.sleep(random.uniform(3, 5))
                return True, "Success"
            else:
                return False, "Submit failed"
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)[:80]}")
            return False, str(e)
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def run(self, total_votes=5000, duration_seconds=3600):
        """Main execution"""
        print(f"\n{'='*70}")
        print(f"🚀 CAMPAIGN: {total_votes} VOTES IN {duration_seconds/3600:.1f} HOURS")
        print(f"{'='*70}")
        
        stats = self.data_gen.get_stats()
        print(f"Data pool: {stats['total_unique_names']} previous names")
        print(f"Will generate {total_votes} NEW unique names\n")
        
        input("⚠️  Press ENTER to start (Ctrl+C to stop)... ")
        
        delay = duration_seconds / total_votes
        print(f"\n⏱️  Delay: {delay:.3f}s between votes")
        print(f"🚀 Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Expected: {(datetime.now() + timedelta(seconds=duration_seconds)).strftime('%H:%M:%S')}\n")
        
        self.start_time = time.time()
        
        try:
            for i in range(1, total_votes + 1):
                elapsed = time.time() - self.start_time
                if elapsed >= duration_seconds:
                    print(f"\n⏰ Time limit reached")
                    break
                
                # Generate NEW unique profile (name always changes)
                profile = self.data_gen.generate_complete_profile()
                
                # Submit
                success, msg = self.submit_vote(profile)
                
                if success:
                    self.success_count += 1
                else:
                    self.fail_count += 1
                
                # Progress every 10 votes
                if i % 10 == 0 or i == 1:
                    rate = i / elapsed * 3600 if elapsed > 0 else 0
                    eta = (datetime.now() + timedelta(seconds=(total_votes-i) * delay)).strftime('%H:%M:%S')
                    
                    print(f"\n[{i:4d}/{total_votes}] Success: {self.success_count} | Fail: {self.fail_count} | Rate: {rate:.0f}/hr | ETA: {eta}")
                    print(f"  Latest: {profile['full_name']} | {profile['email'][:40]}")
                
                # Delay
                next_vote = self.start_time + (i * delay)
                sleep_time = next_vote - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopped by user")
        
        # Report
        total_time = time.time() - self.start_time
        total = self.success_count + self.fail_count
        
        print(f"\n{'='*70}")
        print(f"📊 FINAL REPORT")
        print(f"{'='*70}")
        print(f"Duration: {total_time:.1f}s")
        print(f"Successful: {self.success_count:,}")
        print(f"Failed: {self.fail_count:,}")
        print(f"Success rate: {self.success_count/total*100:.1f}%" if total > 0 else "N/A")
        print(f"\n🎯 All {self.success_count} votes for:")
        print(f"   Senator: {self.YOUTH_SENATOR}")
        print(f"   Woman Rep: {self.WOMAN_REP}")
        
        final_stats = self.data_gen.get_stats()
        print(f"\n📧 Unique data generated: {final_stats['total_unique_names']} names, {final_stats['total_emails']} emails")
        print(f"{'='*70}")
        
        return self.fail_count == 0


def main():
    parser = argparse.ArgumentParser(
        description='Google Form Bot - Unique Names Every Vote',
        epilog="Names change every time, emails contain real names"
    )
    
    parser.add_argument('--url', '-u', required=True, help='Google Form URL')
    parser.add_argument('--votes', '-n', type=int, default=5000, help='Total votes')
    parser.add_argument('--duration', '-d', type=int, default=3600, help='Seconds')
    
    args = parser.parse_args()
    
    bot = GoogleFormVoteBot(form_url=args.url)
    success = bot.run(total_votes=args.votes, duration_seconds=args.duration)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()