import streamlit as st
import random
from openai import OpenAI
from datetime import date

# 1. 準備：タロットカードのリスト
TAROT_CARDS = [
    "愚者", "魔術師", "女教皇", "女帝", "皇帝", "法王", "恋人", "戦車", "正義",
    "隠者", "運命の輪", "力", "吊るされた男", "死神", "節制", "悪魔", "塔",
    "星", "月", "太陽", "審判", "世界"
]

# 2. 画面のデザイン設定
st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")
st.title("🔮 神秘の誕生日タロット占い")
st.write("ニックネームと誕生日から、あなたの宿命とメッセージを読み解きます。")

# --- カレンダーの範囲設定 ---
today = date.today()
min_year = today.year - 80
birthday = st.date_input(
    "生年月日を選択してください",
    value=date(2000, 1, 1),
    min_value=date(min_year, 1, 1),
    max_value=today
)

nickname = st.text_input("ニックネームを入力してください", placeholder="例：タロちゃん")

# APIキー設定（Secretsから読み込む設定です）
api_key = st.secrets.get("OPENAI_API_KEY") or st.sidebar.text_input("OpenAI API Keyを入力", type="password")

# 4. 数秘術の計算
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
        selected_card = random.choice(TAROT_CARDS)
        
        st.divider()
        st.subheader(f"✨ {nickname} さんの鑑定結果")
        st.write(f"**あなたのライフパスナンバー:** {life_path}")
        st.write(f"**引き当てたカード:** {selected_card}")

        client = OpenAI(api_key=api_key)
        
        with st.spinner("星の声を聴いています..."):
            prompt = f"""
            プロの占い師として、親しみやすくも神秘的なトーンで鑑定してください。
            【ユーザー情報】ニックネーム：{nickname}, ライフパスナンバー：{life_path}
            【タロット】{selected_card}
            【鑑定内容】
            1. {nickname}さんのライフパスナンバーが持つ「魂の性質」を解説してください。
            2. 今回引いた「{selected_card}」が、今の{nickname}さんに伝えたいメッセージを優しく教えてください。
            3. これからの日々をより良く過ごすためのアドバイスを最後に添えてください。
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            st.write(response.choices[0].message.content)
            st.success("鑑定が終わりました。あなたに幸運がありますように！")
    else:
        st.warning("ニックネームを入力してくださいね。")
