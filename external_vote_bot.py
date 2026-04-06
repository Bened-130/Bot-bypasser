import time
import random
import json
import argparse
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os

from data_generator import DataGenerator


class GoogleFormVoteBot:
    def __init__(self, form_url, google_email=None, google_password=None):
        self.form_url = form_url
        self.google_email = google_email
        self.google_password = google_password
        self.data_gen = DataGenerator()
        self.start_time = None
        
        # Voting choices (fixed for this form)
        self.YOUTH_SENATOR = "Lizadro Peter"
        self.WOMAN_REP = "Nancy Gaichiumia Mwongela"
    
    def create_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"Error creating Chrome driver: {e}")
            return None
    
    def login_google(self, driver, email, password):
        """Login to Google account."""
        try:
            # Navigate to Google login page
            driver.get("https://accounts.google.com/")
            time.sleep(3)
            
            # Wait for and fill email
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_input.clear()
            email_input.send_keys(email)
            
            # Click Next
            next_button = driver.find_element(By.ID, "identifierNext")
            next_button.click()
            time.sleep(3)
            
            # Wait for password field
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            time.sleep(1)
            password_input.clear()
            password_input.send_keys(password)
            
            # Click Next
            next_button = driver.find_element(By.ID, "passwordNext")
            next_button.click()
            time.sleep(5)  # Wait for login to complete
            
            return True
        except Exception as e:
            print(f"Login failed: {str(e)[:100]}")
            return False
    
    def fill_input_by_label(self, driver, label_text, value):
        """Fill input fields - handles both <input> and contenteditable divs."""
        try:
            time.sleep(0.5)
            
            # Strategy 1: Find input near label text in same container
            try:
                labels = driver.find_elements(By.XPATH, f'//span[contains(text(), "{label_text}")]')
                for label in labels:
                    parent = label
                    for _ in range(8):
                        try:
                            parent = parent.find_element(By.XPATH, '..')
                            # Try input element
                            try:
                                inp = parent.find_element(By.TAG_NAME, 'input')
                                if inp.is_displayed():
                                    inp.clear()
                                    inp.send_keys(value)
                                    time.sleep(0.4)
                                    return True
                            except:
                                pass
                            # Try contenteditable div
                            try:
                                content_div = parent.find_element(By.XPATH, './/*[@contenteditable="true"]')
                                if content_div.is_displayed():
                                    content_div.clear()
                                    content_div.send_keys(value)
                                    time.sleep(0.4)
                                    return True
                            except:
                                pass
                        except:
                            pass
            except:
                pass
            
            # Strategy 2: Find any visible text input (by order)
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
            for inp in inputs:
                if inp.is_displayed():
                    try:
                        if not inp.get_attribute('value'):
                            inp.clear()
                            inp.send_keys(value)
                            time.sleep(0.4)
                            return True
                    except:
                        pass
            
            # Strategy 3: Find contenteditable divs
            contenteditable_divs = driver.find_elements(By.XPATH, '//*[@contenteditable="true"]')
            for div in contenteditable_divs:
                if div.is_displayed():
                    try:
                        text = div.text.strip() if div.text else ""
                        if not text:
                            div.clear()
                            div.send_keys(value)
                            time.sleep(0.4)
                            return True
                    except:
                        pass
            
            return False
        except Exception as e:
            return False
    
    def select_radio(self, driver, text):
        """Select radio option."""
        try:
            time.sleep(0.3)
            
            # Find span with the radio option text
            spans = driver.find_elements(By.XPATH, f'//span[contains(text(), "{text}")]')
            
            for span in spans:
                if span.is_displayed():
                    try:
                        # Scroll to element
                        driver.execute_script("arguments[0].scrollIntoView(true);", span)
                        time.sleep(0.3)
                        # Try clicking the span directly
                        span.click()
                        time.sleep(0.4)
                        return True
                    except:
                        try:
                            # Fallback: find parent radio button
                            parent = span.find_element(By.XPATH, 'ancestor::div[@role="radio" or @role="button"][1]')
                            parent.click()
                            time.sleep(0.4)
                            return True
                        except:
                            continue
            
            return False
        except:
            return False
    
    def click_button(self, driver, text):
        try:
            time.sleep(0.8)
            # Scroll to bottom to ensure button is visible
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            
            # Try: Find span with matching text, get parent button div
            buttons = driver.find_elements(By.XPATH, 
                f'//span[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{text.lower()}")]/ancestor::div[@role="button"][1]')
            for btn in buttons:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.4)
                    try:
                        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(btn))
                    except:
                        pass
                    btn.click()
                    time.sleep(1.5)
                    return True
            
            # Try: Exact text match
            buttons = driver.find_elements(By.XPATH, 
                f'//span[text()="{text}"]/ancestor::div[@role="button"][1]')
            for btn in buttons:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.4)
                    btn.click()
                    time.sleep(1.5)
                    return True
            
            # Try: Contains text
            buttons = driver.find_elements(By.XPATH, 
                f'//span[contains(text(), "{text}")]/ancestor::div[@role="button"][1]')
            for btn in buttons:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.4)
                    btn.click()
                    time.sleep(1.5)
                    return True
            
            # Try: Actual button elements
            buttons = driver.find_elements(By.XPATH, f'//button[contains(text(), "{text}")]')
            for btn in buttons:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.4)
                    btn.click()
                    time.sleep(1.5)
                    return True
            
            # Last resort: click any button div
            buttons = driver.find_elements(By.XPATH, '//div[@role="button" and .//span]')
            if buttons:
                last_btn = buttons[-1]
                if last_btn.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", last_btn)
                    time.sleep(0.4)
                    last_btn.click()
                    time.sleep(1.5)
                    return True
            
            return False
        except Exception as e:
            return False
    
    def submit_vote(self, profile, login_first_vote=False):
        driver = None
        try:
            driver = self.create_driver()
            print(f"\n{profile['full_name']} | {profile['email']}")
            
            if login_first_vote and self.google_email and self.google_password:
                print("  Logging in with Google account...")
                if not self.login_google(driver, self.google_email, self.google_password):
                    print("  Google login failed. Aborting this vote.")
                    return False, "Google login failed"
                print("  Login successful. Loading form...")
            
            driver.get(self.form_url)
            time.sleep(random.uniform(4, 6))
            
            # PAGE 1: Personal Info
            print("  Page 1: Personal Info")
            
            # Take screenshot for debugging
            driver.save_screenshot(f"form_page1_{int(time.time())}.png")
            
            print(f"    Filling Full Name: {profile['full_name']}")
            if self.fill_input_by_label(driver, "Full Name", profile['full_name']):
                print("    ✓ Full Name filled")
            else:
                print("    ✗ Full Name NOT filled")
            
            print(f"    Filling Email: {profile['email']}")
            if self.fill_input_by_label(driver, "Email", profile['email']):
                print("    ✓ Email filled")
            else:
                print("    ✗ Email NOT filled")
            
            print(f"    Filling WhatsApp: {profile['whatsapp']}")
            if self.fill_input_by_label(driver, "WhatsApp Number", profile['whatsapp']):
                print("    ✓ WhatsApp filled")
            else:
                print("    ✗ WhatsApp NOT filled")
            
            print(f"    Selecting Age: {profile['age_bracket']}")
            if self.select_radio(driver, profile['age_bracket']):
                print("    ✓ Age selected")
            else:
                print("    ✗ Age NOT selected")
            
            print(f"    Selecting Gender: {profile['gender']}")
            if self.select_radio(driver, profile['gender']):
                print("    ✓ Gender selected")
            else:
                print("    ✗ Gender NOT selected")
            
            # Click Next button to page 2
            print("    Clicking Next button...")
            if not self.click_button(driver, "Next"):
                print("  Failed to click Next on page 1")
                return False, "Page 1: Next button not found"
            print("  Clicked Next -> Page 2")
            time.sleep(random.uniform(3, 5))
            
            # PAGE 2: Voting
            print("  Page 2: Voting")
            print(f"    Selecting Senator: {self.YOUTH_SENATOR}")
            if self.select_radio(driver, self.YOUTH_SENATOR):
                print("    ✓ Senator selected")
            else:
                print("    ✗ Senator NOT selected")
            
            print(f"    Selecting Woman Rep: {self.WOMAN_REP}")
            if self.select_radio(driver, self.WOMAN_REP):
                print("    ✓ Woman Rep selected")
            else:
                print("    ✗ Woman Rep NOT selected")
            
            # Click Next to page 3
            if not self.click_button(driver, "Next"):
                print("  Failed to click Next on page 2")
                return False, "Page 2: Next button not found"
            print("  Clicked Next -> Page 3")
            time.sleep(random.uniform(3, 5))
            
            # PAGE 3: Final page
            print("  Page 3: Contact Preference")
            print(f"    Selecting Contact: {profile['contact_preference']}")
            if self.select_radio(driver, profile['contact_preference']):
                print("    ✓ Contact preference selected")
            else:
                print("    ✗ Contact preference NOT selected")
            
            # Submit the form
            print("  Submitting...")
            if self.click_button(driver, "Submit"):
                print("  SUBMITTED ✓")
                time.sleep(random.uniform(2, 3))
                return True, "Success"
            else:
                print("  Submit button not found")
                return False, "Submit failed"
        except Exception as e:
            print(f"  ERROR: {str(e)[:80]}")
            return False, str(e)
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def run(self, total_votes=5000, duration_seconds=3600):
        """Main execution - submit votes."""
        print(f"\n{'='*70}")
        print(f"CAMPAIGN: {total_votes} VOTES IN {duration_seconds/3600:.1f} HOURS")
        print(f"{'='*70}")
        
        stats = self.data_gen.get_stats()
        print(f"Data pool: {stats['total_unique_names']} previous names")
        print(f"Will generate {total_votes} NEW unique names\n")
        
        print("Starting automatically...")
        
        delay = duration_seconds / total_votes
        print(f"\nDelay: {delay:.3f}s between votes")
        print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Expected: {(datetime.now() + timedelta(seconds=duration_seconds)).strftime('%H:%M:%S')}\n")
        
        self.start_time = time.time()
        successful = 0
        failed = 0
        
        try:
            for i in range(1, total_votes + 1):
                elapsed = time.time() - self.start_time
                if elapsed >= duration_seconds:
                    print(f"\nTime limit reached")
                    break
                
                # Generate new unique profile
                profile = self.data_gen.generate_complete_profile()
                
                # First vote: login, subsequent votes: no login
                if i == 1:
                    success, msg = self.submit_vote(profile, login_first_vote=True)
                else:
                    success, msg = self.submit_vote(profile, login_first_vote=False)
                
                if success:
                    successful += 1
                else:
                    failed += 1
                
                # Print progress
                elapsed = time.time() - self.start_time
                rate = successful / elapsed * 3600 if elapsed > 0 else 0
                print(f"[{i:4d}/{total_votes}] Success: {successful} | Fail: {failed} | Rate: {rate:10.0f}/hr")
                
                # Wait before next vote
                if i < total_votes:
                    wait_time = max(0, delay - (time.time() - self.start_time - elapsed))
                    if wait_time > 0:
                        time.sleep(wait_time)
        
        except KeyboardInterrupt:
            print("\n\nStopped by user")
        
        # Final report
        elapsed = time.time() - self.start_time
        print(f"\n{'='*70}")
        print(f"FINAL REPORT")
        print(f"{'='*70}")
        print(f"Duration: {elapsed:.1f}s")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        success_rate = (successful / (successful + failed) * 100) if (successful + failed) > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        print(f"\nAll {successful} votes for:")
        print(f"  Senator: {self.YOUTH_SENATOR}")
        print(f"  Woman Rep: {self.WOMAN_REP}")
        
        stats = self.data_gen.get_stats()
        print(f"\nUnique data generated: {stats['total_unique_names']} names, {stats['total_unique_emails']} emails")
        print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description='MKYA Voting Bot')
    parser.add_argument('--url', required=True, help='Google Form URL')
    parser.add_argument('--email', help='Google account email')
    parser.add_argument('--password', help='Google account password')
    parser.add_argument('--votes', type=int, default=5, help='Number of votes to submit')
    parser.add_argument('--duration', type=int, default=3600, help='Duration in seconds')
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f"GOOGLE FORM BOT - FIXED (UNIQUE NAMES)")
    print(f"{'='*70}")
    print("Features:")
    print("  ✓ Names: Always unique, never repeated")
    print("  ✓ Emails: Contain real names (john.mwangi@gmail.com)")
    print("  ✓ Senator: Lizadro Peter")
    print("  ✓ Woman Rep: Nancy Gaichiumia Mwongela")
    print("  ✓ County: Meru")
    print(f"{'='*70}\n")
    
    bot = GoogleFormVoteBot(args.url, args.email, args.password)
    bot.run(args.votes, args.duration)


if __name__ == "__main__":
    main()
