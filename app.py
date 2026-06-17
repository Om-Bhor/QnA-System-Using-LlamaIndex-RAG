import streamlit as st
from file_registry import register_file
from file_registry import get_uploaded_files
from file_registry import delete_file
from backend import process_file
from backend import ask_question


import os
 
st.set_page_config(
    page_title = "AI Academic Assistant",
    page_icon = "🎓",
    layout = "wide"
)
st.title("🎓 AI Academic Assistant")
st.write("Upload Study Material and Ask Question")

with st.sidebar:
    st.header("Faculty Panel")
    uploaded_files = st.file_uploader(
        "Uplaod Files",
        type = ["pdf","txt","docx"],
        accept_multiple_files = True
    )
    process_button = st.button(
    "Process Documents"
    )
    from file_registry import load_files_registry
    st.divider()
    st.subheader("Available Files")
    files = get_uploaded_files()
    for file in files:

        col1, col2 = st.columns([4,1])

        with col1:
            st.write(f"📄 {file}")

        with col2:

            if st.button(
                "🗑️",
                key=f"available_{file}"
            ):

                delete_file(file)

                st.rerun()
    st.subheader("Uploaded Files")
    files = load_files_registry()
    for file in files:

        col1, col2 = st.columns([4,1])

        with col1:
            st.write(f"📄 {file['filename']}")

        with col2:

            if st.button(
                "🗑️",
                key=f"uploaded_{file['filename']}"
            ):

                delete_file(file)

                st.rerun()
 
question = st.text_input(
    "Ask Your Question"
)
ask_button =st.button("Get Answer")
if process_button:
    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_path = os.path.join(
                "Data",
                uploaded_file.name
            )
            with open(save_path,"wb") as f:
                f.write(uploaded_file.getbuffer())
            process_file(save_path)
            register_file(uploaded_file.name)

        st.success("File Processed Successfully!")

if ask_button:
    if question:
        with st.spinner("Generating Answer"):
            response = ask_question(question)
        st.header("Answer")
        st.divider()
        st.markdown(response["answer"])
        st.subheader("Sources")
        for source in response["sources"]:
            st.write(source)