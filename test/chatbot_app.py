import os
import time
from io import BytesIO

import streamlit as st
import chatbot_lib as glib

st.set_page_config(page_title="Chatbot")
st.title("Chatbot")

if 'memory' not in st.session_state:
    st.session_state.memory = glib.get_memory()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

voice_output = st.checkbox("음성 출력", value=False)

input_text = st.chat_input("Chat with your bot here")

if input_text:
    with st.chat_message("user"):
        st.markdown(input_text)
    st.session_state.chat_history.append({"role": "user", "text": input_text})

    chat_response = glib.get_chat_response(input_text=input_text, memory=st.session_state.memory)

    with st.chat_message("assistant"):
        st.markdown(chat_response)
    st.session_state.chat_history.append({"role": "assistant", "text": chat_response})

    if voice_output:
        audio_bytes = BytesIO()
        glib.synthesize_speech(chat_response, audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format='audio/mp3', start_time=0)
        time.sleep(0.5)  # 오디오 재생 시간을 주기 위해 잠시 대기