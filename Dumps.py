import requests
import openpyxl
import os
import time
from urllib.parse import quote

def create_dump_from_excel(excel_file_path, output_folder):
    # Loading Excel file
    workbook = openpyxl.load_workbook(excel_file_path)
    sheet = workbook.active

    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

   
    for row in sheet.iter_rows(min_row=2, values_only=True):
        url = row[0]  # URLs are in the first column

        try:
            # Retry mechanism with a delay between retries
            max_retries = 3
            for retry_count in range(max_retries):
                try:
                    # GET request 
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()  # Raise an exception for bad responses

                   
                    sanitized_url = quote(url, safe='-_')
                    filename = os.path.join(output_folder, f"{sanitized_url}.html")

                    with open(filename, 'w', encoding='utf-8') as file:
                        file.write(response.text)

                    print(f"Successfully downloaded {url}")
                    break  # Break the retry loop if successful

                except requests.RequestException as e:
                    if retry_count < max_retries - 1:
                        # Retring with a delay between retries
                        print(f"Retrying ({retry_count + 1}/{max_retries}) after error: {e}")
                        time.sleep(5) 
                    else:
                        print(f"Error downloading {url} after {max_retries} retries: {e}")

        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")



if __name__ == "__main__":

    excel_file_path = r'C:\Users\AJAY RAJARAM\Desktop\Bard Chat\Dump_links.xlsx'
    output_folder = r'C:\Users\AJAY RAJARAM\Desktop\Bard Chat\Dumps'

    
    create_dump_from_excel(excel_file_path, output_folder)
