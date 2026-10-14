import shutil
import socket
import threading
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import uvicorn
from vocabmaster.api.app import create_app


@pytest.mark.skipif(not shutil.which("google-chrome"), reason="google-chrome not installed")
def test_desktop_and_mobile_sidebar_toggle():
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

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,900")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        # 1. Desktop Test (1440x900)
        driver.get(f"http://127.0.0.1:{port}")
        time.sleep(1.5)

        # 1-Click admin login
        admin_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '1 chạm') or contains(., '1-Click')]")))
        driver.execute_script("arguments[0].click();", admin_btn)
        time.sleep(2)

        wait.until(EC.visibility_of_element_located((By.ID, "view-dashboard")))

        # Check toggle button is visible in header
        header_toggle = driver.find_element(By.ID, "btnToggleMobileSidebar")
        assert header_toggle.is_displayed(), "Header sidebar toggle button should be visible on desktop"

        sidebar = driver.find_element(By.ID, "appSidebar")
        assert "sidebar-collapsed" not in sidebar.get_attribute("class").split(), "Sidebar should start expanded"

        # Check desktop collapse button in sidebar header
        collapse_btn = driver.find_element(By.ID, "btnSidebarCollapse")
        assert collapse_btn.is_displayed(), "Desktop collapse button in sidebar header should be visible"

        # Click collapse button
        driver.execute_script("arguments[0].click();", collapse_btn)
        time.sleep(0.5)
        assert "sidebar-collapsed" in sidebar.get_attribute("class").split(), "Sidebar should have sidebar-collapsed after click"

        # Click collapse button again to expand
        driver.execute_script("arguments[0].click();", collapse_btn)
        time.sleep(0.5)
        assert "sidebar-collapsed" not in sidebar.get_attribute("class").split(), "Sidebar should expand again"

        # Click header toggle button to collapse on desktop
        driver.execute_script("arguments[0].click();", header_toggle)
        time.sleep(0.5)
        assert "sidebar-collapsed" in sidebar.get_attribute("class").split(), "Header toggle should collapse sidebar on desktop"

        # Click header toggle button again to expand
        driver.execute_script("arguments[0].click();", header_toggle)
        time.sleep(0.5)
        assert "sidebar-collapsed" not in sidebar.get_attribute("class").split(), "Header toggle should expand sidebar on desktop"

        # 2. Mobile Drawer Test (375x667)
        driver.set_window_size(375, 667)
        time.sleep(0.5)

        assert header_toggle.is_displayed(), "Header toggle button should be visible on mobile"
        assert "-translate-x-full" in sidebar.get_attribute("class").split(), "Sidebar drawer should start closed on mobile"

        # Click header toggle to open mobile drawer
        driver.execute_script("arguments[0].click();", header_toggle)
        time.sleep(0.5)
        assert "-translate-x-full" not in sidebar.get_attribute("class").split(), "Sidebar drawer should open on mobile click"

        backdrop = driver.find_element(By.ID, "sidebarBackdrop")
        assert "hidden" not in backdrop.get_attribute("class").split(), "Backdrop should be visible when drawer is open"

        # Click backdrop to close mobile drawer
        driver.execute_script("arguments[0].click();", backdrop)
        time.sleep(0.5)
        assert "-translate-x-full" in sidebar.get_attribute("class").split(), "Sidebar drawer should close when backdrop is clicked"
        assert "hidden" in backdrop.get_attribute("class").split(), "Backdrop should be hidden when drawer is closed"

        print("ALL SIDEBAR TOGGLE AND COLLAPSE CHECKS PASSED!")

    finally:
        driver.quit()
