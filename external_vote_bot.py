#!/usr/bin/env python3
"""
External Voting Bot - For websites you don't control
Works by analyzing the target site and simulating votes

Usage:
    python external_vote_bot.py --url "https://example.com/vote" --candidate "Alice" --votes 5000 --duration 3600
"""

import requests
import time
import random
import argparse
import sys
import re
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class ExternalVoteBot:
    def __init__(self, target_url, candidate_name=None, use_selenium=False):
        self.target_url = target_url
        self.candidate_name = candidate_name
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        })
        
        self.vote_endpoint = None
        self.candidates = []
        self.csrf_token = None
        
    def analyze_website(self):
        """
        Analyze the target website to find:
        - Voting endpoint
        - Candidate names
        - Required tokens/parameters
        - Request format (GET/POST, headers needed)
        """
        print(f"\n🔍 Analyzing: {self.target_url}")
        
        try:
            response = self.session.get(self.target_url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # Look for vote buttons/forms
            vote_buttons = soup.find_all(['button', 'input', 'a'], 
                string=re.compile(r'vote|submit|cast', re.I))
            print(f"Found {len(vote_buttons)} potential vote elements")
            
            # Look for candidate names
            candidates = []
            for elem in soup.find_all(['h1', 'h2', 'h3', 'span', 'div', 'label']):
                text = elem.get_text().strip()
                if text and len(text) < 50 and text not in ['Vote', 'Submit', 'Cancel']:
                    candidates.append(text)
            
            self.candidates = list(set(candidates))[:20]  # Limit and dedupe
            print(f"Potential candidates found: {self.candidates[:10]}")
            
            # Look for forms
            forms = soup.find_all('form')
            print(f"Found {len(forms)} form(s)")
            
            for form in forms:
                action = form.get('action', '')
                method = form.get('method', 'get').upper()
                print(f"  Form: {method} {action}")
                
                # If this looks like a vote form, save it
                if any(kw in action.lower() for kw in ['vote', 'submit', 'poll']):
                    self.vote_endpoint = urljoin(self.target_url, action)
                    print(f"  ⭐ Vote endpoint detected: {self.vote_endpoint}")
                    
                    # Look for CSRF token
                    csrf_input = form.find('input', {'name': re.compile(r'csrf|token|_token', re.I)})
                    if csrf_input:
                        self.csrf_token = csrf_input.get('value')
                        print(f"  CSRF token found: {self.csrf_token[:20]}...")
            
            # Look for JavaScript API endpoints
            scripts = soup.find_all('script')
            api_patterns = []
            for script in scripts:
                if script.string:
                    # Look for API URLs
                    urls = re.findall(r'["\'](https?://[^"\']*vote[^"\']*)["\']', script.string)
                    api_patterns.extend(urls)
            
            if api_patterns:
                print(f"API endpoints found in JS: {api_patterns[:3]}")
                if not self.vote_endpoint:
                    self.vote_endpoint = api_patterns[0]
            
            return True
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False
    
    def detect_request_format(self):
        """
        Try to detect if the site uses:
        - Simple POST with JSON
        - Form data
        - AJAX with specific headers
        """
        print("\n🧪 Testing request formats...")
        
        test_formats = [
            {
                'name': 'JSON POST',
                'headers': {'Content-Type': 'application/json'},
                'data': lambda name: json.dumps({'candidate': name, 'vote': 1})
            },
            {
                'name': 'Form POST',
                'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                'data': lambda name: {'candidate': name, 'vote': '1', 'submit': 'Vote'}
            },
            {
                'name': 'GET with params',
                'headers': {},
                'data': lambda name: None  # Will use params
            }
        ]
        
        # We can't actually test without voting, so we'll document the options
        print("Available request formats:")
        for fmt in test_formats:
            print(f"  - {fmt['name']}")
        
        return test_formats
    
    def vote_requests(self, candidate):
        """
        Submit vote using HTTP requests (faster, no browser overhead)
        """
        if not self.vote_endpoint:
            print("❌ No vote endpoint detected. Cannot proceed with requests mode.")
            return False
        
        try:
            headers = {
                'Referer': self.target_url,
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': urlparse(self.target_url).scheme + '://' + urlparse(self.target_url).netloc
            }
            
            # Try JSON format first
            payload = {
                'candidate': candidate,
                'vote': 1,
                'timestamp': int(time.time() * 1000)
            }
            
            if self.csrf_token:
                payload['csrf_token'] = self.csrf_token
            
            response = self.session.post(
                self.vote_endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201, 204]:
                return True
            else:
                print(f"  Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"  Request failed: {e}")
            return False
    
    def vote_selenium(self, candidate):
        """
        Submit vote using Selenium (simulates real user)
        Slower but bypasses more protections
        """
        try:
            # Setup headless Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument(f'--user-agent={self.session.headers["User-Agent"]}')
            
            # Randomize fingerprint
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Load page
                driver.get(self.target_url)
                time.sleep(random.uniform(2, 4))  # Random delay
                
                # Find and click on candidate
                # This is site-specific - needs customization per target
                candidate_xpath = f"//*[contains(text(), '{candidate}')]"
                candidate_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, candidate_xpath))
                )
                candidate_elem.click()
                time.sleep(random.uniform(0.5, 1.5))
                
                # Find vote button
                vote_button = driver.find_element(By.XPATH, 
                    "//button[contains(text(), 'Vote') or contains(text(), 'Submit')]")
                vote_button.click()
                
                # Wait for confirmation
                time.sleep(random.uniform(1, 3))
                
                return True
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"  Selenium vote failed: {e}")
            return False
    
    def run(self, total_votes, duration_seconds, candidate=None):
        """
        Execute voting campaign
        """
        target_candidate = candidate or self.candidate_name
        
        print(f"\n{'='*60}")
        print(f"🎯 EXTERNAL VOTE BOT")
        print(f"{'='*60}")
        print(f"Target URL: {self.target_url}")
        print(f"Candidate: {target_candidate or 'Auto-detect'}")
        print(f"Total votes: {total_votes:,}")
        print(f"Duration: {duration_seconds}s ({duration_seconds/3600:.2f}h)")
        print(f"Method: {'Selenium' if self.use_selenium else 'HTTP Requests'}")
        print(f"{'='*60}\n")
        
        # Analyze site first
        if not self.analyze_website():
            return False
        
        # If no candidate specified, use first detected
        if not target_candidate and self.candidates:
            target_candidate = self.candidates[0]
            print(f"Auto-selected candidate: {target_candidate}")
        
        if not target_candidate:
            print("❌ No candidate specified or detected")
            return False
        
        # Calculate timing
        delay = duration_seconds / total_votes
        print(f"Delay between votes: {delay:.3f}s")
        
        # Voting loop
        successful = 0
        failed = 0
        start_time = time.time()
        
        print(f"\n🚀 Starting at {time.strftime('%H:%M:%S')}")
        
        for i in range(total_votes):
            # Check time
            elapsed = time.time() - start_time
            if elapsed >= duration_seconds:
                print(f"\n⏰ Time limit reached at vote {i}")
                break
            
            # Vote
            if self.use_selenium:
                success = self.vote_selenium(target_candidate)
            else:
                success = self.vote_requests(target_candidate)
            
            if success:
                successful += 1
                status = "✅"
            else:
                failed += 1
                status = "❌"
            
            # Progress
            if (i + 1) % 100 == 0 or i == 0:
                rate = (i + 1) / elapsed * 3600 if elapsed > 0 else 0
                print(f"[{i+1:5d}/{total_votes}] {status} {target_candidate:15s} | "
                      f"Rate: {rate:6.1f}/hr | Success: {successful}/{i+1}")
            
            # Delay
            next_vote = start_time + (i + 1) * delay
            sleep_time = next_vote - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Report
        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"📊 RESULTS")
        print(f"{'='*60}")
        print(f"Duration: {total_time:.1f}s")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {successful/(successful+failed)*100:.1f}%")
        print(f"{'='*60}")
        
        return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description='External Website Voting Bot',
        epilog="""
Examples:
  # Analyze a site first (dry run)
  python external_vote_bot.py --url "https://example.com/vote" --analyze-only
  
  # Vote using HTTP requests (fast)
  python external_vote_bot.py --url "https://example.com/vote" --candidate "Alice" --votes 100
  
  # Vote using Selenium (stealth mode, slower)
  python external_vote_bot.py --url "https://example.com/vote" --candidate "Bob" --selenium --votes 50
  
  # Spread 5000 votes over 1 hour
  python external_vote_bot.py --url "https://example.com/vote" --candidate "Charlie" --votes 5000 --duration 3600
        """
    )
    
    parser.add_argument('--url', '-u', required=True, help='Target voting page URL')
    parser.add_argument('--candidate', '-c', help='Candidate name to vote for')
    parser.add_argument('--votes', '-n', type=int, default=100, help='Number of votes')
    parser.add_argument('--duration', '-d', type=int, default=3600, help='Duration in seconds')
    parser.add_argument('--selenium', '-s', action='store_true', help='Use browser automation')
    parser.add_argument('--analyze-only', '-a', action='store_true', help='Just analyze, don\'t vote')
    
    args = parser.parse_args()
    
    bot = ExternalVoteBot(
        target_url=args.url,
        candidate_name=args.candidate,
        use_selenium=args.selenium
    )
    
    if args.analyze_only:
        bot.analyze_website()
        bot.detect_request_format()
        return
    
    success = bot.run(
        total_votes=args.votes,
        duration_seconds=args.duration
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()