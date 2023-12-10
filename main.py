import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import streamlit as st

nltk.download('stopwords')
nltk.download('punkt')
st.title("SEO Analyzer")
url = st.text_input("Enter URL")

def seo_analysis(url):
    # Save the good and the warnings in lists
    good = []
    bad = []
    linkcheck = []
    # Send a GET request to the website
    response = requests.get(url)
    # Check the response status code
    if response.status_code != 200:
        st.error("Error: Unable to access the website.")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text()
        good.append("<Title> " + title)
    else:
        bad.append("Title does not exist! Add a Title")

    # Extract the description
    meta_description_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_description_tag and 'content' in meta_description_tag.attrs:
        description = meta_description_tag['content']
        good.append("<Meta Description> " + description)
    else:
        bad.append("Meta Description does not exist! Add a Meta Description")

    # Define the heading tags to check
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    # Dictionary to keep track of which headings are found
    found_headings = {tag: False for tag in heading_tags}
    # Iterate over all headings in the HTML
    for h in soup.find_all(heading_tags):
        good.append(f"{h.name} --> {h.text.strip()}")
        found_headings[h.name] = True
    # Check which headings were not found
    for tag in heading_tags:
        if not found_headings[tag]:
            bad.append(f"No {tag.upper()} found!")

    # Extract the images without Alt
    for img in soup.find_all('img', alt=''):
        img_src = img.get('src', '')  # Get the 'src' attribute, default to empty string if not found
        if img_src:
            # Create a Markdown string with the image URL as a hyperlink
            bad.append(f"No Image Alt: [{img_src}]({img_src})")

    # Extract keywords
    # Grab the text from the body of html
    bod = soup.find('body').text

    # Extract all the words in the body and lowercase them in a list
    words = [i.lower() for i in word_tokenize(bod)]

    # Grab a list of English stopwords
    sw = nltk.corpus.stopwords.words('english')
    new_words = []

    # Put the tokens which are not stopwords and are actual words (no punctuation) in a new list
    for i in words:
        if i not in sw and i.isalpha():
            new_words.append(i)

    # Extract the frequency of the words and get the 10 most common ones
    freq = nltk.FreqDist(new_words)
    keywords = freq.most_common(10)
    # Extract just the keywords from the tuples
    optimized_keywords = [word[0] for word in keywords]

    # Analyze the links
    links = soup.find_all('a')
    for link in links:
        if 'href' in link.attrs:
            link_text = link.get_text().lower()
            if not any(keyword in link_text for keyword in optimized_keywords):
                linkcheck.append(f"Link Optimization: {link.get('href')}")

    # Extract the bigrams from tokens
    bi_grams = ngrams(new_words, 2)
    tri_grams = ngrams(new_words, 3)
    freq_bigrams = nltk.FreqDist(bi_grams)
    ten_bigrams = freq_bigrams.most_common(10)
    freq_trigrams = nltk.FreqDist(tri_grams)
    ten_trigrams = freq_trigrams.most_common(10)

    # Print the results
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Keywords", "Bigrams", "Trigrams", "Link Checker", "Good", "Bad"])
    with tab1:
        for i in keywords:
            st.text(i)
    with tab2:
        for i in ten_bigrams:
            st.text(i)
    with tab3:
        for i in ten_trigrams:
            st.text(i)
    with tab5:
        for i in good:
            st.success(i)
    with tab6:
        for i in bad:
            st.error(i)
    with tab4:
        for i in linkcheck:
            st.info(i)

# Call the function to see the results
if url:
    seo_analysis(url)
else:
    st.write("Please enter a URL to analyze.")

