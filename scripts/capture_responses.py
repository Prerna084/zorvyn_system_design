from playwright.sync_api import sync_playwright
import time
import os

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Big viewport to ensure everything is visible without weird scrolling if possible
        page = browser.new_page(viewport={'width': 1200, 'height': 2000})
        page.goto('http://127.0.0.1:8000/docs')
        
        # 1. AUTHENTICATE AS ADMIN so we have data
        page.wait_for_selector('.authorize.unlocked', timeout=5000)
        page.click('.authorize.unlocked')
        page.wait_for_selector('.auth-container', timeout=5000)
        
        # Type credentials and login
        page.fill('input[type="text"]', 'admin@example.com') # username could be in input elements
        page.fill('input[type="password"]', 'admin12345')
        
        # Click the authorize button inside the modal
        page.click('.auth-container .authorize')
        time.sleep(1)
        
        # Close modal
        page.click('.auth-container .btn-done')
        time.sleep(1)
        
        # 2. CAPTURE /api/users response
        # Find the GET /api/users accordion
        user_endpoint = page.locator('#operations-users-list_users_api_users_get')
        user_endpoint.click()
        
        user_endpoint.locator('.try-out__btn').click()
        time.sleep(0.5)
        user_endpoint.locator('.execute').click()
        time.sleep(1) # wait for response
        
        # Capture the response body
        # Hide copy/download buttons for a cleaner screenshot
        page.evaluate('''
            document.querySelectorAll('.download-contents, .copy-to-clipboard').forEach(el => el.style.display = 'none');
        ''')
        
        user_response_box = user_endpoint.locator('.responses-inner .highlight-code').first
        user_response_box.screenshot(path='assets/users.png')
        
        # Close the accordion
        user_endpoint.click()
        time.sleep(0.5)
        
        # 3. CAPTURE /api/dashboard/summary
        dashboard_endpoint = page.locator('#operations-dashboard-dashboard_summary_api_dashboard_summary_get')
        dashboard_endpoint.click()
        time.sleep(0.5)
        
        dashboard_endpoint.locator('.try-out__btn').click()
        time.sleep(0.5)
        dashboard_endpoint.locator('.execute').click()
        time.sleep(1)
        
        dashboard_response_box = dashboard_endpoint.locator('.responses-inner .highlight-code').first
        
        # Hide copy/download buttons again just in case new ones appeared
        page.evaluate('''
            document.querySelectorAll('.download-contents, .copy-to-clipboard').forEach(el => el.style.display = 'none');
        ''')
        
        dashboard_response_box.screenshot(path='assets/dashboard.png')

        browser.close()
        print("Successfully captured Users and Dashboard screenshots!")

if __name__ == '__main__':
    main()
