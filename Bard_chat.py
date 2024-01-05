# Importing libraries
import streamlit as st
from bardapi import Bard
from serpapi import GoogleSearch
from streamlit_chat import message
import os
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from summarizer import Summarizer  
import webbrowser

# Define API_KEYS 
os.environ["_BARD_API_KEY"] = "Browser Cookie"
SERP_API_KEY = "API KEY"

# Define List of trusted domain names as of yet I just stored it here, if needed can be stored in an excel file or even in db and can be accessed
trusted_domains = ["climate.nasa.gov","climatefactchecks.org","eu.usatoday.com","www.ncbi.nlm.nih.gov"
,"diabetesjournals.org"
,"www.thip.media"
,"www.sciencedaily.com"
,"www.cancer.gov"
,"www.cancer.org"
,"factcheck.afp.com"
,"climatefactchecks.org"
,"leadstories.com"
,"www.cell.com"
,"factly.in"
,"eu.usatoday.com"
,"www.fda.gov"
,"www.nia.nih.gov"
,"www.aap.com.au"
,"www.politifact.com"
,"www.thequint.com"
,"www.snopes.com"
,"pubmed.ncbi.nlm.nih.gov"
,"news.cancerresearchuk.org"
,"fullfact.org"
,"climate.nasa.gov"
,"www.mdanderson.org"
,"www.medicalnewstoday.com"
,"timesofindia.indiatimes.com"
,"www.ctif.org"
,"www.poynter.org"
,"www.nissan-global.com"
,"www.factcheck.org"
,"apnews.com"
,"www.logicallyfacts.com"
,"www.sochfactcheck.com"
,"theswisstimes.ch"
,"usa.nissannews.com"
]  #  more domain names can be added if needed

st.set_page_config(page_title="Claim Verification and Summarization", layout="wide")

with st.sidebar:
    image = st.sidebar.image('Bard Chat/ovgu logo.png', caption ='Let Me Google That For You Webapp')
    page = st.selectbox("Select a page", ["Bard Chat", "Google Search Chat", "Search and Summarize Text"])

def response_api(prompt):
    message=Bard().get_answer(str(prompt))['content']
    return message

def search_serpapi(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results["organic_results"]

def user_input(page):
    input_text = st.text_input(f"Enter your prompt for {page}: ")
    return input_text

if 'generate_bard' not in st.session_state:
    st.session_state['generate_bard'] = {}

if 'past_bard' not in st.session_state:
    st.session_state['past_bard'] = []

if 'generate_google' not in st.session_state:
    st.session_state['generate_google'] = {}

if 'past_google' not in st.session_state:
    st.session_state['past_google'] = []

if page == "Bard Chat":
    user_text = user_input(page)

    if user_text:
        output_text = response_api(user_text)
        st.session_state.generate_bard[user_text] = output_text
        st.session_state.past_bard.append(user_text)

    if st.session_state['generate_bard']:
        for i in range(len(st.session_state['generate_bard']) - 1, -1, -1):
            message(st.session_state['past_bard'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state.generate_bard[st.session_state['past_bard'][i]])


elif page == "Google Search Chat":
    user_text = user_input(page)

    if user_text:
        output_text = search_serpapi(user_text)
        st.session_state.generate_google[user_text] = output_text
        st.session_state.past_google.append(user_text)

    if st.session_state['generate_google']:
        for i in range(len(st.session_state['generate_google']) - 1, -1, -1):
            message(st.session_state['past_google'][i], is_user=True, key=str(i) + '_user')
            message_text = ""
            for result in st.session_state.generate_google[st.session_state['past_google'][i]]:
                message_text += f"{result['title']}\n{result['link']}\n{result['snippet']}\n\n"
            message(message_text)

elif page == "Search and Summarize Text":
    user_text = user_input(page)

    if user_text:
        # organic results from SerpApi
        endpoint_serpapi = 'https://serpapi.com/search'
        params_serpapi = {'q': user_text, 'api_key': SERP_API_KEY}

        try:
            response_serpapi = requests.get(endpoint_serpapi, params=params_serpapi)
            response_serpapi.raise_for_status()
            data_serpapi = response_serpapi.json()
            organic_results_serpapi = data_serpapi.get('organic_results', [])

            if organic_results_serpapi:
                st.write("Bot:", "SerpApi Organic Results:")

                for result in organic_results_serpapi:
                    title = result.get('title', 'N/A')
                    link = result.get('link', 'N/A')
                    source_info_link = result.get('source_info_link', 'N/A')

                    # ectracting the domain name from the link
                    domain_name = urlparse(link).hostname

                    # Check if the domain name matches any trusted domain name
                    if domain_name in trusted_domains:
                        st.write("Bot:", f"Title: {title}")
                        st.write("Bot:", f"Link: {link}")
                    #   st.write("Bot:", f"Source Info Link: {source_info_link}")

                        # summary of the redirected page by using bert-extractive-summarizer
                        try:
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                            response_page = requests.get(link, headers=headers)
                            response_page.raise_for_status()
                            soup = BeautifulSoup(response_page.content, 'html.parser')
                            page_text = ' '.join([p.text for p in soup.find_all('p')])

                        
                            summarizer = Summarizer()
                            summary = summarizer(page_text)

                            st.write("Bot:", "\nPage Summary:")
                            st.write("Bot:", summary)

                        except requests.exceptions.RequestException as e:
                            st.write("Bot:", f"Error fetching page content: {e}")

                        # Redirect to the trusted link
                        st.write("Bot:", f"Redirecting to trusted link: {source_info_link}")
                        webbrowser.open(source_info_link)

                        break  # Stop processing if a match is found

            else:
                st.write("Bot:", "No organic results from SerpApi or an error occurred.")

        except requests.exceptions.RequestException as e:
            st.write("Bot:", f"Error making the request to SerpApi: {e}")

