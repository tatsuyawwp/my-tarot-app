import streamlit as st
import random
from openai import OpenAI
from datetime import date

# 1. 準備：タロットカードデータ（リンクを非常に安定したものに固定）
TAROT_DATA = {
    TAROT_DATA = {
    "愚者": "https://raw.githubusercontent.com/tatsuyawwp/my-tarot-app/main/fool.png",
    "魔術師":"https://raw.githubusercontent.com/tatsuyawwp/my-tarot-app/main/magician.png",
    "女教皇": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/high%20priestess.jpg?raw=true",
    "女帝": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/empress.png?raw=true",
    "皇帝": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/emperor.png?raw=true",
    "法王": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/hierophant.png?raw=true",
    "恋人": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/lovers.png?raw=true",
    "戦車": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/chariot.png?raw=true",
    "力": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/strength.png?raw=true",
    "隠者": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/hermit.png?raw=true",
    "運命の輪": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/wheel.png?raw=true",
    "正義": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/justice.png?raw=true",
    "吊るされた男": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/hanged_man.png?raw=true",
    "死神": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/death.png?raw=true",
    "節制": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/temperance.png?raw=true",
    "悪魔": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/devil.png?raw=true",
    "塔": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/tower.png?raw=true",
    "星": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/star.png?raw=true",
    "月": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/moon.png?raw=true",
    "太陽": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/sun.png?raw=true",
    "審判": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/judgement.png?raw=true",
    "世界": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/world.png?raw=true"
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






