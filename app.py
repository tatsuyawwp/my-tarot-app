import streamlit as st
import random
from openai import OpenAI
from datetime import date

# 1) タロット画像（表）
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

st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")
st.title("🔮 神秘の誕生日タロット占い（無料版）")

# --- Secrets ---
raw_key = st.secrets.get("OPENAI_API_KEY")
api_key = raw_key.strip() if raw_key else None

# --- Numerology ---
def calculate_numerology(date_obj):
    digits = date_obj.strftime("%Y%m%d")
    while len(digits) > 1 and digits not in ["11", "22", "33"]:
        digits = str(sum(int(d) for d in digits))
    return digits

# --- Session State ---
# stage: 0=未開始, 1=シャッフル済, 2=カット済, 3=引いた(裏), 4=開いた(表), 5=鑑定済
if "stage" not in st.session_state:
    st.session_state.stage = 0

if "deck" not in st.session_state:
    st.session_state.deck = []

if "selected_card_name" not in st.session_state:
    st.session_state.selected_card_name = None

if "revealed" not in st.session_state:
    st.session_state.revealed = False

if "reading_text" not in st.session_state:
    st.session_state.reading_text = None

# --- Input ---
today = date.today()
birthday = st.date_input(
    "生年月日を選択してください",
    value=date(2000, 1, 1),
    min_value=date(today.year - 80, 1, 1),
    max_value=today
)
nickname = st.text_input("ニックネームを入力してください", placeholder="例：たろちゃん")

st.divider()

# --- Reset ---
if st.button("🔄 最初からやり直す"):
    st.session_state.stage = 0
    st.session_state.deck = []
    st.session_state.selected_card_name = None
    st.session_state.revealed = False
    st.session_state.reading_text = None
    st.rerun()

# --- Guidance text ---
life_path = calculate_numerology(birthday) if nickname else None

st.subheader("🧘‍♂️ 占いの手順（ワンオラクル）")
st.write("1) 質問を心に思い浮かべる → 2) シャッフル → 3) カット → 4) 1枚引く → 5) 開く → 6) 鑑定")

# ===== Step 0: 準備 =====
if st.session_state.stage == 0:
    st.info("まずはニックネームを入れて、心の中で『今日の自分に必要なメッセージは？』と唱えてください。")
    if st.button("🌀 シャッフルする（カードを混ぜる）"):
        if not nickname:
            st.warning("ニックネームを入れてください。")
        else:
            st.session_state.deck = list(TAROT_DATA.keys())
            random.shuffle(st.session_state.deck)
            st.session_state.stage = 1
            st.rerun()

# ===== Step 1: シャッフル済 =====
elif st.session_state.stage == 1:
    st.success("シャッフルしました。次は直感で『カット』します。")
    st.write("山札を2〜3つに分けて重ね直すイメージでOK。")
    if st.button("✂️ カットする"):
        # カット演出（実際はランダムで山の分割→合体）
        deck = st.session_state.deck
        if len(deck) >= 10:
            cut1 = random.randint(3, len(deck) - 3)
            cut2 = random.randint(3, len(deck) - 3)
            a = deck[:cut1]
            b = deck[cut1:cut2]
            c = deck[cut2:]
            new_deck = b + c + a
        else:
            new_deck = deck[:]
            random.shuffle(new_deck)

        st.session_state.deck = new_deck
        st.session_state.stage = 2
        st.rerun()

# ===== Step 2: カット済 → 引く =====
elif st.session_state.stage == 2:
    st.success("カットしました。次はいよいよ1枚引きます。")
    st.write("直感で『今だ』と思ったらボタンを押してください。")
    # 裏向きカードの雰囲気
    cols = st.columns(7)
    for i in range(7):
        with cols[i]:
            st.markdown("🂠")

    if st.button("🎴 1枚引く（まだ開かない）"):
        st.session_state.selected_card_name = st.session_state.deck.pop()
        st.session_state.revealed = False
        st.session_state.reading_text = None
        st.session_state.stage = 3
        st.rerun()

# ===== Step 3: 引いた（裏向き） → 開く =====
elif st.session_state.stage == 3:
    st.success("カードを引きました。今はまだ裏向きです。")
    st.write("深呼吸して、準備ができたらカードを開いてください。")

    # 裏向き表示（本当の裏面画像があるなら差し替え推奨）
    st.markdown("### 🂠 ここにあなたのカード（裏向き）が置かれています")

    if st.button("✨ カードを開く"):
        st.session_state.revealed = True
        st.session_state.stage = 4
        st.rerun()

# ===== Step 4: 開いた（表） → 鑑定 =====
elif st.session_state.stage == 4:
    selected_card_name = st.session_state.selected_card_name
    card_image_url = TAROT_DATA[selected_card_name]

    st.subheader(f"✨ {nickname} さんの無料鑑定（簡易）")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(card_image_url, width=220)
        st.caption(f"引いたカード: {selected_card_name}")
    with col2:
        st.write(f"**ライフパスナンバー:** {life_path}")
        st.write("**質問:** 今日の自分に必要なメッセージは？")

    st.divider()
    st.write("🔮 準備ができたら、鑑定を開始します。")
    if st.button("🔮 鑑定する（無料・簡易）"):
        if not api_key:
            st.error("APIキーが設定されていません。Secretsを確認してください。")
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner("星の声を聴いています..."):
                prompt = (
                    f"あなたは神秘的で優しい占い師です。"
                    f"{nickname}さん（ライフパスナンバー{life_path}）が引いたタロット『{selected_card_name}』について、"
                    f"無料版として短めに、"
                    f"1) 今日のテーマ（1〜2行）"
                    f"2) ひとことメッセージ（1〜2行）"
                    f"3) 今日の開運アクション（箇条書きで3つ）"
                    f"の形式で日本語で鑑定してください。"
                )
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.session_state.reading_text = response.choices[0].message.content

            st.session_state.stage = 5
            st.rerun()

# ===== Step 5: 鑑定結果表示 =====
elif st.session_state.stage == 5:
    selected_card_name = st.session_state.selected_card_name
    card_image_url = TAROT_DATA[selected_card_name]

    st.subheader(f"✨ {nickname} さんの鑑定結果（無料版）")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(card_image_url, width=220)
        st.caption(f"引いたカード: {selected_card_name}")
    with col2:
        st.write(f"**ライフパスナンバー:** {life_path}")
        st.write(f"**引き当てたカード:** {selected_card_name}")

    st.write(st.session_state.reading_text)
    st.success("鑑定が完了しました！")

    # 有料導線はまだ「予告」だけにしておく（次フェーズで実装）
    st.divider()
    st.write("### 🔒 もっと深く占う（有料版で追加予定）")
    st.write("- 過去/現在/未来（3枚引き）\n- 相手の気持ち\n- 具体的な行動プラン\n- 追加で1枚引き（アドバイスカード）")

    st.divider()
    st.write("### 🔮 もっと深いお悩みをお持ちですか？")
    my_sales_url = "https://coconala.com/"
    st.link_button("✨ 個人鑑定の詳細・お申し込みはこちら", my_sales_url, type="primary")
