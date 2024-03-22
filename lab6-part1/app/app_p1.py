import argparse
import glob
import os
import warnings

import streamlit as st
from dotenv import load_dotenv
from htmlTemplates import bot_template, css, user_template
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from PyPDF2 import PdfReader

warnings.simplefilter("ignore")

load_dotenv()


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=500, chunk_overlap=100, length_function=len)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4}),
        memory=memory,
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({"question": user_question})
    st.session_state.chat_history = response["chat_history"]

    pairs = [st.session_state.chat_history[i : i + 2] for i in range(0, len(st.session_state.chat_history), 2)]
    # Reverse pairs
    reversed_pairs = reversed(pairs)

    # Iterate over reversed pairs to maintain order of conversation
    for pair in reversed_pairs:
        st.write(user_template.replace("{{MSG}}", pair[0].content), unsafe_allow_html=True)
        st.write(bot_template.replace("{{MSG}}", pair[1].content), unsafe_allow_html=True)


def handle_userinput_stdout(user_question, conversation_chain):
    response = conversation_chain({"question": user_question})
    pairs = [response["chat_history"][i : i + 2] for i in range(0, len(response["chat_history"]), 2)]
    pair = pairs[-1]
    print("\033[94mUser:\033[0m", pair[0].content)
    print("\033[92mBot:\033[0m", pair[1].content, "\n")


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with PDFs", page_icon=":robot_face:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with PDFs :robot_face:")

    user_question = st.text_input("Ask questions about your documents (type 'exit' to quit):")

    if user_question.lower().strip() == "exit":
        # st.session_state.chat_history = None
        # st.session_state.conversation = None
        st.warning("Conversation ended...")
        st.stop()

    if user_question:
        if st.session_state.conversation is None:
            st.warning("Please upload PDFs and click on 'Process' first.")
        else:
            handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)

        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(vectorstore)


def driver(folder_path):
    # Search for pdfs under folder path
    pdf_docs = glob.glob(f"{folder_path}/**/*.pdf", recursive=True)

    print("\033[96mProcessing PDF files...\033[0m")
    # get pdf text
    raw_text = get_pdf_text(pdf_docs)

    # get the text chunks
    text_chunks = get_text_chunks(raw_text)

    # create vector store
    vectorstore = get_vectorstore(text_chunks)

    # Conversation chain
    conversation_chain = get_conversation_chain(vectorstore)
    print("\033[92mChatbot ready!\033[0m\n")

    while True:
        user_question = input("\033[93mAsk a question (type 'quit' to exit):\033[0m ")
        if user_question.lower().strip() == "quit":
            print("\033[91mConversation ended.\033[0m")
            break
        else:
            handle_userinput_stdout(user_question, conversation_chain)


if __name__ == "__main__":
    # main()
    parser = argparse.ArgumentParser(description="Chat with PDFs")
    parser.add_argument(
        "--folder_path",
        type=str,
        help="Path to the folder containing PDF files",
        default=os.path.dirname(__file__),
        required=False,
    )

    args = parser.parse_args()
    driver(args.folder_path)
