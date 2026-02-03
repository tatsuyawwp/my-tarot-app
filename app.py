import streamlit as st
import random
import time
import urllib.parse
from datetime import date
from openai import OpenAI

# =========================
# ページ設定
# =========================
st.set_page_config(page_title="『数命アルカナ（Sumei Arcana）：今の自分を整理するためのタロット（無料）』", page_icon="🔮")
st.title("🔮 『数命アルカナ（Sumei Arcana）：今の自分を整理するためのタロット（無料）』（無料版）")
st.write(
   "数命アルカナは、
生年月日とタロットを使って
**「今の自分の状態」を整理するための占いです。

未来を断定したり、
正解を押しつけたりはしません。

✔ やりたいことが分からない
✔ 仕事やお金のことでモヤモヤしている
✔ 決断する前に、一度立ち止まりたい

そんな時に、
自分の内側を見つめ直す
きっかけとして使ってください。


st.caption("※エンタメ要素を含む占いとしてお楽しみください。
    )")

# =========================
# 画像URLとメタデータ（22枚維持）
# =========================
TAROT_BACK_URL = (
    "https://github.com/tatsuyawwp/my-tarot-app/blob/main/tarrotback.png?raw=true"
)

TAROT_DATA = {
    "愚者": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/fool.png?raw=true",
        "element": "風",
        "astro": "天王星",
    },
    "魔術師": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/magician.png?raw=true",
        "element": "風",
        "astro": "水星",
    },
    "女教皇": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/high%20priestess.jpg?raw=true",
        "element": "水",
        "astro": "月",
    },
    "女帝": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/empress.png?raw=true",
        "element": "地",
        "astro": "金星",
    },
    "皇帝": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/emperor.png?raw=true",
        "element": "火",
        "astro": "牡羊座",
    },
    "法王": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/hierophant.png?raw=true",
        "element": "地",
        "astro": "牡牛座",
    },
    "恋人": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/lovers.png?raw=true",
        "element": "風",
        "astro": "双子座",
    },
    "戦車": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/chariot.png?raw=true",
        "element": "水",
        "astro": "蟹座",
    },
    "力": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/strength.png?raw=true",
        "element": "火",
        "astro": "獅子座",
    },
    "隠者": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/hermit.png?raw=true",
        "element": "地",
        "astro": "乙女座",
    },
    "運命の輪": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/wheel.png?raw=true",
        "element": "火",
        "astro": "木星",
    },
    "正義": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/justice.png?raw=true",
        "element": "風",
        "astro": "天秤座",
    },
    "吊るされた男": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/hanged_man.png?raw=true",
        "element": "水",
        "astro": "海王星",
    },
    "死神": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/death.png?raw=true",
        "element": "水",
        "astro": "蠍座",
    },
    "節制": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/temperance.png?raw=true",
        "element": "火",
        "astro": "射手座",
    },
    "悪魔": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/devil.png?raw=true",
        "element": "地",
        "astro": "山羊座",
    },
    "塔": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/tower.png?raw=true",
        "element": "火",
        "astro": "火星",
    },
    "星": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/star.png?raw=true",
        "element": "風",
        "astro": "水瓶座",
    },
    "月": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/moon.png?raw=true",
        "element": "水",
        "astro": "魚座",
    },
    "太陽": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/sun.png?raw=true",
        "element": "火",
        "astro": "太陽",
    },
    "審判": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/judgement.png?raw=true",
        "element": "火",
        "astro": "冥王星",
    },
    "世界": {
        "url": "https://github.com/tatsuyawwp/my-tarot-app/blob/main/world.png?raw=true",
        "element": "地",
        "astro": "土星",
    },
}

# =========================
# ロジック関数
# =========================
def calc_life_path(bday: date) -> int:
    """
    生年月日からライフパスナンバーを算出する。
    11, 22, 33 はマスターナンバーとして分解せず、そのまま返す。
    それ以外は1桁になるまで足し合わせる。
    """
    digits = bday.strftime("%Y%m%d")
    s = sum(int(d) for d in digits)
    while s > 9 and s not in [11, 22, 33]:
        s = sum(int(d) for d in str(s))
    return s


def get_life_path_info(num: int) -> str:
    info = {
        1: "自立心の強い開拓者",
        2: "繊細な調停者",
        3: "明るい表現者",
        4: "誠実な構築者",
        5: "自由な冒険者",
        6: "深い慈愛の博愛者",
        7: "心理を追う探求者",
        8: "成功を掴む達成者",
        9: "精神性の高い完結者",
        11: "直感のメッセンジャー",
        22: "大きな理想を叶える創造主",
        33: "宇宙的な愛を持つ菩薩",
    }
    return info.get(num, "未知の可能性を秘めた人")



# =========================
# APIキー・CSS
# =========================
raw_key = st.secrets.get("OPENAI_API_KEY")
api_key = raw_key.strip() if raw_key else None

css = """
<style>
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css");

/* ===== 鑑定結果ボックス ===== */
.result-box{
  background: #fbfbfd;
  border-left: 6px solid #d4af37;
  padding: 18px;
  border-radius: 12px;
  line-height: 1.95;
  font-size: 1.03rem;
  color: #222;
}

/* ===== SNS ボタン共通 ===== */
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
.sns-button i{
  margin-right:8px;
  font-size:18px;
}

/* 各サービスの色 */
.btn-x{ background:#000; }
.btn-line{ background:#06C755; }
.btn-fb{ background:#1877F2; }
.btn-threads{ background:#000; }

/* Instagram & TikTok の背景 */
.btn-insta{
  background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);
}
.btn-tiktok{
  background:#010101;
}

/* カード画像の演出（裏面と共通） */
.fade-img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

/* 表示用タロットカード */
.tarot-card{
  width: 100%;
  max-width: 260px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
.tarot-card.reversed{
  transform: rotate(180deg);
}

/* ふわふわ上下に揺れる（シャッフル演出） */
@keyframes floaty {
  0%   { transform: translateY(0px); }
  50%  { transform: translateY(-6px); }
  100% { transform: translateY(0px); }
}

/* ほんのり明るさが変わる */
@keyframes shimmer {
  0%   { filter: brightness(1); }
  50%  { filter: brightness(1.08); }
  100% { filter: brightness(1); }
}

.shuffle {
  animation: floaty 1.2s ease-in-out infinite, shimmer 1.6s ease-in-out infinite;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# =========================
# Session State 初期化
# =========================
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "deck" not in st.session_state:
    st.session_state.deck = []
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "selected_cards" not in st.session_state:
    st.session_state.selected_cards = []
# 逆位置フラグ（True: 逆位置 / False: 正位置）
if "selected_reversed" not in st.session_state:
    st.session_state.selected_reversed = []
if "reading_text" not in st.session_state:
    st.session_state.reading_text = None


def reset_all():
    st.session_state.stage = 0
    st.session_state.deck = []
    st.session_state.candidates = []
    st.session_state.selected_cards = []
    st.session_state.selected_reversed = []
    st.session_state.reading_text = None


def show_card(name: str, is_reversed: bool, label: str):
    """カード画像＋キャプションを表示する共通関数"""
    url = TAROT_DATA[name]["url"]
    rev_label = "（逆位置）" if is_reversed else "（正位置）"
    extra_class = " reversed" if is_reversed else ""
    html = f"""
<div style="text-align:center;">
  <img src="{url}" class="tarot-card{extra_class}">
  <div style="margin-top:6px;font-weight:bold;">
    {label}：{name}{rev_label}
  </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


# =========================
# メイン画面
# =========================
today = date.today()
birthday = st.date_input(
    "生年月日を選択",
    value=date(2000, 1, 1),
    min_value=date(today.year - 80, 1, 1),
    max_value=today,
)
nickname = st.text_input("ニックネーム", placeholder="例：たろちゃん")
fortune_topic = st.selectbox(
    "占いたいテーマを選んでください",
    [
        "① 全体運（今の運勢）",
        "② 恋愛・パートナーシップ",
        "③ 仕事・キャリア",
        "④ 才能・適性・ライフワーク",
        "⑤ 人間関係・家族・友人",
        "⑥ お金・豊かさ・働き方",
    ],
    index=0,
)

one_line = st.text_input("気になっていること（任意）", placeholder="例：今日の大事な会議について")

if st.button("🔄 最初からやり直す"):
    reset_all()
    st.rerun()

st.divider()

# =========================
# ステージ制御
# =========================

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
if not api_key:
    st.error("APIキーが必要です。Streamlitの『Secrets』に OPENAI_API_KEY を設定してください。")
    st.stop()

# --- stage 1: シャッフル演出 ---
elif st.session_state.stage == 1:
    st.subheader("🌀 カードをミックスしています…")

    st.markdown(
        f"""
<div style="text-align:center;margin-top:10px;margin-bottom:10px;">
  <img src="{TAROT_BACK_URL}" class="fade-img shuffle" style="max-width:180px;">
</div>
""",
        unsafe_allow_html=True,
    )
    st.caption("ピンときたタイミングで「⏹️ ストップ」を押してください。")

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
            opacity = "0.3" if name in st.session_state.selected_cards else "1.0"
            st.markdown(
                f'<img src="{TAROT_BACK_URL}" '
                f'style="width:100%; opacity:{opacity}; border-radius:5px;">',
                unsafe_allow_html=True,
            )
            if name not in st.session_state.selected_cards:
                if st.button("選択", key=f"btn_{name}_{i}"):
                    st.session_state.selected_cards.append(name)
                    # ★ ここで 50% の確率で逆位置を判定
                    st.session_state.selected_reversed.append(
                        bool(random.getrandbits(1))
                    )
                    if len(st.session_state.selected_cards) == 2:
                        st.session_state.stage = 3
                    st.rerun()

# --- stage 3: 鑑定準備 ---
elif st.session_state.stage == 3:
    st.subheader("🔮 選ばれた2枚のメッセージ")

    c1, c2 = st.columns(2)
    card1 = st.session_state.selected_cards[0]
    card2 = st.session_state.selected_cards[1]
    rev1 = st.session_state.selected_reversed[0]
    rev2 = st.session_state.selected_reversed[1]

    with c1:
        show_card(card1, rev1, "1. 現在の状況")
    with c2:
        show_card(card2, rev2, "2. 未来の鍵")

    if st.button("🔮 鑑定結果を生成する（無料）", use_container_width=True):
        if not api_key:
            st.error("APIキーが必要です。")
        else:
            lp_num = calc_life_path(birthday)
            lp_info = get_life_path_info(lp_num)

            meta1 = TAROT_DATA[card1]
            meta2 = TAROT_DATA[card2]

            pos1 = "逆位置" if rev1 else "正位置"
            pos2 = "逆位置" if rev2 else "正位置"

            prompt = f"""
あなたは、数秘術と黄金の夜明け団のタロット象徴体系を極めた超一流の占い師です。口調は優しくて説明上手なプロの占い師です。
数秘術（ライフパスナンバー）とタロットを組み合わせて、相談者の気持ちに寄り添いながら精密に鑑定してください。

まず最初に、
・ライフパスナンバーとは「生年月日から計算する、その人の人生の基本的なテーマやクセを表す数秘術の数字」であることを、やさしく1〜2文で説明する
・そのうえで、「ライフパス{lp_num}番を持つあなたは、{lp_info}という気質がありますね」のように、相談者の性質を丁寧に伝える

そのあと、次の構成で文章を作ってください。

【相談者情報】
ニックネーム：{nickname}
ライフパスナンバー：{lp_num}（{lp_info}）
相談内容：{fortune_topic}
補足メモ：{one_line}

【引いたカード】
1. 現状：{card1}（{pos1} / 元素：{meta1['element']} / 占星術的キーワード：{meta1['astro']}）
2. 助言：{card2}（{pos2} / 元素：{meta2['element']} / 占星術的キーワード：{meta2['astro']}）

【出力構成】
1. ライフパス{lp_num}の簡単な説明と、今日のテーマとのかかわり
2. 今のあなたが引き寄せている「エネルギーの正体」（主に {card1} を中心に）
3. 未来を好転させるために、{card2} をどう使えばいいか（具体的な行動レベルで）
4. 守護のメッセージ

【トーンと逆位置の扱い】
・難しい専門用語はできるだけ噛み砕いて説明する
・不安をあおる言い方や、「絶対こうなる」といった断定は避ける
・前向きだけど現実味のあるアドバイスにする
・カードが逆位置（{pos1} や {pos2}）で出ている場合は、「悪い」「不吉」と断定するのではなく、「内省、過剰、遅延、隠れた可能性」としてポジティブなニュアンスで、やさしく解釈する
・2つのカードの元素の組み合わせ（例：火×地など）から、現在の運気の流れ（スムーズか、摩擦があるか）を述べてください
・「今日から3日以内にできる具体的アクション」を3つ提示してください
・どのカードが逆位置なのか、本文のどこかで必ず一度は説明に触れる
・文字量は、スマホで読んで「お得感があるな」と思えるボリュームにする
・見出しは「## 見出しタイトル」のようにMarkdown形式で入れてください
・具体的な行動は「- 箇条書き」で3つ以上、わかりやすく書いてください
"""

            client = OpenAI(api_key=api_key)

            try:
                with st.spinner("深層意識を読み解いています..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                    )

                text = response.choices[0].message.content.strip()
                st.session_state.reading_text = text
                st.session_state.stage = 4
                st.rerun()

            except Exception as e:
                st.error("少し混み合っているようです。時間をおいてもう一度お試しください。")
                st.caption(f"（エラー内容: {e}）")


# --- stage 4: 結果表示 ---
elif st.session_state.stage == 4:
    st.subheader(f"✨ {nickname} さんの鑑定結果")

    c1, c2 = st.columns(2)
    card1 = st.session_state.selected_cards[0]
    card2 = st.session_state.selected_cards[1]
    rev1 = st.session_state.selected_reversed[0]
    rev2 = st.session_state.selected_reversed[1]

    with c1:
        show_card(card1, rev1, "現状")
    with c2:
        show_card(card2, rev2, "助言")

    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown(st.session_state.reading_text)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- SNS シェア ---
    st.divider()
    st.write("### 🔮 幸運をシェアする")

    share_url = "https://my-tarot-app.streamlit.app/"
    share_text = f"今日の鑑定は『{card1}』と『{card2}』🔮 #AIタロット"
    encoded_text = urllib.parse.quote(share_text)
    encoded_url = urllib.parse.quote(share_url)

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
     <i class="fa-brands fa-facebook"></i> FB
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

    # --- 応援（Buy Me a Coffee / OFUSE）---
    st.divider()
    st.markdown("### ☕ この占いを続ける応援")
    st.write(
        "この占いは広告なし・無料で運営しています。"
        "「また引きたいな」と感じてもらえたら、"
        "コーヒー1杯分の応援がアプリの維持、次の改善や新メニューの開発につながります。"
    )

    st.link_button(
        "☕ Buy Me a Coffee で応援する",
        "https://buymeacoffee.com/mystic_tarot",
        use_container_width=True,
    )

    st.link_button(
        "💌 OFUSEで応援メッセージを送る（おすすめ）",
        "https://ofuse.me/mystictarot",
        use_container_width=True,
    )











