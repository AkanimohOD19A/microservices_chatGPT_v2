import openai
import pandas as pd
import streamlit as st
from datetime import date
from streamlit import cache
from datetime import datetime
from collections import Counter
import time


# import hydralit_components as hc

# st.set_page_config(layout='wide',initial_sidebar_state='collapsed',)

## Handling Cache
def cache_clear_dt(dummy):
    clear_dt = date.today()
    return clear_dt


if cache_clear_dt("dummy") < date.today():
    cache.clear_cache()


def create_action(adj_response_type, response_type):
    # for adjective in adj_response_type:
    #     prefix_adj = adjective.join(adjective).split(',')
    strList = [str(i) for i in adj_response_type]
    myString = ", ".join(strList)
    prefix_keyword = myString + " and " + str(response_type)
    return prefix_keyword


def ChatGPT(user_query):
    '''
    This function uses the OpenAI API to generate a response to the given
    user_query using the ChatGPT model
    :param user_query:
    :return:
    '''
    # Use the OpenAI API to generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=user_query,
        max_tokens=1024,
        n=1,
        temperature=0.5,
    )
    response = completion.choices[0].text
    return response


## Word count
def word_count(string):
    strip_words = (len(string.strip().split(" ")))
    return strip_words


response = ""


@st.cache_data
def api_call_on(query):
    '''
    This function gets the user input, pass it to ChatGPT function and
    displays the response
    '''

    response = ChatGPT(query)
    return response


# Set the model engine and your OpenAI API key
model_engine = "text-davinci-003"
openai.api_key = st.secrets["Openai_SECRET_KEY"]

st.title("Auto-Query Customer engagements with ChatGPT")
st.markdown("##### This is a web application that allows you to interact with "
            "the OpenAI API's implementation of the ChatGPT model.")

st.markdown('##')  ##-> Empty Space Divider

st.sidebar.header("Instructions")
st.sidebar.info(
    '''
       Enter a **query** in the **text box** and **press enter** to receive 
       a **response** from the ChatGPT
    '''
)
# Get user input
user_query = st.text_input("Enter query here, to exit enter :q",
                           "what is Customer Lifeclycle?")

# os.environ["Openai_SECRET_KEY"] ==  st.secrets["Openai_SECRET_KEY"]
option = st.sidebar.selectbox("How would you like to run your query?", ("Use Keywords",
                                                                        "Just run"))
## start timer
start = time.time()
if option == "Use Keywords":
    ## Read a list of adjectives and actions
    adjs = pd.read_csv('./prefix_data/adjectives.csv')
    actions = pd.read_csv('./prefix_data/document.csv')

    adj_response_type = st.sidebar.multiselect("Please specify keywords", adjs)
    response_type = st.sidebar.selectbox("Please specify action", actions)
    if adj_response_type != "" and response_type != "":
        prefix_keyword = create_action(adj_response_type, response_type)
        prefix_query = f'A {prefix_keyword} response to {user_query}'
        st.sidebar.markdown('##')  ##-> Empty Space Divider
        if st.sidebar.button("Run"):
            with st.spinner('Your query is running...'):
                response = api_call_on(prefix_query)
                st.success(f"{response}")
else:
    response = api_call_on(user_query)
    st.success(f"{response}")
## End Timer
end = time.time()
## Query Time
query_time = end - start

st.markdown('##')  ##-> Empty Space Divider
st.markdown("---")  ## Divider
col1, col2, col3 = st.columns(3)

with col1:
    st.warning("Query Data")
    st.write('You selected: ', option)
    if option == "Just run":
        st.write('Keywords: None Selected')
    else:
        st.write('Keywords: ', prefix_keyword)

with col2:
    st.warning("Basic Text Analysis")
    st.write("Query Time :   s", round(query_time / 1000, 2), "-", round(query_time, 2), "ms")
    st.write("Word Count: ", word_count(response) - 1)

with col3:
    # st.warning("Text Distribution")
    words = response.split()
    wordCount = Counter(words)
    wordCountDf = pd.DataFrame(wordCount.items(),
                               columns=['word', 'count'])
    st.dataframe(wordCountDf, height=200, use_container_width=True)

st.sidebar.markdown("---")  ## Divider
st.sidebar.info("We have a bunch of keywords to articulate our query, this might not meet your requirement. "
                "Click on the button below to modify.")
if st.sidebar.button("Edit Keywords"):
    ### Lifecycle of Dataframe
    ## Read csv
    df1 = pd.read_csv('./prefix_data/actions.csv', names=['ACTIONS'], header=1)
    df2 = pd.read_csv('./prefix_data/adjectives.csv', names=['ADJECTIVES'], header=1)

    ## Editable Dataframe
    editable_df = st.sidebar.experimental_data_editor(pd.concat([df1, df2], axis=1), num_rows="dynamic")

    ## Update csv
    editable_df['ACTIONS'].to_csv('./prefix_data/actions.csv', index=False)
    editable_df['ADJECTIVES'].to_csv('./prefix_data/adjectives.csv', index=False)

st.sidebar.info("Made with ❤ by the AfroLogicInsect")
