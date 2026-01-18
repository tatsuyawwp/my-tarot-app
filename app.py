import streamlit as st
import random
import time
import hashlib
import urllib.parse
from datetime import date
from openai import OpenAI

# =========================
# ページ設定
# =========================
st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")
st.title("🔮 神秘の誕生日タロット占い（無料版）")

# =========================
# 画像URLとメタデータ（22枚維持）
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
    "世界": {"url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/world.png?raw=true", "element": "地", "astro": "土星"}
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
    info = {1: "自立心の強い開拓者", 2: "繊細な調停者", 3: "明るい表現者", 4: "誠実な構築者", 5: "自由な冒険者", 6: "深い慈愛の博愛者", 7: "心理を追う探求者", 8: "成功を掴む達成者", 9: "精神性の高い完結者", 11: "直感のメッセンジャー", 22: "大きな理想を叶える創造主", 33: "宇宙的な愛を持つ菩薩"}
    return info.get(num, "未知の可能性を秘めた人")

# =========================
# APIキー・CSS
# =========================
raw_key = st.secrets.get("OPENAI_API_KEY")
api_key = raw_key.strip() if raw_key else None

st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
.result-box{ background: #fbfbfd; border-left: 6px solid #d4af37; padding: 18px; border-radius: 12px; line-height: 1.95; font-size: 1.03rem; color: #222; }
.sns-button{ display:inline-flex; align-items:center; justify-content:center; padding:10px 15px; border-radius:8px; margin:5px; color:#fff !important; text-decoration:none !important; font-weight:bold; font-size:14px; width:100%; box-sizing:border-box; transition:0.3s; }
.sns-button i{ margin-right:8px; font-size:18px; }
.btn-x{ background:#000; } .btn-line{ background:#06C755; } .btn-fb{ background:#1877F2; } .btn-threads{ background:#000; }
.fade-img { width: 100%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# =========================
# Session State 初期化
# =========================
if "stage" not in st.session_state: st.session_state.stage = 0
if "deck" not in st.session_state: st.session_state.deck = []
if "candidates" not in st.session_state: st.session_state.candidates = []
if "selected_cards" not in st.session_state: st.session_state.selected_cards = []
if "reading_text" not in st.session_state: st.session_state.reading_text = None

def reset_all():
    st.session_state.stage = 0
    st.session_state.deck = []
    st.session_state.candidates = []
    st.session_state.selected_cards = []
    st.session_state.reading_text = None

# =========================
# メイン画面
# =========================
today = date.today()
birthday = st.date_input("生年月日を選択", value=date(2000, 1, 1), min_value=date(today.year - 80, 1, 1), max_value=today)
nickname = st.text_input("ニックネーム", placeholder="例：たろちゃん")
fortune_topic = st.selectbox("占いたい内容", ["今日の運勢", "恋愛", "仕事"], index=0)
one_line = st.text_input("気になっていること（任意）", placeholder="例：今日の大事な会議について")

if st.button("🔄 最初からやり直す"):
    reset_all()
    st.rerun()

st.divider()

# --- stage 0: 準備 ---
if st.session_state.stage == 0:
    st.subheader("🧘‍♂️ 準備")
    st.write("「今の自分」と「未来への鍵」の2枚を引き当てます。")
    if st.button("🌀 占いを開始する"):
        if not nickname:
            st.warning("ニックネームを入れてください。")
        else:
            st.session_state.deck = list(TAROT_DATA.keys())
            random.shuffle(st.session_state.deck)
            st.session_state.stage = 1
            st.rerun()

# --- stage 1: シャッフル演出 ---
elif st.session_state.stage == 1:
    st.subheader("🌀 ミックス中…")
    st.image(TAROT_BACK_URL, width=200)
    if st.button("⏹️ ストップ"):
        st.session_state.candidates = random.sample(st.session_state.deck, 7)
        st.session_state.stage = 2
        st.rerun()
    time.sleep(0.1)

# --- stage 2: 2枚選ぶ ---
elif st.session_state.stage == 2:
    num_selected = len(st.session_state.selected_cards)
    if num_selected == 0:
        st.subheader("✨ 1枚目：『現在のあなた』を選んでください")
    else:
        st.subheader("✨ 2枚目：『未来へのアドバイス』を選んでください")

    cols = st.columns(7)
    for i, name in enumerate(st.session_state.candidates):
        with cols[i]:
            # 選んだカードは少し透明にする
            opacity = "0.3" if name in st.session_state.selected_cards else "1.0"
            st.markdown(f'<img src="{TAROT_BACK_URL}" style="width:100%; opacity:{opacity}; border-radius:5px;">', unsafe_allow_html=True)
            if name not in st.session_state.selected_cards:
                if st.button("選択", key=f"btn_{name}_{i}"):
                    st.session_state.selected_cards.append(name)
                    if len(st.session_state.selected_cards) == 2:
                        st.session_state.stage = 3
                    st.rerun()

# --- stage 3: 鑑定準備 ---
elif st.session_state.stage == 3:
    st.subheader("🔮 選ばれた2枚のメッセージ")
    c1, c2 = st.columns(2)
    card1 = st.session_state.selected_cards[0]
    card2 = st.session_state.selected_cards[1]
    with c1: st.image(TAROT_DATA[card1]["url"], caption=f"1. 現在の状況: {card1}")
    with c2: st.image(TAROT_DATA[card2]["url"], caption=f"2. 未来の鍵: {card2}")

    if st.button("🔮 鑑定結果を生成する（無料）", use_container_width=True):
        if not api_key:
            st.error("APIキーが必要です。")
        else:
            lp_num = calc_life_path(birthday)
            lp_info = get_life_path_info(lp_num)
            with st.spinner("深層意識を読み解いています..."):
                meta1 = TAROT_DATA[card1]
                meta2 = TAROT_DATA[card2]
                prompt = f"""
占い師として、数秘術とタロットを融合した精密鑑定を行ってください。
相談者：{nickname}
ライフパス：{lp_num}（{lp_info}）
内容：{fortune_topic} / {one_line}
引いたカード：
1. 現状：{card1}（{meta1['element']}元素 / {meta1['astro']}）
2. 助言：{card2}（{meta2['element']}元素 / {meta2['astro']}）

【構成】
1. あなたが今、引き寄せている「エネルギーの正体」
2. 数秘{lp_num}から見る「今の課題」と「{card1}」の関係
3. 未来を好転させる「{card2}」の具体的な使い道
4. 鑑定のまとめと背中を押す言葉
"""
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.session_state.reading_text = response.choices[0].message.content.strip().replace("■ ", "\n### ")
                st.session_state.stage = 4
                st.rerun()

# --- stage 4: 結果表示 ---
elif st.session_state.stage == 4:
    # 常に選んだカードを一番上に表示する
    st.subheader(f"✨ {nickname} さんの鑑定結果")
    c1, c2 = st.columns(2)
    card1 = st.session_state.selected_cards[0]
    card2 = st.session_state.selected_cards[1]
    with c1: st.image(TAROT_DATA[card1]["url"], caption=f"現状：{card1}")
    with c2: st.image(TAROT_DATA[card2]["url"], caption=f"助言：{card2}")

    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown(st.session_state.reading_text)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- SNS シェア（元のボタンを復旧） ---
    st.divider()
    st.write("### 🔮 幸運をシェアする")
    share_url = "https://my-tarot-app.streamlit.app/"
    share_text = f"今日の鑑定は『{card1}』と『{card2}』🔮 #AIタロット"
    encoded_text = urllib.parse.quote(share_text)
    encoded_url = urllib.parse.quote(share_url)

    sns_html = f"""
    <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;">
      <a href="https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}" target="_blank" class="sns-button btn-x"><i class="fa-brands fa-x-twitter"></i> X</a>
      <a href="https://social-plugins.line.me/lineit/share?url={encoded_url}" target="_blank" class="sns-button btn-line"><i class="fa-brands fa-line"></i> LINE</a>
      <a href="https://www.facebook.com/sharer/sharer.php?u={encoded_url}" target="_blank" class="sns-button btn-fb"><i class="fa-brands fa-facebook"></i> FB</a>
      <a href="https://www.threads.net/intent/post?text={encoded_text}%0A{encoded_url}" target="_blank" class="sns-button btn-threads">
         <i class="fa-brands fa-threads"></i> Threads
      </a>
      <a href="https://www.instagram.com/" target="_blank" class="sns-button btn-insta">
         <i class="fa-brands fa-instagram"></i> Instagram
      </a>
      <a href="https://www.tiktok.com/" target="_blank" class="sns-button btn-tiktok">
         <i class="fa-brands fa-tiktok"></i> TikTok
      </a>
    </div>
    """

    </div>
    """
    st.markdown(sns_html, unsafe_allow_html=True)

      # --- 応援（Buy Me a Coffee）---
    st.divider()
    st.markdown("### ☕ この占いを続ける応援")
    st.write("この占いは無料で公開しています。もし少しでも役に立ったら、コーヒー1杯の応援で活動を続けられます。")

    st.divider()
    st.link_button("☕ Buy Me a Coffee で応援する", "https://buymeacoffee.com/mystic_tarot", use_container_width=True)






