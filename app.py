import streamlit as st
import random
from openai import OpenAI
from datetime import date

# 1. 準備：タロットカード名と画像URLの紐付け（パブリックドメイン画像を使用）
# カード名とWikimedia Commonsの画像を対応させています
TAROT_DATA = {
    "愚者": "https://upload.wikimedia.org/wikipedia/commons/9/90/RWS_Tarot_00_Fool.jpg",
    "魔術師": "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_01_Magician.jpg",
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

# 2. 画面のデザイン設定
st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")
st.title("🔮 神秘の誕生日タロット占い")
st.write("ニックネームと誕生日から、あなたの宿命とメッセージを読み解きます。")

# 3. ユーザー入力
today = date.today()
min_year = today.year - 80
birthday = st.date_input(
    "生年月日を選択してください",
    value=date(2000, 1, 1),
    min_value=date(min_year, 1, 1),
    max_value=today
)
nickname = st.text_input("ニックネームを入力してください", placeholder="例：タロちゃん")

# APIキー設定（Secretsまたはサイドバーから読み込み）
api_key = st.secrets.get("OPENAI_API_KEY") or st.sidebar.text_input("OpenAI API Keyを入力", type="password")

# 4. 数秘術の計算
def calculate_numerology(date_obj):
    digits = date_obj.strftime("%Y%m%d")
    while len(digits) > 1 and digits not in ["11", "22", "33"]:
        digits = str(sum(int(d) for d in digits))
    return digits

# 5. メインロジック
if st.button("運命を占う"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    elif nickname:
        life_path = calculate_numerology(birthday)
        selected_card_name = random.choice(list(TAROT_DATA.keys()))
        card_image_url = TAROT_DATA[selected_card_name]
        
        st.divider()
        st.subheader(f"✨ {nickname} さんの鑑定結果")
        
        # カード画像を表示する部分を追加
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(card_image_url, caption=f"引いたカード: {selected_card_name}", use_container_width=True)
        with col2:
            st.write(f"**あなたのライフパスナンバー:** {life_path}")
            st.write(f"**引き当てたカード:** {selected_card_name}")

        client = OpenAI(api_key=api_key)
        
        with st.spinner("星の声を聴いています..."):
            prompt = f"""
            プロの占い師として、親しみやすくも神秘的なトーンで鑑定してください。
            【ユーザー情報】ニックネーム：{nickname}, ライフパスナンバー：{life_path}
            【タロット】{selected_card_name}
            【鑑定内容】
            1. {nickname}さんのライフパスナンバーが持つ「魂の性質」を解説。
            2. 今回引いた「{selected_card_name}」が、今の{nickname}さんに伝えたいメッセージを優しく。
            3. これからのアドバイス。
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            st.write(response.choices[0].message.content)
            st.success("鑑定が終わりました。あなたに幸運がありますように！")
    else:
        st.warning("ニックネームを入力してくださいね。")

# --- ここから追加：マネタイズ（販売）用の導線 ---
        st.divider() # 区切り線を入れて見やすくします
        st.write("### 🔮 もっと深いお悩みをお持ちですか？")
        st.write(f"{nickname}さんの今の状況に合わせた、より具体的でパーソナルな鑑定を個別にお受けしています。")
        st.write("恋愛、仕事、人間関係など、AIでは届かない細かな星の導きをプロの視点でお伝えします。")
        
        # あなたの販売ページ（ココナラやSTORESなど）のURLをここに貼り付けてください
        # まだ決まっていない場合は、仮のURL（https://coconala.com/ など）でテストできます
        my_sales_url = "https://coconala.com/" 
        
        st.link_button("✨ 個人鑑定の詳細・お申し込みはこちら", my_sales_url, type="primary")
        # --------------------------------------------
        
      

