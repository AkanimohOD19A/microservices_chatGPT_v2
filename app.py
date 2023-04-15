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


# def create_action(adj_response_type, response_type):
#     # for adjective in adj_response_type:
#     #     prefix_adj = adjective.join(adjective).split(',')
#     strList = [str(i) for i in adj_response_type]
#     myString = ", ".join(strList)
#     prefix_keyword = myString + " and " + str(response_type)
#     return prefix_keyword

def create_action(tone_response_type, comprehension_response_type,
                  style_response_type, revision_response_type):
    strList = [str(tone_response_type), str(comprehension_response_type),
               str(style_response_type), str(revision_response_type)]
    prefix_keyword = ", ".join(strList)
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
    tone = pd.read_csv('./prefix_data/tone.csv')
    comprehension = pd.read_csv('./prefix_data/comprehension.csv')
    revisions = pd.read_csv('./prefix_data/revision.csv')
    style = pd.read_csv('./prefix_data/style.csv')

    tone_response_type = st.sidebar.selectbox("Please specify Tone*", tone)
    comprehension_response_type = st.sidebar.selectbox("Please specify Reader Comprehension*", comprehension)
    style_response_type = st.sidebar.selectbox("Please specify your style*", style)
    revision_response_type = st.sidebar.selectbox("Please specify Degree of Revision", revisions)
    response_length = st.sidebar.slider("Please specify the length of words to return", 25, 750, 100)
    if tone_response_type != "" and comprehension_response_type != "" and style_response_type != "" \
            or revision_response_type != "" or response_length != "":
        prefix_keyword = create_action(tone_response_type, comprehension_response_type,
                                       style_response_type, revision_response_type)
        prefix_query = f'Using Keywords: {prefix_keyword} provide a response to {user_query} ' \
                       f'with a length of {response_length} words'
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

# st.sidebar.markdown("---")  ## Divider
# st.sidebar.info("We have a bunch of keywords to articulate our query, this might not meet your requirement. "
#                 "Click on the button below to modify.")
# if st.sidebar.button("Edit Keywords"):
#     ### Lifecycle of Dataframe
#     ## Read csv
#     df1 = pd.read_csv('./prefix_data/tone.csv', names=['ACTIONS'], header=1)
#     df2 = pd.read_csv('./prefix_data/tone.csv', names=['ADJECTIVES'], header=1)

#     ## Editable Dataframe
#     editable_df = st.sidebar.experimental_data_editor(pd.concat([df1, df2], axis=1), num_rows="dynamic")

#     ## Update csv
#     editable_df['ACTIONS'] = editable_df['ACTIONS'].to_csv('./prefix_data/tone.csv', index=False)
#     editable_df['ADJECTIVES'] = editable_df['ADJECTIVES'].to_csv('./prefix_data/adjectives.csv', index=False)

st.sidebar.info("Made with ❤ by the AfroLogicInsect")
