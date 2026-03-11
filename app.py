import streamlit as st
from openai import OpenAI
import base64

# --- 1. ページ設定 ---
st.set_page_config(page_title="KAIGOE Demo", layout="centered")

# --- 2. APIキーの設定（StreamlitのSecretsから取得） ---
# 注意：Streamlit CloudのSettings > Secrets に OPENAI_API_KEY を設定している必要があります
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = "sk-xxxxxxxxxxxx" # ここはSecretsが優先されるのでそのままでOK

client = OpenAI(api_key=api_key)

# --- 3. 投資家向けサイドバー ---
with st.sidebar:
    st.title("💡 デモ用コントロール")
    st.write("利用者の背景を書き換えると、AIの反応が即座に変わります。")
    
    user_bio = st.text_area("自分史（バイオグラフィー）設定", 
        value="よしおさん（85歳）。元・電気エンジニア。岐阜県出身。クラシック音楽が好き。少し耳が遠いので、ゆっくり話してほしい。",
        height=150)
    
    st.divider()
    if st.button("今日の日報を生成（デモ）"):
        st.subheader("📋 スタッフ向け日報")
        st.info("【様子】昔のダム建設の話をされ、非常に活気がありました。\n【予兆】言葉の詰まりはなく、認知機能は安定しています。")

# --- 4. メイン画面のUI ---
st.title("👵 KAIGOE：親友AI")
st.caption("家族以上にその人を知っている、パーソナル対話AI")

# 会話履歴の保持
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"あなたは『KAIGOE』というサービスのAIです。以下の利用者の親友として、相手を尊重し、回想法（昔の話を引き出す）を取り入れて優しく対話してください：{user_bio}"}
    ]

# 履歴の表示
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# --- 5. 対話処理 ---
if prompt := st.chat_input("おじいちゃん・おばあちゃんに話しかけてください"):
    # ユーザーの入力を追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # AIの返答
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages
        )
        msg = response.choices[0].message.content
        st.write(msg)
        
        # --- 音声生成（再生ボタンを表示する確実な設定） ---
        try:
            audio_response = client.audio.speech.create(
                model="tts-1",
                voice="shimmer", # 落ち着いた女性の声
                input=msg
            )
            b64 = base64.b64encode(audio_response.content).decode()
            
            # 再生ボタン（プレーヤー）を表示し、自動再生も試みる
            audio_html = f'''
                <audio controls autoplay style="width: 100%;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                '''
            st.markdown(audio_html, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"音声生成エラー: {e}")

    # 履歴に保存
    st.session_state.messages.append({"role": "assistant", "content": msg})
