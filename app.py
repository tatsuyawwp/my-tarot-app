import streamlit as st
import random
from openai import OpenAI
from datetime import date

# 1. 準備：タロットカードデータ（リンクを非常に安定したものに固定）
TAROT_DATA = {
    TAROT_DATA = {
    "愚者": "https://raw.githubusercontent.com/tatsuyawwp/my-tarot-app/main/fool.png",
    "魔術師":"https://raw.githubusercontent.com/tatsuyawwp/my-tarot-app/main/magician.png",
    "女教皇": "https://upload.wikimedia.org/wikipedia/commons/8/8d/RWS_Tarot_02_High_Priestess.jpg",
    "女帝": "https://upload.wikimedia.org/wikipedia/commons/a/af/RWS_Tarot_03_Empress.jpg",
    "皇帝": "https://upload.wikimedia.org/wikipedia/commons/c/c3/RWS_Tarot_04_Emperor.jpg",
    "法王": "https://upload.wikimedia.org/wikipedia/commons/8/8d/RWS_Tarot_05_Hierophant.jpg",
    "恋人": "https://upload.wikimedia.org/wikipedia/commons/3/3a/RWS_Tarot_06_Lovers.jpg",
    "戦車": "https://upload.wikimedia.org/wikipedia/commons/9/9b/RWS_Tarot_07_Chariot.jpg",
    "力": "https://upload.wikimedia.org/wikipedia/commons/f/f5/RWS_Tarot_08_Strength.jpg",
    "隠者": "https://upload.wikimedia.org/wikipedia/commons/4/4d/RWS_Tarot_09_Hermit.jpg",
    "運命の輪": "https://upload.wikimedia.org/wikipedia/commons/3/3c/RWS_Tarot_10_Wheel_of_Fortune.jpg",
    "正義": "https://upload.wikimedia.org/wikipedia/commons/e/e0/RWS_Tarot_11_Justice.jpg",
    "吊るされた男": "https://upload.wikimedia.org/wikipedia/commons/2/2b/RWS_Tarot_12_Hanged_Man.jpg",
    "死神": "https://upload.wikimedia.org/wikipedia/commons/d/d7/RWS_Tarot_13_Death.jpg",
    "節制": "https://upload.wikimedia.org/wikipedia/commons/f/f8/RWS_Tarot_14_Temperance.jpg",
    "悪魔": "https://upload.wikimedia.org/wikipedia/commons/5/55/RWS_Tarot_15_Devil.jpg",
    "塔": "https://upload.wikimedia.org/wikipedia/commons/5/53/RWS_Tarot_16_Tower.jpg",
    "星": "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_17_Star.jpg",
    "月": "https://upload.wikimedia.org/wikipedia/commons/7/7f/RWS_Tarot_18_Moon.jpg",
    "太陽": "https://upload.wikimedia.org/wikipedia/commons/1/17/RWS_Tarot_19_Sun.jpg",
    "審判": "https://upload.wikimedia.org/wikipedia/commons/d/dd/RWS_Tarot_20_Judgement.jpg",
    "世界": "https://upload.wikimedia.org/wikipedia/commons/f/ff/RWS_Tarot_21_World.jpg"
}

st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")
st.title("🔮 神秘の誕生日タロット占い")

# ユーザー入力
today = date.today()
birthday = st.date_input("生年月日を選択してください", value=date(2000, 1, 1), min_value=date(today.year - 80, 1, 1), max_value=today)
nickname = st.text_input("ニックネームを入力してください", placeholder="例：たろちゃん")

# SecretsからAPIキーを取得
raw_key = st.secrets.get("OPENAI_API_KEY")
api_key = raw_key.strip() if raw_key else None

def calculate_numerology(date_obj):
    digits = date_obj.strftime("%Y%m%d")
    while len(digits) > 1 and digits not in ["11", "22", "33"]:
        digits = str(sum(int(d) for d in digits))
    return digits

if st.button("運命を占う"):
    if not api_key:
        st.error("APIキーが設定されていません。Secretsを確認してください。")
    elif nickname:
        life_path = calculate_numerology(birthday)
        selected_card_name = random.choice(list(TAROT_DATA.keys()))
        card_image_url = TAROT_DATA[selected_card_name]
        
        st.divider()
        st.subheader(f"✨ {nickname} さんの鑑定結果")
        
        # 写真と結果を表示
        col1, col2 = st.columns([1, 2])
        with col1:
            # 画像URLを直接表示してデバッグ（動作確認用）
            st.image(card_image_url, width=200)
            st.caption(f"引いたカード: {selected_card_name}")
        with col2:
            st.write(f"**あなたのライフパスナンバー:** {life_path}")
            st.write(f"**引き当てたカード:** {selected_card_name}")

        client = OpenAI(api_key=api_key)
        with st.spinner("星の声を聴いています..."):
            prompt = f"占い師として、{nickname}さん（ライフパスナンバー{life_path}）が引いたタロット『{selected_card_name}』を神秘的に鑑定してください。"
            response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            st.write(response.choices[0].message.content)
            st.success("鑑定が完了しました！")

        # 決済ボタン
        st.divider()
        st.write("### 🔮 もっと深いお悩みをお持ちですか？")
        my_sales_url = "https://coconala.com/" 
        st.link_button("✨ 個人鑑定の詳細・お申し込みはこちら", my_sales_url, type="primary")
    else:
        st.warning("ニックネームを入れてください。")





