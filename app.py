import streamlit as st
import random
from openai import OpenAI
from datetime import date

# 1. 準備：タロットカードデータ（リンクを最新・安定版に更新）
TAROT_DATA = {
    "愚者": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/00.jpg",
    "魔術師": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/01.jpg",
    "女教皇": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/02.jpg",
    "女帝": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/03.jpg",
    "皇帝": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/04.jpg",
    "法王": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/05.jpg",
    "恋人": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/06.jpg",
    "戦車": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/07.jpg",
    "力": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/08.jpg",
    "隠者": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/09.jpg",
    "運命の輪": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/10.jpg",
    "正義": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/11.jpg",
    "吊るされた男": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/12.jpg",
    "死神": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/13.jpg",
    "節制": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/14.jpg",
    "悪魔": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/15.jpg",
    "塔": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/16.jpg",
    "星": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/17.jpg",
    "月": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/18.jpg",
    "太陽": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/19.jpg",
    "審判": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/20.jpg",
    "世界": "https://raw.githubusercontent.com/Learn-From-Code/tarot-images/main/21.jpg"
}

st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")
st.title("🔮 神秘の誕生日タロット占い")
st.write("ニックネームと誕生日から、あなたの宿命とメッセージを読み解きます。")

today = date.today()
min_year = today.year - 80
birthday = st.date_input("生年月日を選択してください", value=date(2000, 1, 1), min_value=date(min_year, 1, 1), max_value=today)
nickname = st.text_input("ニックネームを入力してください", placeholder="例：たろちゃん")

# APIキー読み込み（Secrets優先）
raw_key = st.secrets.get("OPENAI_API_KEY") or st.sidebar.text_input("OpenAI API Keyを入力", type="password")
api_key = raw_key.strip() if raw_key else None

def calculate_numerology(date_obj):
    digits = date_obj.strftime("%Y%m%d")
    while len(digits) > 1 and digits not in ["11", "22", "33"]:
        digits = str(sum(int(d) for d in digits))
    return digits

if st.button("運命を占う"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    elif nickname:
        life_path = calculate_numerology(birthday)
        selected_card_name = random.choice(list(TAROT_DATA.keys()))
        card_image_url = TAROT_DATA[selected_card_name]
        
        st.divider()
        st.subheader(f"✨ {nickname} さんの鑑定結果")
        
        # レイアウト調整（画像とテキスト）
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(card_image_url, caption=f"引いたカード: {selected_card_name}", width=200)
        with col2:
            st.write(f"**あなたのライフパスナンバー:** {life_path}")
            st.write(f"**引き当てたカード:** {selected_card_name}")

        client = OpenAI(api_key=api_key)
        with st.spinner("星の声を聴いています..."):
            prompt = f"占い師として、{nickname}さん（ライフパスナンバー{life_path}）の引いたタロット『{selected_card_name}』を解説してください。神秘的な口調でお願いします。"
            response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            st.write(response.choices[0].message.content)
            st.success("鑑定が完了しました！")

        # 決済ボタン
        st.divider()
        st.write("### 🔮 もっと深いお悩みをお持ちですか？")
        st.write("AI鑑定では届かない細かな星の導きを、プロの視点でより深くお伝えします。")
        my_sales_url = "https://coconala.com/"  # ここを書き換える
        st.link_button("✨ 個人鑑定の詳細・お申し込みはこちら", my_sales_url, type="primary")
    else:
        st.warning("ニックネームを入れてくださいね。")
