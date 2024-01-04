import pandas as pd
from urllib.parse import urlparse

# Loading the Excel sheet
excel_file = "Domain.xlsx"
sheet_name = "URL_FILE"
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Extracting domain names
df['Domain Name'] = df['Evidence link'].apply(lambda url: urlparse(url).netloc if pd.notna(url) else '')

# extracetd values are stored in the exel file 
df.to_excel(excel_file, sheet_name=sheet_name, index=False)


print(df[['Evidence link', 'Domain Name']])
