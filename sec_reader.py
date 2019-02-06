# Setup
import pandas as pd
import pickle
from datetime import datetime

# List of Investments
CIK_LIST = [{
    'name': 'Buffett',
    'cik': '0001067983'
}, {
    'name': 'JPMorgan',
    'cik': '0000019617'
}, {
    'name': 'Bridgewater',
    'cik': '0001350694'
}, {
    'name': 'Renaissance',
    'cik': '0001037389'
}, {
    'name': 'TwoSigma',
    'cik': '0001179392'
}, {
    'name': 'DEShaw',
    'cik': '0001009207'
}, {
    'name': 'Millenium',
    'cik': '0001273087'
}, {
    'name': 'Bluecrest',
    'cik': '0001610880'
}, {
    'name': 'AQR',
    'cik': '0001167557'
}]

CIK_LIST = [{'name': 'Buffett', 'cik': '0001067983'}]

output_names = ['Current', 'Previous']

for item in CIK_LIST:
    # Get list of filings
    p1 = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK='
    p2 = '&type=13F-HR'
    path = p1 + item['cik'] + p2
    print('Getting latest {}, {}'.format(item['name'], path))
    raw_data = pd.read_html(path)[2]

    # Filter by specific id
    filing_id_filter = raw_data['Filings'] == '13F-HR'
    filing_data = raw_data[filing_id_filter].reset_index()
    print(filing_data)

    for index, value in enumerate(output_names):
        # Get cell based on integer index and column name
        desc = filing_data.iloc[index]['Description']
        date = filing_data.iloc[index]['Filing Date']

        # Get the account number
        acct_no = desc.split(',')[1].split(' ')[2].split('\xa0')[0].replace(
            '-', '')
        print('{}, {}'.format(acct_no, date))

        # Get list of documents inside one filing
        p1 = 'https://www.sec.gov/Archives/edgar/data/'
        p2 = item['cik'] + '/' + acct_no
        path = p1 + p2
        print('Getting html {}, {}'.format(item['name'], path))
        doc_data = pd.read_html(path)[0]

        # Filter for xml files that don't have primary in the name
        xml_filter = doc_data['Name'].str.contains('xml')
        primary_filter = doc_data['Name'].str.contains('primary')
        data = doc_data[xml_filter & ~primary_filter].reset_index()
        file_name = data.iloc[0]['Name']
        print(file_name)

        # Download and cache xml file
        html_path = path + '/' + 'xslForm13F_X01/' + file_name
        cache_path = 'api_data/' + '{}_{}.pkl'.format(item['name'], date)
        try:
            f = open(cache_path, 'rb')
            df = pickle.load(f)
            print('Loaded {} from cache'.format(item['name']))
        except (OSError, IOError):
            print('Downloading {}, {}'.format(item['name'], html_path))
            df = pd.read_html(html_path)[3]
            df = df.iloc[3:][[0, 3, 4]]
            df.columns = ['Name', 'Value', 'Amount']
            df['Value'] = df['Value'].astype(int)
            df['Amount'] = df['Amount'].astype(int)
            df.to_pickle(cache_path)
