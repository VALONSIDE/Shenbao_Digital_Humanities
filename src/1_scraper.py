"""
Module: Data Acquisition
Description: Semi-automated web scraper for 'Shen Bao' (1872-1949) database.
             Utilizes Selenium for browser automation to bypass complex VPN authentications.
Author: Lei Wu, Lister Zhu, Lao Biao
Date: 2025-12-25
"""

import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# --- Configuration ---
TARGET_URL = "https://elib.cuc.edu.cn/go?id=12"  # Entry point for the database
KEYWORDS = ["神经衰弱", "补脑", "减肥", "函授"]  # Keywords: Neurasthenia, Brain Tonic, Weight Loss, Correspondence Course
DATE_START = "1927.01.01"
DATE_END = "1937.07.01"
OUTPUT_DIR = "../data/raw_ads"

def init_driver():
    """Initialize Edge WebDriver."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(current_dir, "msedgedriver.exe")
    service = Service(executable_path=driver_path)
    return webdriver.Edge(service=service)

def run_scraper():
    """Main execution flow for the scraper."""
    driver = init_driver()
    
    try:
        driver.get(TARGET_URL)
        print("[-] Please verify VPN login manually in the browser window.")
        input("[-] Press [Enter] after the 'Advertisement Search' page is loaded...")

        for keyword in KEYWORDS:
            print(f"[*] Starting collection for keyword: {keyword}")
            
            # --- Step 1: Reset Page State ---
            print("[-] Please click the 'Advertisement Search' tab manually to reset the form.")
            input("[-] Press [Enter] when ready...")

            # --- Step 2: Form Submission ---
            try:
                # Input Keyword
                driver.find_element(By.NAME, "FullText,Subtitle1,Subtitle2,Articletitle+").clear()
                driver.find_element(By.NAME, "FullText,Subtitle1,Subtitle2,Articletitle+").send_keys(keyword)
                
                # Input Date Range
                driver.find_element(By.NAME, "begintime").clear()
                driver.find_element(By.NAME, "begintime").send_keys(DATE_START)
                driver.find_element(By.NAME, "endtime").clear()
                driver.find_element(By.NAME, "endtime").send_keys(DATE_END)
                
                # Submit
                driver.find_element(By.NAME, "image1").click()
                time.sleep(5) # Wait for server response
            except Exception as e:
                print(f"[!] Error during form submission: {e}")
                continue

            # --- Step 3: Deep Scraping Loop ---
            # Logic for iterating through pages and extracting full text is omitted for brevity.
            # (Insert the deep scraping logic from previous versions here if needed)
            
            print(f"[+] Completed: {keyword}")

    except Exception as e:
        print(f"[!] Critical Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    run_scraper()