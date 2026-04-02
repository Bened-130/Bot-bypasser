#!/usr/bin/env python3
"""Debug script to inspect form HTML structure."""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import subprocess
import sys

def create_driver():
    """Create Chrome driver."""
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
        print(f"Chrome driver error: {e}")
        return None

def login_google_improved(driver, email, password):
    """Login to Google with improved handling."""
    try:
        driver.get("https://accounts.google.com/")
        time.sleep(3)
        
        # Email field  
        try:
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_input.clear()
            email_input.send_keys(email)
            print(f"  Entered email: {email}")
        except Exception as e:
            print(f"  Error entering email: {e}")
            return False
        
        # Click Next
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "identifierNext"))
            )
            next_button.click()
            time.sleep(2)
            print("  Clicked Next after email")
        except Exception as e:
            print(f"  Error clicking Next after email: {e}")
            return False
        
        # Wait for password field
        try:
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            time.sleep(1)
            password_input.clear()
            password_input.send_keys(password)
            print(f"  Entered password")
        except Exception as e:
            print(f"  Error entering password: {e}")
            return False
        
        # Click Next for password
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "passwordNext"))
            )
            next_button.click()
            time.sleep(5)
            print("  Clicked Next after password, waiting for redirect...")
        except Exception as e:
            print(f"  Error clicking Next after password: {e}")
            return False
        
        # Check if login was successful by looking for redirects
        print(f"  Current URL after login: {driver.current_url}")
        time.sleep(2)
        
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False

def analyze_form(driver, form_url):
    """Analyze form structure."""
    print("Loading form...")
    driver.get(form_url)
    time.sleep(5)
    
    print("\n" + "="*80)
    print("FORM ANALYSIS - PAGE 1")
    print("="*80)
    
    # Find all input elements
    all_inputs = driver.find_elements(By.TAG_NAME, 'input')
    print(f"\nTotal input elements found: {len(all_inputs)}")
    print("\nInput Details:")
    for i, inp in enumerate(all_inputs):
        print(f"\n  Input {i}:")
        print(f"    Type: {inp.get_attribute('type')}")
        print(f"    Aria-label: {inp.get_attribute('aria-label')}")
        print(f"    Placeholder: {inp.get_attribute('placeholder')}")
        print(f"    Name: {inp.get_attribute('name')}")
        print(f"    ID: {inp.get_attribute('id')}")
        print(f"    Class: {inp.get_attribute('class')}")
        print(f"    Displayed: {inp.is_displayed()}")
        
        # Get parent div
        try:
            parent = inp.find_element(By.XPATH, '..')
            parent_text = parent.text[:100] if parent.text else "No text"
            print(f"    Parent text: {parent_text}")
        except:
            pass
    
    # Find all labels
    all_labels = driver.find_elements(By.TAG_NAME, 'label')
    print(f"\n\nTotal label elements found: {len(all_labels)}")
    print("\nLabel Details:")
    for i, label in enumerate(all_labels[:10]):  # First 10
        print(f"\n  Label {i}: {label.text[:100]}")
    
    # Find all radio buttons / select options
    radio_spans = driver.find_elements(By.XPATH, '//span[contains(text(), "Male") or contains(text(), "Female") or contains(text(), "25-30") or contains(text(), "18-24")]')
    print(f"\n\nRadio/Option spans found: {len(radio_spans)}")
    for i, span in enumerate(radio_spans):
        print(f"\n  Option {i}: {span.text}")
        try:
            parent = span.find_element(By.XPATH, '/ancestor::*[@role="radio"][1]')
            print(f"    Has radio role parent: Yes")
        except:
            print(f"    Has radio role parent: No")
    
    # Find all buttons
    all_buttons = driver.find_elements(By.XPATH, '//div[@role="button"]')
    print(f"\n\nTotal button divs found: {len(all_buttons)}")
    print("\nButton Details:")
    for i, btn in enumerate(all_buttons):
        btn_text = btn.text[:50] if btn.text else "No text"
        print(f"  Button {i}: {btn_text}")
    
    print("\n" + "="*80)

def main():
    driver = create_driver()
    if not driver:
        print("Failed to create driver")
        return
    
    try:
        # Step 1: Login 
        print("Step 1: Logging in to Google...")
        if not login_google_improved(driver, "balagazikino@gmail.com", "123456789A.@"):
            print("ERROR: Login failed!")
            driver.quit()
            return
        
        # Step 2: Analyze form (now that we're logged in)
        print("\nStep 2: Going directly to form...")
        analyze_form(driver, "https://forms.gle/8YnqGUP36d9ySGQH9")
        
        # Take screenshot
        print("\nTaking screenshot...")
        driver.save_screenshot("form_screenshot.png")
        print("Screenshot saved as form_screenshot.png")
        
        # Save page source
        print("Saving page source...")
        with open("form_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved as form_source.html")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
