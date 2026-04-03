from playwright.sync_api import sync_playwright
import time
import os

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 800, 'height': 800})
        page.goto('http://127.0.0.1:8000/docs')
        
        page.wait_for_selector('.authorize.unlocked', timeout=5000)
        page.click('.authorize.unlocked')
        page.wait_for_selector('.auth-container', timeout=5000)
        time.sleep(1)

        page.evaluate('''
            document.querySelectorAll('.auth-container .wrapper').forEach(el => {
                const text = el.textContent || '';
                if(text.includes('username') || 
                   text.includes('password') || 
                   text.includes('client_secret') || 
                   text.includes('Client credentials location') || 
                   text.includes('Client ID')) {
                    el.style.display = 'none';
                }
            });
            
            // Try to remove background
            const backdrop = document.querySelector('.dialog-ux-backdrop');
            if(backdrop) backdrop.style.background = 'white';
        ''')
        
        os.makedirs('assets', exist_ok=True)
        time.sleep(0.5)
        
        # Take a screenshot of the main auth container dialog
        target = page.locator('.dialog-ux')
        target.screenshot(path='assets/auth.png')
        
        browser.close()
        print("Successfully captured cropped auth screenshot without credentials!")

if __name__ == '__main__':
    main()
