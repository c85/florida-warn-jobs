# FloridaJobs WARN Notice Alerts

## Overview
The Florida WARN Jobs Scraper is a Streamlit application designed to scrape the WARN (Worker Adjustment and Retraining Notification) notices provided by the Florida Department of Economic Opportunity for the current year. The app allows users to search through the WARN notices based on company names and download the filtered data in CSV format. Additionally, the scraped data includes a column containing PDF links to the official WARN notices posted by the companies.

## Features
* Data Fetching: Scrapes WARN notices for the current year from the official [Florida WARN notices website](https://floridajobs.org/office-directory/division-of-workforce-services/workforce-programs/reemployment-and-emergency-assistance-coordination-team-react/warn-notices).
* Search Functionality: Allows users to search through the WARN notices by entering the company names. Users can enter multiple company names, separated by commas.
* Data Display: Presents the scraped and filtered data in a neatly formatted table.
* Downloadable Data: Enables users to download the filtered data in CSV format.
* PDF Links: Provides direct links to the PDFs of the WARN notices, making it easier for users to access official documents.

## How to Use
1. Search: Input the company name(s) you want to search for in the "Search company name" text box. You can enter multiple company names separated by commas.
* *Note: You can leave the input blank to get all the available records.*
2. Fetch Data: Click the "Search" button to fetch and display the filtered data.
3. Download: Use the "Download" button to download the filtered data as a CSV file.