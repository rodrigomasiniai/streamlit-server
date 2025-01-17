import streamlit as st
from txtai.pipeline import Textractor
from txtai.embeddings import Embeddings
import nltk
nltk.download('punkt')
  #Web Scraping
import bs4 as bs
import urllib.request
import re
from PyPDF2 import PdfReader
from nltk import tokenize

# Create embeddings model, backed by sentence-transformers & transformers
embeddings = Embeddings({"path": "sentence-transformers/nli-mpnet-base-v2"})

url = "https://cdn.pixabay.com/photo/2022/02/25/09/23/background-7033808_1280.jpg"

st.title("AIP-S³")
st.write("AI Powered Smart Search System")
st.image(url)

st.markdown('_Welecome to Question Answering System 🧠 🤖_')

a = st.sidebar.radio("SELECT -", ['File Upload', 'Website'])

## webscrap function
def my_web():
  from txtai.pipeline import Textractor
  textract = Textractor(sentences=True)
  data_lines = []
  total_lines = []
  article_text = " "
  for i in (locations_max):
    #print(i)
    scraped_data = urllib.request.urlopen(i)
    article = scraped_data.read()
    parsed_article = bs.BeautifulSoup(article,'lxml')
    paragraphs = parsed_article.find_all('p')
    for p in paragraphs:
      article_text += p.text
    lines = textract(i)
    data_lines.append(lines)
  total_lines = []
  for i in data_lines:
    total_lines += i
  seq = embeddings.similarity(quer, total_lines)
  three_most = seq[0:3]
  indexes = []
  for i in three_most:
    indexes.append(i[0])
  for j in indexes:
    st.write(total_lines[j])


if a == 'File Upload' :
  uploaded_files = st.file_uploader("Upload files - ", accept_multiple_files=True , 
                  type = ['pdf', 'docx' , 'txt'] )

# for query
    
  quer = st.text_input('ask me anything!', placeholder = 'ex - what is AI?')
  st.write('Your query is - ', quer)  

  if st.button("Confirm!"):
    text_raw = ""
    for i in uploaded_files:
      if i.type == "application/pdf" :
        reader = PdfReader(i)
      # print(reader.numPages) 
        pageObj = reader.getPage(0)
      # print(pageObj.extractText())
        text_raw += pageObj.extract_text() + "\n"

    all_tokens = tokenize.sent_tokenize(text_raw)
    seq = embeddings.similarity(quer, all_tokens)

    three_most = seq[0:3]
    indexes = []
    for i in three_most:
      indexes.append(i[0])
      # print(indexes)
    for j in indexes:
      st.write(all_tokens[j])


## web
else:
  number = st.number_input('Insert a number of Links -',value =1, step =1)
  st.write('Number of web pages - ', number)  
  st.markdown("---")
  locations_max = []
  for i in range (number) :
    loc = st.text_input('Enter the URL :', placeholder = 'ex- https:\\', key = i)
    locations_max.append(loc)

  # for query
  quer = st.text_input('ask me anything!', placeholder = 'ex - what is AI?')
  st.write('Your query is - ', quer)
  
  if st.button('Confirm!'):
     st.write('Confirmed')
     my_web()
  else:
     st.write('')