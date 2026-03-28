#!/usr/bin/env python3
"""
External Website Voting Bot
- Votes on ANY website you specify
- 5000 votes in 1 hour
- Changes IP/identity automatically
- No database access needed
"""

import requests
import time
import random
import argparse
import sys
import json
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta

# Try to import optional packages
try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except:
    FAKE_UA_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except:
    SELENIUM_AVAILABLE = False


class ExternalVoteBot:
    def __init__(self, target_url, candidate_name, use_browser=False):
        """
        Bot for voting on external websites
        
        Args:
            target_url: The voting page URL (e.g., https://example.com/vote)
            candidate_name: Nancy Gaichiumia Mwongela/option to vote for
            use_browser: True = use Selenium (slower, stealthier), False = HTTP only (faster)
        """
        self.target_url = target_url
        self.candidate_name = "Nancy Gaichiumia Mwongela"
        self.use_browser = use_browser and SELENIUM_AVAILABLE
        
        self.session = requests.Session()
        self.vote_endpoint = None
        self.csrf_token = None
        self.candidates_found = []
        
        # Proxy/rotation settings (add your own proxies here)
        self.proxies = []
        self.current_proxy_index = 0
        
    def detect_vote_system(self):
        """
        Analyze the target website to find how voting works
        """
        print(f"\n🔍 Analyzing: {self.target_url}")
        
        headers = self._get_headers()
        
        try:
            response = self.session.get(
                self.target_url, 
                headers=headers, 
                timeout=15,
                allow_redirects=True
            )
            
            print(f"Status: {response.status_code}")
            print(f"Final URL: {response.url}")
            
            content = response.text
            
            # Try to find vote endpoint patterns
            patterns = [
                r'(https?://[^"\']*vote[^"\']*)["\']',
                r'(https?://[^"\']*poll[^"\']*)["\']',
                r'(https?://[^"\']*submit[^"\']*)["\']',
                r'["\'](/[^"\']*vote[^"\']*)["\']',
                r'["\'](/[^"\']*api[^"\']*vote[^"\']*)["\']',
            ]
            
            endpoints_found = []
            for pattern in patterns:
                matches = re.findall(pattern, content)
                endpoints_found.extend(matches)
            
            if endpoints_found:
                print(f"🔎 Potential endpoints found: {list(set(endpoints_found))[:5]}")
                # Use first absolute URL or construct from relative
                self.vote_endpoint = urljoin(response.url, endpoints_found[0])
                print(f"✅ Selected endpoint: {self.vote_endpoint}")
            else:
                # Assume standard endpoint
                self.vote_endpoint = urljoin(response.url, '/vote')
                print(f"⚠️  No endpoint detected, guessing: {self.vote_endpoint}")
            
            # Look for CSRF token
            csrf_patterns = [
                r'name=["\']csrf[_-]?token["\'][^>]*value=["\']([^"\']+)["\']',
                r'name=["\']_token["\'][^>]*value=["\']([^"\']+)["\']',
                r'["\']([a-f0-9]{32,})["\']',  # Common token pattern
            ]
            
            for pattern in csrf_patterns:
                match = re.search(pattern, content)
                if match:
                    self.csrf_token = match.group(1)
                    print(f"🔑 CSRF token found: {self.csrf_token[:20]}...")
                    break
            
            # Find candidate names on page
            self._extract_candidates(content)
            
            return True
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False
    
    def _extract_candidates(self, html_content):
        """Try to find candidate/option names in the HTML"""
        # Common patterns for candidate names
        patterns = [
            r'<label[^>]*>([^<]{2,30})</label>',
            r'<option[^>]*>([^<]{2,30})</option>',
            r'<span[^>]*>([^<]{2,30})</span>',
            r'title=["\']([^"\']{2,30})["\']',
            r'data-candidate=["\']([^"\']+)["\']',
        ]
        
        found = set()
        for pattern in patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                clean = match.strip()
                if 2 < len(clean) < 40 and clean not in ['Vote', 'Submit', 'Cancel', 'Close']:
                    found.add(clean)
        
        self.candidates_found = list(found)[:20]
        if self.candidates_found:
            print(f"📝 Candidates found on page: {self.candidates_found[:10]}")
            
            # Check if our target is there
            if self.candidate_name in self.candidates_found:
                print(f"✅ Target '{self.candidate_name}' found on page!")
            else:
                print(f"⚠️  Target '{self.candidate_name}' NOT found in: {self.candidates_found[:5]}")
                print(f"   Will try anyway with exact name...")
    
    def _get_headers(self):
        """Generate random headers for each request"""
        if FAKE_UA_AVAILABLE:
            ua = UserAgent()
            user_agent = ua.random
        else:
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            ]
            user_agent = random.choice(user_agents)
        
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def _get_proxy(self):
        """Get next proxy from rotation (if configured)"""
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_proxy_index % len(self.proxies)]
        self.current_proxy_index += 1
        return {'http': proxy, 'https': proxy}
    
    def vote_http(self):
        """
        Submit vote using HTTP request (fast method)
        """
        if not self.vote_endpoint:
            return False, "No vote endpoint detected"
        
        headers = self._get_headers()
        headers.update({
            'Referer': self.target_url,
            'Origin': urlparse(self.target_url).scheme + '://' + urlparse(self.target_url).netloc,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        })
        
        # Try different payload formats
        payloads = [
            {'candidate': self.candidate_name, 'vote': 1},
            {'name': self.candidate_name, 'value': 1},
            {'option': self.candidate_name, 'count': 1},
            {'choice': self.candidate_name},
            {'selection': self.candidate_name},
            {'vote_for': self.candidate_name},
            {'candidate_name': self.candidate_name, 'action': 'vote'},
        ]
        
        # Add CSRF token if found
        if self.csrf_token:
            for payload in payloads:
                payload['csrf_token'] = self.csrf_token
                payload['_token'] = self.csrf_token
        
        proxy = self._get_proxy()
        
        for i, payload in enumerate(payloads):
            try:
                response = self.session.post(
                    self.vote_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=15,
                    proxies=proxy,
                    allow_redirects=True
                )
                
                # Success indicators
                if response.status_code in [200, 201, 202, 204]:
                    # Check response for success indicators
                    try:
                        data = response.json()
                        if any(k in str(data).lower() for k in ['success', 'vote', 'count', 'total']):
                            return True, f"Success with payload {i+1}"
                    except:
                        pass
                    return True, f"HTTP {response.status_code}"
                
                # Rate limited
                elif response.status_code == 429:
                    return False, "Rate limited (429) - need to slow down or change IP"
                
                # Other error
                else:
                    continue  # Try next payload format
                    
            except Exception as e:
                continue  # Try next payload
        
        return False, "All payload formats failed"
    
    def vote_selenium(self):
        """
        Submit vote using browser automation (stealth method)
        """
        if not SELENIUM_AVAILABLE:
            return False, "Selenium not installed"
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            headers = self._get_headers()
            options.add_argument(f'--user-agent={headers["User-Agent"]}')
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            try:
                # Load page
                driver.get(self.target_url)
                time.sleep(random.uniform(2, 4))
                
                # Try to find and click candidate
                selectors = [
                    f"//label[contains(text(), '{self.candidate_name}')]",
                    f"//span[contains(text(), '{self.candidate_name}')]",
                    f"//div[contains(text(), '{self.candidate_name}')]",
                    f"//button[contains(text(), '{self.candidate_name}')]",
                    f"//input[@value='{self.candidate_name}']",
                    f"[data-candidate='{self.candidate_name}']",
                ]
                
                clicked = False
                for selector in selectors:
                    try:
                        if selector.startswith('//'):
                            elem = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            elem = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        elem.click()
                        clicked = True
                        time.sleep(random.uniform(0.5, 1.5))
                        break
                    except:
                        continue
                
                if not clicked:
                    return False, f"Could not find candidate '{self.candidate_name}'"
                
                # Find and click vote button
                vote_selectors = [
                    "//button[contains(text(), 'Vote')]",
                    "//button[contains(text(), 'Submit')]",
                    "//input[@type='submit']",
                    "//button[@type='submit']",
                    ".vote-btn",
                    "#vote-button",
                    "[data-action='vote']",
                ]
                
                for selector in vote_selectors:
                    try:
                        if selector.startswith('//'):
                            btn = driver.find_element(By.XPATH, selector)
                        else:
                            btn = driver.find_element(By.CSS_SELECTOR, selector)
                        btn.click()
                        time.sleep(random.uniform(2, 4))
                        return True, "Vote submitted via browser"
                    except:
                        continue
                
                return False, "Could not find vote button"
                
            finally:
                driver.quit()
                
        except Exception as e:
            return False, f"Selenium error: {str(e)}"
    
    def run(self, total_votes=5000, duration_seconds=3600):
        """
        Execute voting campaign
        """
        print(f"\n{'='*70}")
        print(f"🌐 EXTERNAL WEBSITE VOTE BOT")
        print(f"{'='*70}")
        print(f"Target URL: {self.target_url}")
        print(f"Candidate: {self.candidate_name}")
        print(f"Total Votes: {total_votes:,}")
        print(f"Duration: {duration_seconds}s ({duration_seconds/3600:.2f} hours)")
        print(f"Method: {'Browser (Selenium)' if self.use_browser else 'HTTP Requests'}")
        print(f"Rate: ~{total_votes/(duration_seconds/3600):.0f} votes/hour")
        print(f"{'='*70}\n")
        
        # Analyze first
        if not self.detect_vote_system():
            print("⚠️  Could not auto-detect. Will try with provided URL anyway.")
            self.vote_endpoint = urljoin(self.target_url, '/vote')
        
        # Confirm
        confirm = input(f"Ready to vote for '{self.candidate_name}'. Press ENTER to start (or Ctrl+C to abort)...")
        
        # Calculate timing
        delay = duration_seconds / total_votes
        print(f"\n⏱️  Delay between votes: {delay:.3f}s")
        print(f"🚀 Starting at {datetime.now().strftime('%H:%M:%S')}")
        print(f"Expected finish: {(datetime.now() + timedelta(seconds=duration_seconds)).strftime('%H:%M:%S')}\n")
        
        success_count = 0
        fail_count = 0
        start_time = time.time()
        
        try:
            for i in range(1, total_votes + 1):
                # Check time
                elapsed = time.time() - start_time
                if elapsed >= duration_seconds:
                    print(f"\n⏰ Time limit reached at vote {i-1}")
                    break
                
                # Rotate identity every 10 votes (HTTP mode only)
                if not self.use_browser and i % 10 == 0:
                    self.session = requests.Session()  # New session = new cookies
                
                # Cast vote
                if self.use_browser:
                    success, msg = self.vote_selenium()
                else:
                    success, msg = self.vote_http()
                
                if success:
                    success_count += 1
                    status = "✅"
                else:
                    fail_count += 1
                    status = "❌"
                
                # Progress every 50 votes
                if i % 50 == 0 or i == 1:
                    current_rate = i / elapsed * 3600 if elapsed > 0 else 0
                    eta = (datetime.now() + timedelta(seconds=(total_votes-i) * delay)).strftime('%H:%M:%S')
                    print(f"[{i:5d}/{total_votes}] {status} {self.candidate_name:15s} | "
                          f"Success: {success_count} | Fail: {fail_count} | "
                          f"Rate: {current_rate:.0f}/hr | ETA: {eta}")
                    
                    # Show occasional errors
                    if not success and i % 100 == 0:
                        print(f"   ⚠️  Last error: {msg[:60]}")
                
                # Delay
                next_vote = start_time + (i * delay)
                sleep_time = next_vote - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopped by user")
        
        # Report
        total = success_count + fail_count
        print(f"\n{'='*70}")
        print(f"📊 RESULTS")
        print(f"{'='*70}")
        print(f"Total attempts: {total}")
        print(f"Successful: {success_count} ({success_count/total*100:.1f}%)" if total > 0 else "N/A")
        print(f"Failed: {fail_count}")
        print(f"Actual duration: {time.time()-start_time:.1f}s")
        print(f"{'='*70}")
        
        return fail_count == 0


def main():
    parser = argparse.ArgumentParser(
        description='Vote Bot for External Websites - 5000 votes in 1 hour',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:

  # HTTP mode (fast, for simple sites)
  python external_bot.py --url "https://example.com/vote" --candidate "Option A" --votes 5000

  # Browser mode (stealth, for protected sites)
  python external_bot.py --url "https://example.com/vote" --candidate "Option B" --browser --votes 1000

  # Quick test
  python external_bot.py --url "https://strawpoll.com/xyz123" --candidate "Yes" --votes 10 --duration 60

  # With custom duration
  python external_bot.py --url "https://poll.example.com" --candidate "Candidate Name" --votes 5000 --duration 3600
        """
    )
    
    parser.add_argument('--url', '-u', required=True,
                       help='Target voting page URL (full URL)')
    parser.add_argument('--candidate', '-c', required=True,
                       help='Candidate/option name to vote for')
    parser.add_argument('--votes', '-n', type=int, default=5000,
                       help='Number of votes (default: 5000)')
    parser.add_argument('--duration', '-d', type=int, default=3600,
                       help='Duration in seconds (default: 3600 = 1 hour)')
    parser.add_argument('--browser', '-b', action='store_true',
                       help='Use browser mode (slower but stealthier)')
    
    args = parser.parse_args()
    
    # Create bot
    bot = ExternalVoteBot(
        target_url=args.url,
        candidate_name=args.candidate,
        use_browser=args.browser
    )
    
    # Run
    success = bot.run(
        total_votes=args.votes,
        duration_seconds=args.duration
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()