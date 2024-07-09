import streamlit as st
from openai import OpenAI
import mysql.connector

# DBへ接続
conn = mysql.connector.connect(
    user='smairuser',
    password='smairuser',
    host='www.ryhintl.com',
    database='smair',
    port=36000
)

# DBの接続確認
if not conn.is_connected():
    raise Exception("MySQLサーバへの接続に失敗しました")

cur = conn.cursor(dictionary=True)  # 取得結果を辞書型で扱う設定
#cur = conn.cursor()

query__for_fetching = """
SELECT api_key FROM openai_payload;
"""

cur.execute(query__for_fetching)

data1 = {'ID':[],'Issue':[],'Status':[],'Priority':[],'Date Submitted':[]}
for fetched_line in cur.fetchall():
    openai_api_key = fetched_line['api_key']

cur.close()


# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:

        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)
