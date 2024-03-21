import os
import warnings

import streamlit as st
from dotenv import load_dotenv
from htmlTemplates import bot_template, css, user_template
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings, huggingface, huggingface_hub
from langchain_community.llms import LlamaCpp, llamacpp
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
    # embeddings = OpenAIEmbeddings()
    embeddings = huggingface.HuggingFaceInferenceAPIEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        api_key=os.environ["HUGGINGFACEHUB_API_TOKEN"],
        # model_kwargs={"device": "cpu"}, multi_process=True
    )
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    # llm = HuggingFacePipeline.from_model_id(
    #     model_id="lmsys/vicuna-7b-v1.3",
    #     task="text-generation",
    #     model_kwargs={"temperature": 0.01, "max_length": 1000},
    # )
    llm = llamacpp.LlamaCpp(model_path="models/llama-2-7b-chat.Q3_K_S.gguf", n_ctx=1024, n_batch=512)

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

    # for i, message in enumerate(st.session_state.chat_history):
    #     if i % 2 == 0:
    #         st.write(user_template.replace(
    #             "{{MSG}}", message.content), unsafe_allow_html=True)
    #     else:
    #         st.write(bot_template.replace(
    #             "{{MSG}}", message.content), unsafe_allow_html=True)

    pairs = [st.session_state.chat_history[i : i + 2] for i in range(0, len(st.session_state.chat_history), 2)]
    # Reverse pairs
    reversed_pairs = reversed(pairs)

    # Iterate over reversed pairs to maintain order of conversation
    for pair in reversed_pairs:
        st.write(user_template.replace("{{MSG}}", pair[0].content), unsafe_allow_html=True)
        st.write(bot_template.replace("{{MSG}}", pair[1].content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with PDFs", page_icon=":robot_face:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with PDFs :robot_face:")

    user_question = st.text_input("Ask questions about your documents:")

    # if user_question.lower().strip() == "exit":
    #     # st.session_state.chat_history = None
    #     # st.session_state.conversation = None
    #     st.warning("Conversation ended...")
    #     st.stop()

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


if __name__ == "__main__":
    main()
