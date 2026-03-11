import streamlit as st
from openai import OpenAI
import base64

# APIキーの設定（公開時は後述のSecrets機能を使います）
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="KAIGOE Demo", layout="centered")

# 投資家に説明するためのサイドバー
with st.sidebar:
    st.title("💡 デモ設定")
    biography = st.text_area("自分史データ（息子は48歳。息子の名前はよしろう。息子の奥さんは45歳。息子の奥さんの名前はよしこ）", 
        value="よしおさん。85歳。元電気エンジニア。岐阜県出身。孫のサクラちゃんが大好き。")
    if st.button("日報（見守りログ）を生成"):
        st.info("ここにAIが会話を要約したスタッフ向け日報が表示されます（実装予定）")

st.title("👵 KAIGOE 対話デモ")
st.write("「その人を知っている親友」としてのAI体験")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": f"あなたは利用者の親友です。以下の背景を持つ相手に優しく話して：{biography}"}]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

if prompt := st.chat_input("お話ししましょう"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
        msg = response.choices[0].message.content
        st.write(msg)
        
        # 音声の生成と自動再生
        audio = client.audio.speech.create(model="tts-1", voice="alloy", input=msg)
        b64 = base64.b64encode(audio.content).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay></audio>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": msg})