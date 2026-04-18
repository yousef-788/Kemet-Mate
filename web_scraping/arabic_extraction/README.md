# Kemet Mate - MoTA ETL Data Pipeline

An automated data collection and extraction pipeline built to populate the **Kemet Mate** intelligent tourism platform. These scripts utilize Python, Selenium, and Pandas to scrape official Egyptian tourism data from the Ministry of Tourism and Antiquities (MoTA) and egymonuments.com.

## 🚀 Overview

This repository contains the ETL (Extract, Transform, Load) scripts responsible for building the foundational data warehouse for Kemet Mate. Because the government websites heavily utilize dynamic JavaScript rendering (lazy-loading and Vue.js pagination), standard HTML parsers like BeautifulSoup are insufficient. This pipeline uses Selenium WebDriver to simulate human interaction, ensuring 100% data capture without triggering server blocks.

## 📂 Repository Structure

### 1. Antiquities & Archaeological Sites
* **`antiquities_ar.py`**: The master script for archaeological sites.
    * Uses a custom **"Strike System"** keyboard-scrolling algorithm to force the website's lazy-loader to expose all governorates.
    * Extracts monument names, cleans descriptive text, and logically splits Arabic opening/closing hours.
    * **Relational Mapping**: Automatically detects online reservation links, navigates to `egymonuments.com`, and extracts real-time ticket prices for both Foreigners and Egyptians (Adult/Student).

### 2. Museums
* **`museams_ar.py`**: Operates on the same robust lazy-loading and ticket-scraping architecture as the antiquities script, tailored specifically for the MoTA museums directory.
* **`museams_ar.csv`**: The extracted and cleaned dataset of Egyptian museums.

### 3. Tourism Companies
* **`tourism_companies.py`**: A specialized script for paginated data tables. Simulates human data entry by scraping a table, hunting for dynamic "Next Page" pagination triggers, and looping until the final disabled state is reached (handling over 200+ pages).
* **`tourism_companies.csv`**: The resulting dataset of officially licensed tourism companies (includes Company Name, License No, Governorate, and Email).

### 4. Hotel Establishments
* **`hotels_ar.py`**: Utilizes the pagination-handling architecture to scrape the directory of officially registered hotel establishments across Egypt, capturing Hotel Name, Governorate, City, and official Star Rating.

## ⚙️ Technical Highlights

* **Dynamic Lazy-Load Defeat**: Implements a "Strike System" that wiggles the viewport and waits for slow network responses rather than failing instantly, ensuring zero dropped records on heavily loaded government servers.
* **Bulletproof Exception Handling**: Uses nested `try...except` blocks to survive "Dirty Data" (e.g., broken URLs, misspellings like `#pills-Egyption`, or missing HTML containers) without crashing mid-extraction.
* **Data Transformation**: Cleans raw Arabic text in real-time, strips unwanted boilerplate footers, and utilizes `utf-8-sig` encoding via Pandas to ensure seamless CSV exports for Arabic characters.

## 🛠️ Prerequisites

To run these scripts locally, you will need:
* Python 3.x
* Google Chrome installed
* The following Python libraries:
    ```bash
    pip install pandas selenium
    ```

## ▶️ Usage

Simply execute any of the Python scripts from your terminal. Ensure that no output CSV files are currently open in Excel to prevent `PermissionError: [Errno 13]`.

```bash
python antiquities_ar.py
