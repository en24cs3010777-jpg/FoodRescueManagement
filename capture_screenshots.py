import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

options = Options()
options.add_argument('--headless=new')
options.add_argument('--window-size=1280,850')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
BASE_URL = "http://127.0.0.1:8000"

try:
    # 1. Home Page
    print("1. Capturing Home Page...")
    driver.get(f"{BASE_URL}/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/01_home_page.png")

    # 2. Signup Page
    print("2. Capturing Sign Up Page...")
    driver.get(f"{BASE_URL}/signup/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/02_signup_page.png")

    # 3. Login Page
    print("3. Capturing Login Page...")
    driver.get(f"{BASE_URL}/login/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/03_login_page.png")

    # 4. View Food (Browse Food Catalog)
    print("4. Capturing View Food Catalog...")
    driver.get(f"{BASE_URL}/view-food/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/04_view_food_catalog.png")

    # Find first food detail URL if available
    food_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/food/')]")
    food_detail_url = food_links[0].get_attribute('href') if food_links else None

    # 5. Database Status / Diagnostics Page
    print("5. Capturing Database Diagnostics Page...")
    driver.get(f"{BASE_URL}/db-status/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/05_database_status.png")

    # Log in as Food Provider (provider_demo)
    print("Logging in as Provider...")
    driver.get(f"{BASE_URL}/login/")
    time.sleep(0.5)
    driver.find_element(By.ID, "username_or_email").send_keys("provider_demo")
    driver.find_element(By.ID, "password").send_keys("password123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(1.5)

    # 6. Provider Dashboard
    print("6. Capturing Provider Dashboard...")
    driver.get(f"{BASE_URL}/dashboard/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/06_provider_dashboard.png")

    # 7. Add Food Listing
    print("7. Capturing Add Food Form...")
    driver.get(f"{BASE_URL}/add-food/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/07_add_food_form.png")

    # 8. Provider My Listings
    print("8. Capturing Provider My Listings...")
    driver.get(f"{BASE_URL}/my-listings/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/08_provider_my_listings.png")

    # 9. Account Settings - Profile
    print("9. Capturing Account Settings Profile...")
    driver.get(f"{BASE_URL}/account-settings/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/09_account_settings_profile.png")

    # 10. Account Settings - Password & Delete Account
    print("10. Capturing Account Settings Password/Delete...")
    try:
        pwd_btn = driver.find_element(By.XPATH, "//button[contains(., 'Password Setting')]")
        pwd_btn.click()
        time.sleep(0.5)
        driver.save_screenshot(f"{SCREENSHOT_DIR}/10_account_settings_password.png")
    except Exception as e:
        print("Password tab click error:", e)

    # 11. Food Detail Page
    if food_detail_url:
        print("11. Capturing Food Detail Page...")
        driver.get(food_detail_url)
        time.sleep(1)
        driver.save_screenshot(f"{SCREENSHOT_DIR}/11_food_detail_view.png")

    # Log out provider
    driver.get(f"{BASE_URL}/logout/")
    time.sleep(1)

    # Log in as Food Seeker (seeker_demo)
    print("Logging in as Seeker...")
    driver.get(f"{BASE_URL}/login/")
    time.sleep(0.5)
    driver.find_element(By.ID, "username_or_email").send_keys("seeker_demo")
    driver.find_element(By.ID, "password").send_keys("password123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(1.5)

    # 12. Seeker Dashboard
    print("12. Capturing Seeker Dashboard...")
    driver.get(f"{BASE_URL}/dashboard/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/12_seeker_dashboard.png")

    # 13. Seeker My Claims
    print("13. Capturing Seeker My Claims...")
    driver.get(f"{BASE_URL}/my-claims/")
    time.sleep(1)
    driver.save_screenshot(f"{SCREENSHOT_DIR}/13_seeker_my_claims.png")

    print("All screenshots successfully captured!")

finally:
    driver.quit()
