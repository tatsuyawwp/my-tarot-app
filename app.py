import streamlit as st
import random
import time
from openai import OpenAI
from datetime import date

# =========================
# 設定
# =========================
st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")
st.title("🔮 神秘の誕生日タロット占い（無料版）")

# 裏面（バックプリント）
TAROT_BACK_URL = "https://github.com/tatsuyawwp/my-tarot-app/blob/main/tarrotback.png?raw=true"

# 表面カード
TAROT_DATA = {
    "愚者": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/fool.png?raw=true",
    "魔術師": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/magician.png?raw=true",
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

# APIキー
raw_key = st.secrets.get("OPENAI_API_KEY")
api_key = raw_key.strip() if raw_key else None

# =========================
# ユーティリティ
# =========================
def calculate_numerology(date_obj):
    digits = date_obj.strftime("%Y%m%d")
    while len(digits) > 1 and digits not in ["11", "22", "33"]:
        digits = str(sum(int(d) for d in digits))
    return digits

# =========================
# CSS（演出）
# =========================
st.markdown("""
<style>
.fade-container { width: 260px; margin: 0 auto; }
.fade-img {
    width: 100%;
    border-radius: 14px;
    transition: opacity 0.8s ease-in-out;
    display: block;
}
.hidden { opacity: 0; }
.visible { opacity: 1; }
.small-note { opacity: 0.85; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# =========================
# Session State 初期化
# stage:
# 0=未開始（入力）
# 1=シャッフル/カット完了、ミックス開始待ち
# 2=ミックス中（擬似アニメ）
# 3=ストップ後、候補提示（選ぶ）
# 4=選んだカード（裏向き）
# 5=フェードで表へ（開いた）
# 6=鑑定結果表示
# =========================
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "deck" not in st.session_state:
    st.session_state.deck = []
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "selected_card_name" not in st.session_state:
    st.session_state.selected_card_name = None
if "reading_text" not in st.session_state:
    st.session_state.reading_text = None
if "fade_step" not in st.session_state:
    st.session_state.fade_step = 0

def reset_all():
    st.session_state.stage = 0
    st.session_state.deck = []
    st.session_state.candidates = []
    st.session_state.selected_card_name = None
    st.session_state.reading_text = None
    st.session_state.fade_step = 0

# =========================
# 入力（fortune_topic は必ずここで定義）
# =========================
today = date.today()
birthday = st.date_input(
    "生年月日を選択してください",
    value=date(2000, 1, 1),
    min_value=date(today.year - 80, 1, 1),
    max_value=today
)
nickname = st.text_input("ニックネームを入力してください", placeholder="例：たろちゃん")

fortune_topic = st.selectbox(
    "占いたい内容を選んでください",
    ["今日の運勢", "恋愛", "仕事"],
    index=0
)

TOPIC_GUIDE = {
    "今日の運勢": "今日1日の流れに焦点を当て、朝〜夜の過ごし方のコツも入れてください。",
    "恋愛": "相手の気持ちを断定せず、距離の縮め方・言葉選び・やってはいけないことを具体的に。",
    "仕事": "仕事の進め方、評価されるポイント、トラブル回避、今日の優先順位を具体的に。"
}
topic_guide = TOPIC_GUIDE.get(fortune_topic, "具体的で現実的なアドバイスを入れてください。")

col_r1, col_r2 = st.columns([1, 2])
with col_r1:
    if st.button("🔄 最初からやり直す"):
        reset_all()
        st.rerun()

st.divider()

life_path = calculate_numerology(birthday) if nickname else None

# =========================
# メインフロー
# =========================

# --- stage 0: 準備 ---
if st.session_state.stage == 0:
    st.subheader("🧘‍♂️ 準備")
    st.write("心の中で『今日の自分に必要なメッセージは？』と唱えてください。")
    st.markdown('<div class="small-note">※ ニックネームを入力してから進めます</div>', unsafe_allow_html=True)

    if st.button("🌀 シャッフル＆カットして準備する"):
        if not nickname:
            st.warning("ニックネームを入れてください。")
        else:
            # 山札作成 → シャッフル
            st.session_state.deck = list(TAROT_DATA.keys())
            random.shuffle(st.session_state.deck)

            # カット演出（安全版）
            deck = st.session_state.deck
            n = len(deck)

            if n >= 10:
                cut1 = random.randint(3, n - 4)
                cut2 = random.randint(cut1 + 1, n - 3)

                a = deck[:cut1]
                b = deck[cut1:cut2]
                c = deck[cut2:]
                st.session_state.deck = b + c + a
            else:
                random.shuffle(st.session_state.deck)

            # ★ ここは「else の中」で、インデントはこの深さ
            st.session_state.stage = 1
            st.rerun()

# --- stage 1: ミックス開始待ち ---
elif st.session_state.stage == 1:
    st.subheader("🃏 ミックス開始")
    st.write("目の前でカードがぐるぐる混ざります。直感で『今だ！』と思ったら止めてください。")

    if st.button("🌀 ミックス開始"):
        st.session_state.stage = 2
        st.rerun()

# --- stage 2: ミックス中（擬似アニメ） ---
elif st.session_state.stage == 2:
    st.subheader("🌀 ミックス中…")
    st.write("止めたいタイミングで下のボタンを押してください。")

    anim = st.empty()
    wobble = random.choice([248, 252, 256, 260, 264])

    anim.markdown(f"""
    <div class="fade-container">
        <img src="{TAROT_BACK_URL}" class="fade-img visible" style="width:{wobble}px;">
    </div>
    """, unsafe_allow_html=True)

    if st.button("⏹️ ストップ（止める）"):
        if not st.session_state.deck:
            st.session_state.deck = list(TAROT_DATA.keys())
            random.shuffle(st.session_state.deck)

        # 候補7枚（重複なし）
        candidates = []
        for _ in range(7):
            if len(st.session_state.deck) == 0:
                st.session_state.deck = list(TAROT_DATA.keys())
                random.shuffle(st.session_state.deck)
            candidates.append(st.session_state.deck.pop())

        st.session_state.candidates = candidates
        st.session_state.stage = 3
        st.rerun()

    time.sleep(0.12)
    st.rerun()

# --- stage 3: 候補提示（選ぶ） ---
elif st.session_state.stage == 3:
    st.subheader("✨ 目の前に浮かび上がったカード")
    st.write("この中から **直感で1枚** 選んでください（まだ表は見えません）。")

    cols = st.columns(7)
    for i, name in enumerate(st.session_state.candidates):
        with cols[i]:
            st.markdown(f"""
            <div class="fade-container">
                <img src="{TAROT_BACK_URL}" class="fade-img visible">
            </div>
            """, unsafe_allow_html=True)
            if st.button("選ぶ", key=f"pick_{name}"):
                st.session_state.selected_card_name = name
                st.session_state.reading_text = None
                st.session_state.fade_step = 0
                st.session_state.stage = 4
                st.rerun()

# --- stage 4: 選んだカード（裏向き） ---
elif st.session_state.stage == 4:
    st.subheader("🂠 あなたが選んだカード（裏向き）")
    st.write("深呼吸して、準備ができたらカードを開いてください。")

    st.markdown(f"""
    <div class="fade-container">
        <img src="{TAROT_BACK_URL}" class="fade-img visible">
    </div>
    """, unsafe_allow_html=True)

    if st.button("✨ カードを開く"):
        st.session_state.fade_step = 1
        st.session_state.stage = 5
        st.rerun()

# --- stage 5: フェードで表へ＆鑑定 ---
elif st.session_state.stage == 5:
    card_name = st.session_state.selected_card_name
    card_url = TAROT_DATA[card_name]

    st.subheader("✨ カードが示されました…")

    # fade_step 1: 裏を消す（暗転風）
    if st.session_state.fade_step == 1:
        st.markdown(f"""
        <div class="fade-container">
            <img src="{TAROT_BACK_URL}" class="fade-img hidden">
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.25)
        st.session_state.fade_step = 2
        st.rerun()

    # fade_step 2: 表を表示
    st.markdown(f"""
    <div class="fade-container">
        <img src="{card_url}" class="fade-img visible">
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"引いたカード: {card_name}")
    st.write(f"**{nickname} さんのライフパスナンバー:** {life_path}")
    st.write(f"**占いたい内容:** {fortune_topic}")

    st.divider()
    st.write("🔮 準備ができたら鑑定を開始します。")

    if st.button("🔮 鑑定する（無料・簡易）"):
        if not api_key:
            st.error("APIキーが設定されていません。Secretsを確認してください。")
        elif not nickname:
            st.warning("ニックネームを入れてください。")
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner("星の声を聴いています..."):
                prompt = f"""
あなたは経験豊富で思いやりのある占い師です。
決して不安を煽らず、相談者の味方として語りかけてください。
文章は人間味があり、優しく頼りがいのある口調にしてください（上から目線や説教口調は禁止）。

【相談者情報】
ニックネーム：{nickname}
ライフパスナンバー：{life_path}
占いたい内容：{fortune_topic}
引いたタロットカード：{card_name}

【鑑定の狙い】
・誕生日占い（ライフパス）とタロットを「別々に説明」せず、
  「この性格のあなたに、このカードが出た意味」として掛け合わせて語ること。
・不安を煽る言い方、断定的な不幸表現は禁止（怖い言い方はしない）。
・{topic_guide}
・抽象論だけで終わらせず、今日すぐできる行動に落とす。

【出力形式】（必ずこの順番）
■ あなたの本質（誕生日占い）
■ 今回このカードが出た意味（あなたの本質×カードの掛け算）
■ {fortune_topic}についてのメッセージ（具体的に）
■ 今のあなたへの一言メッセージ（寄り添い・励まし）
■ 今日の開運アクション（3つ：短く、実行しやすく）

日本語で、対面の占い師がやさしく語りかけるように鑑定してください。
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.session_state.reading_text = response.choices[0].message.content

            st.session_state.stage = 6
            st.rerun()

# --- stage 6: 結果表示 ---
elif st.session_state.stage == 6:
    card_name = st.session_state.selected_card_name
    card_url = TAROT_DATA[card_name]

    st.subheader(f"✨ {nickname} さんの鑑定結果（無料版）")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(card_url, width=240)
        st.caption(f"引いたカード: {card_name}")
    with col2:
        st.write(f"**ライフパスナンバー:** {life_path}")
        st.write(f"**占いたい内容:** {fortune_topic}")

    st.write(st.session_state.reading_text)
    st.success("鑑定が完了しました！")

    st.divider()
    st.write("### 🔒 もっと深く占う（有料版で追加予定）")
    st.write("- 過去/現在/未来（3枚引き）\n- 相手の気持ち\n- 具体的な行動プラン\n- 追加で1枚（アドバイスカード）")

    st.divider()
    st.write("### 🔮 もっと深いお悩みをお持ちですか？")
    my_sales_url = "https://coconala.com/"
    st.link_button("✨ 個人鑑定の詳細・お申し込みはこちら", my_sales_url, type="primary")







