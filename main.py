import streamlit as st

from gigachat_api import get_access_token, send_prompt, send_prompt_and_get_response

st.title("Ботяра")

if "access_token" not in st.session_state:
    try:
        st.session_state.access_token = get_access_token()
        st.toast("Токен на базе")
    except Exception as e:
        st.toast(f"Сорян:( токен не получен{e}")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "ai", "content": "Чем вам помочь?"}]

for msg in st.session_state.messages:
    if msg.get("is_image"):
        st.chat_message(msg["role"]).image(msg["content"])
    else:
        st.chat_message(msg["role"]).write(msg["content"])

if user_prompt := st.chat_input():
    st.chat_message("user").write(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.spinner("Формирую ответ"):
        response, is_image = send_prompt_and_get_response(user_prompt, st.session_state.access_token)
        if is_image:
            st.chat_message("ai").image(response)
            st.session_state.messages.append({"role": "ai", "content": response, "is_image": True})
        else:
            st.chat_message("ai").write(response)
            st.session_state.messages.append({"role": "ai", "content": response})