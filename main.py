import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import streamlit as st
from io import BytesIO

@st.cache_data
def fetch_data():
    current_year = datetime.datetime.now().year
    url = f"https://reactwarn.floridajobs.org/WarnList/Records?year={current_year}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        raise Exception("Unable to fetch data.")

    data = BeautifulSoup(response.text, "html.parser")
    table = data.find('table')

    list_of_urls = parse_pages(table)
    dfs = []
    for i in list_of_urls:
        response = requests.get(i, headers=headers, verify=False)
        if response.status_code == 200:
            data = BeautifulSoup(response.text, "html.parser")
            table = data.find('table')
            dfs.append(parse_data(table))
        else:
            raise Exception("Unable to fetch data.")

    df = pd.concat(dfs, ignore_index=True)
    return df, current_year

def parse_pages(table):
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
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())
    
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

def filter_results(df, company_list):
    filtered_dfs = []
    if not company_list:
        filtered_df = df
    else:
        for i in company_list:
            filtered_dfs.append(df.loc[df['COMPANY_NAME'].str.lower().str.contains(i)])
            filtered_df = pd.concat(filtered_dfs, ignore_index=True)
    filtered_df = filtered_df.sort_values(by=["STATE_NOTIFICATION_DATE", "LAYOFF_DATE"], ascending=False)
    filtered_row_count = filtered_df.shape[0]
    return filtered_df, filtered_row_count

def main():
    st.title("FloridaJobs WARN Notice Alerts")
    
    try:
        df, current_year = fetch_data()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return
    
    company_input = st.text_input("Search company name (comma separate for each company):")
    st.write("**You may leave input blank to return all results**")
    company_list = [x.strip().lower() for x in company_input.split(",")] if company_input else []

    if st.button("Search"):
        try:
            filtered_df, filtered_row_count = filter_results(df, company_list)
            st.dataframe(filtered_df, hide_index=True, column_config={"FILENAME": st.column_config.LinkColumn("FILENAME")})
            st.success(f"Returned {filtered_row_count} record(s) for {company_input} in {current_year}")
            csv_buffer = BytesIO()
            filtered_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            st.download_button(
                label="Download",
                data=csv_buffer,
                file_name=f"florida_warn_jobs_{current_year}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
