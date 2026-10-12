import os
import shutil
import socket
import threading
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import uvicorn
from vocabmaster.api.app import create_app


@pytest.mark.skipif(not shutil.which("google-chrome"), reason="google-chrome not installed")
def test_browser_admin_login_and_dashboard_display():
    # 1. Start test uvicorn server on dynamic free port
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    app = create_app()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    time.sleep(1.2)

    # 2. Configure headless Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(f"http://127.0.0.1:{port}")
        time.sleep(2)

        # Check console logs for JS parse errors
        logs = driver.get_log("browser")
        js_errors = [
            l for l in logs
            if l["level"] in ["SEVERE", "ERROR"] and "favicon" not in l["message"]
        ]
        assert not js_errors, f"JavaScript errors found on load: {js_errors}"

        # 3. Test 1-click admin login
        admin_btn = driver.find_element(By.XPATH, "//button[contains(., 'Đăng nhập 1 chạm')]")
        admin_btn.click()
        time.sleep(2.5)

        # Verify auth view is hidden and dashboard is visible
        auth_view = driver.find_element(By.ID, "view-auth")
        dashboard_view = driver.find_element(By.ID, "view-dashboard")
        assert "hidden" in auth_view.get_attribute("class"), "view-auth must be hidden after login"
        assert "hidden" not in dashboard_view.get_attribute("class"), "view-dashboard must be visible after login"

        token = driver.execute_script("return localStorage.getItem('vocabmaster_token');")
        assert token, "vocabmaster_token must be saved to localStorage"

        post_click_errors = [
            l for l in driver.get_log("browser")
            if l["level"] in ["SEVERE", "ERROR"] and "favicon" not in l["message"]
        ]
        assert not post_click_errors, f"JavaScript errors found after login: {post_click_errors}"
    finally:
        driver.quit()
