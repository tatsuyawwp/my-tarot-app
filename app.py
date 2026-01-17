import streamlit as st
import random
import time
import hashlib
import urllib.parse  # ← これを追加
from datetime import date
from openai import OpenAI

# =========================
# ページ設定
# =========================
st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮")
st.title("🔮 神秘の誕生日タロット占い（無料版）")

# =========================
# 画像URL（表・裏）
# =========================
TAROT_BACK_URL = "https://github.com/tatsuyawwp/my-tarot-app/blob/main/tarrotback.png?raw=true"

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

# =========================
# APIキー
# =========================
raw_key = st.secrets.get("OPENAI_API_KEY")
api_key = raw_key.strip() if raw_key else None
# =========================
# CSS（見た目）
# =========================
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

<style>
/* Result readability */
.result-title{
  font-size: 1.15rem;
  font-weight: 800;
  margin-bottom: 10px;
}

.result-box{
  background: #fbfbfd;
  border-left: 6px solid #d4af37;
  padding: 18px;
  border-radius: 12px;
  line-height: 1.95;
  font-size: 1.03rem;
  color: #222;
}

.result-box p{ margin: 0.6em 0; }
.result-box ul{ margin: 0.6em 0 0.9em 1.2em; }
.result-box li{ margin: 0.4em 0; }
.result-box strong{ color:#111; }

/* SNS buttons */
.sns-button{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  padding:10px 15px;
  border-radius:8px;
  margin:5px;
  color:#fff !important;
  text-decoration:none !important;
  font-weight:bold;
  font-size:14px;
  width:100%;
  box-sizing:border-box;
  transition:0.3s;
}
.sns-button i{ margin-right:8px; font-size:18px; }
.sns-button:hover{
  opacity:0.85;
  transform:translateY(-2px);
}

.btn-x{ background:#000; }
.btn-line{ background:#06C755; }
.btn-fb{ background:#1877F2; }
.btn-threads{ background:#000; }
.btn-insta{
  background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);
}
.btn-tiktok{ background:#010101; }
</style>
""", unsafe_allow_html=True)

# =========================
# 365日パーソナリティ（全日平等・自動生成）
# =========================
def seed_from_mmdd(mmdd: str) -> int:
    h = hashlib.sha256(mmdd.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def pick(items, s: int) -> str:
    return items[s % len(items)]

def build_birthday_profile(mmdd: str) -> dict:
    s = seed_from_mmdd(mmdd)

    tones = ["gentle", "bright", "calm", "bold"]
    tone = tones[s % len(tones)]

    titles = [
        "月光の紋章を継ぐ人", "蔦花の誓いを抱く人", "蒼金の導きを持つ人", "星屑の調律を担う人",
        "黎明の灯を守る人", "静謐の輪郭を纏う人", "光彩堂々の表現者", "花弁の慈愛を宿す人",
        "風紋の直感を持つ人", "水鏡の真心を映す人", "翠の秩序を編む人", "金線の決断を刻む人",
        "宵闇の叡智を抱く人", "白百合の癒し手", "扉の鍵を見つける人", "織紋の守護者",
        "天空の羅針盤の人"
    ]
    cores = [
        "繊細な感受性と芯の強さを併せ持ち、場の空気をやさしく整えながら前へ進める人です。",
        "小さな違和感を見逃さず、静かに秩序を編み直して運の流れを美しく整える人です。",
        "人の想いを受け止める器が大きく、必要な時には堂々と自分の輪郭を示せる人です。",
        "感性の光で道を照らし、心をほどく言葉と行動で周囲に安心を広げられる人です。",
        "守りたいものがあるほど力が澄み、迷いをほどいて現実を前向きに動かせる人です。",
        "波のように柔らかく変化しながらも、自分の軸は折らずに歩みを重ねられる人です。",
        "直感の閃きを形にするのが上手く、選び直しで運命の糸を整えられる人です。",
        "静けさを味方にして深く観察し、最適な一手を淡々と打てる人です。"
    ]
    strengths_pool = [
        "気配りが繊細", "直感が冴える", "誠実で信頼される", "段取りが上手い", "共感力が高い",
        "場を整える力", "言葉選びが丁寧", "学びが深い", "切り替えが上手い", "行動が早い",
        "美意識がある", "粘り強く続ける", "人を励ますのが得意", "視野が広い", "決断に芯がある"
    ]
    pitfalls_pool = [
        "抱え込みやすい", "気を遣いすぎる", "完璧を求めがち", "遠慮が先に立つ", "考えすぎて止まる",
        "頑張り過ぎて疲れる", "自分に厳しくなる", "本音を後回しに", "不安を溜めやすい", "決断に時間がかかる"
    ]
    growth_pool = [
        "安心できる土台を整えるほど、あなたの魅力は自然に外へ広がっていきます。",
        "小さくても“今日できる一歩”に落とすと、運の流れが軽やかに動き始めます。",
        "本音を短く言語化して共有できると、関係性も現実もするりと整います。",
        "優先順位を三つに絞ると、迷いがほどけて成果が結晶のように残ります。",
        "休むことを予定に入れるほど、直感と集中が澄んで戻ってきます。",
        "手放す基準を一つ決めると、あなたの時間と運気の余白が増えていきます。"
    ]
    mantras = [
        "静かに、強く", "やさしく選ぶ", "整えるほど進む", "焦らず進む", "本音を大切に",
        "守りながら変える", "小さく始める", "深呼吸で切り替え", "今ここに戻る", "丁寧に動く",
        "迷ったらシンプルに", "光に寄せていく", "一歩で十分", "選び直して美しく"
    ]

    title = pick(titles, s)
    core = pick(cores, s * 7 + 3)
    growth = pick(growth_pool, s * 11 + 5)
    mantra = pick(mantras, s * 13 + 9)

    strengths = [strengths_pool[(s + i * 17) % len(strengths_pool)] for i in range(3)]
    pitfalls = [pitfalls_pool[(s + i * 19 + 7) % len(pitfalls_pool)] for i in range(3)]

    return {
        "title": title,
        "core": core,
        "strengths": strengths,
        "pitfalls": pitfalls,
        "growth": growth,
        "mantra": mantra,
        "tone": tone
    }

# =========================
# 誕生タロット（バースカード）
# =========================
def birth_tarot_number(bday: date) -> int:
    s = sum(int(ch) for ch in bday.strftime("%Y%m%d"))
    while s > 22:
        s = sum(int(ch) for ch in str(s))
    return 22 if s == 0 else s

MAJOR_BY_NUM = {
    1: "魔術師",
    2: "女教皇",
    3: "女帝",
    4: "皇帝",
    5: "法王",
    6: "恋人",
    7: "戦車",
    8: "力",
    9: "隠者",
    10: "運命の輪",
    11: "正義",
    12: "吊るされた男",
    13: "死神",
    14: "節制",
    15: "悪魔",
    16: "塔",
    17: "星",
    18: "月",
    19: "太陽",
    20: "審判",
    21: "世界",
    22: "愚者"
}

# =========================
# テーマ（3択）
# =========================
TOPIC_GUIDE = {
    "今日の運勢": "今日1日の流れに焦点を当て、朝〜夜の過ごし方のコツも入れてください。",
    "恋愛": "相手の気持ちを断定せず、距離の縮め方・言葉選び・やってはいけないことを具体的に。",
    "仕事": "仕事の進め方、評価されるポイント、トラブル回避、今日の優先順位を具体的に。"
}

# =========================
# Session State 初期化
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
# 入力
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

one_line = st.text_input("いま気になっていること（任意・一言でOK）", placeholder="例：気になる人と距離を縮めたい")

col_r1, col_r2 = st.columns([1, 2])
with col_r1:
    if st.button("🔄 最初からやり直す"):
        reset_all()
        st.rerun()

st.divider()

birthday_key = birthday.strftime("%m/%d")
profile = build_birthday_profile(birthday_key)

birth_num = birth_tarot_number(birthday)
birth_card_name = MAJOR_BY_NUM[birth_num]
birth_card_url = TAROT_DATA.get(birth_card_name)

topic_guide = TOPIC_GUIDE.get(fortune_topic, "")

# =========================
# メインフロー（演出）
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

# --- stage 5: 表を表示＆鑑定開始 ---
elif st.session_state.stage == 5:
    card_name = st.session_state.selected_card_name
    card_url = TAROT_DATA[card_name]

    st.subheader("✨ カードが示されました…")
    st.markdown(
        f'<div class="fade-container"><img src="{card_url}" class="fade-img visible"></div>',
        unsafe_allow_html=True
    )
    st.caption(f"今日引いたカード: {card_name}")

    st.divider()
    st.write("🔮 準備ができたら鑑定を開始します。")

    if st.button("🔮 鑑定する（無料・簡易）", use_container_width=True):
        if not api_key:
            st.error("APIキーが設定されていません。")
        elif not nickname:
            st.warning("ニックネームを入れてください。")
        else:
            tone_hint = {
                "gentle": "やわらかく包む口調",
                "bright": "明るく前向きな口調",
                "calm": "静かな自信の口調",
                "bold": "頼りがいのある口調"
            }.get(profile["tone"], "やわらかく包む口調")

            prompt = f"""
あなたは経験豊富で、現実を見つめる力も備えた占い師です。
相談者の味方として、対面で静かに語りかけるように鑑定してください。

【全体方針】
・不安を煽らない
・根拠のない万能肯定はしない
・優しさの中に、少しだけ「気づき」や「核心」を含める
・占い師としての洞察を感じさせる言葉選びをする

【相談者情報】
ニックネーム：{nickname}
占いたい内容：{fortune_topic}

【誕生日パーソナリティ】
称号：{profile['title']}
本質：{profile['core']}
強み：{', '.join(profile['strengths'])}
気をつけたい傾向：{', '.join(profile['pitfalls'])}
運が伸びるヒント：{profile['growth']}
合言葉：{profile['mantra']}

【誕生タロット（人生の軸）】
{birth_card_name}

【今日のタロット（今日のテーマ）】
{card_name}

【鑑定ルール】
・最初に「あなたは今、どんな状態にいそうか」をやさしく言語化する
・その人の強みが、今どんな形で活きているか／活かしきれていないかを示す
・必要に応じて「分かっているのに後回しにしていること」「同じ所で止まりやすい点」を一つだけ示す（断定しない）
・{fortune_topic}にフォーカスし、「今日できる現実的な一歩」を提示する
・説教や断罪はせず、伴走者のような語り口にする

【出力形式】
■ 今のあなたの状態
■ このカードが今出た意味
■ {fortune_topic}についてのメッセージ
■ 今のあなたへの一言メッセージ
■ 今日の開運アクション（3つ）

【トーン指定】
・人間味があり、落ち着いていて、少しだけ核心を突く
・「大丈夫」だけで終わらせず、「だからこうするといい」に繋げる
・読み終えたあと、静かに背中を押される感覚を大切にする
"""
            client = OpenAI(api_key=api_key)
            with st.spinner("星の声を聴いています..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=900
                )

            # ★ここ重要：必ず button の中
            text = response.choices[0].message.content.strip()
            text = text.replace("■ ", "\n### ").replace("■", "\n### ")
            st.session_state.reading_text = text

            st.session_state.stage = 6
            st.rerun()

# --- stage 6: 結果表示 ---
elif st.session_state.stage == 6:
    card_name = st.session_state.selected_card_name
    card_url = TAROT_DATA[card_name]

    st.subheader(f"✨ {nickname} さんの鑑定結果")

    # 結果本文（読みやすい表示）
    st.markdown('<div class="result-title">🔮 鑑定メッセージ</div>', unsafe_allow_html=True)
    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown(st.session_state.reading_text or "")
    st.markdown("</div>", unsafe_allow_html=True)

      # --- シェア ---
    st.divider()
    st.write("### 🔮 結果をシェアして幸運を広げる")

    share_url = "https://my-tarot-app.streamlit.app/"

    share_variant = st.radio(
        "シェア文を選ぶ",
        ["短め", "しっかり", "かわいく"],
        horizontal=True
    )

    if share_variant == "短め":
        share_text = f"今日のカードは『{card_name}』🔮 #AIタロット"
    elif share_variant == "しっかり":
        share_text = f"【神秘の誕生日タロット】今日のカードは『{card_name}』でした🔮 誕生日×タロットで背中を押してもらえた… #AIタロット"
    else:
        share_text = f"今日のわたしに必要なメッセージ…『{card_name}』だったよ🫶🔮 #AIタロット"

    encoded_text = urllib.parse.quote(share_text)
    encoded_url = urllib.parse.quote(share_url)

    share_pack = f"{share_text}\n{share_url}"

    c_copy1, c_copy2 = st.columns([1, 1])
    with c_copy1:
        if st.button("📋 文章をコピー（Instagram / TikTok向け）", use_container_width=True):
            st.toast("この下の文章を選択してコピーしてね ✨", icon="✅")
    with c_copy2:
        if st.button("📋 URLだけコピー（LINE / Facebook向け）", use_container_width=True):
            st.toast("URLをコピーしてシェアしよう ✨", icon="✅")

    st.code(share_pack, language="text")
    st.caption("↑ ここをドラッグしてコピーしてね（スマホは長押し→コピー）")

    sns_html = f"""
    <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;">

      <a href="https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}"
         target="_blank" class="sns-button btn-x">
         <i class="fa-brands fa-x-twitter"></i> X
      </a>

      <a href="https://social-plugins.line.me/lineit/share?url={encoded_url}"
         target="_blank" class="sns-button btn-line">
         <i class="fa-brands fa-line"></i> LINE
      </a>

      <a href="https://www.facebook.com/sharer/sharer.php?u={encoded_url}"
         target="_blank" class="sns-button btn-fb">
         <i class="fa-brands fa-facebook"></i> Facebook
      </a>

      <a href="https://www.threads.net/intent/post?text={encoded_text}%0A{encoded_url}"
         target="_blank" class="sns-button btn-threads">
         <i class="fa-brands fa-threads"></i> Threads
      </a>

      <a href="https://www.instagram.com/"
         target="_blank" class="sns-button btn-insta">
         <i class="fa-brands fa-instagram"></i> Instagram
      </a>

      <a href="https://www.tiktok.com/"
         target="_blank" class="sns-button btn-tiktok">
         <i class="fa-brands fa-tiktok"></i> TikTok
      </a>

    </div>
    """
    st.markdown(sns_html, unsafe_allow_html=True)

   st.divider()
st.markdown("## ☕ この占いを続ける応援")

st.write(
    "この占いは無料で公開しています。\n"
    "もし少しでも役に立ったと感じたら、"
    "コーヒー1杯分の応援で活動を続けることができます。"
)

st.link_button(
    "☕ Buy Me a Coffee で応援する",
    "https://buymeacoffee.com/mystic_tarot",
    use_container_width=True
)










