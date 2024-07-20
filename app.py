import streamlit as st
from rohit_section import generate_response_from_chunks, get_relevant_chunks, create_index, extract_text_from_pdfs, clean_text, chunk_text, store_chunks_in_pinecone
from translate import translate, generate_audio

# Streamlit app

# Display the custom logo using st.image
st.sidebar.image("logo.jpg")
st.title("Aryacci Research Paper Bot")
st.sidebar.title("PDF Research Assistant")
pdf_files = st.sidebar.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

lang = st.sidebar.radio("Choose", ["English", "French", "Spanish"])

if pdf_files:

    if 'index' not in st.session_state:
        st.session_state.index = None

    if st.session_state.index is None:
        with st.spinner("Processing PDFs..."):
            # Extract text from all uploaded PDFs
            text = extract_text_from_pdfs(pdf_files)
            cleaned_text = clean_text(text)
            chunks = chunk_text(cleaned_text)
            
            # Create Pinecone index and store chunks
            st.session_state.index = create_index()
            if st.session_state.index:
                store_chunks_in_pinecone(chunks, st.session_state.index)
                st.success("PDFs processed and indexed successfully!")
            else:
                st.error("Failed to create Pinecone index.")
    
    # Query handling
    if st.session_state.index:
        query = st.text_input("Enter your question:")
        if st.button("Ask"):
            with st.spinner("Searching for answers..."):
                relevant_chunks = get_relevant_chunks(query, st.session_state.index)
                response = generate_response_from_chunks(relevant_chunks, query)
                
                if lang != "English":
                    translated_response = translate(response, lang)
                    st.write(translated_response)
                    audio_io = generate_audio(translated_response, lang)
                else:
                    st.write(response)
                    audio_io = generate_audio(response, lang)
                    
                # Generate and display audio response
                st.audio(audio_io, format='audio/mp3')
                st.download_button(label="Download Audio Response", data=audio_io, file_name="response.mp3", mime="audio/mp3")

        if st.button("Ask another question"):
            st.experimental_rerun()
        
        if st.button("End conversation"):
            st.session_state.index = None
            st.stop()  # Close the Streamlit app
