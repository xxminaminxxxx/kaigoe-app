import streamlit as st
from openai import OpenAI
import base64
from streamlit_mic_recorder import mic_recorder

# --- 1. ページ設定 ---
st.set_page_config(page_title="KAIGOE Demo", layout="centered")

# --- 2. APIキーの設定 ---
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = "sk-xxxx"

client = OpenAI(api_key=api_key)

# --- 3. サイドバー設定 ---
with st.sidebar:
    st.title("💡 デモ設定")
    user_bio = st.text_area("自分史設定", 
        value="よしおさん（85歳）。元・電気エンジニア。岐阜県出身。孫のサクラちゃんが大好き。",
        height=150)

# --- 4. メインUI ---
st.title("👵 KAIGOE：親友AI")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": f"あなたは利用者の親友です。以下の背景を持つ相手に優しく、回想法を交えて話して：{user_bio}"}]

# 会話のログを先に表示
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# --- 5. 音声入力ボタンを「一番下」に配置 ---
st.divider()
st.write("👇 ボタンを押して話しかけてください")
audio_data = mic_recorder(
    start_prompt="🔴 声で話しかける（クリックして開始）",
    stop_prompt="⏹️ 話し終わったらクリック",
    just_once=True,
    key='recorder'
)

# 音声が入力された時の処理
if audio_data:
    with st.spinner("あなたの声を聴いています..."):
        audio_bytes = audio_data['bytes']
        with open("temp_audio.mp3", "wb") as f:
            f.write(audio_bytes)
        
        with open("temp_audio.mp3", "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
            user_input = transcript.text

    # 履歴に追加して即座に画面を更新
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # AIの返答生成
    response = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    
    # 音声生成
    audio_response = client.audio.speech.create(model="tts-1", voice="shimmer", input=msg)
    b64 = base64.b64encode(audio_response.content).decode()
    
    # ページを再起動して最新の会話と音声プレーヤーを表示
    st.rerun()

# 一番新しい返答に音声プレーヤーを付ける（自動再生用）
if st.session_state.messages[-1]["role"] == "assistant":
    # 再生が終わった後に何度も鳴らないよう、最新のメッセージの時だけプレーヤーを出す
    audio_html = f'<audio src="data:audio/mp3;base64,{b64}" autoplay controls style="width: 100%; margin-top: 10px;"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)
