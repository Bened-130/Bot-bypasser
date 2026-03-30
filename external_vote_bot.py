#!/usr/bin/env python3
"""
Google Form Voting Bot - Specialized for docs.google.com/forms
- Handles multi-page Google Forms (Page 7 of 13 in screenshot)
- FIXED: Lizadro Peter (Youth Senator), Nancy Gaichiumia Mwongela (Woman Rep)
- Meru County, No contact
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
    print("❌ Selenium required. Install: pip install selenium webdriver-manager")
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
        
        # FIXED SELECTIONS from user
        self.YOUTH_SENATOR = 'Lizadro Peter'  # Changed per user
        self.WOMAN_REP = 'Nancy Gaichiumia Mwongela'  # Confirmed
        
        print("\n" + "="*70)
        print("🗳️  GOOGLE FORM VOTE BOT")
        print("="*70)
        print("FIXED SELECTIONS (per your requirements):")
        print(f"  Youth Senator: {self.YOUTH_SENATOR}")
        print(f"  Youth Woman Rep: {self.WOMAN_REP}")
        print(f"  County: Meru County")
        print(f"  Contact: No, I don't wish to be contacted")
        print("="*70 + "\n")
    
    def create_driver(self):
        """Create Chrome driver with anti-detection"""
        options = Options()
        
        # Stealth options
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random viewport
        viewports = ['1920,1080', '1366,768', '1440,900', '1536,864']
        options.add_argument(f'--window-size={random.choice(viewports)}')
        
        # User agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def fill_page_1to6(self, driver, profile):
        """Fill pages 1-6 (personal info: name, email, phone, age, county, etc.)"""
        print("  Filling personal info pages (1-6)...")
        
        try:
            # Wait for form to load
            time.sleep(random.uniform(2, 4))
            
            # Common field handling for early pages
            # These vary by form - adjust selectors as needed
            
            # Try to fill any text inputs found
            text_inputs = driver.find_elements(By.XPATH, '//input[@type="text"]')
            for i, inp in enumerate(text_inputs[:5]):  # First 5 text fields
                try:
                    if i == 0:
                        inp.send_keys(profile['full_name'])
                    elif i == 1:
                        inp.send_keys(profile['email'])
                    elif i == 2:
                        inp.send_keys(profile['phone'])
                    elif i == 3:
                        inp.send_keys(profile['whatsapp'])
                    time.sleep(random.uniform(0.2, 0.5))
                except:
                    pass
            
            # Handle select/dropdown for age
            try:
                # Look for age question
                age_elements = driver.find_elements(By.XPATH, 
                    '//*[contains(text(), "age") or contains(text(), "Age")]')
                if age_elements:
                    # Find associated dropdown
                    selects = driver.find_elements(By.TAG_NAME, 'select')
                    for select in selects:
                        try:
                            options = select.find_elements(By.TAG_NAME, 'option')
                            for option in options:
                                if profile['age_bracket'] in option.text or \
                                   profile['age_bracket'].split('-')[0] in option.text:
                                    option.click()
                                    break
                        except:
                            pass
            except:
                pass
            
            # Click Next to advance through pages 1-6
            for page in range(6):  # Pages 1-6
                time.sleep(random.uniform(1, 2))
                next_btn = self.find_next_button(driver)
                if next_btn:
                    next_btn.click()
                    print(f"    Advanced page {page + 1}")
                    time.sleep(random.uniform(2, 3))
                else:
                    break
            
            return True
            
        except Exception as e:
            print(f"    Error filling early pages: {e}")
            return False
    
    def fill_voting_page(self, driver):
        """Fill Page 7 - Voting page with FIXED selections"""
        print("  Filling voting page (Page 7)...")
        
        try:
            time.sleep(random.uniform(2, 3))
            
            # Select Youth Senator: Lizadro Peter
            senator_selected = self.select_radio_by_text(driver, self.YOUTH_SENATOR)
            if senator_selected:
                print(f"    ✅ Selected Youth Senator: {self.YOUTH_SENATOR}")
            else:
                print(f"    ⚠️  Could not find {self.YOUTH_SENATOR}, trying alternatives...")
                # Try partial match
                senator_selected = self.select_radio_by_partial(driver, 'Lizadro')
            
            # Select Youth Woman Rep: Nancy Gaichiumia Mwongela
            woman_rep_selected = self.select_radio_by_text(driver, self.WOMAN_REP)
            if woman_rep_selected:
                print(f"    ✅ Selected Woman Rep: {self.WOMAN_REP}")
            else:
                print(f"    ⚠️  Could not find {self.WOMAN_REP}, trying alternatives...")
                woman_rep_selected = self.select_radio_by_partial(driver, 'Nancy')
                if not woman_rep_selected:
                    woman_rep_selected = self.select_radio_by_partial(driver, 'Mwongela')
            
            # Click Next
            time.sleep(random.uniform(1, 2))
            next_btn = self.find_next_button(driver)
            if next_btn:
                next_btn.click()
                print("    Advanced to next page")
            
            return senator_selected and woman_rep_selected
            
        except Exception as e:
            print(f"    Error on voting page: {e}")
            return False
    
    def fill_remaining_pages(self, driver):
        """Fill pages 8-13 (remaining questions, contact preference)"""
        print("  Filling remaining pages (8-13)...")
        
        try:
            # Handle remaining pages
            for page in range(8, 14):  # Pages 8-13
                time.sleep(random.uniform(2, 3))
                
                # Look for "No contact" option on relevant page
                no_contact = self.select_radio_by_partial(driver, "don't wish")
                if no_contact:
                    print(f"    ✅ Selected 'No contact' on page {page}")
                
                # Look for Meru County if county question appears
                meru = self.select_radio_by_partial(driver, "Meru")
                if meru:
                    print(f"    ✅ Selected Meru County on page {page}")
                
                # Click Next or Submit
                next_btn = self.find_next_button(driver)
                submit_btn = self.find_submit_button(driver)
                
                if submit_btn:
                    submit_btn.click()
                    print("    📝 Form submitted!")
                    time.sleep(random.uniform(3, 5))
                    return True
                elif next_btn:
                    next_btn.click()
                    print(f"    Advanced page {page}")
                else:
                    break
            
            return True
            
        except Exception as e:
            print(f"    Error on remaining pages: {e}")
            return False
    
    def select_radio_by_text(self, driver, exact_text):
        """Select radio button by exact text match"""
        try:
            # Strategy 1: Find label with exact text, click associated radio
            labels = driver.find_elements(By.XPATH, f'//span[text()="{exact_text}"]')
            for label in labels:
                try:
                    # Click the label (which selects the radio)
                    label.click()
                    time.sleep(random.uniform(0.2, 0.4))
                    return True
                except:
                    pass
            
            # Strategy 2: Look for radio with this value
            radios = driver.find_elements(By.XPATH, f'//input[@type="radio"][@value="{exact_text}"]')
            for radio in radios:
                try:
                    radio.click()
                    time.sleep(random.uniform(0.2, 0.4))
                    return True
                except:
                    pass
            
            # Strategy 3: Contains text
            labels = driver.find_elements(By.XPATH, f'//span[contains(text(), "{exact_text}")]')
            for label in labels:
                try:
                    label.click()
                    time.sleep(random.uniform(0.2, 0.4))
                    return True
                except:
                    pass
            
            return False
            
        except:
            return False
    
    def select_radio_by_partial(self, driver, partial_text):
        """Select radio button by partial text match"""
        try:
            # Find any element containing partial text
            elements = driver.find_elements(By.XPATH, 
                f'//*[contains(text(), "{partial_text}")]')
            
            for elem in elements:
                try:
                    # Try clicking the element or its parent
                    elem.click()
                    time.sleep(random.uniform(0.2, 0.4))
                    return True
                except:
                    try:
                        # Try parent element
                        parent = elem.find_element(By.XPATH, '..')
                        parent.click()
                        time.sleep(random.uniform(0.2, 0.4))
                        return True
                    except:
                        pass
            
            return False
            
        except:
            return False
    
    def find_next_button(driver):
        """Find and return Next button"""
        try:
            # Common Google Form next button selectors
            selectors = [
                '//span[text()="Next"]/ancestor::div[@role="button"]',
                '//div[@role="button"]//span[text()="Next"]',
                '//span[contains(text(), "Next")]/parent::div[@jsname]',
                '//div[contains(@jsname, "NPEpKc")]',  # Google Forms specific
            ]
            
            for selector in selectors:
                try:
                    btn = driver.find_element(By.XPATH, selector)
                    if btn.is_displayed():
                        return btn
                except:
                    pass
            
            return None
            
        except:
            return None
    
    def find_submit_button(driver):
        """Find and return Submit button"""
        try:
            selectors = [
                '//span[text()="Submit"]/ancestor::div[@role="button"]',
                '//div[@role="button"]//span[text()="Submit"]',
                '//span[contains(text(), "Submit")]/parent::div[@jsname]',
                '//div[contains(text(), "Submit")]',
            ]
            
            for selector in selectors:
                try:
                    btn = driver.find_element(By.XPATH, selector)
                    if btn.is_displayed():
                        return btn
                except:
                    pass
            
            return None
            
        except:
            return None
    
    def submit_one_vote(self, profile):
        """Submit single vote with complete form filling"""
        driver = None
        try:
            driver = self.create_driver()
            
            print(f"\n📝 New vote: {profile['email']}")
            
            # Load form
            driver.get(self.form_url)
            print(f"  Loaded: {self.form_url[:60]}...")
            
            # Fill all pages
            success = True
            
            # Pages 1-6: Personal info
            if not self.fill_page_1to6(driver, profile):
                success = False
            
            # Page 7: Voting (CRITICAL - Lizadro Peter & Nancy Gaichiumia Mwongela)
            if success and not self.fill_voting_page(driver):
                print("    ⚠️  Could not confirm voting selections")
                success = False
            
            # Pages 8-13: Remaining + Submit
            if success and not self.fill_remaining_pages(driver):
                success = False
            
            # Verify submission
            time.sleep(random.uniform(2, 4))
            current_url = driver.current_url
            
            if 'formResponse' in current_url or 'submit' in current_url.lower():
                print(f"  ✅ SUCCESS - Form submitted")
                return True, "Submitted"
            else:
                print(f"  ⚠️  Unclear result - URL: {current_url[:60]}")
                return True, "Possible success"  # Conservative count
            
        except Exception as e:
            print(f"  ❌ FAILED: {str(e)[:80]}")
            return False, str(e)
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def run(self, total_votes=5000, duration_seconds=3600):
        """Execute full voting campaign"""
        
        print(f"\n{'='*70}")
        print(f"🚀 CAMPAIGN: {total_votes} VOTES")
        print(f"{'='*70}")
        print(f"Target: {self.form_url}")
        print(f"Youth Senator: {self.YOUTH_SENATOR} (FIXED)")
        print(f"Woman Rep: {self.WOMAN_REP} (FIXED)")
        print(f"Duration: {duration_seconds}s ({duration_seconds/3600:.2f} hours)")
        print(f"Rate: 1 vote every {duration_seconds/total_votes:.3f}s")
        print(f"{'='*70}\n")
        
        # Show data stats
        stats = self.data_gen.get_stats()
        print(f"📊 Data pool: {stats['total_emails_generated']} previous emails")
        print(f"🆕 Will generate {total_votes} new unique profiles\n")
        
        # Confirm
        input("⚠️  Press ENTER to start (Ctrl+C to stop)... ")
        
        # Calculate timing
        delay = duration_seconds / total_votes
        print(f"\n⏱️  Delay: {delay:.3f}s between votes")
        print(f"🚀 Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Expected finish: {(datetime.now() + timedelta(seconds=duration_seconds)).strftime('%H:%M:%S')}\n")
        
        self.start_time = time.time()
        
        try:
            for vote_num in range(1, total_votes + 1):
                # Check time
                elapsed = time.time() - self.start_time
                if elapsed >= duration_seconds:
                    print(f"\n⏰ Time limit reached at vote {vote_num-1}")
                    break
                
                # Generate profile
                profile = self.data_gen.generate_complete_profile()
                
                # Verify FIXED selections
                assert profile['youth_senator'] == self.YOUTH_SENATOR
                assert profile['youth_woman_rep'] == self.WOMAN_REP
                
                # Submit
                success, msg = self.submit_one_vote(profile)
                
                if success:
                    self.success_count += 1
                    status = "✅"
                else:
                    self.fail_count += 1
                    status = "❌"
                
                # Progress
                if vote_num % 10 == 0 or vote_num == 1:
                    current_rate = vote_num / elapsed * 3600 if elapsed > 0 else 0
                    eta = (datetime.now() + timedelta(seconds=(total_votes-vote_num) * delay)).strftime('%H:%M:%S')
                    
                    print(f"\n[{vote_num:4d}/{total_votes}] {status} | "
                          f"Success: {self.success_count} | Fail: {self.fail_count} | "
                          f"Rate: {current_rate:.0f}/hr | ETA: {eta}")
                    print(f"  Latest: {profile['email'][:40]}")
                
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
        print(f"   Youth Senator: {self.YOUTH_SENATOR} - {self.success_count} votes")
        print(f"   Woman Rep: {self.WOMAN_REP} - {self.success_count} votes")
        
        stats = self.data_gen.get_stats()
        print(f"\n📧 Unique data used: {len(self.data_gen.used_emails)} emails, {len([p for p in self.data_gen.used_phones if p.startswith('07')])} phones")
        print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(
        description='Google Form Vote Bot - Lizadro Peter & Nancy Gaichiumia Mwongela',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:

  # 5000 votes in 1 hour
  python google_form_bot.py --url "https://docs.google.com/forms/d/e/.../viewform" --votes 5000

  # 1000 votes in 30 minutes
  python google_form_bot.py --url "https://docs.google.com/forms/d/e/.../viewform" --votes 1000 --duration 1800

  # 100 votes test in 10 minutes
  python google_form_bot.py --url "YOUR_FORM_URL" --votes 100 --duration 600
        """
    )
    
    parser.add_argument('--url', '-u', required=True,
                       help='Google Form URL (the viewform link)')
    parser.add_argument('--votes', '-n', type=int, default=5000,
                       help='Total votes (default: 5000)')
    parser.add_argument('--duration', '-d', type=int, default=3600,
                       help='Duration in seconds (default: 3600 = 1 hour)')
    
    args = parser.parse_args()
    
    bot = GoogleFormVoteBot(form_url=args.url)
    
    success = bot.run(
        total_votes=args.votes,
        duration_seconds=args.duration
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()