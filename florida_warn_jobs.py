import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os
import smtplib
from email.mime.text import MIMEText

# Store secrets/keys to variables
gmail_pass = os.environ['gmail_pass']
email_sender = os.environ['email_sender']
email_recipient = os.environ['email_recipient']

def parse_pages(table):
    # Find all pages
    pages = set()
    pages_list = []

    for a in table.find_all('a'):
        href = a.get('href')
        if href and "page" in href:
           pages.add("https://reactwarn.floridajobs.org" + href)
    
    for i in pages:
        pages_list.append(i)

    return pages_list

def parse_data(table):
    # Extract column headers
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())
    
    # Extract row data
    rows = []
    company_name = []

    for tr in table.find_all('tr'):
        row = []
        b_tags = tr.find_all('b')
        c_name = [b.text.strip() for b in b_tags]
        if c_name:
            company_name.append(' '.join(c_name))

        for td in tr.find_all('td'):
            row.append(td.text.strip())
        for input_tag in tr.find_all('input'):
            row.append(input_tag.get('value'))
        if len(row) > 0:
            rows.append(row)

    df = pd.DataFrame(rows, columns=headers + ['Button', 'Filename'])
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.upper()
    df = df.dropna(subset=['STATE_NOTIFICATION_DATE'])
    
    df['COMPANY_NAME'] = company_name

    df['FILENAME'] = 'https://reactwarn.floridajobs.org/WarnList/DownloadAzureFile?file=' + df['FILENAME']
    df = df[[
        'COMPANY_NAME',
        'STATE_NOTIFICATION_DATE',
        'LAYOFF_DATE',
        'EMPLOYEES_AFFECTED',
        'INDUSTRY',
        'FILENAME'
        ]]
    
    return df

def filter_results(company_list):
    filtered_dfs = []
    if not company_list:
        filtered_df = df
    else:
        for i in company_list:
            filtered_dfs.append(df.loc[df['COMPANY_NAME'].str.lower().str.contains(i)])
            filtered_df = pd.concat(filtered_dfs, ignore_index=True)

    filtered_row_count = filtered_df.shape[0]

    alert_msg = []
    if filtered_df.empty:
        return alert_msg, filtered_row_count
    else:
        for i in range(len(filtered_df)):
            alert_msg.append("Company Name: " + filtered_df.loc[i, 'COMPANY_NAME'] + "\n" +
            "State Notification Date: " + filtered_df.loc[i, 'STATE_NOTIFICATION_DATE'] + "\n" +
            "Layoff Date: " + filtered_df.loc[i, 'LAYOFF_DATE'] + "\n" +
            "Employees Affected: " + filtered_df.loc[i, 'EMPLOYEES_AFFECTED'] + "\n" +
            "Industry: " + filtered_df.loc[i, 'INDUSTRY'] + "\n" +
            "PDF Attachment: " + filtered_df.loc[i, 'FILENAME'] + "\n")
        return alert_msg, filtered_row_count

def send_email(receiver_email, body):
    if filtered_row_count == 0:
        print(f"Returned {filtered_row_count} record(s), no matches found.")
    else:
        print(f"Returned {filtered_row_count} record(s) that matched, please review!")
        msg = MIMEText(body)
        msg['Subject'] = "FloridaJobs WARN Alert"
        msg['From'] = 'ccmartin@gmail.com'
        msg['To'] = receiver_email
        msg['X-Priority'] = '1'

        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = email_sender
        password = gmail_pass

        try:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
            server.quit()
            print("Email sent successfully.")
        except Exception as e:
            print("Email failed " + e)

current_year = datetime.datetime.now().year
url = f"https://reactwarn.floridajobs.org/WarnList/Records?year={current_year}"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Connection": "keep-alive",
    "Host": "reactwarn.floridajobs.org",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers, verify=False)

if response.status_code == 200:
    data = BeautifulSoup(response.text, "html.parser")
    table = data.find('table')

    list_of_urls = parse_pages(table)

    if not list_of_urls:
        df = parse_data(table)
    else:
        dfs = []
        for i in list_of_urls:
            response = requests.get(i, headers=headers, verify=False)
            if response.status_code == 200:
                data = BeautifulSoup(response.text, "html.parser")
                table = data.find('table')
                urls = parse_pages(table)
                for i in urls:
                    if i not in list_of_urls:
                        list_of_urls.append(i)
                dfs.append(parse_data(table))
            else:
                print("Error: unable to retrieve data.")
        df = pd.concat(dfs, ignore_index=True)

    company_list = ['university of miami', 'uhealth', 'nicklaus'] # leave blank to output all records
    alert_msg, filtered_row_count = filter_results(company_list)
    alert_msg = '\n'.join(alert_msg)
    send_email('ccmartin@gmail.com', alert_msg)
else:
    print("Error: unable to retrieve data.")