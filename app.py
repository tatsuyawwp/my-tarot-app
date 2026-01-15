import streamlit as st
import random
from openai import OpenAI

# 1. 準備：タロットカードのリスト（大アルカナ22枚）
TAROT_CARDS = [
    "愚者", "魔術師", "女教皇", "女帝", "皇帝", "法王", "恋人", "戦車", "正義",
    "隠者", "運命の輪", "力", "吊るされた男", "死神", "節制", "悪魔", "塔",
    "星", "月", "太陽", "審判", "世界"
]

# 2. 画面のデザイン設定
st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")
st.title("🔮 神秘の誕生日タロット占い")
st.write("あなたの誕生日から導き出す宿命と、タロットのメッセージを届けます。")

# 3. ユーザー入力
name = st.text_input("お名前を教えてください")
birthday = st.date_input("生年月日を選択してください", min_value=None)

# APIキーの入力設定（※後でネットに公開する時に安全に設定します）
api_key = st.sidebar.text_input("OpenAI API Keyを入力（テスト用）", type="password")

# 4. 数秘術の計算（ライフパスナンバー）
def calculate_numerology(date):
    digits = "".join(filter(str.isdigit, str(date)))
    while len(digits) > 1 and digits not in ["11", "22", "33"]:
        digits = str(sum(int(d) for d in digits))
    return digits

if st.button("運命を占う"):
    if not api_key:
        st.error("APIキーを入力してください。")
    elif name:
        # 計算と選択
        life_path = calculate_numerology(birthday)
        selected_card = random.choice(TAROT_CARDS)
        
        st.divider()
        st.subheader(f"✨ {name}さんの鑑定結果")
        st.write(f"**あなたのライフパスナンバー:** {life_path}")
        st.write(f"**引き当てたカード:** {selected_card}")

        # AI（OpenAI）による鑑定文の生成
        client = OpenAI(api_key=api_key)
        
        with st.spinner("星の声を聴いています..."):
            prompt = f"""
            占い師として、以下の情報から深みのある鑑定文を作成してください。
            【ユーザー情報】名前：{name}, ライフパスナンバー：{life_path}
            【タロット】{selected_card}
            【依頼】
            1. まず、ライフパスナンバーが示すその人の本質を解説してください。
            2. 次に、引いたタロットカードが今のその人に何を伝えているか解説してください。
            3. 最後に、全体をまとめたポジティブなアドバイスをください。
            4. 占い師らしい、神秘的で丁寧な口調でお願いします。
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.choices[0].message.content
            st.write(result_text)
            st.success("鑑定が完了しました！")
    else:
        st.warning("お名前を入力してください。")