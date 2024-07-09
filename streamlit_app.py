import streamlit as st
import mysql.connector
#from openai import OpenAI
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template

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

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


#def get_vectorstore(text_chunks):
def get_vectorstore():
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local("./vectorstore", embeddings,allow_dangerous_deserialization=True)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="PDF エンベディング",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
        #st.session_state.conversation = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
        #st.session_state.chat_history = ""

    st.header("PDF エンベディング :books:")
    user_question = st.text_input("検索したい質問を入力して下さい。:")
    if user_question:
        handle_userinput(user_question)
        #handle_userinput("正職員の人件費時間単価の積算方法について教えて")
        
    # create vector store
    vectorstore = get_vectorstore()
                #vectorstore = get_vectorstore()

    # create conversation chain
    st.session_state.conversation = get_conversation_chain(vectorstore)

    #with st.sidebar:
        #st.subheader("PDF ドキュメント")
        #pdf_docs = st.file_uploader(
            #"アップロードするPDFファイルを選択して'アップロード'をクリックして下さい。", accept_multiple_files=True)
        #if st.button("アップロード"):
            #with st.spinner("処理中..."):
                # get pdf text
                #raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                #text_chunks = get_text_chunks(raw_text)

                # create vector store
                #vectorstore = get_vectorstore(text_chunks)
                #vectorstore = get_vectorstore()

                # create conversation chain
                #st.session_state.conversation = get_conversation_chain(
                    #vectorstore)
                    


if __name__ == '__main__':
    main()



