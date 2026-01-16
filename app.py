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
st.set_page_config(page_title="神秘の誕生日タロット", page_icon="🔮", layout="centered")
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
# CSS（スマホ・見た目最適化）
# =========================
st.markdown("""
<style>
/* スマホでもはみ出さないコンテナ設定 */
.fade-container { 
    max-width: 280px; 
    width: 80%; 
    margin: 0 auto; 
}
.fade-img {
    width: 100%;
    border-radius: 14px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.3); /* カードに影をつけて立体的に */
    transition: opacity 0.8s ease-in-out;
    display: block;
}
.hidden { opacity: 0; }
.visible { opacity: 1; }

/* 鑑定結果のテキストボックスを装飾 */
.result-box {
    background-color: #f9f9fb;
    border-left: 5px solid #d4af37;
    padding: 20px;
    border-radius: 8px;
    margin: 15px 0;
    line-height: 1.7;
    color: #333;
}
.small-note { opacity: 0.85; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# =========================
# 365日パーソナリティ（ロジック）
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
    titles = ["月光の紋章を継ぐ人", "蔦花の誓いを抱く人", "蒼金の導きを持つ人", "星屑の調律を担う人", "黎明の灯を守る人", "静謐の輪郭を纏う人", "光彩堂々の表現者", "花弁の慈愛を宿す人", "風紋の直感を持つ人", "水鏡の真心を映す人", "翠の秩序を編む人", "金線の決断を刻む人", "宵闇の叡智を抱く人", "白百合の癒し手", "扉の鍵を見つける人", "織紋の守護者", "天空の羅針盤の人"]
    cores = ["繊細な感受性と芯の強さを併せ持ち、場の空気をやさしく整えながら前へ進める人です。", "小さな違和感を見逃さず、静かに秩序を編み直して運の流れを美しく整える人です。", "人の想いを受け止める器が大きく、必要な時には堂々と自分の輪郭を示せる人です。", "感性の光で道を照らし、心をほどく言葉と行動で周囲に安心を広げられる人です。", "守りたいものがあるほど力が澄み、迷いをほどいて現実を前向きに動かせる人です。", "波のように柔らかく変化しながらも、自分の軸は折らずに歩みを重ねられる人です。", "直感の閃きを形にするのが上手く、選び直しで運命の糸を整えられる人です。", "静けさを味方にして深く観察し、最適な一手を淡々と打てる人です。"]
    strengths_pool = ["気配りが繊細", "直感が冴える", "誠実で信頼される", "段取りが上手い", "共感力が高い", "場を整える力", "言葉選びが丁寧", "学びが深い", "切り替えが上手い", "行動が早い", "美意識がある", "粘り強く続ける", "人を励ますのが得意", "視野が広い", "決断に芯がある"]
    pitfalls_pool = ["抱え込みやすい", "気を遣いすぎる", "完璧を求めがち", "遠慮が先に立つ", "考えすぎて止まる", "頑張り過ぎて疲れる", "自分に厳しくなる", "本音を後回しに", "不安を溜めやすい", "決断に時間がかかる"]
    growth_pool = ["安心できる土台を整えるほど、あなたの魅力は自然に外へ広がっていきます。", "小さくても“今日できる一歩”に落とすと、運の流れが軽やかに動き始めます。", "本音を短く言語化して共有できると、関係性も現実もするりと整います。", "優先順位を三つに絞ると、迷いがほどけて成果が結晶のように残ります。", "休むことを予定に入れるほど、直感と集中が澄んで戻ってきます。", "手放す基準を一つ決めると、あなたの時間と運気の余白が増えていきます。"]
    mantras = ["静かに、強く", "やさしく選ぶ", "整えるほど進む", "焦らず進む", "本音を大切に", "守りながら変える", "小さく始める", "深呼吸で切り替え", "今ここに戻る", "丁寧に動く", "迷ったらシンプルに", "光に寄せていく", "一歩で十分", "選び直して美しく"]

    return {
        "title": pick(titles, s),
        "core": pick(cores, s * 7 + 3),
        "strengths": [strengths_pool[(s + i * 17) % len(strengths_pool)] for i in range(3)],
        "pitfalls": [pitfalls_pool[(s + i * 19 + 7) % len(pitfalls_pool)] for i in range(3)],
        "growth": pick(growth_pool, s * 11 + 5),
        "mantra": pick(mantras, s * 13 + 9),
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

MAJOR_BY_NUM = {1: "魔術師", 2: "女教皇", 3: "女帝", 4: "皇帝", 5: "法王", 6: "恋人", 7: "戦車", 8: "力", 9: "隠者", 10: "運命の輪", 11: "正義", 12: "吊るされた男", 13: "死神", 14: "節制", 15: "悪魔", 16: "塔", 17: "星", 18: "月", 19: "太陽", 20: "審判", 21: "世界", 22: "愚者"}

TOPIC_GUIDE = {
    "今日の運勢": "今日1日の流れに焦点を当て、朝〜夜の過ごし方のコツも入れてください。",
    "恋愛": "相手の気持ちを断定せず、距離の縮め方・言葉選び・やってはいけないことを具体的に。",
    "仕事": "仕事の進め方、評価されるポイント、トラブル回避、今日の優先順位を具体的に。"
}

# =========================
# Session State 初期化
# =========================
for key in ["stage", "deck", "candidates", "selected_card_name", "reading_text", "fade_step"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key in ["stage", "fade_step"] else ([] if key in ["deck", "candidates"] else None)

def reset_all():
    for key in ["stage", "deck", "candidates", "selected_card_name", "reading_text", "fade_step"]:
        st.session_state[key] = 0 if key in ["stage", "fade_step"] else ([] if key in ["deck", "candidates"] else None)

# =========================
# 入力 UI
# =========================
today = date.today()
birthday = st.date_input("生年月日を選択", value=date(2000, 1, 1), min_value=date(today.year - 80, 1, 1), max_value=today)
nickname = st.text_input("ニックネーム", placeholder="例：たろちゃん")
fortune_topic = st.selectbox("占いたい内容", ["今日の運勢", "恋愛", "仕事"])
one_line = st.text_input("気になっていること（任意）", placeholder="例：新しい環境に馴染めるか不安")

if st.button("🔄 最初からやり直す", use_container_width=True):
    reset_all()
    st.rerun()

st.divider()

# データ準備
birthday_key = birthday.strftime("%m/%d")
profile = build_birthday_profile(birthday_key)
birth_num = birth_tarot_number(birthday)
birth_card_name = MAJOR_BY_NUM[birth_num]
birth_card_url = TAROT_DATA.get(birth_card_name)
api_key = st.secrets.get("OPENAI_API_KEY", "").strip()

# =========================
# メインフロー（演出）
# =========================

if st.session_state.stage == 0:
    st.subheader("🧘‍♂️ 準備")
    st.write("心の中で『今日の自分に必要なメッセージは？』と唱えてください。")
    if st.button("🌀 シャッフル＆カットする", use_container_width=True):
        if not nickname:
            st.warning("ニックネームを入れてください。")
        else:
            st.session_state.deck = list(TAROT_DATA.keys())
            random.shuffle(st.session_state.deck)
            # カット
            deck = st.session_state.deck
            n = len(deck)
            cut = random.randint(5, n-5)
            st.session_state.deck = deck[cut:] + deck[:cut]
            st.session_state.stage = 1
            st.rerun()

elif st.session_state.stage == 1:
    st.subheader("🃏 ミックス開始")
    if st.button("🌀 ミックス開始", use_container_width=True):
        st.session_state.stage = 2
        st.rerun()

elif st.session_state.stage == 2:
    st.subheader("🌀 ミックス中…")
    anim = st.empty()
    wobble = random.choice([250, 260, 270])
    anim.markdown(f'<div class="fade-container"><img src="{TAROT_BACK_URL}" class="fade-img visible" style="width:{wobble}px;"></div>', unsafe_allow_html=True)
    if st.button("⏹️ ストップ！", use_container_width=True):
        candidates = [st.session_state.deck.pop() for _ in range(7)]
        st.session_state.candidates = candidates
        st.session_state.stage = 3
        st.rerun()
    time.sleep(0.12)
    st.rerun()

elif st.session_state.stage == 3:
    st.subheader("✨ 直感で1枚選んでください")
    cols = st.columns(7)
    for i, name in enumerate(st.session_state.candidates):
        with cols[i]:
            st.markdown(f'<div class="fade-container"><img src="{TAROT_BACK_URL}" class="fade-img visible"></div>', unsafe_allow_html=True)
            if st.button("選", key=f"pick_{i}"):
                st.session_state.selected_card_name = name
                st.session_state.stage = 4
                st.rerun()

elif st.session_state.stage == 4:
    st.subheader("🂠 選んだカードをめくります")
    st.markdown(f'<div class="fade-container"><img src="{TAROT_BACK_URL}" class="fade-img visible"></div>', unsafe_allow_html=True)
    if st.button("✨ オープン！", use_container_width=True):
        st.session_state.stage = 5
        st.rerun()

elif st.session_state.stage == 5:
    card_name = st.session_state.selected_card_name
    card_url = TAROT_DATA[card_name]
    st.markdown(f'<div class="fade-container"><img src="{card_url}" class="fade-img visible"></div>', unsafe_allow_html=True)
    st.caption(f"運命のカード: {card_name}")

    if st.button("🔮 鑑定結果を読み解く", use_container_width=True, type="primary"):
        if not api_key:
            st.error("APIキーが必要です。")
        else:
            tone_map = {"gentle": "やわらかく寄り添う口調", "bright": "明るく前向きな口調", "calm": "静かで上品な導きの口調", "bold": "頼りがいのある力強い口調"}
            tone_hint = tone_map.get(profile["tone"], "やわらかい口調")
            
            prompt = f"""占い師として{nickname}さんを鑑定してください。口調は{tone_hint}。
相談内容：{fortune_topic}（{one_line}）
誕生日特徴：{profile['core']}
誕生タロット：{birth_card_name}
今日のタロット：{card_name}
アールヌーヴォーの比喩（金線、星屑、花弁など）を交え、前向きな行動指針を提示してください。恐怖や断定は厳禁。"""

            client = OpenAI(api_key=api_key)
            with st.spinner("星の声を聴いています..."):
                response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                st.session_state.reading_text = response.choices[0].message.content
                st.session_state.stage = 6
                st.rerun()

elif st.session_state.stage == 6:
    card_name = st.session_state.selected_card_name
    st.subheader(f"✨ {nickname} さんの鑑定結果")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.image(birth_card_url, use_container_width=True, caption=f"誕生カード: {birth_card_name}")
    with col_b:
        st.image(TAROT_DATA[card_name], use_container_width=True, caption=f"今日のカード: {card_name}")

    st.markdown(f'<div class="result-box">{st.session_state.reading_text}</div>', unsafe_allow_html=True)

    # --- SNSシェア機能 ---
    st.divider()
    share_text = urllib.parse.quote(f"【神秘の誕生日タロット】今日の私のカードは『{card_name}』でした！🔮 {nickname}さんの運勢は... #AIタロット #占い")
    # ここにご自身のアプリのURLを入れてください
    share_url = "https://my-tarot-app.streamlit.app/" 
    x_share_link = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
    st.link_button("🐦 X(Twitter)で結果をシェアする", x_share_link, use_container_width=True)

    st.link_button("✨ もっと深く占う（個人鑑定）", "https://coconala.com/", use_container_width=True, type="primary")
