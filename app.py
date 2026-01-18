import streamlit as st
import random
import time
import urllib.parse
from datetime import date
from openai import OpenAI

# =========================
# ページ設定
# =========================
st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")

# CSSの注入（画面上に余白を作らないよう、先頭でまとめて定義）
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    /* 画面上の不要な余白を削る */
    .block-container { padding-top: 2rem; }
    
    /* 鑑定結果ボックス */
    .result-box {
        background: #fbfbfd;
        border-left: 6px solid #d4af37;
        padding: 18px;
        border-radius: 12px;
        line-height: 1.95;
        font-size: 1.03rem;
        color: #222;
        margin-bottom: 20px;
    }

    /* SNS ボタン共通 */
    .sns-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 5px;
        color: #fff !important;
        text-decoration: none !important;
        font-weight: bold;
        font-size: 14px;
        width: 130px; /* サイズ固定 */
        box-sizing: border-box;
        transition: 0.3s;
    }
    .sns-button i { margin-right: 8px; font-size: 18px; }

    /* 各サービスの色 */
    .btn-x { background: #000; }
    .btn-line { background: #06C755; }
    .btn-fb { background: #1877F2; }
    .btn-threads { background: #000; }
    .btn-insta { background: linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); }
    .btn-tiktok { background: #010101; }

    /* カード画像の演出 */
    .fade-img { width: 100%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    .shuffle { animation: spin 1.2s linear infinite; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔮 神秘の誕生日タロット占い")

# =========================
# 画像URLとメタデータ
# =========================
TAROT_BACK_URL = "https://github.com/tatsuyawwp/my-tarot-app/blob/main/tarrotback.png?raw=true"

TAROT_DATA = {
    "愚者": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/fool.png?raw=true", "element": "風", "astro": "天王星"},
    "魔術師": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/magician.png?raw=true", "element": "風", "astro": "水星"},
    "女教皇": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/high%20priestess.jpg?raw=true", "element": "水", "astro": "月"},
    "女帝": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/empress.png?raw=true", "element": "地", "astro": "金星"},
    "皇帝": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/emperor.png?raw=true", "element": "火", "astro": "牡羊座"},
    "法王": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/hierophant.png?raw=true", "element": "地", "astro": "牡牛座"},
    "恋人": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/lovers.png?raw=true", "element": "風", "astro": "双子座"},
    "戦車": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/chariot.png?raw=true", "element": "水", "astro": "蟹座"},
    "力": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/strength.png?raw=true", "element": "火", "astro": "獅子座"},
    "隠者": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/hermit.png?raw=true", "element": "地", "astro": "乙女座"},
    "運命の輪": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/wheel.png?raw=true", "element": "火", "astro": "木星"},
    "正義": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/justice.png?raw=true", "element": "風", "astro": "天秤座"},
    "吊るされた男": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/hanged_man.png?raw=true", "element": "水", "astro": "海王星"},
    "死神": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/death.png?raw=true", "element": "水", "astro": "蠍座"},
    "節制": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/temperance.png?raw=true", "element": "火", "astro": "射手座"},
    "悪魔": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/devil.png?raw=true", "element": "地", "astro": "山羊座"},
    "塔": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/tower.png?raw=true", "element": "火", "astro": "火星"},
    "星": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/star.png?raw=true", "element": "風", "astro": "水瓶座"},
    "月": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/moon.png?raw=true", "element": "水", "astro": "魚座"},
    "太陽": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/sun.png?raw=true", "element": "火", "astro": "太陽"},
    "審判": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/judgement.png?raw=true", "element": "火", "astro": "冥王星"},
    "世界": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/world.png?raw=true", "element": "地", "astro": "土星"},
}

# =========================
# ロジック関数
# =========================
def calc_life_path(bday: date) -> int:
    digits = bday.strftime("%Y%m%d")
    s = sum(int(d) for d in digits)
    while s > 9 and s not in [11, 22, 33]:
        s = sum(int(d) for d in str(s))
    return s

def get_life_path_info(num: int) -> str:
    info = {
        1: "自立心の強い開拓者", 2: "繊細な調停者", 3: "明るい表現者",
        4: "誠実な構築者", 5: "自由な冒険者", 6: "深い慈愛の博愛者",
        7: "心理を追う探求者", 8: "成功を掴む達成者", 9: "精神性の高い完結者",
        11: "直感のメッセンジャー", 22: "大きな理想を叶える創造主", 33: "宇宙的な愛を持つ菩薩",
    }
    return info.get(num, "未知の可能性を秘めた人")

# =========================
# APIキー取得
# =========================
api_key = st.secrets.get("OPENAI_API_KEY", "").strip()

# =========================
# Session State 初期化
# =========================
if "stage" not in st.session_state: st.session_state.stage = 0
if "selected_cards" not in st.session_state: st.session_state.selected_cards = []
if "reading_text" not in st.session_state: st.session_state.reading_text = None

def reset_all():
    st.session_state.stage = 0
    st.session_state.selected_cards = []
    st.session_state.reading_text = None

# =========================
# メイン画面
# =========================
with st.sidebar:
    st.header("設定")
    birthday = st.date_input("生年月日", value=date(2000, 1, 1))
    nickname = st.text_input("ニックネーム", placeholder="例：たろちゃん")
    fortune_topic = st.selectbox("占いたい内容", ["今日の運勢", "恋愛", "仕事"])
    one_line = st.text_input("補足（任意）")
    if st.button("🔄 最初からやり直す"):
        reset_all()
        st.rerun()

# --- ステージ 0: 開始 ---
if st.session_state.stage == 0:
    st.subheader("🧘‍♂️ あなたの運命を読み解きます")
    if st.button("🌀 占いを開始する"):
        if not nickname: st.warning("ニックネームを入れてください。")
        else:
            st.session_state.deck = list(TAROT_DATA.keys())
            random.shuffle(st.session_state.deck)
            st.session_state.stage = 1
            st.rerun()

# --- ステージ 1: シャッフル ---
elif st.session_state.stage == 1:
    st.markdown(f'<div style="text-align:center;"><img src="{TAROT_BACK_URL}" class="shuffle" style="width:150px;"></div>', unsafe_allow_html=True)
    if st.button("⏹️ ストップ"):
        st.session_state.candidates = random.sample(st.session_state.deck, 7)
        st.session_state.stage = 2
        st.rerun()

# --- ステージ 2: カード選択 ---
elif st.session_state.stage == 2:
    num_sel = len(st.session_state.selected_cards)
    st.subheader("✨ カードを1枚選んでください" if num_sel == 0 else "✨ もう1枚選んでください")
    cols = st.columns(7)
    for i, name in enumerate(st.session_state.candidates):
        with cols[i]:
            if name in st.session_state.selected_cards:
                st.markdown(f'<img src="{TAROT_BACK_URL}" style="width:100%; opacity:0.3;">', unsafe_allow_html=True)
            else:
                if st.button("選ぶ", key=f"c_{i}"):
                    st.session_state.selected_cards.append(name)
                    if len(st.session_state.selected_cards) == 2: st.session_state.stage = 3
                    st.rerun()
                st.markdown(f'<img src="{TAROT_BACK_URL}" style="width:100%;">', unsafe_allow_html=True)

# --- ステージ 3: 鑑定ボタン ---
elif st.session_state.stage == 3:
    c1, c2 = st.columns(2)
    card1, card2 = st.session_
