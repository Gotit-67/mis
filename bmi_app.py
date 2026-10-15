import base64
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="轻盈 BMI · 健康管理", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

ASSET = Path(__file__).resolve().parent / "assets" / "health-pyramid.png"
ASSET_DATA = "data:image/png;base64," + base64.b64encode(ASSET.read_bytes()).decode("ascii") if ASSET.exists() else ""
PET_ASSET = Path(__file__).resolve().parent / "assets" / "health-pet.png"
PET_DATA = "data:image/png;base64," + base64.b64encode(PET_ASSET.read_bytes()).decode("ascii") if PET_ASSET.exists() else ""

st.markdown("""
<style>
:root { --ink:#183b31; --muted:#526b60; --green:#2f765f; --mint:#e6f3ec; --peach:#fff0df; --purple:#5948c7; }
* { font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",Arial,sans-serif; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }
.stMarkdown, .stText, label, button, input, textarea { line-height:1.65; }
.stApp { background-color:#f7faf4; background-image:linear-gradient(135deg,#fbfaf3e8 0%,#f0f7f0e8 53%,#fff5eae8 100%),url("__PYRAMID__"); background-size:cover; background-position:center; background-attachment:fixed; color:var(--ink); }
.main, .main .block-container { position:relative; z-index:auto; }
section[data-testid="stSidebar"] { z-index:2; }
.block-container { max-width:1180px; padding-top:3.6rem; padding-bottom:3rem; }
.brand { display:flex; align-items:center; gap:12px; margin-bottom:4px; }
.brand { min-height:52px; line-height:1.25; }
.brand-mark { width:43px; height:43px; display:grid; place-items:center; background:#d8eee2; border-radius:15px; font-size:25px; box-shadow:0 4px 15px #8ebc9b35; }
.brand h1 { font-size:25px; margin:0; letter-spacing:-1px; color:#2e584a; }
.brand small { color:#82948b; font-size:12px; }
.hero { position:relative; min-height:320px; margin:8px 0 20px; border:1px solid #e1ede4; border-radius:28px; overflow:hidden; background:#fffdf7; box-shadow:0 15px 42px #547b5b18; }
.hero-copy { position:absolute; z-index:2; left:34px; top:31px; max-width:340px; }
.hero-copy .eyebrow { color:#4d9b78; font-weight:700; font-size:13px; letter-spacing:2px; }
.hero-copy h2 { font-size:34px; line-height:1.2; margin:8px 0 10px; color:#284b40; }
.hero-copy p { color:#405f53; line-height:1.8; margin:0; }
.hero img { position:absolute; right:-2%; bottom:-5%; width:72%; min-width:520px; max-height:104%; object-fit:contain; object-position:center; opacity:.20; mix-blend-mode:multiply; }
.pill { display:inline-block; background:#f0eaff; color:#6753c8; border-radius:99px; padding:6px 12px; font-size:12px; font-weight:600; margin-top:17px; }
.card { background:#fff; border:1px solid #e5eee9; border-radius:22px; padding:22px; box-shadow:0 8px 24px #4d6e5b12; }
.section-title { font-size:22px; color:#2e5146; font-weight:800; margin:4px 0 2px; }
.section-sub { color:#526b60; font-size:13px; margin-bottom:16px; }
.gender-card { border:1.5px solid #e5eee9; border-radius:18px; padding:13px; background:#fbfdfb; text-align:center; transition:.2s; }
.gender-card:hover { transform:translateY(-2px); box-shadow:0 8px 20px #6f9e801c; }
.gender-icon { font-size:39px; display:inline-block; animation:gentle-bob 2.8s ease-in-out infinite; }
.gender-card:nth-of-type(2) .gender-icon { animation-delay:.4s; }
.gender-card:hover .gender-icon { animation:happy-hop .55s ease-in-out infinite alternate; }
.mood-switch { position:relative; width:48px; height:48px; vertical-align:middle; }
.mood-switch span { position:absolute; inset:0; opacity:0; animation:mood-flip 3.6s ease-in-out infinite; }
.mood-switch span:first-child { opacity:1; }
.mood-switch span:last-child { animation-delay:1.8s; }
.gender-name { font-weight:700; color:#254d3f; }
.gender-note { font-size:11px; color:#60786d; margin-top:3px; }
.result-box { border-radius:24px; padding:24px; color:#fff; background:linear-gradient(135deg,#376f5d,#77ad83); box-shadow:0 12px 30px #4e916e40; }
.result-box .label { opacity:.8; font-size:13px; }
.bmi-number { font-size:64px; font-weight:800; letter-spacing:-3px; line-height:1; margin:10px 0; }
.result-tag { display:inline-block; padding:6px 13px; border-radius:99px; background:#ffffff26; font-weight:700; }
.tip { background:#fffaf0; border:1px solid #f4e2bd; color:#735b33; border-radius:16px; padding:13px 15px; line-height:1.65; font-size:13px; }
.envelope { background:repeating-linear-gradient(0deg,#fff9ee,#fff9ee 8px,#ffeed3 9px,#fff9ee 10px); border:1px solid #f4d9aa; border-radius:18px; padding:16px 20px; font-weight:800; color:#8a6234; text-align:center; font-size:16px; }
.history-empty { text-align:center; color:#91a198; padding:30px 10px; }
.metric-note { font-size:12px; color:#526b60; }
.stMarkdown p, .stMarkdown li, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] { color:#38594d; }
[data-testid="stRadio"] label p { color:#234b3d !important; font-weight:600; }
[data-testid="stRadio"] label { border:1px solid #cfe2d5; border-radius:16px; padding:10px 14px; background:#fbfefb; transition:.2s; }
[data-testid="stRadio"] label:hover { border-color:#56a976; background:#eff9f0; transform:translateY(-2px); }
[data-testid="stRadio"] [aria-checked="true"] + div { color:#214e3e; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:99px; padding:8px 18px; background:#edf5ef; color:#537466; }
.stTabs [aria-selected="true"] { background:#6958d8 !important; color:#fff !important; }
.gauge-card { background:#fff; border:1px solid #e5eee9; border-radius:24px; padding:20px 18px 15px; box-shadow:0 8px 24px #4d6e5b12; text-align:center; }
.gauge-title { color:#70847a; font-size:13px; margin-bottom:2px; }
.gauge { width:280px; height:190px; position:relative; margin:0 auto; overflow:hidden; }
.gauge-arc { position:absolute; width:255px; height:255px; left:12px; top:20px; border-radius:50%; background:conic-gradient(from 225deg, #efb06d 0deg, #6fbd7c 100deg, #8ac998 150deg, #efb06d 210deg, #e88775 270deg, transparent 270deg); -webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); }
.gauge-pointer { position:absolute; width:3px; height:105px; background:#5c6b64; left:50%; top:47px; transform-origin:50% 100%; border-radius:4px; z-index:3; }
.gauge-pointer:after { content:''; position:absolute; width:12px; height:12px; background:#5c6b64; border-radius:50%; left:50%; top:-4px; transform:translateX(-50%); }
.gauge-center { position:absolute; z-index:2; left:0; right:0; top:95px; }
.gauge-number { font-size:48px; line-height:1; font-weight:800; color:#55ad6d; letter-spacing:-2px; }
.gauge-sub { margin-top:8px; color:#93a099; font-size:15px; }
.gauge-tag { display:inline-block; padding:5px 11px; border-radius:99px; background:#63bb78; color:white; font-weight:700; font-size:13px; }
.gauge-label { position:absolute; z-index:3; font-weight:600; color:#506058; font-size:14px; }
.gauge-label.l1 { left:5px; top:84px; }.gauge-label.l2 { left:132px; top:18px; }.gauge-label.l3 { right:5px; top:84px; }
.gauge-scale { display:flex; justify-content:space-around; color:#9aa8a0; font-size:11px; margin-top:-2px; }
.pet-title { display:flex; align-items:center; gap:8px; color:#2e584a; font-weight:800; font-size:18px; }
.pet-hint { color:#244f3d; background:linear-gradient(90deg,#e2f5e5,#f5fbe9); border:2px solid #9dcea4; border-radius:16px; padding:12px 16px; margin:4px 0 10px; font-size:14px; font-weight:700; box-shadow:0 5px 16px #6ba77c22; }
.streamlit-expanderHeader { color:#285541 !important; font-weight:800 !important; font-size:15px !important; }
div[data-testid="stExpander"] { border:2px solid #c9e2cb; border-radius:18px; background:#fbfffa; box-shadow:0 7px 20px #5b906820; }
.pet-avatar { width:118px; height:118px; object-fit:contain; display:block; margin:0 auto -8px; filter:drop-shadow(0 8px 7px #5a9c7030); animation:pet-float 3.2s ease-in-out infinite; }
.pet-bubble { background:#f2f8ed; border:1px solid #d9ead5; border-radius:16px 16px 16px 4px; padding:11px 12px; color:#496a5a; font-size:12px; line-height:1.75; animation:bubble-breathe 3s ease-in-out infinite; }
.food-chip { display:inline-block; background:#fff7e7; border:1px solid #f2dfb9; border-radius:99px; padding:4px 8px; margin:3px 2px; font-size:11px; }
.shutter-shell { position:relative; overflow:hidden; border-radius:18px; }
.shutter-shell:before { content:''; position:absolute; inset:0; height:20px; background:repeating-linear-gradient(0deg,#fff4d8 0 5px,#f5d49d 6px 7px); transform-origin:top; z-index:2; pointer-events:none; opacity:.9; }
.shutter-shell:hover:before { height:0; transition:height .45s ease; }
div[data-testid="stNumberInput"] input { border-radius:12px; }
div.stButton > button { border-radius:14px; border:0; background:#3b806b; color:white; font-weight:700; padding:10px 18px; }
div.stButton > button:hover { background:#2d6553; color:white; }
@keyframes gentle-bob { 0%,100%{transform:translateY(0) rotate(-2deg)} 50%{transform:translateY(-5px) rotate(2deg)} }
@keyframes happy-hop { from{transform:translateY(0) scale(1)} to{transform:translateY(-8px) scale(1.06)} }
@keyframes pet-float { 0%,100%{transform:translateY(0) rotate(-1deg)} 50%{transform:translateY(-9px) rotate(1deg)} }
@keyframes bubble-breathe { 0%,100%{box-shadow:0 0 0 #9bc88a00} 50%{box-shadow:0 0 0 5px #9bc88a18} }
@keyframes mood-flip { 0%,42%{opacity:1;transform:scale(1)} 50%,92%{opacity:0;transform:scale(.82)} 100%{opacity:1;transform:scale(1)} }
</style>
""".replace("__PYRAMID__", ASSET_DATA), unsafe_allow_html=True)


def init_state():
    if "records" not in st.session_state:
        st.session_state.records = []
    if "food_log" not in st.session_state:
        st.session_state.food_log = []
    if "exercise_minutes" not in st.session_state:
        st.session_state.exercise_minutes = 0
    if "pet_reply" not in st.session_state:
        st.session_state.pet_reply = "嗨！我是轻盈仔 🌿 你可以问我 BMI、饮食、运动和作息，我会结合你的记录一起想办法。"


def pet_reply(question, latest, food_log, exercise_minutes):
    context = f"当前 BMI：{latest['bmi']:.1f}（{latest['level']}）" if latest else "还没有 BMI 记录"
    foods = "、".join(food_log[-6:]) if food_log else "暂未投喂食物"
    if question:
        q = question.lower()
        if any(k in q for k in ["吃", "饮食", "食物", "饭"]):
            return f"根据{context}，今天你记录了：{foods}。建议把蔬菜和蛋白质放在主食前，饮料优先选白水或无糖茶；我不会要求你极端节食，先把一餐吃得更均衡就很好。"
        if any(k in q for k in ["运动", "锻炼", "走", "跑"]):
            return f"你目前累计运动 {exercise_minutes} 分钟。可以从快走 20–30 分钟开始，每周逐步靠近 150–300 分钟；如果今天很忙，分成 2–3 次完成也算数。"
        if any(k in q for k in ["风险", "疾病", "健康"]):
            return f"{context}。BMI 是筛查参考，不是诊断；如果你属于超重或肥胖，建议关注血压、血糖、血脂和肝功能，并在需要时咨询医生。"
    if not latest:
        return "先完成一次 BMI 测量，我就能把建议变得更具体；也可以先把今天吃过的食物喂给我。"
    return f"我记住啦：{context}。今天已投喂 {len(food_log)} 次食物，运动 {exercise_minutes} 分钟。你可以继续问我‘晚餐怎么吃’或‘今天适合做什么运动’。"


def food_feedback(text, latest):
    lower = text.lower()
    suggestions = {
        "蔬菜": "🥬 成年人每天建议摄入蔬菜约 300–500g，深色蔬菜最好占一半以上。",
        "水果": "🍎 水果每天建议约 200–350g，优先完整水果，不用果汁替代。",
        "奶": "🥛 奶及奶制品每天可按约 300g 液态奶或等量替代品安排。",
        "酸奶": "🥣 酸奶可以作为奶制品来源，优先无糖款，注意看配料表和添加糖。",
        "鸡蛋": "🥚 鸡蛋是优质蛋白来源，可以和蔬菜、全谷物搭配。",
        "肉": "🍗 鱼、禽、蛋、瘦肉要适量搭配，优先鱼虾、禽肉和瘦肉。",
        "米饭": "🍚 主食不必完全不吃，可用部分糙米、燕麦、玉米、红薯替换精白米面。",
        "油炸": "🍟 油炸食物偶尔少量即可，今天可以用烤、蒸、煮替代。",
        "奶茶": "🧋 奶茶通常含糖和能量较高，建议选无糖茶、白水或无糖咖啡。",
        "饮料": "🥤 含糖饮料尽量少喝，口渴优先选择白水或无糖茶。",
    }
    matched = next((value for key, value in suggestions.items() if key in lower), "🍽️ 我暂时没识别出具体食物，可以写成‘食物 + 量’，例如‘苹果 200g’。")
    if any(k in lower for k in ["苹果", "香蕉", "橙", "梨", "桃", "水果"]):
        unit_hint = "这类食物用‘几个’最方便，例如苹果 1 个、香蕉 1 根。"
    elif any(k in lower for k in ["鸡蛋", "面包", "包子", "馒头"]):
        unit_hint = "这类食物可以按‘个 / 片’填写，例如鸡蛋 2 个、面包 2 片。"
    elif any(k in lower for k in ["米饭", "面条", "粥", "粉"]):
        unit_hint = "主食可以按‘碗 / 份’填写，例如米饭 1 碗、面条 1 份。"
    elif any(k in lower for k in ["牛奶", "豆浆", "酸奶", "饮料", "水"]):
        unit_hint = "饮品可以按‘毫升 / 盒’填写，例如牛奶 250ml、酸奶 1 盒。"
    else:
        unit_hint = "蔬菜、肉类等可以按克填写，例如青菜 200g、鸡胸肉 100g。"
    amount_hint = "我已经记下这次的食物和份量。" if any(ch.isdigit() for ch in text) else f"记得补充食用量。{unit_hint}"
    context = f"结合你最近 BMI {latest['bmi']:.1f}（{latest['level']}），" if latest else "结合一般成人膳食建议，"
    return f"{context}{matched}<br>📌 {amount_hint}<br>🌱 建议把这一餐搭配蔬菜和蛋白质。"


def pet_panel():
    st.markdown('<div class="pet-hint">🌿 点击下面的绿色卡片打开「轻盈仔」：它只有一个输入框，先点三个小想法，再输入内容发送。</div>', unsafe_allow_html=True)
    with st.expander("🌿 点击这里打开轻盈仔 · 你的健康电子 Pet", expanded=True):
        st.markdown('<div class="pet-title">🌿 轻盈仔 <span style="font-size:11px;color:#58786a">你的健康电子 Pet</span></div>', unsafe_allow_html=True)
        if PET_ASSET.exists():
            st.image(str(PET_ASSET), width=150)
        st.markdown(f'<div class="pet-bubble">{st.session_state.pet_reply}</div>', unsafe_allow_html=True)
        latest = st.session_state.records[-1] if st.session_state.records else None
        st.markdown("#### 💭 轻盈仔的三个小想法")
        q1, q2, q3 = st.columns(3)
        with q1: food_mode = st.button("🍽️ 我吃了什么？", use_container_width=True)
        with q2: exercise_mode = st.button("🏃 我运动多久？", use_container_width=True)
        with q3: ask_mode = st.button("💬 我想问健康", use_container_width=True)
        if food_mode: st.session_state.pet_mode = "food"
        elif exercise_mode: st.session_state.pet_mode = "exercise"
        elif ask_mode: st.session_state.pet_mode = "ask"
        mode = st.session_state.get("pet_mode", "ask")
        labels = {"food": "输入食物 + 食用量", "exercise": "输入运动 + 时长", "ask": "输入健康问题"}
        hints = {"food": "例如：苹果 1 个、米饭 1 碗、鸡蛋 2 个、牛奶 250ml", "exercise": "例如：快走 30 分钟、跳绳 15 分钟", "ask": "例如：晚餐怎么吃？最近总熬夜怎么办？"}
        prompt = st.text_input(labels[mode], placeholder=hints[mode], key="pet_single_input")
        if st.button("发送给轻盈仔 ✨", use_container_width=True, disabled=not prompt.strip()):
            if mode == "food":
                st.session_state.food_log.append(prompt.strip())
                st.session_state.pet_reply = food_feedback(prompt.strip(), latest)
            elif mode == "exercise":
                found = re.search(r"(\d+(?:\.\d+)?)", prompt)
                added = int(float(found.group(1))) if found else 0
                st.session_state.exercise_minutes += added
                st.session_state.pet_reply = f"我记下啦：{prompt.strip()}。今天累计运动 {st.session_state.exercise_minutes} 分钟。<br>🎯 每周可以逐步靠近 150–300 分钟，忙的时候分段完成也算数。"
            else:
                st.session_state.pet_reply = pet_reply(prompt.strip(), latest, st.session_state.food_log, st.session_state.exercise_minutes)
            st.rerun()
        if st.session_state.food_log:
            st.markdown("".join(f'<span class="food-chip">🍴 {item}</span>' for item in st.session_state.food_log[-6:]), unsafe_allow_html=True)
        st.markdown("#### 📊 轻盈仔的小图表")
        if st.session_state.records:
            pet_chart = pd.DataFrame(st.session_state.records)
            pet_chart["时间"] = pd.to_datetime(pet_chart["date"])
            st.line_chart(pet_chart.set_index("时间")["bmi"], color="#55a96f", height=180)
            st.caption(f"已记录 {len(st.session_state.records)} 次 BMI · 今日运动 {st.session_state.exercise_minutes} 分钟 · 已记录 {len(st.session_state.food_log)} 次饮食")
        else:
            st.info("完成第一次 BMI 测量后，这里会出现你的趋势图；先和轻盈仔说说今天吃了什么吧。")
        st.caption("食物请写清楚数量，例如克、毫升、个或碗；轻盈仔会结合 BMI 和记录给出份量建议。")


def classify(bmi):
    if bmi < 18.5:
        return "偏瘦", "🍃", "建议适当增加营养与优质蛋白，规律吃饭，慢慢把身体养回来。", "low"
    if bmi < 24:
        return "正常", "😊", "状态很棒！继续保持吃动平衡、规律作息，让好习惯成为你的超能力。", "good"
    if bmi < 28:
        return "超重", "🙂", "别着急，先从少一杯含糖饮料、多走十分钟开始，稳定的小改变最有力量。", "watch"
    return "肥胖", "💪", "建议温和、持续地管理体重；如有基础疾病或明显不适，请咨询医生或营养师。", "high"


def advice(level, gender):
    if level == "偏瘦":
        return [
            ("🥣 饮食核心", "🍚 三餐 + 1–2 次加餐，先把规律吃饭做起来。<br>🥚 每餐加入蛋、奶、鱼、肉、豆类中的 1–2 种优质蛋白。<br>🥜 加餐可选坚果、酸奶、香蕉、全麦面包；不要只靠奶茶和甜点增重。<br>📈 每周观察一次体重，缓慢增加比突然暴食更稳妥。"),
            ("🍱 一日餐盘", "🌞 早餐：牛奶 / 豆浆 + 鸡蛋 + 全麦主食。<br>☀️ 午餐：米饭 + 鱼肉或鸡肉 + 两份蔬菜。<br>🌙 晚餐：面 / 杂粮饭 + 豆腐或瘦肉 + 菌菇蔬菜。<br>🍎 加餐：酸奶、水果、坚果三选一，感觉饱胀就减少份量。"),
            ("🏋️ 运动方案", "💪 每周 2–3 次力量训练：深蹲、臀桥、俯卧撑、弹力带划船各 2–3 组。<br>🚶 搭配轻松有氧，每次 20–30 分钟。<br>🎯 重点是保留肌肉，不用用大量跑步抵消进食。<br>🩺 体重持续下降、乏力或食欲异常时请咨询医生。"),
            ("🌙 生活节奏", "⏰ 固定起床和入睡时间，争取 7–9 小时睡眠。<br>💧 白天分次饮水，避免用咖啡或能量饮料顶替正餐。<br>🧡 每天记录一次‘吃饭 / 精力 / 心情’，找到影响食欲的原因。"),
        ]
    return [
        ("🥗 饮食核心", "🍽️ 进餐顺序：蔬菜 → 蛋白质 → 主食，先吃慢吃，七八分饱即可。<br>🥬 每餐至少一半是蔬菜，优先深色叶菜、菌菇、番茄。<br>🥚 蛋白质选鱼虾、鸡蛋、瘦肉、豆制品和奶。<br>🚫 少吃油炸、含糖饮料、甜点和酒；盐尽量控制在每日 5g 内，烹调油约 25–30g。"),
        ("🍱 一日餐盘", "🌞 早餐：无糖奶 / 豆浆 + 鸡蛋 + 全麦面包。<br>☀️ 午餐：半盘蔬菜 + 一掌心蛋白质 + 半拳到一拳主食。<br>🌙 晚餐：清淡蛋白质 + 蔬菜 + 适量杂粮主食，睡前 2–3 小时尽量不再进食。<br>🍎 想吃零食时：先喝水，优先水果、原味坚果或无糖酸奶。"),
        ("🏃 运动方案", "🚶 每周累计 150–300 分钟中等强度运动：快走、游泳、骑车都可以。<br>💪 每周 2–3 天抗阻训练：深蹲、臀桥、哑铃推举、弹力带划船。<br>⏱️ 久坐每 60 分钟起身 3–5 分钟，接水、拉伸、走动都算。<br>🌱 先从每天 20 分钟开始，稳定两周后再增加时长。"),
        ("🧘 心理与作息", "🌙 目标是 7–9 小时睡眠，尽量固定入睡和起床时间。<br>📝 想吃东西时先问自己：我是饿了、累了，还是在焦虑？<br>🌬️ 情绪上来时先做 3 分钟深呼吸、散步或伸展，再决定要不要吃。<br>👏 关注一周趋势，不因某一顿饭或某一天的体重责怪自己。"),
    ]


def risk_page(level):
    if level == "偏瘦":
        return ("🌿 体重过低的照顾提醒", "体重过低可能与营养摄入不足、肌肉量下降或潜在健康问题有关。可以关注食欲、疲劳感和近期体重变化，采用少量多餐、增加优质蛋白的方式温和调整；若体重持续下降或伴随不适，请及时咨询医生。", "需要留意：持续下降、乏力、食欲明显变化")
    if level == "正常":
        return ("🌈 继续守护你的健康", "BMI 在正常范围并不等于所有健康指标都正常。建议继续关注血压、血糖和血脂，保持规律运动与作息，让好状态稳稳延续。", "建议关注：血压、血糖、血脂")
    if level == "超重":
        return ("🔎 超重阶段的风险参照", "超重可能增加高血压、血糖异常、血脂异常、脂肪肝等代谢问题的发生风险。越早从饮食、运动和睡眠做小调整，越容易把变化控制在可管理的范围内；这不是对个人疾病的诊断。", "建议留意：血压、空腹血糖、血脂")
        return ("🧡 肥胖阶段的风险参照", "肥胖与高血压、2 型糖尿病、血脂异常、脂肪肝及心脑血管疾病等风险增加有关。建议在专业人士指导下制定循序渐进的体重管理计划；如已有慢性病或明显不适，请优先就医。", "建议留意：血压、血糖、血脂、肝功能及睡眠情况")


def gauge_html(bmi, level, emoji):
    # 成人 BMI 展示区间为 15–35；分类仍严格使用中国成人 BMI 口径。
    pct = max(0.0, min(1.0, (bmi - 15) / 20))
    angle = -135 + 270 * pct
    return f'''<div class="gauge-card">
        <div class="gauge-title">你的 BMI 身体质量指数</div>
        <div class="gauge">
          <div class="gauge-arc"></div>
          <div class="gauge-pointer" style="transform:translateX(-50%) rotate({angle:.1f}deg)"></div>
          <div class="gauge-center"><div class="gauge-number">{bmi:.1f}</div><div class="gauge-sub">BMI&nbsp; <span class="gauge-tag">{emoji} {level}</span></div></div>
          <span class="gauge-label l1">18.5</span><span class="gauge-label l2">24</span><span class="gauge-label l3">28</span>
        </div>
        <div class="gauge-scale"><span>偏瘦</span><span>正常</span><span>超重</span><span>肥胖</span></div>
    </div>'''


def main():
    init_state()
    pet_panel()
    st.markdown('<div class="brand"><div class="brand-mark">🌿</div><div><h1>轻盈 BMI</h1><small>把健康，变成每天都做得到的小事</small></div></div>', unsafe_allow_html=True)

    st.markdown(f'''<div class="hero"><div class="hero-copy"><div class="eyebrow">HEALTHY HABITS · 健康习惯</div><h2>今天的你，<br>值得被好好照顾。</h2><p>从一次 BMI 查询开始，发现身体发来的小信号，给自己一份温柔又具体的行动计划。</p><span class="pill">✨ 记录每一次轻盈变化</span></div><img src="{ASSET_DATA}" /></div>''', unsafe_allow_html=True)

    tab_check, tab_profile, tab_guide = st.tabs(["🌱 开始测量", "📈 个人中心", "📚 官方健康建议"])
    with tab_check:
        st.markdown('<div class="section-title">先认识一下今天的你</div><div class="section-sub">选择性别后，我们会给你更贴合的健康建议。成人 BMI 参考适用于 18 岁及以上人群。</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.2, 1], gap="medium")
        with c1:
            selected_gender = st.radio("你的性别（点击图标即可选择）", ["🧒🏻 男生", "👧🏻 女生"], horizontal=True, label_visibility="visible")
            gender = selected_gender.split(" ", 1)[1]
        with c2:
            age = st.number_input("年龄", min_value=1, max_value=120, value=25, step=1)

        st.markdown("#### 📏 输入身体数据")
        i1, i2 = st.columns(2)
        with i1:
            height = st.number_input("身高（米）｜例如：1.70", min_value=0.5, max_value=2.5, value=1.70, step=0.01, format="%.2f", help="请用米填写：170 厘米 = 1.70 米")
        with i2:
            weight = st.number_input("体重（千克）｜例如：60.0", min_value=10.0, max_value=300.0, value=60.0, step=0.1, format="%.1f", help="请用千克填写：60 斤约等于 30 千克")

        if st.button("✨ 查看我的 BMI", use_container_width=True):
            bmi = weight / (height ** 2)
            level, emoji, tip, tone = classify(bmi)
            previous = st.session_state.records[-1] if st.session_state.records else None
            delta = None if previous is None else bmi - previous["bmi"]
            st.session_state.current = {"bmi": bmi, "weight": weight, "level": level, "emoji": emoji, "tip": tip, "gender": gender, "age": age, "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
            st.session_state.records.append(st.session_state.current.copy())
            st.session_state.delta = delta

        if "current" in st.session_state:
            r = st.session_state.current
            delta = st.session_state.get("delta")
            left, right = st.columns([1.2, 1], gap="large")
            with left:
                st.markdown(gauge_html(r["bmi"], r["level"], r["emoji"]), unsafe_allow_html=True)
                st.markdown(f'<div class="result-box" style="margin-top:12px"><div class="label">轻盈小提醒</div><p style="margin:8px 0 0;opacity:.95;line-height:1.7">{r["tip"]}</p></div>', unsafe_allow_html=True)
                low_w, high_w = 18.5 * height ** 2, 23.9 * height ** 2
                a, b, c = st.columns(3)
                a.metric("健康体重下限", f"{low_w:.1f} kg")
                b.metric("健康体重上限", f"{high_w:.1f} kg")
                c.metric("本次体重", f"{weight:.1f} kg")
                st.caption("按中国成人 BMI 18.5–23.9 的参考区间换算；不适用于未成年人、孕期及特殊人群。")
            with right:
                st.markdown("#### 🧭 你的健康坐标")
                st.progress(min(r["bmi"] / 40, 1.0))
                st.caption("偏瘦 18.5　　正常 24　　超重 28　　肥胖")
                st.markdown('<div class="tip">BMI 是筛查参考，不是疾病诊断。建议结合血压、血糖、血脂、睡眠和日常精力综合观察。</div>', unsafe_allow_html=True)
                if delta is not None:
                    if delta < -0.1:
                        st.success(f"👍 比上一次下降 {abs(delta):.1f}，你的坚持正在发生变化！")
                    elif delta > 0.1:
                        st.info(f"🌤️ 比上一次上升 {delta:.1f}，别责怪自己，看看近期作息和饮食即可。")
                    else:
                        st.info("🌼 和上次差不多，稳定也是一种进步。")

            st.markdown("#### ✉️ 你的专属健康手册已送达")
            with st.expander("📨 点击打开专属健康手册 · 查看你的行动方案", expanded=True):
                st.markdown('<div class="envelope">💌 你的专属健康手册到了！<br><span style="font-size:12px;font-weight:500">点击上方绿色标题，逐页查看饮食、运动、作息和风险参照</span></div>', unsafe_allow_html=True)
                handbook = advice(r["level"], r["gender"])
                risk_title, risk_text, risk_watch = risk_page(r["level"])
                pages = [(title, text) for title, text in handbook] + [(risk_title, risk_text)]
                page_names = [f"第 {i + 1} 页 · {title.split(' ', 1)[-1]}" for i, (title, _) in enumerate(pages)]
                selected_page = st.radio("手册分页", page_names, horizontal=True, label_visibility="collapsed")
                page_index = page_names.index(selected_page)
                page_title, page_text = pages[page_index]
                st.markdown(f"### {page_title}")
                st.markdown(f'<div class="tip" style="font-size:15px;line-height:2">{page_text}</div>', unsafe_allow_html=True)
                if page_index == len(pages) - 1:
                    st.info(f"🩺 {risk_watch}\n\n以上是风险参照，不代表你已经患有相关疾病。")
                st.caption(f"{page_index + 1} / {len(pages)}　·　左右选择上方分页，逐页阅读你的行动建议")
                st.warning("⚠️ 以上是成人健康管理参考。孕期、未成年人、运动员或有慢性病者，请遵循专业人士建议。")

    with tab_profile:
        st.markdown('<div class="section-title">你的身体变化日记</div><div class="section-sub">每次测量都会留下一个小脚印，关注趋势，比盯着某一个数字更重要。</div>', unsafe_allow_html=True)
        records = st.session_state.records
        if not records:
            st.markdown('<div class="card history-empty">🌱 还没有测量记录<br><span class="metric-note">完成第一次测量后，这里会出现你的 BMI 趋势折线和鼓励徽章。</span></div>', unsafe_allow_html=True)
        else:
            df = pd.DataFrame(records)
            df["时间"] = pd.to_datetime(df["date"])
            f1, f2, f3, f4 = st.columns(4)
            with f1: view = st.radio("查看范围", ["最近", "今年", "近半年", "全部"], horizontal=True, label_visibility="collapsed")
            with f2: chart_metric = st.radio("指标", ["BMI", "体重"], horizontal=True, label_visibility="collapsed")
            if view == "今年": chart_df = df[df["时间"].dt.year == datetime.now().year]
            elif view == "近半年": chart_df = df[df["时间"] >= datetime.now() - timedelta(days=183)]
            elif view == "最近": chart_df = df.tail(8)
            else: chart_df = df
            if chart_df.empty: chart_df = df.tail(1)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            metric_key = {"BMI": "bmi", "体重": "weight"}[chart_metric]
            metric_data = chart_df.dropna(subset=[metric_key]).set_index("时间")[metric_key]
            st.line_chart(metric_data, color="#6958d8", height=300)
            mn, mx = chart_df[metric_key].min(), chart_df[metric_key].max()
            m1, m2, m3 = st.columns(3)
            unit = "" if chart_metric == "BMI" else " kg"
            m1.metric(f"最低 {chart_metric}", f"{mn:.1f}{unit}")
            m2.metric(f"最高 {chart_metric}", f"{mx:.1f}{unit}")
            m3.metric("测量次数", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("#### 🧡 最近记录")
            for idx, row in df.iloc[::-1].head(10).iterrows():
                prev = df.iloc[idx-1]["bmi"] if idx > 0 else None
                badge = "👍" if prev is not None and row["bmi"] < prev - .1 else ""
                st.markdown(f'<div class="card" style="padding:14px 18px;margin:8px 0"><b>{row["emoji"]} {row["level"]}</b>　BMI <b>{row["bmi"]:.1f}</b>　<span class="metric-note">{row["date"]} · {row["gender"]}</span> <span style="float:right;font-size:20px">{badge}</span></div>', unsafe_allow_html=True)
            if st.button("清空本地记录"):
                st.session_state.records = []
                st.rerun()

    with tab_guide:
        st.markdown('<div class="section-title">官方健康建议</div><div class="section-sub">把可靠的知识，变成今天就能做到的选择。</div>', unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown('<div class="card"><div style="font-size:30px">🥗</div><b>平衡膳食</b><p class="metric-note">食物多样、规律三餐，少油少盐，优先选择蔬菜、全谷物、奶豆和优质蛋白。</p><a href="https://www.nhc.gov.cn/wjw/c100378/202412/f3f58b54fbeb4c87b14164fac898bf08/files/1736390749000_59785.pdf" target="_blank">查看国家卫健委体重管理规范化流程 ↗</a></div>', unsafe_allow_html=True)
        with g2:
            st.markdown('<div class="card"><div style="font-size:30px">🚶</div><b>动起来</b><p class="metric-note">逐步达到每周 150–300 分钟中等强度身体活动，并加入抗阻训练。</p><a href="https://www.nhc.gov.cn/wjw/c100175/202005/7757e4f72e13402a97b42f785d7a335a.shtml" target="_blank">查看国家卫健委膳食与运动建议 ↗</a></div>', unsafe_allow_html=True)
        with g3:
            st.markdown('<div class="card"><div style="font-size:30px">😴</div><b>睡眠与压力</b><p class="metric-note">保持规律作息，减少情绪化进食，用散步、冥想或瑜伽给自己一点缓冲。</p><a href="https://www.nhc.gov.cn/cms-search/downFiles/5e20de34c0fe45bb9fcac0636b21ad98.pdf" target="_blank">查看居民体重管理核心知识 ↗</a></div>', unsafe_allow_html=True)
        st.caption("口径参考：国家卫生健康委《体重管理指导原则（2024年版）》、居民体重管理核心知识（2024年版）。本工具仅供健康管理参考。")


if __name__ == "__main__":
    main()
import base64
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="轻盈 BMI · 健康管理", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

ASSET = Path(__file__).resolve().parent / "assets" / "health-pyramid.png"
ASSET_DATA = "data:image/png;base64," + base64.b64encode(ASSET.read_bytes()).decode("ascii") if ASSET.exists() else ""
PET_ASSET = Path(__file__).resolve().parent / "assets" / "health-pet.png"
PET_DATA = "data:image/png;base64," + base64.b64encode(PET_ASSET.read_bytes()).decode("ascii") if PET_ASSET.exists() else ""

st.markdown("""
<style>
:root { --ink:#183b31; --muted:#526b60; --green:#2f765f; --mint:#e6f3ec; --peach:#fff0df; --purple:#5948c7; }
* { font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",Arial,sans-serif; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }
.stMarkdown, .stText, label, button, input, textarea { line-height:1.65; }
.stApp { background-color:#f7faf4; background-image:linear-gradient(135deg,#fbfaf3e8 0%,#f0f7f0e8 53%,#fff5eae8 100%),url("__PYRAMID__"); background-size:cover; background-position:center; background-attachment:fixed; color:var(--ink); }
.main, .main .block-container { position:relative; z-index:auto; }
section[data-testid="stSidebar"] { z-index:2; }
.block-container { max-width:1180px; padding-top:3.6rem; padding-bottom:3rem; }
.brand { display:flex; align-items:center; gap:12px; margin-bottom:4px; }
.brand { min-height:52px; line-height:1.25; }
.brand-mark { width:43px; height:43px; display:grid; place-items:center; background:#d8eee2; border-radius:15px; font-size:25px; box-shadow:0 4px 15px #8ebc9b35; }
.brand h1 { font-size:25px; margin:0; letter-spacing:-1px; color:#2e584a; }
.brand small { color:#82948b; font-size:12px; }
.hero { position:relative; min-height:320px; margin:8px 0 20px; border:1px solid #e1ede4; border-radius:28px; overflow:hidden; background:#fffdf7; box-shadow:0 15px 42px #547b5b18; }
.hero-copy { position:absolute; z-index:2; left:34px; top:31px; max-width:340px; }
.hero-copy .eyebrow { color:#4d9b78; font-weight:700; font-size:13px; letter-spacing:2px; }
.hero-copy h2 { font-size:34px; line-height:1.2; margin:8px 0 10px; color:#284b40; }
.hero-copy p { color:#405f53; line-height:1.8; margin:0; }
.hero img { position:absolute; right:-2%; bottom:-5%; width:72%; min-width:520px; max-height:104%; object-fit:contain; object-position:center; opacity:.20; mix-blend-mode:multiply; }
.pill { display:inline-block; background:#f0eaff; color:#6753c8; border-radius:99px; padding:6px 12px; font-size:12px; font-weight:600; margin-top:17px; }
.card { background:#fff; border:1px solid #e5eee9; border-radius:22px; padding:22px; box-shadow:0 8px 24px #4d6e5b12; }
.section-title { font-size:22px; color:#2e5146; font-weight:800; margin:4px 0 2px; }
.section-sub { color:#526b60; font-size:13px; margin-bottom:16px; }
.gender-card { border:1.5px solid #e5eee9; border-radius:18px; padding:13px; background:#fbfdfb; text-align:center; transition:.2s; }
.gender-card:hover { transform:translateY(-2px); box-shadow:0 8px 20px #6f9e801c; }
.gender-icon { font-size:39px; display:inline-block; animation:gentle-bob 2.8s ease-in-out infinite; }
.gender-card:nth-of-type(2) .gender-icon { animation-delay:.4s; }
.gender-card:hover .gender-icon { animation:happy-hop .55s ease-in-out infinite alternate; }
.mood-switch { position:relative; width:48px; height:48px; vertical-align:middle; }
.mood-switch span { position:absolute; inset:0; opacity:0; animation:mood-flip 3.6s ease-in-out infinite; }
.mood-switch span:first-child { opacity:1; }
.mood-switch span:last-child { animation-delay:1.8s; }
.gender-name { font-weight:700; color:#254d3f; }
.gender-note { font-size:11px; color:#60786d; margin-top:3px; }
.result-box { border-radius:24px; padding:24px; color:#fff; background:linear-gradient(135deg,#376f5d,#77ad83); box-shadow:0 12px 30px #4e916e40; }
.result-box .label { opacity:.8; font-size:13px; }
.bmi-number { font-size:64px; font-weight:800; letter-spacing:-3px; line-height:1; margin:10px 0; }
.result-tag { display:inline-block; padding:6px 13px; border-radius:99px; background:#ffffff26; font-weight:700; }
.tip { background:#fffaf0; border:1px solid #f4e2bd; color:#735b33; border-radius:16px; padding:13px 15px; line-height:1.65; font-size:13px; }
.envelope { background:repeating-linear-gradient(0deg,#fff9ee,#fff9ee 8px,#ffeed3 9px,#fff9ee 10px); border:1px solid #f4d9aa; border-radius:18px; padding:16px 20px; font-weight:800; color:#8a6234; text-align:center; font-size:16px; }
.history-empty { text-align:center; color:#91a198; padding:30px 10px; }
.metric-note { font-size:12px; color:#526b60; }
.stMarkdown p, .stMarkdown li, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] { color:#38594d; }
[data-testid="stRadio"] label p { color:#234b3d !important; font-weight:600; }
[data-testid="stRadio"] label { border:1px solid #cfe2d5; border-radius:16px; padding:10px 14px; background:#fbfefb; transition:.2s; }
[data-testid="stRadio"] label:hover { border-color:#56a976; background:#eff9f0; transform:translateY(-2px); }
[data-testid="stRadio"] [aria-checked="true"] + div { color:#214e3e; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:99px; padding:8px 18px; background:#edf5ef; color:#537466; }
.stTabs [aria-selected="true"] { background:#6958d8 !important; color:#fff !important; }
.gauge-card { background:#fff; border:1px solid #e5eee9; border-radius:24px; padding:20px 18px 15px; box-shadow:0 8px 24px #4d6e5b12; text-align:center; }
.gauge-title { color:#70847a; font-size:13px; margin-bottom:2px; }
.gauge { width:280px; height:190px; position:relative; margin:0 auto; overflow:hidden; }
.gauge-arc { position:absolute; width:255px; height:255px; left:12px; top:20px; border-radius:50%; background:conic-gradient(from 225deg, #efb06d 0deg, #6fbd7c 100deg, #8ac998 150deg, #efb06d 210deg, #e88775 270deg, transparent 270deg); -webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); }
.gauge-pointer { position:absolute; width:3px; height:105px; background:#5c6b64; left:50%; top:47px; transform-origin:50% 100%; border-radius:4px; z-index:3; }
.gauge-pointer:after { content:''; position:absolute; width:12px; height:12px; background:#5c6b64; border-radius:50%; left:50%; top:-4px; transform:translateX(-50%); }
.gauge-center { position:absolute; z-index:2; left:0; right:0; top:95px; }
.gauge-number { font-size:48px; line-height:1; font-weight:800; color:#55ad6d; letter-spacing:-2px; }
.gauge-sub { margin-top:8px; color:#93a099; font-size:15px; }
.gauge-tag { display:inline-block; padding:5px 11px; border-radius:99px; background:#63bb78; color:white; font-weight:700; font-size:13px; }
.gauge-label { position:absolute; z-index:3; font-weight:600; color:#506058; font-size:14px; }
.gauge-label.l1 { left:5px; top:84px; }.gauge-label.l2 { left:132px; top:18px; }.gauge-label.l3 { right:5px; top:84px; }
.gauge-scale { display:flex; justify-content:space-around; color:#9aa8a0; font-size:11px; margin-top:-2px; }
.pet-title { display:flex; align-items:center; gap:8px; color:#2e584a; font-weight:800; font-size:18px; }
.pet-hint { color:#244f3d; background:linear-gradient(90deg,#e2f5e5,#f5fbe9); border:2px solid #9dcea4; border-radius:16px; padding:12px 16px; margin:4px 0 10px; font-size:14px; font-weight:700; box-shadow:0 5px 16px #6ba77c22; }
.streamlit-expanderHeader { color:#285541 !important; font-weight:800 !important; font-size:15px !important; }
div[data-testid="stExpander"] { border:2px solid #c9e2cb; border-radius:18px; background:#fbfffa; box-shadow:0 7px 20px #5b906820; }
.pet-avatar { width:118px; height:118px; object-fit:contain; display:block; margin:0 auto -8px; filter:drop-shadow(0 8px 7px #5a9c7030); animation:pet-float 3.2s ease-in-out infinite; }
.pet-bubble { background:#f2f8ed; border:1px solid #d9ead5; border-radius:16px 16px 16px 4px; padding:11px 12px; color:#496a5a; font-size:12px; line-height:1.75; animation:bubble-breathe 3s ease-in-out infinite; }
.food-chip { display:inline-block; background:#fff7e7; border:1px solid #f2dfb9; border-radius:99px; padding:4px 8px; margin:3px 2px; font-size:11px; }
.shutter-shell { position:relative; overflow:hidden; border-radius:18px; }
.shutter-shell:before { content:''; position:absolute; inset:0; height:20px; background:repeating-linear-gradient(0deg,#fff4d8 0 5px,#f5d49d 6px 7px); transform-origin:top; z-index:2; pointer-events:none; opacity:.9; }
.shutter-shell:hover:before { height:0; transition:height .45s ease; }
div[data-testid="stNumberInput"] input { border-radius:12px; }
div.stButton > button { border-radius:14px; border:0; background:#3b806b; color:white; font-weight:700; padding:10px 18px; }
div.stButton > button:hover { background:#2d6553; color:white; }
@keyframes gentle-bob { 0%,100%{transform:translateY(0) rotate(-2deg)} 50%{transform:translateY(-5px) rotate(2deg)} }
@keyframes happy-hop { from{transform:translateY(0) scale(1)} to{transform:translateY(-8px) scale(1.06)} }
@keyframes pet-float { 0%,100%{transform:translateY(0) rotate(-1deg)} 50%{transform:translateY(-9px) rotate(1deg)} }
@keyframes bubble-breathe { 0%,100%{box-shadow:0 0 0 #9bc88a00} 50%{box-shadow:0 0 0 5px #9bc88a18} }
@keyframes mood-flip { 0%,42%{opacity:1;transform:scale(1)} 50%,92%{opacity:0;transform:scale(.82)} 100%{opacity:1;transform:scale(1)} }
</style>
""".replace("__PYRAMID__", ASSET_DATA), unsafe_allow_html=True)


def init_state():
    if "records" not in st.session_state:
        st.session_state.records = []
    if "food_log" not in st.session_state:
        st.session_state.food_log = []
    if "exercise_minutes" not in st.session_state:
        st.session_state.exercise_minutes = 0
    if "pet_reply" not in st.session_state:
        st.session_state.pet_reply = "嗨！我是轻盈仔 🌿 你可以问我 BMI、饮食、运动和作息，我会结合你的记录一起想办法。"


def pet_reply(question, latest, food_log, exercise_minutes):
    context = f"当前 BMI：{latest['bmi']:.1f}（{latest['level']}）" if latest else "还没有 BMI 记录"
    foods = "、".join(food_log[-6:]) if food_log else "暂未投喂食物"
    if question:
        q = question.lower()
        if any(k in q for k in ["吃", "饮食", "食物", "饭"]):
            return f"根据{context}，今天你记录了：{foods}。建议把蔬菜和蛋白质放在主食前，饮料优先选白水或无糖茶；我不会要求你极端节食，先把一餐吃得更均衡就很好。"
        if any(k in q for k in ["运动", "锻炼", "走", "跑"]):
            return f"你目前累计运动 {exercise_minutes} 分钟。可以从快走 20–30 分钟开始，每周逐步靠近 150–300 分钟；如果今天很忙，分成 2–3 次完成也算数。"
        if any(k in q for k in ["风险", "疾病", "健康"]):
            return f"{context}。BMI 是筛查参考，不是诊断；如果你属于超重或肥胖，建议关注血压、血糖、血脂和肝功能，并在需要时咨询医生。"
    if not latest:
        return "先完成一次 BMI 测量，我就能把建议变得更具体；也可以先把今天吃过的食物喂给我。"
    return f"我记住啦：{context}。今天已投喂 {len(food_log)} 次食物，运动 {exercise_minutes} 分钟。你可以继续问我‘晚餐怎么吃’或‘今天适合做什么运动’。"


def food_feedback(text, latest):
    lower = text.lower()
    suggestions = {
        "蔬菜": "🥬 成年人每天建议摄入蔬菜约 300–500g，深色蔬菜最好占一半以上。",
        "水果": "🍎 水果每天建议约 200–350g，优先完整水果，不用果汁替代。",
        "奶": "🥛 奶及奶制品每天可按约 300g 液态奶或等量替代品安排。",
        "酸奶": "🥣 酸奶可以作为奶制品来源，优先无糖款，注意看配料表和添加糖。",
        "鸡蛋": "🥚 鸡蛋是优质蛋白来源，可以和蔬菜、全谷物搭配。",
        "肉": "🍗 鱼、禽、蛋、瘦肉要适量搭配，优先鱼虾、禽肉和瘦肉。",
        "米饭": "🍚 主食不必完全不吃，可用部分糙米、燕麦、玉米、红薯替换精白米面。",
        "油炸": "🍟 油炸食物偶尔少量即可，今天可以用烤、蒸、煮替代。",
        "奶茶": "🧋 奶茶通常含糖和能量较高，建议选无糖茶、白水或无糖咖啡。",
        "饮料": "🥤 含糖饮料尽量少喝，口渴优先选择白水或无糖茶。",
    }
    matched = next((value for key, value in suggestions.items() if key in lower), "🍽️ 我暂时没识别出具体食物，可以写成‘食物 + 量’，例如‘苹果 200g’。")
    if any(k in lower for k in ["苹果", "香蕉", "橙", "梨", "桃", "水果"]):
        unit_hint = "这类食物用‘几个’最方便，例如苹果 1 个、香蕉 1 根。"
    elif any(k in lower for k in ["鸡蛋", "面包", "包子", "馒头"]):
        unit_hint = "这类食物可以按‘个 / 片’填写，例如鸡蛋 2 个、面包 2 片。"
    elif any(k in lower for k in ["米饭", "面条", "粥", "粉"]):
        unit_hint = "主食可以按‘碗 / 份’填写，例如米饭 1 碗、面条 1 份。"
    elif any(k in lower for k in ["牛奶", "豆浆", "酸奶", "饮料", "水"]):
        unit_hint = "饮品可以按‘毫升 / 盒’填写，例如牛奶 250ml、酸奶 1 盒。"
    else:
        unit_hint = "蔬菜、肉类等可以按克填写，例如青菜 200g、鸡胸肉 100g。"
    amount_hint = "我已经记下这次的食物和份量。" if any(ch.isdigit() for ch in text) else f"记得补充食用量。{unit_hint}"
    context = f"结合你最近 BMI {latest['bmi']:.1f}（{latest['level']}），" if latest else "结合一般成人膳食建议，"
    return f"{context}{matched}<br>📌 {amount_hint}<br>🌱 建议把这一餐搭配蔬菜和蛋白质。"


def pet_panel():
    st.markdown('<div class="pet-hint">🌿 点击下面的绿色卡片打开「轻盈仔」：它只有一个输入框，先点三个小想法，再输入内容发送。</div>', unsafe_allow_html=True)
    with st.expander("🌿 点击这里打开轻盈仔 · 你的健康电子 Pet", expanded=True):
        st.markdown('<div class="pet-title">🌿 轻盈仔 <span style="font-size:11px;color:#58786a">你的健康电子 Pet</span></div>', unsafe_allow_html=True)
        if PET_ASSET.exists():
            st.image(str(PET_ASSET), width=150)
        st.markdown(f'<div class="pet-bubble">{st.session_state.pet_reply}</div>', unsafe_allow_html=True)
        latest = st.session_state.records[-1] if st.session_state.records else None
        st.markdown("#### 💭 轻盈仔的三个小想法")
        q1, q2, q3 = st.columns(3)
        with q1: food_mode = st.button("🍽️ 我吃了什么？", use_container_width=True)
        with q2: exercise_mode = st.button("🏃 我运动多久？", use_container_width=True)
        with q3: ask_mode = st.button("💬 我想问健康", use_container_width=True)
        if food_mode: st.session_state.pet_mode = "food"
        elif exercise_mode: st.session_state.pet_mode = "exercise"
        elif ask_mode: st.session_state.pet_mode = "ask"
        mode = st.session_state.get("pet_mode", "ask")
        labels = {"food": "输入食物 + 食用量", "exercise": "输入运动 + 时长", "ask": "输入健康问题"}
        hints = {"food": "例如：苹果 1 个、米饭 1 碗、鸡蛋 2 个、牛奶 250ml", "exercise": "例如：快走 30 分钟、跳绳 15 分钟", "ask": "例如：晚餐怎么吃？最近总熬夜怎么办？"}
        prompt = st.text_input(labels[mode], placeholder=hints[mode], key="pet_single_input")
        if st.button("发送给轻盈仔 ✨", use_container_width=True, disabled=not prompt.strip()):
            if mode == "food":
                st.session_state.food_log.append(prompt.strip())
                st.session_state.pet_reply = food_feedback(prompt.strip(), latest)
            elif mode == "exercise":
                found = re.search(r"(\d+(?:\.\d+)?)", prompt)
                added = int(float(found.group(1))) if found else 0
                st.session_state.exercise_minutes += added
                st.session_state.pet_reply = f"我记下啦：{prompt.strip()}。今天累计运动 {st.session_state.exercise_minutes} 分钟。<br>🎯 每周可以逐步靠近 150–300 分钟，忙的时候分段完成也算数。"
            else:
                st.session_state.pet_reply = pet_reply(prompt.strip(), latest, st.session_state.food_log, st.session_state.exercise_minutes)
            st.rerun()
        if st.session_state.food_log:
            st.markdown("".join(f'<span class="food-chip">🍴 {item}</span>' for item in st.session_state.food_log[-6:]), unsafe_allow_html=True)
        st.markdown("#### 📊 轻盈仔的小图表")
        if st.session_state.records:
            pet_chart = pd.DataFrame(st.session_state.records)
            pet_chart["时间"] = pd.to_datetime(pet_chart["date"])
            st.line_chart(pet_chart.set_index("时间")["bmi"], color="#55a96f", height=180)
            st.caption(f"已记录 {len(st.session_state.records)} 次 BMI · 今日运动 {st.session_state.exercise_minutes} 分钟 · 已记录 {len(st.session_state.food_log)} 次饮食")
        else:
            st.info("完成第一次 BMI 测量后，这里会出现你的趋势图；先和轻盈仔说说今天吃了什么吧。")
        st.caption("食物请写清楚数量，例如克、毫升、个或碗；轻盈仔会结合 BMI 和记录给出份量建议。")


def classify(bmi):
    if bmi < 18.5:
        return "偏瘦", "🍃", "建议适当增加营养与优质蛋白，规律吃饭，慢慢把身体养回来。", "low"
    if bmi < 24:
        return "正常", "😊", "状态很棒！继续保持吃动平衡、规律作息，让好习惯成为你的超能力。", "good"
    if bmi < 28:
        return "超重", "🙂", "别着急，先从少一杯含糖饮料、多走十分钟开始，稳定的小改变最有力量。", "watch"
    return "肥胖", "💪", "建议温和、持续地管理体重；如有基础疾病或明显不适，请咨询医生或营养师。", "high"


def advice(level, gender):
    if level == "偏瘦":
        return [
            ("🥣 饮食核心", "🍚 三餐 + 1–2 次加餐，先把规律吃饭做起来。<br>🥚 每餐加入蛋、奶、鱼、肉、豆类中的 1–2 种优质蛋白。<br>🥜 加餐可选坚果、酸奶、香蕉、全麦面包；不要只靠奶茶和甜点增重。<br>📈 每周观察一次体重，缓慢增加比突然暴食更稳妥。"),
            ("🍱 一日餐盘", "🌞 早餐：牛奶 / 豆浆 + 鸡蛋 + 全麦主食。<br>☀️ 午餐：米饭 + 鱼肉或鸡肉 + 两份蔬菜。<br>🌙 晚餐：面 / 杂粮饭 + 豆腐或瘦肉 + 菌菇蔬菜。<br>🍎 加餐：酸奶、水果、坚果三选一，感觉饱胀就减少份量。"),
            ("🏋️ 运动方案", "💪 每周 2–3 次力量训练：深蹲、臀桥、俯卧撑、弹力带划船各 2–3 组。<br>🚶 搭配轻松有氧，每次 20–30 分钟。<br>🎯 重点是保留肌肉，不用用大量跑步抵消进食。<br>🩺 体重持续下降、乏力或食欲异常时请咨询医生。"),
            ("🌙 生活节奏", "⏰ 固定起床和入睡时间，争取 7–9 小时睡眠。<br>💧 白天分次饮水，避免用咖啡或能量饮料顶替正餐。<br>🧡 每天记录一次‘吃饭 / 精力 / 心情’，找到影响食欲的原因。"),
        ]
    return [
        ("🥗 饮食核心", "🍽️ 进餐顺序：蔬菜 → 蛋白质 → 主食，先吃慢吃，七八分饱即可。<br>🥬 每餐至少一半是蔬菜，优先深色叶菜、菌菇、番茄。<br>🥚 蛋白质选鱼虾、鸡蛋、瘦肉、豆制品和奶。<br>🚫 少吃油炸、含糖饮料、甜点和酒；盐尽量控制在每日 5g 内，烹调油约 25–30g。"),
        ("🍱 一日餐盘", "🌞 早餐：无糖奶 / 豆浆 + 鸡蛋 + 全麦面包。<br>☀️ 午餐：半盘蔬菜 + 一掌心蛋白质 + 半拳到一拳主食。<br>🌙 晚餐：清淡蛋白质 + 蔬菜 + 适量杂粮主食，睡前 2–3 小时尽量不再进食。<br>🍎 想吃零食时：先喝水，优先水果、原味坚果或无糖酸奶。"),
        ("🏃 运动方案", "🚶 每周累计 150–300 分钟中等强度运动：快走、游泳、骑车都可以。<br>💪 每周 2–3 天抗阻训练：深蹲、臀桥、哑铃推举、弹力带划船。<br>⏱️ 久坐每 60 分钟起身 3–5 分钟，接水、拉伸、走动都算。<br>🌱 先从每天 20 分钟开始，稳定两周后再增加时长。"),
        ("🧘 心理与作息", "🌙 目标是 7–9 小时睡眠，尽量固定入睡和起床时间。<br>📝 想吃东西时先问自己：我是饿了、累了，还是在焦虑？<br>🌬️ 情绪上来时先做 3 分钟深呼吸、散步或伸展，再决定要不要吃。<br>👏 关注一周趋势，不因某一顿饭或某一天的体重责怪自己。"),
    ]


def risk_page(level):
    if level == "偏瘦":
        return ("🌿 体重过低的照顾提醒", "体重过低可能与营养摄入不足、肌肉量下降或潜在健康问题有关。可以关注食欲、疲劳感和近期体重变化，采用少量多餐、增加优质蛋白的方式温和调整；若体重持续下降或伴随不适，请及时咨询医生。", "需要留意：持续下降、乏力、食欲明显变化")
    if level == "正常":
        return ("🌈 继续守护你的健康", "BMI 在正常范围并不等于所有健康指标都正常。建议继续关注血压、血糖和血脂，保持规律运动与作息，让好状态稳稳延续。", "建议关注：血压、血糖、血脂")
    if level == "超重":
        return ("🔎 超重阶段的风险参照", "超重可能增加高血压、血糖异常、血脂异常、脂肪肝等代谢问题的发生风险。越早从饮食、运动和睡眠做小调整，越容易把变化控制在可管理的范围内；这不是对个人疾病的诊断。", "建议留意：血压、空腹血糖、血脂")
        return ("🧡 肥胖阶段的风险参照", "肥胖与高血压、2 型糖尿病、血脂异常、脂肪肝及心脑血管疾病等风险增加有关。建议在专业人士指导下制定循序渐进的体重管理计划；如已有慢性病或明显不适，请优先就医。", "建议留意：血压、血糖、血脂、肝功能及睡眠情况")


def gauge_html(bmi, level, emoji):
    # 成人 BMI 展示区间为 15–35；分类仍严格使用中国成人 BMI 口径。
    pct = max(0.0, min(1.0, (bmi - 15) / 20))
    angle = -135 + 270 * pct
    return f'''<div class="gauge-card">
        <div class="gauge-title">你的 BMI 身体质量指数</div>
        <div class="gauge">
          <div class="gauge-arc"></div>
          <div class="gauge-pointer" style="transform:translateX(-50%) rotate({angle:.1f}deg)"></div>
          <div class="gauge-center"><div class="gauge-number">{bmi:.1f}</div><div class="gauge-sub">BMI&nbsp; <span class="gauge-tag">{emoji} {level}</span></div></div>
          <span class="gauge-label l1">18.5</span><span class="gauge-label l2">24</span><span class="gauge-label l3">28</span>
        </div>
        <div class="gauge-scale"><span>偏瘦</span><span>正常</span><span>超重</span><span>肥胖</span></div>
    </div>'''


def main():
    init_state()
    pet_panel()
    st.markdown('<div class="brand"><div class="brand-mark">🌿</div><div><h1>轻盈 BMI</h1><small>把健康，变成每天都做得到的小事</small></div></div>', unsafe_allow_html=True)

    st.markdown(f'''<div class="hero"><div class="hero-copy"><div class="eyebrow">HEALTHY HABITS · 健康习惯</div><h2>今天的你，<br>值得被好好照顾。</h2><p>从一次 BMI 查询开始，发现身体发来的小信号，给自己一份温柔又具体的行动计划。</p><span class="pill">✨ 记录每一次轻盈变化</span></div><img src="{ASSET_DATA}" /></div>''', unsafe_allow_html=True)

    tab_check, tab_profile, tab_guide = st.tabs(["🌱 开始测量", "📈 个人中心", "📚 官方健康建议"])
    with tab_check:
        st.markdown('<div class="section-title">先认识一下今天的你</div><div class="section-sub">选择性别后，我们会给你更贴合的健康建议。成人 BMI 参考适用于 18 岁及以上人群。</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.2, 1], gap="medium")
        with c1:
            selected_gender = st.radio("你的性别（点击图标即可选择）", ["🧒🏻 男生", "👧🏻 女生"], horizontal=True, label_visibility="visible")
            gender = selected_gender.split(" ", 1)[1]
        with c2:
            age = st.number_input("年龄", min_value=1, max_value=120, value=25, step=1)

        st.markdown("#### 📏 输入身体数据")
        i1, i2 = st.columns(2)
        with i1:
            height = st.number_input("身高（米）｜例如：1.70", min_value=0.5, max_value=2.5, value=1.70, step=0.01, format="%.2f", help="请用米填写：170 厘米 = 1.70 米")
        with i2:
            weight = st.number_input("体重（千克）｜例如：60.0", min_value=10.0, max_value=300.0, value=60.0, step=0.1, format="%.1f", help="请用千克填写：60 斤约等于 30 千克")

        if st.button("✨ 查看我的 BMI", use_container_width=True):
            bmi = weight / (height ** 2)
            level, emoji, tip, tone = classify(bmi)
            previous = st.session_state.records[-1] if st.session_state.records else None
            delta = None if previous is None else bmi - previous["bmi"]
            st.session_state.current = {"bmi": bmi, "weight": weight, "level": level, "emoji": emoji, "tip": tip, "gender": gender, "age": age, "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
            st.session_state.records.append(st.session_state.current.copy())
            st.session_state.delta = delta

        if "current" in st.session_state:
            r = st.session_state.current
            delta = st.session_state.get("delta")
            left, right = st.columns([1.2, 1], gap="large")
            with left:
                st.markdown(gauge_html(r["bmi"], r["level"], r["emoji"]), unsafe_allow_html=True)
                st.markdown(f'<div class="result-box" style="margin-top:12px"><div class="label">轻盈小提醒</div><p style="margin:8px 0 0;opacity:.95;line-height:1.7">{r["tip"]}</p></div>', unsafe_allow_html=True)
                low_w, high_w = 18.5 * height ** 2, 23.9 * height ** 2
                a, b, c = st.columns(3)
                a.metric("健康体重下限", f"{low_w:.1f} kg")
                b.metric("健康体重上限", f"{high_w:.1f} kg")
                c.metric("本次体重", f"{weight:.1f} kg")
                st.caption("按中国成人 BMI 18.5–23.9 的参考区间换算；不适用于未成年人、孕期及特殊人群。")
            with right:
                st.markdown("#### 🧭 你的健康坐标")
                st.progress(min(r["bmi"] / 40, 1.0))
                st.caption("偏瘦 18.5　　正常 24　　超重 28　　肥胖")
                st.markdown('<div class="tip">BMI 是筛查参考，不是疾病诊断。建议结合血压、血糖、血脂、睡眠和日常精力综合观察。</div>', unsafe_allow_html=True)
                if delta is not None:
                    if delta < -0.1:
                        st.success(f"👍 比上一次下降 {abs(delta):.1f}，你的坚持正在发生变化！")
                    elif delta > 0.1:
                        st.info(f"🌤️ 比上一次上升 {delta:.1f}，别责怪自己，看看近期作息和饮食即可。")
                    else:
                        st.info("🌼 和上次差不多，稳定也是一种进步。")

            st.markdown("#### ✉️ 你的专属健康手册已送达")
            with st.expander("📨 点击打开专属健康手册 · 查看你的行动方案", expanded=True):
                st.markdown('<div class="envelope">💌 你的专属健康手册到了！<br><span style="font-size:12px;font-weight:500">点击上方绿色标题，逐页查看饮食、运动、作息和风险参照</span></div>', unsafe_allow_html=True)
                handbook = advice(r["level"], r["gender"])
                risk_title, risk_text, risk_watch = risk_page(r["level"])
                pages = [(title, text) for title, text in handbook] + [(risk_title, risk_text)]
                page_names = [f"第 {i + 1} 页 · {title.split(' ', 1)[-1]}" for i, (title, _) in enumerate(pages)]
                selected_page = st.radio("手册分页", page_names, horizontal=True, label_visibility="collapsed")
                page_index = page_names.index(selected_page)
                page_title, page_text = pages[page_index]
                st.markdown(f"### {page_title}")
                st.markdown(f'<div class="tip" style="font-size:15px;line-height:2">{page_text}</div>', unsafe_allow_html=True)
                if page_index == len(pages) - 1:
                    st.info(f"🩺 {risk_watch}\n\n以上是风险参照，不代表你已经患有相关疾病。")
                st.caption(f"{page_index + 1} / {len(pages)}　·　左右选择上方分页，逐页阅读你的行动建议")
                st.warning("⚠️ 以上是成人健康管理参考。孕期、未成年人、运动员或有慢性病者，请遵循专业人士建议。")

    with tab_profile:
        st.markdown('<div class="section-title">你的身体变化日记</div><div class="section-sub">每次测量都会留下一个小脚印，关注趋势，比盯着某一个数字更重要。</div>', unsafe_allow_html=True)
        records = st.session_state.records
        if not records:
            st.markdown('<div class="card history-empty">🌱 还没有测量记录<br><span class="metric-note">完成第一次测量后，这里会出现你的 BMI 趋势折线和鼓励徽章。</span></div>', unsafe_allow_html=True)
        else:
            df = pd.DataFrame(records)
            df["时间"] = pd.to_datetime(df["date"])
            f1, f2, f3, f4 = st.columns(4)
            with f1: view = st.radio("查看范围", ["最近", "今年", "近半年", "全部"], horizontal=True, label_visibility="collapsed")
            with f2: chart_metric = st.radio("指标", ["BMI", "体重"], horizontal=True, label_visibility="collapsed")
            if view == "今年": chart_df = df[df["时间"].dt.year == datetime.now().year]
            elif view == "近半年": chart_df = df[df["时间"] >= datetime.now() - timedelta(days=183)]
            elif view == "最近": chart_df = df.tail(8)
            else: chart_df = df
            if chart_df.empty: chart_df = df.tail(1)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            metric_key = {"BMI": "bmi", "体重": "weight"}[chart_metric]
            metric_data = chart_df.dropna(subset=[metric_key]).set_index("时间")[metric_key]
            st.line_chart(metric_data, color="#6958d8", height=300)
            mn, mx = chart_df[metric_key].min(), chart_df[metric_key].max()
            m1, m2, m3 = st.columns(3)
            unit = "" if chart_metric == "BMI" else " kg"
            m1.metric(f"最低 {chart_metric}", f"{mn:.1f}{unit}")
            m2.metric(f"最高 {chart_metric}", f"{mx:.1f}{unit}")
            m3.metric("测量次数", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("#### 🧡 最近记录")
            for idx, row in df.iloc[::-1].head(10).iterrows():
                prev = df.iloc[idx-1]["bmi"] if idx > 0 else None
                badge = "👍" if prev is not None and row["bmi"] < prev - .1 else ""
                st.markdown(f'<div class="card" style="padding:14px 18px;margin:8px 0"><b>{row["emoji"]} {row["level"]}</b>　BMI <b>{row["bmi"]:.1f}</b>　<span class="metric-note">{row["date"]} · {row["gender"]}</span> <span style="float:right;font-size:20px">{badge}</span></div>', unsafe_allow_html=True)
            if st.button("清空本地记录"):
                st.session_state.records = []
                st.rerun()

    with tab_guide:
        st.markdown('<div class="section-title">官方健康建议</div><div class="section-sub">把可靠的知识，变成今天就能做到的选择。</div>', unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown('<div class="card"><div style="font-size:30px">🥗</div><b>平衡膳食</b><p class="metric-note">食物多样、规律三餐，少油少盐，优先选择蔬菜、全谷物、奶豆和优质蛋白。</p><a href="https://www.nhc.gov.cn/wjw/c100378/202412/f3f58b54fbeb4c87b14164fac898bf08/files/1736390749000_59785.pdf" target="_blank">查看国家卫健委体重管理规范化流程 ↗</a></div>', unsafe_allow_html=True)
        with g2:
            st.markdown('<div class="card"><div style="font-size:30px">🚶</div><b>动起来</b><p class="metric-note">逐步达到每周 150–300 分钟中等强度身体活动，并加入抗阻训练。</p><a href="https://www.nhc.gov.cn/wjw/c100175/202005/7757e4f72e13402a97b42f785d7a335a.shtml" target="_blank">查看国家卫健委膳食与运动建议 ↗</a></div>', unsafe_allow_html=True)
        with g3:
            st.markdown('<div class="card"><div style="font-size:30px">😴</div><b>睡眠与压力</b><p class="metric-note">保持规律作息，减少情绪化进食，用散步、冥想或瑜伽给自己一点缓冲。</p><a href="https://www.nhc.gov.cn/cms-search/downFiles/5e20de34c0fe45bb9fcac0636b21ad98.pdf" target="_blank">查看居民体重管理核心知识 ↗</a></div>', unsafe_allow_html=True)
        st.caption("口径参考：国家卫生健康委《体重管理指导原则（2024年版）》、居民体重管理核心知识（2024年版）。本工具仅供健康管理参考。")


if __name__ == "__main__":
    main()
import base64
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="轻盈 BMI · 健康管理", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

ASSET = Path(__file__).resolve().parent / "assets" / "health-pyramid.png"
ASSET_DATA = "data:image/png;base64," + base64.b64encode(ASSET.read_bytes()).decode("ascii") if ASSET.exists() else ""
PET_ASSET = Path(__file__).resolve().parent / "assets" / "health-pet.png"
PET_DATA = "data:image/png;base64," + base64.b64encode(PET_ASSET.read_bytes()).decode("ascii") if PET_ASSET.exists() else ""

st.markdown("""
<style>
:root { --ink:#183b31; --muted:#526b60; --green:#2f765f; --mint:#e6f3ec; --peach:#fff0df; --purple:#5948c7; }
* { font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",Arial,sans-serif; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }
.stMarkdown, .stText, label, button, input, textarea { line-height:1.65; }
.stApp { background-color:#f7faf4; background-image:linear-gradient(135deg,#fbfaf3e8 0%,#f0f7f0e8 53%,#fff5eae8 100%),url("__PYRAMID__"); background-size:cover; background-position:center; background-attachment:fixed; color:var(--ink); }
.main, .main .block-container { position:relative; z-index:auto; }
section[data-testid="stSidebar"] { z-index:2; }
.block-container { max-width:1180px; padding-top:3.6rem; padding-bottom:3rem; }
.brand { display:flex; align-items:center; gap:12px; margin-bottom:4px; }
.brand { min-height:52px; line-height:1.25; }
.brand-mark { width:43px; height:43px; display:grid; place-items:center; background:#d8eee2; border-radius:15px; font-size:25px; box-shadow:0 4px 15px #8ebc9b35; }
.brand h1 { font-size:25px; margin:0; letter-spacing:-1px; color:#2e584a; }
.brand small { color:#82948b; font-size:12px; }
.hero { position:relative; min-height:320px; margin:8px 0 20px; border:1px solid #e1ede4; border-radius:28px; overflow:hidden; background:#fffdf7; box-shadow:0 15px 42px #547b5b18; }
.hero-copy { position:absolute; z-index:2; left:34px; top:31px; max-width:340px; }
.hero-copy .eyebrow { color:#4d9b78; font-weight:700; font-size:13px; letter-spacing:2px; }
.hero-copy h2 { font-size:34px; line-height:1.2; margin:8px 0 10px; color:#284b40; }
.hero-copy p { color:#405f53; line-height:1.8; margin:0; }
.hero img { position:absolute; right:-2%; bottom:-5%; width:72%; min-width:520px; max-height:104%; object-fit:contain; object-position:center; opacity:.20; mix-blend-mode:multiply; }
.pill { display:inline-block; background:#f0eaff; color:#6753c8; border-radius:99px; padding:6px 12px; font-size:12px; font-weight:600; margin-top:17px; }
.card { background:#fff; border:1px solid #e5eee9; border-radius:22px; padding:22px; box-shadow:0 8px 24px #4d6e5b12; }
.section-title { font-size:22px; color:#2e5146; font-weight:800; margin:4px 0 2px; }
.section-sub { color:#526b60; font-size:13px; margin-bottom:16px; }
.gender-card { border:1.5px solid #e5eee9; border-radius:18px; padding:13px; background:#fbfdfb; text-align:center; transition:.2s; }
.gender-card:hover { transform:translateY(-2px); box-shadow:0 8px 20px #6f9e801c; }
.gender-icon { font-size:39px; display:inline-block; animation:gentle-bob 2.8s ease-in-out infinite; }
.gender-card:nth-of-type(2) .gender-icon { animation-delay:.4s; }
.gender-card:hover .gender-icon { animation:happy-hop .55s ease-in-out infinite alternate; }
.mood-switch { position:relative; width:48px; height:48px; vertical-align:middle; }
.mood-switch span { position:absolute; inset:0; opacity:0; animation:mood-flip 3.6s ease-in-out infinite; }
.mood-switch span:first-child { opacity:1; }
.mood-switch span:last-child { animation-delay:1.8s; }
.gender-name { font-weight:700; color:#254d3f; }
.gender-note { font-size:11px; color:#60786d; margin-top:3px; }
.result-box { border-radius:24px; padding:24px; color:#fff; background:linear-gradient(135deg,#376f5d,#77ad83); box-shadow:0 12px 30px #4e916e40; }
.result-box .label { opacity:.8; font-size:13px; }
.bmi-number { font-size:64px; font-weight:800; letter-spacing:-3px; line-height:1; margin:10px 0; }
.result-tag { display:inline-block; padding:6px 13px; border-radius:99px; background:#ffffff26; font-weight:700; }
.tip { background:#fffaf0; border:1px solid #f4e2bd; color:#735b33; border-radius:16px; padding:13px 15px; line-height:1.65; font-size:13px; }
.envelope { background:repeating-linear-gradient(0deg,#fff9ee,#fff9ee 8px,#ffeed3 9px,#fff9ee 10px); border:1px solid #f4d9aa; border-radius:18px; padding:16px 20px; font-weight:800; color:#8a6234; text-align:center; font-size:16px; }
.history-empty { text-align:center; color:#91a198; padding:30px 10px; }
.metric-note { font-size:12px; color:#526b60; }
.stMarkdown p, .stMarkdown li, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] { color:#38594d; }
[data-testid="stRadio"] label p { color:#234b3d !important; font-weight:600; }
[data-testid="stRadio"] label { border:1px solid #cfe2d5; border-radius:16px; padding:10px 14px; background:#fbfefb; transition:.2s; }
[data-testid="stRadio"] label:hover { border-color:#56a976; background:#eff9f0; transform:translateY(-2px); }
[data-testid="stRadio"] [aria-checked="true"] + div { color:#214e3e; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:99px; padding:8px 18px; background:#edf5ef; color:#537466; }
.stTabs [aria-selected="true"] { background:#6958d8 !important; color:#fff !important; }
.gauge-card { background:#fff; border:1px solid #e5eee9; border-radius:24px; padding:20px 18px 15px; box-shadow:0 8px 24px #4d6e5b12; text-align:center; }
.gauge-title { color:#70847a; font-size:13px; margin-bottom:2px; }
.gauge { width:280px; height:190px; position:relative; margin:0 auto; overflow:hidden; }
.gauge-arc { position:absolute; width:255px; height:255px; left:12px; top:20px; border-radius:50%; background:conic-gradient(from 225deg, #efb06d 0deg, #6fbd7c 100deg, #8ac998 150deg, #efb06d 210deg, #e88775 270deg, transparent 270deg); -webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); }
.gauge-pointer { position:absolute; width:3px; height:105px; background:#5c6b64; left:50%; top:47px; transform-origin:50% 100%; border-radius:4px; z-index:3; }
.gauge-pointer:after { content:''; position:absolute; width:12px; height:12px; background:#5c6b64; border-radius:50%; left:50%; top:-4px; transform:translateX(-50%); }
.gauge-center { position:absolute; z-index:2; left:0; right:0; top:95px; }
.gauge-number { font-size:48px; line-height:1; font-weight:800; color:#55ad6d; letter-spacing:-2px; }
.gauge-sub { margin-top:8px; color:#93a099; font-size:15px; }
.gauge-tag { display:inline-block; padding:5px 11px; border-radius:99px; background:#63bb78; color:white; font-weight:700; font-size:13px; }
.gauge-label { position:absolute; z-index:3; font-weight:600; color:#506058; font-size:14px; }
.gauge-label.l1 { left:5px; top:84px; }.gauge-label.l2 { left:132px; top:18px; }.gauge-label.l3 { right:5px; top:84px; }
.gauge-scale { display:flex; justify-content:space-around; color:#9aa8a0; font-size:11px; margin-top:-2px; }
.pet-title { display:flex; align-items:center; gap:8px; color:#2e584a; font-weight:800; font-size:18px; }
.pet-hint { color:#244f3d; background:linear-gradient(90deg,#e2f5e5,#f5fbe9); border:2px solid #9dcea4; border-radius:16px; padding:12px 16px; margin:4px 0 10px; font-size:14px; font-weight:700; box-shadow:0 5px 16px #6ba77c22; }
.streamlit-expanderHeader { color:#285541 !important; font-weight:800 !important; font-size:15px !important; }
div[data-testid="stExpander"] { border:2px solid #c9e2cb; border-radius:18px; background:#fbfffa; box-shadow:0 7px 20px #5b906820; }
.pet-avatar { width:118px; height:118px; object-fit:contain; display:block; margin:0 auto -8px; filter:drop-shadow(0 8px 7px #5a9c7030); animation:pet-float 3.2s ease-in-out infinite; }
.pet-bubble { background:#f2f8ed; border:1px solid #d9ead5; border-radius:16px 16px 16px 4px; padding:11px 12px; color:#496a5a; font-size:12px; line-height:1.75; animation:bubble-breathe 3s ease-in-out infinite; }
.food-chip { display:inline-block; background:#fff7e7; border:1px solid #f2dfb9; border-radius:99px; padding:4px 8px; margin:3px 2px; font-size:11px; }
.shutter-shell { position:relative; overflow:hidden; border-radius:18px; }
.shutter-shell:before { content:''; position:absolute; inset:0; height:20px; background:repeating-linear-gradient(0deg,#fff4d8 0 5px,#f5d49d 6px 7px); transform-origin:top; z-index:2; pointer-events:none; opacity:.9; }
.shutter-shell:hover:before { height:0; transition:height .45s ease; }
div[data-testid="stNumberInput"] input { border-radius:12px; }
div.stButton > button { border-radius:14px; border:0; background:#3b806b; color:white; font-weight:700; padding:10px 18px; }
div.stButton > button:hover { background:#2d6553; color:white; }
@keyframes gentle-bob { 0%,100%{transform:translateY(0) rotate(-2deg)} 50%{transform:translateY(-5px) rotate(2deg)} }
@keyframes happy-hop { from{transform:translateY(0) scale(1)} to{transform:translateY(-8px) scale(1.06)} }
@keyframes pet-float { 0%,100%{transform:translateY(0) rotate(-1deg)} 50%{transform:translateY(-9px) rotate(1deg)} }
@keyframes bubble-breathe { 0%,100%{box-shadow:0 0 0 #9bc88a00} 50%{box-shadow:0 0 0 5px #9bc88a18} }
@keyframes mood-flip { 0%,42%{opacity:1;transform:scale(1)} 50%,92%{opacity:0;transform:scale(.82)} 100%{opacity:1;transform:scale(1)} }
</style>
""".replace("__PYRAMID__", ASSET_DATA), unsafe_allow_html=True)


def init_state():
    if "records" not in st.session_state:
        st.session_state.records = []
    if "food_log" not in st.session_state:
        st.session_state.food_log = []
    if "exercise_minutes" not in st.session_state:
        st.session_state.exercise_minutes = 0
    if "pet_reply" not in st.session_state:
        st.session_state.pet_reply = "嗨！我是轻盈仔 🌿 你可以问我 BMI、饮食、运动和作息，我会结合你的记录一起想办法。"


def pet_reply(question, latest, food_log, exercise_minutes):
    context = f"当前 BMI：{latest['bmi']:.1f}（{latest['level']}）" if latest else "还没有 BMI 记录"
    foods = "、".join(food_log[-6:]) if food_log else "暂未投喂食物"
    if question:
        q = question.lower()
        if any(k in q for k in ["吃", "饮食", "食物", "饭"]):
            return f"根据{context}，今天你记录了：{foods}。建议把蔬菜和蛋白质放在主食前，饮料优先选白水或无糖茶；我不会要求你极端节食，先把一餐吃得更均衡就很好。"
        if any(k in q for k in ["运动", "锻炼", "走", "跑"]):
            return f"你目前累计运动 {exercise_minutes} 分钟。可以从快走 20–30 分钟开始，每周逐步靠近 150–300 分钟；如果今天很忙，分成 2–3 次完成也算数。"
        if any(k in q for k in ["风险", "疾病", "健康"]):
            return f"{context}。BMI 是筛查参考，不是诊断；如果你属于超重或肥胖，建议关注血压、血糖、血脂和肝功能，并在需要时咨询医生。"
    if not latest:
        return "先完成一次 BMI 测量，我就能把建议变得更具体；也可以先把今天吃过的食物喂给我。"
    return f"我记住啦：{context}。今天已投喂 {len(food_log)} 次食物，运动 {exercise_minutes} 分钟。你可以继续问我‘晚餐怎么吃’或‘今天适合做什么运动’。"


def food_feedback(text, latest):
    lower = text.lower()
    suggestions = {
        "蔬菜": "🥬 成年人每天建议摄入蔬菜约 300–500g，深色蔬菜最好占一半以上。",
        "水果": "🍎 水果每天建议约 200–350g，优先完整水果，不用果汁替代。",
        "奶": "🥛 奶及奶制品每天可按约 300g 液态奶或等量替代品安排。",
        "酸奶": "🥣 酸奶可以作为奶制品来源，优先无糖款，注意看配料表和添加糖。",
        "鸡蛋": "🥚 鸡蛋是优质蛋白来源，可以和蔬菜、全谷物搭配。",
        "肉": "🍗 鱼、禽、蛋、瘦肉要适量搭配，优先鱼虾、禽肉和瘦肉。",
        "米饭": "🍚 主食不必完全不吃，可用部分糙米、燕麦、玉米、红薯替换精白米面。",
        "油炸": "🍟 油炸食物偶尔少量即可，今天可以用烤、蒸、煮替代。",
        "奶茶": "🧋 奶茶通常含糖和能量较高，建议选无糖茶、白水或无糖咖啡。",
        "饮料": "🥤 含糖饮料尽量少喝，口渴优先选择白水或无糖茶。",
    }
    matched = next((value for key, value in suggestions.items() if key in lower), "🍽️ 我暂时没识别出具体食物，可以写成‘食物 + 量’，例如‘苹果 200g’。")
    if any(k in lower for k in ["苹果", "香蕉", "橙", "梨", "桃", "水果"]):
        unit_hint = "这类食物用‘几个’最方便，例如苹果 1 个、香蕉 1 根。"
    elif any(k in lower for k in ["鸡蛋", "面包", "包子", "馒头"]):
        unit_hint = "这类食物可以按‘个 / 片’填写，例如鸡蛋 2 个、面包 2 片。"
    elif any(k in lower for k in ["米饭", "面条", "粥", "粉"]):
        unit_hint = "主食可以按‘碗 / 份’填写，例如米饭 1 碗、面条 1 份。"
    elif any(k in lower for k in ["牛奶", "豆浆", "酸奶", "饮料", "水"]):
        unit_hint = "饮品可以按‘毫升 / 盒’填写，例如牛奶 250ml、酸奶 1 盒。"
    else:
        unit_hint = "蔬菜、肉类等可以按克填写，例如青菜 200g、鸡胸肉 100g。"
    amount_hint = "我已经记下这次的食物和份量。" if any(ch.isdigit() for ch in text) else f"记得补充食用量。{unit_hint}"
    context = f"结合你最近 BMI {latest['bmi']:.1f}（{latest['level']}），" if latest else "结合一般成人膳食建议，"
    return f"{context}{matched}<br>📌 {amount_hint}<br>🌱 建议把这一餐搭配蔬菜和蛋白质。"


def pet_panel():
    st.markdown('<div class="pet-hint">🌿 点击下面的绿色卡片打开「轻盈仔」：它只有一个输入框，先点三个小想法，再输入内容发送。</div>', unsafe_allow_html=True)
    with st.expander("🌿 点击这里打开轻盈仔 · 你的健康电子 Pet", expanded=True):
        st.markdown('<div class="pet-title">🌿 轻盈仔 <span style="font-size:11px;color:#58786a">你的健康电子 Pet</span></div>', unsafe_allow_html=True)
        if PET_ASSET.exists():
            st.image(str(PET_ASSET), width=150)
        st.markdown(f'<div class="pet-bubble">{st.session_state.pet_reply}</div>', unsafe_allow_html=True)
        latest = st.session_state.records[-1] if st.session_state.records else None
        st.markdown("#### 💭 轻盈仔的三个小想法")
        q1, q2, q3 = st.columns(3)
        with q1: food_mode = st.button("🍽️ 我吃了什么？", use_container_width=True)
        with q2: exercise_mode = st.button("🏃 我运动多久？", use_container_width=True)
        with q3: ask_mode = st.button("💬 我想问健康", use_container_width=True)
        if food_mode: st.session_state.pet_mode = "food"
        elif exercise_mode: st.session_state.pet_mode = "exercise"
        elif ask_mode: st.session_state.pet_mode = "ask"
        mode = st.session_state.get("pet_mode", "ask")
        labels = {"food": "输入食物 + 食用量", "exercise": "输入运动 + 时长", "ask": "输入健康问题"}
        hints = {"food": "例如：苹果 1 个、米饭 1 碗、鸡蛋 2 个、牛奶 250ml", "exercise": "例如：快走 30 分钟、跳绳 15 分钟", "ask": "例如：晚餐怎么吃？最近总熬夜怎么办？"}
        prompt = st.text_input(labels[mode], placeholder=hints[mode], key="pet_single_input")
        if st.button("发送给轻盈仔 ✨", use_container_width=True, disabled=not prompt.strip()):
            if mode == "food":
                st.session_state.food_log.append(prompt.strip())
                st.session_state.pet_reply = food_feedback(prompt.strip(), latest)
            elif mode == "exercise":
                found = re.search(r"(\d+(?:\.\d+)?)", prompt)
                added = int(float(found.group(1))) if found else 0
                st.session_state.exercise_minutes += added
                st.session_state.pet_reply = f"我记下啦：{prompt.strip()}。今天累计运动 {st.session_state.exercise_minutes} 分钟。<br>🎯 每周可以逐步靠近 150–300 分钟，忙的时候分段完成也算数。"
            else:
                st.session_state.pet_reply = pet_reply(prompt.strip(), latest, st.session_state.food_log, st.session_state.exercise_minutes)
            st.rerun()
        if st.session_state.food_log:
            st.markdown("".join(f'<span class="food-chip">🍴 {item}</span>' for item in st.session_state.food_log[-6:]), unsafe_allow_html=True)
        st.markdown("#### 📊 轻盈仔的小图表")
        if st.session_state.records:
            pet_chart = pd.DataFrame(st.session_state.records)
            pet_chart["时间"] = pd.to_datetime(pet_chart["date"])
            st.line_chart(pet_chart.set_index("时间")["bmi"], color="#55a96f", height=180)
            st.caption(f"已记录 {len(st.session_state.records)} 次 BMI · 今日运动 {st.session_state.exercise_minutes} 分钟 · 已记录 {len(st.session_state.food_log)} 次饮食")
        else:
            st.info("完成第一次 BMI 测量后，这里会出现你的趋势图；先和轻盈仔说说今天吃了什么吧。")
        st.caption("食物请写清楚数量，例如克、毫升、个或碗；轻盈仔会结合 BMI 和记录给出份量建议。")


def classify(bmi):
    if bmi < 18.5:
        return "偏瘦", "🍃", "建议适当增加营养与优质蛋白，规律吃饭，慢慢把身体养回来。", "low"
    if bmi < 24:
        return "正常", "😊", "状态很棒！继续保持吃动平衡、规律作息，让好习惯成为你的超能力。", "good"
    if bmi < 28:
        return "超重", "🙂", "别着急，先从少一杯含糖饮料、多走十分钟开始，稳定的小改变最有力量。", "watch"
    return "肥胖", "💪", "建议温和、持续地管理体重；如有基础疾病或明显不适，请咨询医生或营养师。", "high"


def advice(level, gender):
    if level == "偏瘦":
        return [
            ("🥣 饮食核心", "🍚 三餐 + 1–2 次加餐，先把规律吃饭做起来。<br>🥚 每餐加入蛋、奶、鱼、肉、豆类中的 1–2 种优质蛋白。<br>🥜 加餐可选坚果、酸奶、香蕉、全麦面包；不要只靠奶茶和甜点增重。<br>📈 每周观察一次体重，缓慢增加比突然暴食更稳妥。"),
            ("🍱 一日餐盘", "🌞 早餐：牛奶 / 豆浆 + 鸡蛋 + 全麦主食。<br>☀️ 午餐：米饭 + 鱼肉或鸡肉 + 两份蔬菜。<br>🌙 晚餐：面 / 杂粮饭 + 豆腐或瘦肉 + 菌菇蔬菜。<br>🍎 加餐：酸奶、水果、坚果三选一，感觉饱胀就减少份量。"),
            ("🏋️ 运动方案", "💪 每周 2–3 次力量训练：深蹲、臀桥、俯卧撑、弹力带划船各 2–3 组。<br>🚶 搭配轻松有氧，每次 20–30 分钟。<br>🎯 重点是保留肌肉，不用用大量跑步抵消进食。<br>🩺 体重持续下降、乏力或食欲异常时请咨询医生。"),
            ("🌙 生活节奏", "⏰ 固定起床和入睡时间，争取 7–9 小时睡眠。<br>💧 白天分次饮水，避免用咖啡或能量饮料顶替正餐。<br>🧡 每天记录一次‘吃饭 / 精力 / 心情’，找到影响食欲的原因。"),
        ]
    return [
        ("🥗 饮食核心", "🍽️ 进餐顺序：蔬菜 → 蛋白质 → 主食，先吃慢吃，七八分饱即可。<br>🥬 每餐至少一半是蔬菜，优先深色叶菜、菌菇、番茄。<br>🥚 蛋白质选鱼虾、鸡蛋、瘦肉、豆制品和奶。<br>🚫 少吃油炸、含糖饮料、甜点和酒；盐尽量控制在每日 5g 内，烹调油约 25–30g。"),
        ("🍱 一日餐盘", "🌞 早餐：无糖奶 / 豆浆 + 鸡蛋 + 全麦面包。<br>☀️ 午餐：半盘蔬菜 + 一掌心蛋白质 + 半拳到一拳主食。<br>🌙 晚餐：清淡蛋白质 + 蔬菜 + 适量杂粮主食，睡前 2–3 小时尽量不再进食。<br>🍎 想吃零食时：先喝水，优先水果、原味坚果或无糖酸奶。"),
        ("🏃 运动方案", "🚶 每周累计 150–300 分钟中等强度运动：快走、游泳、骑车都可以。<br>💪 每周 2–3 天抗阻训练：深蹲、臀桥、哑铃推举、弹力带划船。<br>⏱️ 久坐每 60 分钟起身 3–5 分钟，接水、拉伸、走动都算。<br>🌱 先从每天 20 分钟开始，稳定两周后再增加时长。"),
        ("🧘 心理与作息", "🌙 目标是 7–9 小时睡眠，尽量固定入睡和起床时间。<br>📝 想吃东西时先问自己：我是饿了、累了，还是在焦虑？<br>🌬️ 情绪上来时先做 3 分钟深呼吸、散步或伸展，再决定要不要吃。<br>👏 关注一周趋势，不因某一顿饭或某一天的体重责怪自己。"),
    ]


def risk_page(level):
    if level == "偏瘦":
        return ("🌿 体重过低的照顾提醒", "体重过低可能与营养摄入不足、肌肉量下降或潜在健康问题有关。可以关注食欲、疲劳感和近期体重变化，采用少量多餐、增加优质蛋白的方式温和调整；若体重持续下降或伴随不适，请及时咨询医生。", "需要留意：持续下降、乏力、食欲明显变化")
    if level == "正常":
        return ("🌈 继续守护你的健康", "BMI 在正常范围并不等于所有健康指标都正常。建议继续关注血压、血糖和血脂，保持规律运动与作息，让好状态稳稳延续。", "建议关注：血压、血糖、血脂")
    if level == "超重":
        return ("🔎 超重阶段的风险参照", "超重可能增加高血压、血糖异常、血脂异常、脂肪肝等代谢问题的发生风险。越早从饮食、运动和睡眠做小调整，越容易把变化控制在可管理的范围内；这不是对个人疾病的诊断。", "建议留意：血压、空腹血糖、血脂")
        return ("🧡 肥胖阶段的风险参照", "肥胖与高血压、2 型糖尿病、血脂异常、脂肪肝及心脑血管疾病等风险增加有关。建议在专业人士指导下制定循序渐进的体重管理计划；如已有慢性病或明显不适，请优先就医。", "建议留意：血压、血糖、血脂、肝功能及睡眠情况")


def gauge_html(bmi, level, emoji):
    # 成人 BMI 展示区间为 15–35；分类仍严格使用中国成人 BMI 口径。
    pct = max(0.0, min(1.0, (bmi - 15) / 20))
    angle = -135 + 270 * pct
    return f'''<div class="gauge-card">
        <div class="gauge-title">你的 BMI 身体质量指数</div>
        <div class="gauge">
          <div class="gauge-arc"></div>
          <div class="gauge-pointer" style="transform:translateX(-50%) rotate({angle:.1f}deg)"></div>
          <div class="gauge-center"><div class="gauge-number">{bmi:.1f}</div><div class="gauge-sub">BMI&nbsp; <span class="gauge-tag">{emoji} {level}</span></div></div>
          <span class="gauge-label l1">18.5</span><span class="gauge-label l2">24</span><span class="gauge-label l3">28</span>
        </div>
        <div class="gauge-scale"><span>偏瘦</span><span>正常</span><span>超重</span><span>肥胖</span></div>
    </div>'''


def main():
    init_state()
    pet_panel()
    st.markdown('<div class="brand"><div class="brand-mark">🌿</div><div><h1>轻盈 BMI</h1><small>把健康，变成每天都做得到的小事</small></div></div>', unsafe_allow_html=True)

    st.markdown(f'''<div class="hero"><div class="hero-copy"><div class="eyebrow">HEALTHY HABITS · 健康习惯</div><h2>今天的你，<br>值得被好好照顾。</h2><p>从一次 BMI 查询开始，发现身体发来的小信号，给自己一份温柔又具体的行动计划。</p><span class="pill">✨ 记录每一次轻盈变化</span></div><img src="{ASSET_DATA}" /></div>''', unsafe_allow_html=True)

    tab_check, tab_profile, tab_guide = st.tabs(["🌱 开始测量", "📈 个人中心", "📚 官方健康建议"])
    with tab_check:
        st.markdown('<div class="section-title">先认识一下今天的你</div><div class="section-sub">选择性别后，我们会给你更贴合的健康建议。成人 BMI 参考适用于 18 岁及以上人群。</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.2, 1], gap="medium")
        with c1:
            selected_gender = st.radio("你的性别（点击图标即可选择）", ["🧒🏻 男生", "👧🏻 女生"], horizontal=True, label_visibility="visible")
            gender = selected_gender.split(" ", 1)[1]
        with c2:
            age = st.number_input("年龄", min_value=1, max_value=120, value=25, step=1)

        st.markdown("#### 📏 输入身体数据")
        i1, i2 = st.columns(2)
        with i1:
            height = st.number_input("身高（米）｜例如：1.70", min_value=0.5, max_value=2.5, value=1.70, step=0.01, format="%.2f", help="请用米填写：170 厘米 = 1.70 米")
        with i2:
            weight = st.number_input("体重（千克）｜例如：60.0", min_value=10.0, max_value=300.0, value=60.0, step=0.1, format="%.1f", help="请用千克填写：60 斤约等于 30 千克")

        if st.button("✨ 查看我的 BMI", use_container_width=True):
            bmi = weight / (height ** 2)
            level, emoji, tip, tone = classify(bmi)
            previous = st.session_state.records[-1] if st.session_state.records else None
            delta = None if previous is None else bmi - previous["bmi"]
            st.session_state.current = {"bmi": bmi, "weight": weight, "level": level, "emoji": emoji, "tip": tip, "gender": gender, "age": age, "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
            st.session_state.records.append(st.session_state.current.copy())
            st.session_state.delta = delta

        if "current" in st.session_state:
            r = st.session_state.current
            delta = st.session_state.get("delta")
            left, right = st.columns([1.2, 1], gap="large")
            with left:
                st.markdown(gauge_html(r["bmi"], r["level"], r["emoji"]), unsafe_allow_html=True)
                st.markdown(f'<div class="result-box" style="margin-top:12px"><div class="label">轻盈小提醒</div><p style="margin:8px 0 0;opacity:.95;line-height:1.7">{r["tip"]}</p></div>', unsafe_allow_html=True)
                low_w, high_w = 18.5 * height ** 2, 23.9 * height ** 2
                a, b, c = st.columns(3)
                a.metric("健康体重下限", f"{low_w:.1f} kg")
                b.metric("健康体重上限", f"{high_w:.1f} kg")
                c.metric("本次体重", f"{weight:.1f} kg")
                st.caption("按中国成人 BMI 18.5–23.9 的参考区间换算；不适用于未成年人、孕期及特殊人群。")
            with right:
                st.markdown("#### 🧭 你的健康坐标")
                st.progress(min(r["bmi"] / 40, 1.0))
                st.caption("偏瘦 18.5　　正常 24　　超重 28　　肥胖")
                st.markdown('<div class="tip">BMI 是筛查参考，不是疾病诊断。建议结合血压、血糖、血脂、睡眠和日常精力综合观察。</div>', unsafe_allow_html=True)
                if delta is not None:
                    if delta < -0.1:
                        st.success(f"👍 比上一次下降 {abs(delta):.1f}，你的坚持正在发生变化！")
                    elif delta > 0.1:
                        st.info(f"🌤️ 比上一次上升 {delta:.1f}，别责怪自己，看看近期作息和饮食即可。")
                    else:
                        st.info("🌼 和上次差不多，稳定也是一种进步。")

            st.markdown("#### ✉️ 你的专属健康手册已送达")
            with st.expander("📨 点击打开专属健康手册 · 查看你的行动方案", expanded=True):
                st.markdown('<div class="envelope">💌 你的专属健康手册到了！<br><span style="font-size:12px;font-weight:500">点击上方绿色标题，逐页查看饮食、运动、作息和风险参照</span></div>', unsafe_allow_html=True)
                handbook = advice(r["level"], r["gender"])
                risk_title, risk_text, risk_watch = risk_page(r["level"])
                pages = [(title, text) for title, text in handbook] + [(risk_title, risk_text)]
                page_names = [f"第 {i + 1} 页 · {title.split(' ', 1)[-1]}" for i, (title, _) in enumerate(pages)]
                selected_page = st.radio("手册分页", page_names, horizontal=True, label_visibility="collapsed")
                page_index = page_names.index(selected_page)
                page_title, page_text = pages[page_index]
                st.markdown(f"### {page_title}")
                st.markdown(f'<div class="tip" style="font-size:15px;line-height:2">{page_text}</div>', unsafe_allow_html=True)
                if page_index == len(pages) - 1:
                    st.info(f"🩺 {risk_watch}\n\n以上是风险参照，不代表你已经患有相关疾病。")
                st.caption(f"{page_index + 1} / {len(pages)}　·　左右选择上方分页，逐页阅读你的行动建议")
                st.warning("⚠️ 以上是成人健康管理参考。孕期、未成年人、运动员或有慢性病者，请遵循专业人士建议。")

    with tab_profile:
        st.markdown('<div class="section-title">你的身体变化日记</div><div class="section-sub">每次测量都会留下一个小脚印，关注趋势，比盯着某一个数字更重要。</div>', unsafe_allow_html=True)
        records = st.session_state.records
        if not records:
            st.markdown('<div class="card history-empty">🌱 还没有测量记录<br><span class="metric-note">完成第一次测量后，这里会出现你的 BMI 趋势折线和鼓励徽章。</span></div>', unsafe_allow_html=True)
        else:
            df = pd.DataFrame(records)
            df["时间"] = pd.to_datetime(df["date"])
            f1, f2, f3, f4 = st.columns(4)
            with f1: view = st.radio("查看范围", ["最近", "今年", "近半年", "全部"], horizontal=True, label_visibility="collapsed")
            with f2: chart_metric = st.radio("指标", ["BMI", "体重"], horizontal=True, label_visibility="collapsed")
            if view == "今年": chart_df = df[df["时间"].dt.year == datetime.now().year]
            elif view == "近半年": chart_df = df[df["时间"] >= datetime.now() - timedelta(days=183)]
            elif view == "最近": chart_df = df.tail(8)
            else: chart_df = df
            if chart_df.empty: chart_df = df.tail(1)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            metric_key = {"BMI": "bmi", "体重": "weight"}[chart_metric]
            metric_data = chart_df.dropna(subset=[metric_key]).set_index("时间")[metric_key]
            st.line_chart(metric_data, color="#6958d8", height=300)
            mn, mx = chart_df[metric_key].min(), chart_df[metric_key].max()
            m1, m2, m3 = st.columns(3)
            unit = "" if chart_metric == "BMI" else " kg"
            m1.metric(f"最低 {chart_metric}", f"{mn:.1f}{unit}")
            m2.metric(f"最高 {chart_metric}", f"{mx:.1f}{unit}")
            m3.metric("测量次数", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("#### 🧡 最近记录")
            for idx, row in df.iloc[::-1].head(10).iterrows():
                prev = df.iloc[idx-1]["bmi"] if idx > 0 else None
                badge = "👍" if prev is not None and row["bmi"] < prev - .1 else ""
                st.markdown(f'<div class="card" style="padding:14px 18px;margin:8px 0"><b>{row["emoji"]} {row["level"]}</b>　BMI <b>{row["bmi"]:.1f}</b>　<span class="metric-note">{row["date"]} · {row["gender"]}</span> <span style="float:right;font-size:20px">{badge}</span></div>', unsafe_allow_html=True)
            if st.button("清空本地记录"):
                st.session_state.records = []
                st.rerun()

    with tab_guide:
        st.markdown('<div class="section-title">官方健康建议</div><div class="section-sub">把可靠的知识，变成今天就能做到的选择。</div>', unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown('<div class="card"><div style="font-size:30px">🥗</div><b>平衡膳食</b><p class="metric-note">食物多样、规律三餐，少油少盐，优先选择蔬菜、全谷物、奶豆和优质蛋白。</p><a href="https://www.nhc.gov.cn/wjw/c100378/202412/f3f58b54fbeb4c87b14164fac898bf08/files/1736390749000_59785.pdf" target="_blank">查看国家卫健委体重管理规范化流程 ↗</a></div>', unsafe_allow_html=True)
        with g2:
            st.markdown('<div class="card"><div style="font-size:30px">🚶</div><b>动起来</b><p class="metric-note">逐步达到每周 150–300 分钟中等强度身体活动，并加入抗阻训练。</p><a href="https://www.nhc.gov.cn/wjw/c100175/202005/7757e4f72e13402a97b42f785d7a335a.shtml" target="_blank">查看国家卫健委膳食与运动建议 ↗</a></div>', unsafe_allow_html=True)
        with g3:
            st.markdown('<div class="card"><div style="font-size:30px">😴</div><b>睡眠与压力</b><p class="metric-note">保持规律作息，减少情绪化进食，用散步、冥想或瑜伽给自己一点缓冲。</p><a href="https://www.nhc.gov.cn/cms-search/downFiles/5e20de34c0fe45bb9fcac0636b21ad98.pdf" target="_blank">查看居民体重管理核心知识 ↗</a></div>', unsafe_allow_html=True)
        st.caption("口径参考：国家卫生健康委《体重管理指导原则（2024年版）》、居民体重管理核心知识（2024年版）。本工具仅供健康管理参考。")


if __name__ == "__main__":
    main()
import base64
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="轻盈 BMI · 健康管理", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

ASSET = Path(__file__).resolve().parent / "assets" / "health-pyramid.png"
ASSET_DATA = "data:image/png;base64," + base64.b64encode(ASSET.read_bytes()).decode("ascii") if ASSET.exists() else ""
PET_ASSET = Path(__file__).resolve().parent / "assets" / "health-pet.png"
PET_DATA = "data:image/png;base64," + base64.b64encode(PET_ASSET.read_bytes()).decode("ascii") if PET_ASSET.exists() else ""

st.markdown("""
<style>
:root { --ink:#183b31; --muted:#526b60; --green:#2f765f; --mint:#e6f3ec; --peach:#fff0df; --purple:#5948c7; }
* { font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",Arial,sans-serif; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }
.stMarkdown, .stText, label, button, input, textarea { line-height:1.65; }
.stApp { background-color:#f7faf4; background-image:linear-gradient(135deg,#fbfaf3e8 0%,#f0f7f0e8 53%,#fff5eae8 100%),url("__PYRAMID__"); background-size:cover; background-position:center; background-attachment:fixed; color:var(--ink); }
.main, .main .block-container { position:relative; z-index:auto; }
section[data-testid="stSidebar"] { z-index:2; }
.block-container { max-width:1180px; padding-top:3.6rem; padding-bottom:3rem; }
.brand { display:flex; align-items:center; gap:12px; margin-bottom:4px; }
.brand { min-height:52px; line-height:1.25; }
.brand-mark { width:43px; height:43px; display:grid; place-items:center; background:#d8eee2; border-radius:15px; font-size:25px; box-shadow:0 4px 15px #8ebc9b35; }
.brand h1 { font-size:25px; margin:0; letter-spacing:-1px; color:#2e584a; }
.brand small { color:#82948b; font-size:12px; }
.hero { position:relative; min-height:320px; margin:8px 0 20px; border:1px solid #e1ede4; border-radius:28px; overflow:hidden; background:#fffdf7; box-shadow:0 15px 42px #547b5b18; }
.hero-copy { position:absolute; z-index:2; left:34px; top:31px; max-width:340px; }
.hero-copy .eyebrow { color:#4d9b78; font-weight:700; font-size:13px; letter-spacing:2px; }
.hero-copy h2 { font-size:34px; line-height:1.2; margin:8px 0 10px; color:#284b40; }
.hero-copy p { color:#405f53; line-height:1.8; margin:0; }
.hero img { position:absolute; right:-2%; bottom:-5%; width:72%; min-width:520px; max-height:104%; object-fit:contain; object-position:center; opacity:.20; mix-blend-mode:multiply; }
.pill { display:inline-block; background:#f0eaff; color:#6753c8; border-radius:99px; padding:6px 12px; font-size:12px; font-weight:600; margin-top:17px; }
.card { background:#fff; border:1px solid #e5eee9; border-radius:22px; padding:22px; box-shadow:0 8px 24px #4d6e5b12; }
.section-title { font-size:22px; color:#2e5146; font-weight:800; margin:4px 0 2px; }
.section-sub { color:#526b60; font-size:13px; margin-bottom:16px; }
.gender-card { border:1.5px solid #e5eee9; border-radius:18px; padding:13px; background:#fbfdfb; text-align:center; transition:.2s; }
.gender-card:hover { transform:translateY(-2px); box-shadow:0 8px 20px #6f9e801c; }
.gender-icon { font-size:39px; display:inline-block; animation:gentle-bob 2.8s ease-in-out infinite; }
.gender-card:nth-of-type(2) .gender-icon { animation-delay:.4s; }
.gender-card:hover .gender-icon { animation:happy-hop .55s ease-in-out infinite alternate; }
.mood-switch { position:relative; width:48px; height:48px; vertical-align:middle; }
.mood-switch span { position:absolute; inset:0; opacity:0; animation:mood-flip 3.6s ease-in-out infinite; }
.mood-switch span:first-child { opacity:1; }
.mood-switch span:last-child { animation-delay:1.8s; }
.gender-name { font-weight:700; color:#254d3f; }
.gender-note { font-size:11px; color:#60786d; margin-top:3px; }
.result-box { border-radius:24px; padding:24px; color:#fff; background:linear-gradient(135deg,#376f5d,#77ad83); box-shadow:0 12px 30px #4e916e40; }
.result-box .label { opacity:.8; font-size:13px; }
.bmi-number { font-size:64px; font-weight:800; letter-spacing:-3px; line-height:1; margin:10px 0; }
.result-tag { display:inline-block; padding:6px 13px; border-radius:99px; background:#ffffff26; font-weight:700; }
.tip { background:#fffaf0; border:1px solid #f4e2bd; color:#735b33; border-radius:16px; padding:13px 15px; line-height:1.65; font-size:13px; }
.envelope { background:repeating-linear-gradient(0deg,#fff9ee,#fff9ee 8px,#ffeed3 9px,#fff9ee 10px); border:1px solid #f4d9aa; border-radius:18px; padding:16px 20px; font-weight:800; color:#8a6234; text-align:center; font-size:16px; }
.history-empty { text-align:center; color:#91a198; padding:30px 10px; }
.metric-note { font-size:12px; color:#526b60; }
.stMarkdown p, .stMarkdown li, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] { color:#38594d; }
[data-testid="stRadio"] label p { color:#234b3d !important; font-weight:600; }
[data-testid="stRadio"] label { border:1px solid #cfe2d5; border-radius:16px; padding:10px 14px; background:#fbfefb; transition:.2s; }
[data-testid="stRadio"] label:hover { border-color:#56a976; background:#eff9f0; transform:translateY(-2px); }
[data-testid="stRadio"] [aria-checked="true"] + div { color:#214e3e; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:99px; padding:8px 18px; background:#edf5ef; color:#537466; }
.stTabs [aria-selected="true"] { background:#6958d8 !important; color:#fff !important; }
.gauge-card { background:#fff; border:1px solid #e5eee9; border-radius:24px; padding:20px 18px 15px; box-shadow:0 8px 24px #4d6e5b12; text-align:center; }
.gauge-title { color:#70847a; font-size:13px; margin-bottom:2px; }
.gauge { width:280px; height:190px; position:relative; margin:0 auto; overflow:hidden; }
.gauge-arc { position:absolute; width:255px; height:255px; left:12px; top:20px; border-radius:50%; background:conic-gradient(from 225deg, #efb06d 0deg, #6fbd7c 100deg, #8ac998 150deg, #efb06d 210deg, #e88775 270deg, transparent 270deg); -webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); }
.gauge-pointer { position:absolute; width:3px; height:105px; background:#5c6b64; left:50%; top:47px; transform-origin:50% 100%; border-radius:4px; z-index:3; }
.gauge-pointer:after { content:''; position:absolute; width:12px; height:12px; background:#5c6b64; border-radius:50%; left:50%; top:-4px; transform:translateX(-50%); }
.gauge-center { position:absolute; z-index:2; left:0; right:0; top:95px; }
.gauge-number { font-size:48px; line-height:1; font-weight:800; color:#55ad6d; letter-spacing:-2px; }
.gauge-sub { margin-top:8px; color:#93a099; font-size:15px; }
.gauge-tag { display:inline-block; padding:5px 11px; border-radius:99px; background:#63bb78; color:white; font-weight:700; font-size:13px; }
.gauge-label { position:absolute; z-index:3; font-weight:600; color:#506058; font-size:14px; }
.gauge-label.l1 { left:5px; top:84px; }.gauge-label.l2 { left:132px; top:18px; }.gauge-label.l3 { right:5px; top:84px; }
.gauge-scale { display:flex; justify-content:space-around; color:#9aa8a0; font-size:11px; margin-top:-2px; }
.pet-title { display:flex; align-items:center; gap:8px; color:#2e584a; font-weight:800; font-size:18px; }
.pet-hint { color:#244f3d; background:linear-gradient(90deg,#e2f5e5,#f5fbe9); border:2px solid #9dcea4; border-radius:16px; padding:12px 16px; margin:4px 0 10px; font-size:14px; font-weight:700; box-shadow:0 5px 16px #6ba77c22; }
.streamlit-expanderHeader { color:#285541 !important; font-weight:800 !important; font-size:15px !important; }
div[data-testid="stExpander"] { border:2px solid #c9e2cb; border-radius:18px; background:#fbfffa; box-shadow:0 7px 20px #5b906820; }
.pet-avatar { width:118px; height:118px; object-fit:contain; display:block; margin:0 auto -8px; filter:drop-shadow(0 8px 7px #5a9c7030); animation:pet-float 3.2s ease-in-out infinite; }
.pet-bubble { background:#f2f8ed; border:1px solid #d9ead5; border-radius:16px 16px 16px 4px; padding:11px 12px; color:#496a5a; font-size:12px; line-height:1.75; animation:bubble-breathe 3s ease-in-out infinite; }
.food-chip { display:inline-block; background:#fff7e7; border:1px solid #f2dfb9; border-radius:99px; padding:4px 8px; margin:3px 2px; font-size:11px; }
.shutter-shell { position:relative; overflow:hidden; border-radius:18px; }
.shutter-shell:before { content:''; position:absolute; inset:0; height:20px; background:repeating-linear-gradient(0deg,#fff4d8 0 5px,#f5d49d 6px 7px); transform-origin:top; z-index:2; pointer-events:none; opacity:.9; }
.shutter-shell:hover:before { height:0; transition:height .45s ease; }
div[data-testid="stNumberInput"] input { border-radius:12px; }
div.stButton > button { border-radius:14px; border:0; background:#3b806b; color:white; font-weight:700; padding:10px 18px; }
div.stButton > button:hover { background:#2d6553; color:white; }
@keyframes gentle-bob { 0%,100%{transform:translateY(0) rotate(-2deg)} 50%{transform:translateY(-5px) rotate(2deg)} }
@keyframes happy-hop { from{transform:translateY(0) scale(1)} to{transform:translateY(-8px) scale(1.06)} }
@keyframes pet-float { 0%,100%{transform:translateY(0) rotate(-1deg)} 50%{transform:translateY(-9px) rotate(1deg)} }
@keyframes bubble-breathe { 0%,100%{box-shadow:0 0 0 #9bc88a00} 50%{box-shadow:0 0 0 5px #9bc88a18} }
@keyframes mood-flip { 0%,42%{opacity:1;transform:scale(1)} 50%,92%{opacity:0;transform:scale(.82)} 100%{opacity:1;transform:scale(1)} }
</style>
""".replace("__PYRAMID__", ASSET_DATA), unsafe_allow_html=True)


def init_state():
    if "records" not in st.session_state:
        st.session_state.records = []
    if "food_log" not in st.session_state:
        st.session_state.food_log = []
    if "exercise_minutes" not in st.session_state:
        st.session_state.exercise_minutes = 0
    if "pet_reply" not in st.session_state:
        st.session_state.pet_reply = "嗨！我是轻盈仔 🌿 你可以问我 BMI、饮食、运动和作息，我会结合你的记录一起想办法。"


def pet_reply(question, latest, food_log, exercise_minutes):
    context = f"当前 BMI：{latest['bmi']:.1f}（{latest['level']}）" if latest else "还没有 BMI 记录"
    foods = "、".join(food_log[-6:]) if food_log else "暂未投喂食物"
    if question:
        q = question.lower()
        if any(k in q for k in ["吃", "饮食", "食物", "饭"]):
            return f"根据{context}，今天你记录了：{foods}。建议把蔬菜和蛋白质放在主食前，饮料优先选白水或无糖茶；我不会要求你极端节食，先把一餐吃得更均衡就很好。"
        if any(k in q for k in ["运动", "锻炼", "走", "跑"]):
            return f"你目前累计运动 {exercise_minutes} 分钟。可以从快走 20–30 分钟开始，每周逐步靠近 150–300 分钟；如果今天很忙，分成 2–3 次完成也算数。"
        if any(k in q for k in ["风险", "疾病", "健康"]):
            return f"{context}。BMI 是筛查参考，不是诊断；如果你属于超重或肥胖，建议关注血压、血糖、血脂和肝功能，并在需要时咨询医生。"
    if not latest:
        return "先完成一次 BMI 测量，我就能把建议变得更具体；也可以先把今天吃过的食物喂给我。"
    return f"我记住啦：{context}。今天已投喂 {len(food_log)} 次食物，运动 {exercise_minutes} 分钟。你可以继续问我‘晚餐怎么吃’或‘今天适合做什么运动’。"


def food_feedback(text, latest):
    lower = text.lower()
    suggestions = {
        "蔬菜": "🥬 成年人每天建议摄入蔬菜约 300–500g，深色蔬菜最好占一半以上。",
        "水果": "🍎 水果每天建议约 200–350g，优先完整水果，不用果汁替代。",
        "奶": "🥛 奶及奶制品每天可按约 300g 液态奶或等量替代品安排。",
        "酸奶": "🥣 酸奶可以作为奶制品来源，优先无糖款，注意看配料表和添加糖。",
        "鸡蛋": "🥚 鸡蛋是优质蛋白来源，可以和蔬菜、全谷物搭配。",
        "肉": "🍗 鱼、禽、蛋、瘦肉要适量搭配，优先鱼虾、禽肉和瘦肉。",
        "米饭": "🍚 主食不必完全不吃，可用部分糙米、燕麦、玉米、红薯替换精白米面。",
        "油炸": "🍟 油炸食物偶尔少量即可，今天可以用烤、蒸、煮替代。",
        "奶茶": "🧋 奶茶通常含糖和能量较高，建议选无糖茶、白水或无糖咖啡。",
        "饮料": "🥤 含糖饮料尽量少喝，口渴优先选择白水或无糖茶。",
    }
    matched = next((value for key, value in suggestions.items() if key in lower), "🍽️ 我暂时没识别出具体食物，可以写成‘食物 + 量’，例如‘苹果 200g’。")
    if any(k in lower for k in ["苹果", "香蕉", "橙", "梨", "桃", "水果"]):
        unit_hint = "这类食物用‘几个’最方便，例如苹果 1 个、香蕉 1 根。"
    elif any(k in lower for k in ["鸡蛋", "面包", "包子", "馒头"]):
        unit_hint = "这类食物可以按‘个 / 片’填写，例如鸡蛋 2 个、面包 2 片。"
    elif any(k in lower for k in ["米饭", "面条", "粥", "粉"]):
        unit_hint = "主食可以按‘碗 / 份’填写，例如米饭 1 碗、面条 1 份。"
    elif any(k in lower for k in ["牛奶", "豆浆", "酸奶", "饮料", "水"]):
        unit_hint = "饮品可以按‘毫升 / 盒’填写，例如牛奶 250ml、酸奶 1 盒。"
    else:
        unit_hint = "蔬菜、肉类等可以按克填写，例如青菜 200g、鸡胸肉 100g。"
    amount_hint = "我已经记下这次的食物和份量。" if any(ch.isdigit() for ch in text) else f"记得补充食用量。{unit_hint}"
    context = f"结合你最近 BMI {latest['bmi']:.1f}（{latest['level']}），" if latest else "结合一般成人膳食建议，"
    return f"{context}{matched}<br>📌 {amount_hint}<br>🌱 建议把这一餐搭配蔬菜和蛋白质。"


def pet_panel():
    st.markdown('<div class="pet-hint">🌿 点击下面的绿色卡片打开「轻盈仔」：它只有一个输入框，先点三个小想法，再输入内容发送。</div>', unsafe_allow_html=True)
    with st.expander("🌿 点击这里打开轻盈仔 · 你的健康电子 Pet", expanded=True):
        st.markdown('<div class="pet-title">🌿 轻盈仔 <span style="font-size:11px;color:#58786a">你的健康电子 Pet</span></div>', unsafe_allow_html=True)
        if PET_ASSET.exists():
            st.image(str(PET_ASSET), width=150)
        st.markdown(f'<div class="pet-bubble">{st.session_state.pet_reply}</div>', unsafe_allow_html=True)
        latest = st.session_state.records[-1] if st.session_state.records else None
        st.markdown("#### 💭 轻盈仔的三个小想法")
        q1, q2, q3 = st.columns(3)
        with q1: food_mode = st.button("🍽️ 我吃了什么？", use_container_width=True)
        with q2: exercise_mode = st.button("🏃 我运动多久？", use_container_width=True)
        with q3: ask_mode = st.button("💬 我想问健康", use_container_width=True)
        if food_mode: st.session_state.pet_mode = "food"
        elif exercise_mode: st.session_state.pet_mode = "exercise"
        elif ask_mode: st.session_state.pet_mode = "ask"
        mode = st.session_state.get("pet_mode", "ask")
        labels = {"food": "输入食物 + 食用量", "exercise": "输入运动 + 时长", "ask": "输入健康问题"}
        hints = {"food": "例如：苹果 1 个、米饭 1 碗、鸡蛋 2 个、牛奶 250ml", "exercise": "例如：快走 30 分钟、跳绳 15 分钟", "ask": "例如：晚餐怎么吃？最近总熬夜怎么办？"}
        prompt = st.text_input(labels[mode], placeholder=hints[mode], key="pet_single_input")
        if st.button("发送给轻盈仔 ✨", use_container_width=True, disabled=not prompt.strip()):
            if mode == "food":
                st.session_state.food_log.append(prompt.strip())
                st.session_state.pet_reply = food_feedback(prompt.strip(), latest)
            elif mode == "exercise":
                found = re.search(r"(\d+(?:\.\d+)?)", prompt)
                added = int(float(found.group(1))) if found else 0
                st.session_state.exercise_minutes += added
                st.session_state.pet_reply = f"我记下啦：{prompt.strip()}。今天累计运动 {st.session_state.exercise_minutes} 分钟。<br>🎯 每周可以逐步靠近 150–300 分钟，忙的时候分段完成也算数。"
            else:
                st.session_state.pet_reply = pet_reply(prompt.strip(), latest, st.session_state.food_log, st.session_state.exercise_minutes)
            st.rerun()
        if st.session_state.food_log:
            st.markdown("".join(f'<span class="food-chip">🍴 {item}</span>' for item in st.session_state.food_log[-6:]), unsafe_allow_html=True)
        st.markdown("#### 📊 轻盈仔的小图表")
        if st.session_state.records:
            pet_chart = pd.DataFrame(st.session_state.records)
            pet_chart["时间"] = pd.to_datetime(pet_chart["date"])
            st.line_chart(pet_chart.set_index("时间")["bmi"], color="#55a96f", height=180)
            st.caption(f"已记录 {len(st.session_state.records)} 次 BMI · 今日运动 {st.session_state.exercise_minutes} 分钟 · 已记录 {len(st.session_state.food_log)} 次饮食")
        else:
            st.info("完成第一次 BMI 测量后，这里会出现你的趋势图；先和轻盈仔说说今天吃了什么吧。")
        st.caption("食物请写清楚数量，例如克、毫升、个或碗；轻盈仔会结合 BMI 和记录给出份量建议。")


def classify(bmi):
    if bmi < 18.5:
        return "偏瘦", "🍃", "建议适当增加营养与优质蛋白，规律吃饭，慢慢把身体养回来。", "low"
    if bmi < 24:
        return "正常", "😊", "状态很棒！继续保持吃动平衡、规律作息，让好习惯成为你的超能力。", "good"
    if bmi < 28:
        return "超重", "🙂", "别着急，先从少一杯含糖饮料、多走十分钟开始，稳定的小改变最有力量。", "watch"
    return "肥胖", "💪", "建议温和、持续地管理体重；如有基础疾病或明显不适，请咨询医生或营养师。", "high"


def advice(level, gender):
    if level == "偏瘦":
        return [
            ("🥣 饮食核心", "🍚 三餐 + 1–2 次加餐，先把规律吃饭做起来。<br>🥚 每餐加入蛋、奶、鱼、肉、豆类中的 1–2 种优质蛋白。<br>🥜 加餐可选坚果、酸奶、香蕉、全麦面包；不要只靠奶茶和甜点增重。<br>📈 每周观察一次体重，缓慢增加比突然暴食更稳妥。"),
            ("🍱 一日餐盘", "🌞 早餐：牛奶 / 豆浆 + 鸡蛋 + 全麦主食。<br>☀️ 午餐：米饭 + 鱼肉或鸡肉 + 两份蔬菜。<br>🌙 晚餐：面 / 杂粮饭 + 豆腐或瘦肉 + 菌菇蔬菜。<br>🍎 加餐：酸奶、水果、坚果三选一，感觉饱胀就减少份量。"),
            ("🏋️ 运动方案", "💪 每周 2–3 次力量训练：深蹲、臀桥、俯卧撑、弹力带划船各 2–3 组。<br>🚶 搭配轻松有氧，每次 20–30 分钟。<br>🎯 重点是保留肌肉，不用用大量跑步抵消进食。<br>🩺 体重持续下降、乏力或食欲异常时请咨询医生。"),
            ("🌙 生活节奏", "⏰ 固定起床和入睡时间，争取 7–9 小时睡眠。<br>💧 白天分次饮水，避免用咖啡或能量饮料顶替正餐。<br>🧡 每天记录一次‘吃饭 / 精力 / 心情’，找到影响食欲的原因。"),
        ]
    return [
        ("🥗 饮食核心", "🍽️ 进餐顺序：蔬菜 → 蛋白质 → 主食，先吃慢吃，七八分饱即可。<br>🥬 每餐至少一半是蔬菜，优先深色叶菜、菌菇、番茄。<br>🥚 蛋白质选鱼虾、鸡蛋、瘦肉、豆制品和奶。<br>🚫 少吃油炸、含糖饮料、甜点和酒；盐尽量控制在每日 5g 内，烹调油约 25–30g。"),
        ("🍱 一日餐盘", "🌞 早餐：无糖奶 / 豆浆 + 鸡蛋 + 全麦面包。<br>☀️ 午餐：半盘蔬菜 + 一掌心蛋白质 + 半拳到一拳主食。<br>🌙 晚餐：清淡蛋白质 + 蔬菜 + 适量杂粮主食，睡前 2–3 小时尽量不再进食。<br>🍎 想吃零食时：先喝水，优先水果、原味坚果或无糖酸奶。"),
        ("🏃 运动方案", "🚶 每周累计 150–300 分钟中等强度运动：快走、游泳、骑车都可以。<br>💪 每周 2–3 天抗阻训练：深蹲、臀桥、哑铃推举、弹力带划船。<br>⏱️ 久坐每 60 分钟起身 3–5 分钟，接水、拉伸、走动都算。<br>🌱 先从每天 20 分钟开始，稳定两周后再增加时长。"),
        ("🧘 心理与作息", "🌙 目标是 7–9 小时睡眠，尽量固定入睡和起床时间。<br>📝 想吃东西时先问自己：我是饿了、累了，还是在焦虑？<br>🌬️ 情绪上来时先做 3 分钟深呼吸、散步或伸展，再决定要不要吃。<br>👏 关注一周趋势，不因某一顿饭或某一天的体重责怪自己。"),
    ]


def risk_page(level):
    if level == "偏瘦":
        return ("🌿 体重过低的照顾提醒", "体重过低可能与营养摄入不足、肌肉量下降或潜在健康问题有关。可以关注食欲、疲劳感和近期体重变化，采用少量多餐、增加优质蛋白的方式温和调整；若体重持续下降或伴随不适，请及时咨询医生。", "需要留意：持续下降、乏力、食欲明显变化")
    if level == "正常":
        return ("🌈 继续守护你的健康", "BMI 在正常范围并不等于所有健康指标都正常。建议继续关注血压、血糖和血脂，保持规律运动与作息，让好状态稳稳延续。", "建议关注：血压、血糖、血脂")
    if level == "超重":
        return ("🔎 超重阶段的风险参照", "超重可能增加高血压、血糖异常、血脂异常、脂肪肝等代谢问题的发生风险。越早从饮食、运动和睡眠做小调整，越容易把变化控制在可管理的范围内；这不是对个人疾病的诊断。", "建议留意：血压、空腹血糖、血脂")
        return ("🧡 肥胖阶段的风险参照", "肥胖与高血压、2 型糖尿病、血脂异常、脂肪肝及心脑血管疾病等风险增加有关。建议在专业人士指导下制定循序渐进的体重管理计划；如已有慢性病或明显不适，请优先就医。", "建议留意：血压、血糖、血脂、肝功能及睡眠情况")


def gauge_html(bmi, level, emoji):
    # 成人 BMI 展示区间为 15–35；分类仍严格使用中国成人 BMI 口径。
    pct = max(0.0, min(1.0, (bmi - 15) / 20))
    angle = -135 + 270 * pct
    return f'''<div class="gauge-card">
        <div class="gauge-title">你的 BMI 身体质量指数</div>
        <div class="gauge">
          <div class="gauge-arc"></div>
          <div class="gauge-pointer" style="transform:translateX(-50%) rotate({angle:.1f}deg)"></div>
          <div class="gauge-center"><div class="gauge-number">{bmi:.1f}</div><div class="gauge-sub">BMI&nbsp; <span class="gauge-tag">{emoji} {level}</span></div></div>
          <span class="gauge-label l1">18.5</span><span class="gauge-label l2">24</span><span class="gauge-label l3">28</span>
        </div>
        <div class="gauge-scale"><span>偏瘦</span><span>正常</span><span>超重</span><span>肥胖</span></div>
    </div>'''


def main():
    init_state()
    pet_panel()
    st.markdown('<div class="brand"><div class="brand-mark">🌿</div><div><h1>轻盈 BMI</h1><small>把健康，变成每天都做得到的小事</small></div></div>', unsafe_allow_html=True)

    st.markdown(f'''<div class="hero"><div class="hero-copy"><div class="eyebrow">HEALTHY HABITS · 健康习惯</div><h2>今天的你，<br>值得被好好照顾。</h2><p>从一次 BMI 查询开始，发现身体发来的小信号，给自己一份温柔又具体的行动计划。</p><span class="pill">✨ 记录每一次轻盈变化</span></div><img src="{ASSET_DATA}" /></div>''', unsafe_allow_html=True)

    tab_check, tab_profile, tab_guide = st.tabs(["🌱 开始测量", "📈 个人中心", "📚 官方健康建议"])
    with tab_check:
        st.markdown('<div class="section-title">先认识一下今天的你</div><div class="section-sub">选择性别后，我们会给你更贴合的健康建议。成人 BMI 参考适用于 18 岁及以上人群。</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.2, 1], gap="medium")
        with c1:
            selected_gender = st.radio("你的性别（点击图标即可选择）", ["🧒🏻 男生", "👧🏻 女生"], horizontal=True, label_visibility="visible")
            gender = selected_gender.split(" ", 1)[1]
        with c2:
            age = st.number_input("年龄", min_value=1, max_value=120, value=25, step=1)

        st.markdown("#### 📏 输入身体数据")
        i1, i2 = st.columns(2)
        with i1:
            height = st.number_input("身高（米）｜例如：1.70", min_value=0.5, max_value=2.5, value=1.70, step=0.01, format="%.2f", help="请用米填写：170 厘米 = 1.70 米")
        with i2:
            weight = st.number_input("体重（千克）｜例如：60.0", min_value=10.0, max_value=300.0, value=60.0, step=0.1, format="%.1f", help="请用千克填写：60 斤约等于 30 千克")

        if st.button("✨ 查看我的 BMI", use_container_width=True):
            bmi = weight / (height ** 2)
            level, emoji, tip, tone = classify(bmi)
            previous = st.session_state.records[-1] if st.session_state.records else None
            delta = None if previous is None else bmi - previous["bmi"]
            st.session_state.current = {"bmi": bmi, "weight": weight, "level": level, "emoji": emoji, "tip": tip, "gender": gender, "age": age, "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
            st.session_state.records.append(st.session_state.current.copy())
            st.session_state.delta = delta

        if "current" in st.session_state:
            r = st.session_state.current
            delta = st.session_state.get("delta")
            left, right = st.columns([1.2, 1], gap="large")
            with left:
                st.markdown(gauge_html(r["bmi"], r["level"], r["emoji"]), unsafe_allow_html=True)
                st.markdown(f'<div class="result-box" style="margin-top:12px"><div class="label">轻盈小提醒</div><p style="margin:8px 0 0;opacity:.95;line-height:1.7">{r["tip"]}</p></div>', unsafe_allow_html=True)
                low_w, high_w = 18.5 * height ** 2, 23.9 * height ** 2
                a, b, c = st.columns(3)
                a.metric("健康体重下限", f"{low_w:.1f} kg")
                b.metric("健康体重上限", f"{high_w:.1f} kg")
                c.metric("本次体重", f"{weight:.1f} kg")
                st.caption("按中国成人 BMI 18.5–23.9 的参考区间换算；不适用于未成年人、孕期及特殊人群。")
            with right:
                st.markdown("#### 🧭 你的健康坐标")
                st.progress(min(r["bmi"] / 40, 1.0))
                st.caption("偏瘦 18.5　　正常 24　　超重 28　　肥胖")
                st.markdown('<div class="tip">BMI 是筛查参考，不是疾病诊断。建议结合血压、血糖、血脂、睡眠和日常精力综合观察。</div>', unsafe_allow_html=True)
                if delta is not None:
                    if delta < -0.1:
                        st.success(f"👍 比上一次下降 {abs(delta):.1f}，你的坚持正在发生变化！")
                    elif delta > 0.1:
                        st.info(f"🌤️ 比上一次上升 {delta:.1f}，别责怪自己，看看近期作息和饮食即可。")
                    else:
                        st.info("🌼 和上次差不多，稳定也是一种进步。")

            st.markdown("#### ✉️ 你的专属健康手册已送达")
            with st.expander("📨 点击打开专属健康手册 · 查看你的行动方案", expanded=True):
                st.markdown('<div class="envelope">💌 你的专属健康手册到了！<br><span style="font-size:12px;font-weight:500">点击上方绿色标题，逐页查看饮食、运动、作息和风险参照</span></div>', unsafe_allow_html=True)
                handbook = advice(r["level"], r["gender"])
                risk_title, risk_text, risk_watch = risk_page(r["level"])
                pages = [(title, text) for title, text in handbook] + [(risk_title, risk_text)]
                page_names = [f"第 {i + 1} 页 · {title.split(' ', 1)[-1]}" for i, (title, _) in enumerate(pages)]
                selected_page = st.radio("手册分页", page_names, horizontal=True, label_visibility="collapsed")
                page_index = page_names.index(selected_page)
                page_title, page_text = pages[page_index]
                st.markdown(f"### {page_title}")
                st.markdown(f'<div class="tip" style="font-size:15px;line-height:2">{page_text}</div>', unsafe_allow_html=True)
                if page_index == len(pages) - 1:
                    st.info(f"🩺 {risk_watch}\n\n以上是风险参照，不代表你已经患有相关疾病。")
                st.caption(f"{page_index + 1} / {len(pages)}　·　左右选择上方分页，逐页阅读你的行动建议")
                st.warning("⚠️ 以上是成人健康管理参考。孕期、未成年人、运动员或有慢性病者，请遵循专业人士建议。")

    with tab_profile:
        st.markdown('<div class="section-title">你的身体变化日记</div><div class="section-sub">每次测量都会留下一个小脚印，关注趋势，比盯着某一个数字更重要。</div>', unsafe_allow_html=True)
        records = st.session_state.records
        if not records:
            st.markdown('<div class="card history-empty">🌱 还没有测量记录<br><span class="metric-note">完成第一次测量后，这里会出现你的 BMI 趋势折线和鼓励徽章。</span></div>', unsafe_allow_html=True)
        else:
            df = pd.DataFrame(records)
            df["时间"] = pd.to_datetime(df["date"])
            f1, f2, f3, f4 = st.columns(4)
            with f1: view = st.radio("查看范围", ["最近", "今年", "近半年", "全部"], horizontal=True, label_visibility="collapsed")
            with f2: chart_metric = st.radio("指标", ["BMI", "体重"], horizontal=True, label_visibility="collapsed")
            if view == "今年": chart_df = df[df["时间"].dt.year == datetime.now().year]
            elif view == "近半年": chart_df = df[df["时间"] >= datetime.now() - timedelta(days=183)]
            elif view == "最近": chart_df = df.tail(8)
            else: chart_df = df
            if chart_df.empty: chart_df = df.tail(1)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            metric_key = {"BMI": "bmi", "体重": "weight"}[chart_metric]
            metric_data = chart_df.dropna(subset=[metric_key]).set_index("时间")[metric_key]
            st.line_chart(metric_data, color="#6958d8", height=300)
            mn, mx = chart_df[metric_key].min(), chart_df[metric_key].max()
            m1, m2, m3 = st.columns(3)
            unit = "" if chart_metric == "BMI" else " kg"
            m1.metric(f"最低 {chart_metric}", f"{mn:.1f}{unit}")
            m2.metric(f"最高 {chart_metric}", f"{mx:.1f}{unit}")
            m3.metric("测量次数", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("#### 🧡 最近记录")
            for idx, row in df.iloc[::-1].head(10).iterrows():
                prev = df.iloc[idx-1]["bmi"] if idx > 0 else None
                badge = "👍" if prev is not None and row["bmi"] < prev - .1 else ""
                st.markdown(f'<div class="card" style="padding:14px 18px;margin:8px 0"><b>{row["emoji"]} {row["level"]}</b>　BMI <b>{row["bmi"]:.1f}</b>　<span class="metric-note">{row["date"]} · {row["gender"]}</span> <span style="float:right;font-size:20px">{badge}</span></div>', unsafe_allow_html=True)
            if st.button("清空本地记录"):
                st.session_state.records = []
                st.rerun()

    with tab_guide:
        st.markdown('<div class="section-title">官方健康建议</div><div class="section-sub">把可靠的知识，变成今天就能做到的选择。</div>', unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown('<div class="card"><div style="font-size:30px">🥗</div><b>平衡膳食</b><p class="metric-note">食物多样、规律三餐，少油少盐，优先选择蔬菜、全谷物、奶豆和优质蛋白。</p><a href="https://www.nhc.gov.cn/wjw/c100378/202412/f3f58b54fbeb4c87b14164fac898bf08/files/1736390749000_59785.pdf" target="_blank">查看国家卫健委体重管理规范化流程 ↗</a></div>', unsafe_allow_html=True)
        with g2:
            st.markdown('<div class="card"><div style="font-size:30px">🚶</div><b>动起来</b><p class="metric-note">逐步达到每周 150–300 分钟中等强度身体活动，并加入抗阻训练。</p><a href="https://www.nhc.gov.cn/wjw/c100175/202005/7757e4f72e13402a97b42f785d7a335a.shtml" target="_blank">查看国家卫健委膳食与运动建议 ↗</a></div>', unsafe_allow_html=True)
        with g3:
            st.markdown('<div class="card"><div style="font-size:30px">😴</div><b>睡眠与压力</b><p class="metric-note">保持规律作息，减少情绪化进食，用散步、冥想或瑜伽给自己一点缓冲。</p><a href="https://www.nhc.gov.cn/cms-search/downFiles/5e20de34c0fe45bb9fcac0636b21ad98.pdf" target="_blank">查看居民体重管理核心知识 ↗</a></div>', unsafe_allow_html=True)
        st.caption("口径参考：国家卫生健康委《体重管理指导原则（2024年版）》、居民体重管理核心知识（2024年版）。本工具仅供健康管理参考。")


if __name__ == "__main__":
    main()
import base64
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="轻盈 BMI · 健康管理", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

ASSET = Path(__file__).resolve().parent / "assets" / "health-pyramid.png"
ASSET_DATA = "data:image/png;base64," + base64.b64encode(ASSET.read_bytes()).decode("ascii") if ASSET.exists() else ""
PET_ASSET = Path(__file__).resolve().parent / "assets" / "health-pet.png"
PET_DATA = "data:image/png;base64," + base64.b64encode(PET_ASSET.read_bytes()).decode("ascii") if PET_ASSET.exists() else ""

st.markdown("""
<style>
:root { --ink:#183b31; --muted:#526b60; --green:#2f765f; --mint:#e6f3ec; --peach:#fff0df; --purple:#5948c7; }
* { font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",Arial,sans-serif; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }
.stMarkdown, .stText, label, button, input, textarea { line-height:1.65; }
.stApp { background-color:#f7faf4; background-image:linear-gradient(135deg,#fbfaf3e8 0%,#f0f7f0e8 53%,#fff5eae8 100%),url("__PYRAMID__"); background-size:cover; background-position:center; background-attachment:fixed; color:var(--ink); }
.main, .main .block-container { position:relative; z-index:auto; }
section[data-testid="stSidebar"] { z-index:2; }
.block-container { max-width:1180px; padding-top:3.6rem; padding-bottom:3rem; }
.brand { display:flex; align-items:center; gap:12px; margin-bottom:4px; }
.brand { min-height:52px; line-height:1.25; }
.brand-mark { width:43px; height:43px; display:grid; place-items:center; background:#d8eee2; border-radius:15px; font-size:25px; box-shadow:0 4px 15px #8ebc9b35; }
.brand h1 { font-size:25px; margin:0; letter-spacing:-1px; color:#2e584a; }
.brand small { color:#82948b; font-size:12px; }
.hero { position:relative; min-height:320px; margin:8px 0 20px; border:1px solid #e1ede4; border-radius:28px; overflow:hidden; background:#fffdf7; box-shadow:0 15px 42px #547b5b18; }
.hero-copy { position:absolute; z-index:2; left:34px; top:31px; max-width:340px; }
.hero-copy .eyebrow { color:#4d9b78; font-weight:700; font-size:13px; letter-spacing:2px; }
.hero-copy h2 { font-size:34px; line-height:1.2; margin:8px 0 10px; color:#284b40; }
.hero-copy p { color:#405f53; line-height:1.8; margin:0; }
.hero img { position:absolute; right:-2%; bottom:-5%; width:72%; min-width:520px; max-height:104%; object-fit:contain; object-position:center; opacity:.20; mix-blend-mode:multiply; }
.pill { display:inline-block; background:#f0eaff; color:#6753c8; border-radius:99px; padding:6px 12px; font-size:12px; font-weight:600; margin-top:17px; }
.card { background:#fff; border:1px solid #e5eee9; border-radius:22px; padding:22px; box-shadow:0 8px 24px #4d6e5b12; }
.section-title { font-size:22px; color:#2e5146; font-weight:800; margin:4px 0 2px; }
.section-sub { color:#526b60; font-size:13px; margin-bottom:16px; }
.gender-card { border:1.5px solid #e5eee9; border-radius:18px; padding:13px; background:#fbfdfb; text-align:center; transition:.2s; }
.gender-card:hover { transform:translateY(-2px); box-shadow:0 8px 20px #6f9e801c; }
.gender-icon { font-size:39px; display:inline-block; animation:gentle-bob 2.8s ease-in-out infinite; }
.gender-card:nth-of-type(2) .gender-icon { animation-delay:.4s; }
.gender-card:hover .gender-icon { animation:happy-hop .55s ease-in-out infinite alternate; }
.mood-switch { position:relative; width:48px; height:48px; vertical-align:middle; }
.mood-switch span { position:absolute; inset:0; opacity:0; animation:mood-flip 3.6s ease-in-out infinite; }
.mood-switch span:first-child { opacity:1; }
.mood-switch span:last-child { animation-delay:1.8s; }
.gender-name { font-weight:700; color:#254d3f; }
.gender-note { font-size:11px; color:#60786d; margin-top:3px; }
.result-box { border-radius:24px; padding:24px; color:#fff; background:linear-gradient(135deg,#376f5d,#77ad83); box-shadow:0 12px 30px #4e916e40; }
.result-box .label { opacity:.8; font-size:13px; }
.bmi-number { font-size:64px; font-weight:800; letter-spacing:-3px; line-height:1; margin:10px 0; }
.result-tag { display:inline-block; padding:6px 13px; border-radius:99px; background:#ffffff26; font-weight:700; }
.tip { background:#fffaf0; border:1px solid #f4e2bd; color:#735b33; border-radius:16px; padding:13px 15px; line-height:1.65; font-size:13px; }
.envelope { background:repeating-linear-gradient(0deg,#fff9ee,#fff9ee 8px,#ffeed3 9px,#fff9ee 10px); border:1px solid #f4d9aa; border-radius:18px; padding:16px 20px; font-weight:800; color:#8a6234; text-align:center; font-size:16px; }
.history-empty { text-align:center; color:#91a198; padding:30px 10px; }
.metric-note { font-size:12px; color:#526b60; }
.stMarkdown p, .stMarkdown li, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] { color:#38594d; }
[data-testid="stRadio"] label p { color:#234b3d !important; font-weight:600; }
[data-testid="stRadio"] label { border:1px solid #cfe2d5; border-radius:16px; padding:10px 14px; background:#fbfefb; transition:.2s; }
[data-testid="stRadio"] label:hover { border-color:#56a976; background:#eff9f0; transform:translateY(-2px); }
[data-testid="stRadio"] [aria-checked="true"] + div { color:#214e3e; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:99px; padding:8px 18px; background:#edf5ef; color:#537466; }
.stTabs [aria-selected="true"] { background:#6958d8 !important; color:#fff !important; }
.gauge-card { background:#fff; border:1px solid #e5eee9; border-radius:24px; padding:20px 18px 15px; box-shadow:0 8px 24px #4d6e5b12; text-align:center; }
.gauge-title { color:#70847a; font-size:13px; margin-bottom:2px; }
.gauge { width:280px; height:190px; position:relative; margin:0 auto; overflow:hidden; }
.gauge-arc { position:absolute; width:255px; height:255px; left:12px; top:20px; border-radius:50%; background:conic-gradient(from 225deg, #efb06d 0deg, #6fbd7c 100deg, #8ac998 150deg, #efb06d 210deg, #e88775 270deg, transparent 270deg); -webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); mask:radial-gradient(farthest-side,transparent calc(100% - 17px),#000 calc(100% - 16px)); }
.gauge-pointer { position:absolute; width:3px; height:105px; background:#5c6b64; left:50%; top:47px; transform-origin:50% 100%; border-radius:4px; z-index:3; }
.gauge-pointer:after { content:''; position:absolute; width:12px; height:12px; background:#5c6b64; border-radius:50%; left:50%; top:-4px; transform:translateX(-50%); }
.gauge-center { position:absolute; z-index:2; left:0; right:0; top:95px; }
.gauge-number { font-size:48px; line-height:1; font-weight:800; color:#55ad6d; letter-spacing:-2px; }
.gauge-sub { margin-top:8px; color:#93a099; font-size:15px; }
.gauge-tag { display:inline-block; padding:5px 11px; border-radius:99px; background:#63bb78; color:white; font-weight:700; font-size:13px; }
.gauge-label { position:absolute; z-index:3; font-weight:600; color:#506058; font-size:14px; }
.gauge-label.l1 { left:5px; top:84px; }.gauge-label.l2 { left:132px; top:18px; }.gauge-label.l3 { right:5px; top:84px; }
.gauge-scale { display:flex; justify-content:space-around; color:#9aa8a0; font-size:11px; margin-top:-2px; }
.pet-title { display:flex; align-items:center; gap:8px; color:#2e584a; font-weight:800; font-size:18px; }
.pet-hint { color:#244f3d; background:linear-gradient(90deg,#e2f5e5,#f5fbe9); border:2px solid #9dcea4; border-radius:16px; padding:12px 16px; margin:4px 0 10px; font-size:14px; font-weight:700; box-shadow:0 5px 16px #6ba77c22; }
.streamlit-expanderHeader { color:#285541 !important; font-weight:800 !important; font-size:15px !important; }
div[data-testid="stExpander"] { border:2px solid #c9e2cb; border-radius:18px; background:#fbfffa; box-shadow:0 7px 20px #5b906820; }
.pet-avatar { width:118px; height:118px; object-fit:contain; display:block; margin:0 auto -8px; filter:drop-shadow(0 8px 7px #5a9c7030); animation:pet-float 3.2s ease-in-out infinite; }
.pet-bubble { background:#f2f8ed; border:1px solid #d9ead5; border-radius:16px 16px 16px 4px; padding:11px 12px; color:#496a5a; font-size:12px; line-height:1.75; animation:bubble-breathe 3s ease-in-out infinite; }
.food-chip { display:inline-block; background:#fff7e7; border:1px solid #f2dfb9; border-radius:99px; padding:4px 8px; margin:3px 2px; font-size:11px; }
.shutter-shell { position:relative; overflow:hidden; border-radius:18px; }
.shutter-shell:before { content:''; position:absolute; inset:0; height:20px; background:repeating-linear-gradient(0deg,#fff4d8 0 5px,#f5d49d 6px 7px); transform-origin:top; z-index:2; pointer-events:none; opacity:.9; }
.shutter-shell:hover:before { height:0; transition:height .45s ease; }
div[data-testid="stNumberInput"] input { border-radius:12px; }
div.stButton > button { border-radius:14px; border:0; background:#3b806b; color:white; font-weight:700; padding:10px 18px; }
div.stButton > button:hover { background:#2d6553; color:white; }
@keyframes gentle-bob { 0%,100%{transform:translateY(0) rotate(-2deg)} 50%{transform:translateY(-5px) rotate(2deg)} }
@keyframes happy-hop { from{transform:translateY(0) scale(1)} to{transform:translateY(-8px) scale(1.06)} }
@keyframes pet-float { 0%,100%{transform:translateY(0) rotate(-1deg)} 50%{transform:translateY(-9px) rotate(1deg)} }
@keyframes bubble-breathe { 0%,100%{box-shadow:0 0 0 #9bc88a00} 50%{box-shadow:0 0 0 5px #9bc88a18} }
@keyframes mood-flip { 0%,42%{opacity:1;transform:scale(1)} 50%,92%{opacity:0;transform:scale(.82)} 100%{opacity:1;transform:scale(1)} }
</style>
""".replace("__PYRAMID__", ASSET_DATA), unsafe_allow_html=True)


def init_state():
    if "records" not in st.session_state:
        st.session_state.records = []
    if "food_log" not in st.session_state:
        st.session_state.food_log = []
    if "exercise_minutes" not in st.session_state:
        st.session_state.exercise_minutes = 0
    if "pet_reply" not in st.session_state:
        st.session_state.pet_reply = "嗨！我是轻盈仔 🌿 你可以问我 BMI、饮食、运动和作息，我会结合你的记录一起想办法。"


def pet_reply(question, latest, food_log, exercise_minutes):
    context = f"当前 BMI：{latest['bmi']:.1f}（{latest['level']}）" if latest else "还没有 BMI 记录"
    foods = "、".join(food_log[-6:]) if food_log else "暂未投喂食物"
    if question:
        q = question.lower()
        if any(k in q for k in ["吃", "饮食", "食物", "饭"]):
            return f"根据{context}，今天你记录了：{foods}。建议把蔬菜和蛋白质放在主食前，饮料优先选白水或无糖茶；我不会要求你极端节食，先把一餐吃得更均衡就很好。"
        if any(k in q for k in ["运动", "锻炼", "走", "跑"]):
            return f"你目前累计运动 {exercise_minutes} 分钟。可以从快走 20–30 分钟开始，每周逐步靠近 150–300 分钟；如果今天很忙，分成 2–3 次完成也算数。"
        if any(k in q for k in ["风险", "疾病", "健康"]):
            return f"{context}。BMI 是筛查参考，不是诊断；如果你属于超重或肥胖，建议关注血压、血糖、血脂和肝功能，并在需要时咨询医生。"
    if not latest:
        return "先完成一次 BMI 测量，我就能把建议变得更具体；也可以先把今天吃过的食物喂给我。"
    return f"我记住啦：{context}。今天已投喂 {len(food_log)} 次食物，运动 {exercise_minutes} 分钟。你可以继续问我‘晚餐怎么吃’或‘今天适合做什么运动’。"


def food_feedback(text, latest):
    lower = text.lower()
    suggestions = {
        "蔬菜": "🥬 成年人每天建议摄入蔬菜约 300–500g，深色蔬菜最好占一半以上。",
        "水果": "🍎 水果每天建议约 200–350g，优先完整水果，不用果汁替代。",
        "奶": "🥛 奶及奶制品每天可按约 300g 液态奶或等量替代品安排。",
        "酸奶": "🥣 酸奶可以作为奶制品来源，优先无糖款，注意看配料表和添加糖。",
        "鸡蛋": "🥚 鸡蛋是优质蛋白来源，可以和蔬菜、全谷物搭配。",
        "肉": "🍗 鱼、禽、蛋、瘦肉要适量搭配，优先鱼虾、禽肉和瘦肉。",
        "米饭": "🍚 主食不必完全不吃，可用部分糙米、燕麦、玉米、红薯替换精白米面。",
        "油炸": "🍟 油炸食物偶尔少量即可，今天可以用烤、蒸、煮替代。",
        "奶茶": "🧋 奶茶通常含糖和能量较高，建议选无糖茶、白水或无糖咖啡。",
        "饮料": "🥤 含糖饮料尽量少喝，口渴优先选择白水或无糖茶。",
    }
    matched = next((value for key, value in suggestions.items() if key in lower), "🍽️ 我暂时没识别出具体食物，可以写成‘食物 + 量’，例如‘苹果 200g’。")
    if any(k in lower for k in ["苹果", "香蕉", "橙", "梨", "桃", "水果"]):
        unit_hint = "这类食物用‘几个’最方便，例如苹果 1 个、香蕉 1 根。"
    elif any(k in lower for k in ["鸡蛋", "面包", "包子", "馒头"]):
        unit_hint = "这类食物可以按‘个 / 片’填写，例如鸡蛋 2 个、面包 2 片。"
    elif any(k in lower for k in ["米饭", "面条", "粥", "粉"]):
        unit_hint = "主食可以按‘碗 / 份’填写，例如米饭 1 碗、面条 1 份。"
    elif any(k in lower for k in ["牛奶", "豆浆", "酸奶", "饮料", "水"]):
        unit_hint = "饮品可以按‘毫升 / 盒’填写，例如牛奶 250ml、酸奶 1 盒。"
    else:
        unit_hint = "蔬菜、肉类等可以按克填写，例如青菜 200g、鸡胸肉 100g。"
    amount_hint = "我已经记下这次的食物和份量。" if any(ch.isdigit() for ch in text) else f"记得补充食用量。{unit_hint}"
    context = f"结合你最近 BMI {latest['bmi']:.1f}（{latest['level']}），" if latest else "结合一般成人膳食建议，"
    return f"{context}{matched}<br>📌 {amount_hint}<br>🌱 建议把这一餐搭配蔬菜和蛋白质。"


def pet_panel():
    st.markdown('<div class="pet-hint">🌿 点击下面的绿色卡片打开「轻盈仔」：它只有一个输入框，先点三个小想法，再输入内容发送。</div>', unsafe_allow_html=True)
    with st.expander("🌿 点击这里打开轻盈仔 · 你的健康电子 Pet", expanded=True):
        st.markdown('<div class="pet-title">🌿 轻盈仔 <span style="font-size:11px;color:#58786a">你的健康电子 Pet</span></div>', unsafe_allow_html=True)
        if PET_ASSET.exists():
            st.image(str(PET_ASSET), width=150)
        st.markdown(f'<div class="pet-bubble">{st.session_state.pet_reply}</div>', unsafe_allow_html=True)
        latest = st.session_state.records[-1] if st.session_state.records else None
        st.markdown("#### 💭 轻盈仔的三个小想法")
        q1, q2, q3 = st.columns(3)
        with q1: food_mode = st.button("🍽️ 我吃了什么？", use_container_width=True)
        with q2: exercise_mode = st.button("🏃 我运动多久？", use_container_width=True)
        with q3: ask_mode = st.button("💬 我想问健康", use_container_width=True)
        if food_mode: st.session_state.pet_mode = "food"
        elif exercise_mode: st.session_state.pet_mode = "exercise"
        elif ask_mode: st.session_state.pet_mode = "ask"
        mode = st.session_state.get("pet_mode", "ask")
        labels = {"food": "输入食物 + 食用量", "exercise": "输入运动 + 时长", "ask": "输入健康问题"}
        hints = {"food": "例如：苹果 1 个、米饭 1 碗、鸡蛋 2 个、牛奶 250ml", "exercise": "例如：快走 30 分钟、跳绳 15 分钟", "ask": "例如：晚餐怎么吃？最近总熬夜怎么办？"}
        prompt = st.text_input(labels[mode], placeholder=hints[mode], key="pet_single_input")
        if st.button("发送给轻盈仔 ✨", use_container_width=True, disabled=not prompt.strip()):
            if mode == "food":
                st.session_state.food_log.append(prompt.strip())
                st.session_state.pet_reply = food_feedback(prompt.strip(), latest)
            elif mode == "exercise":
                found = re.search(r"(\d+(?:\.\d+)?)", prompt)
                added = int(float(found.group(1))) if found else 0
                st.session_state.exercise_minutes += added
                st.session_state.pet_reply = f"我记下啦：{prompt.strip()}。今天累计运动 {st.session_state.exercise_minutes} 分钟。<br>🎯 每周可以逐步靠近 150–300 分钟，忙的时候分段完成也算数。"
            else:
                st.session_state.pet_reply = pet_reply(prompt.strip(), latest, st.session_state.food_log, st.session_state.exercise_minutes)
            st.rerun()
        if st.session_state.food_log:
            st.markdown("".join(f'<span class="food-chip">🍴 {item}</span>' for item in st.session_state.food_log[-6:]), unsafe_allow_html=True)
        st.markdown("#### 📊 轻盈仔的小图表")
        if st.session_state.records:
            pet_chart = pd.DataFrame(st.session_state.records)
            pet_chart["时间"] = pd.to_datetime(pet_chart["date"])
            st.line_chart(pet_chart.set_index("时间")["bmi"], color="#55a96f", height=180)
            st.caption(f"已记录 {len(st.session_state.records)} 次 BMI · 今日运动 {st.session_state.exercise_minutes} 分钟 · 已记录 {len(st.session_state.food_log)} 次饮食")
        else:
            st.info("完成第一次 BMI 测量后，这里会出现你的趋势图；先和轻盈仔说说今天吃了什么吧。")
        st.caption("食物请写清楚数量，例如克、毫升、个或碗；轻盈仔会结合 BMI 和记录给出份量建议。")


def classify(bmi):
    if bmi < 18.5:
        return "偏瘦", "🍃", "建议适当增加营养与优质蛋白，规律吃饭，慢慢把身体养回来。", "low"
    if bmi < 24:
        return "正常", "😊", "状态很棒！继续保持吃动平衡、规律作息，让好习惯成为你的超能力。", "good"
    if bmi < 28:
        return "超重", "🙂", "别着急，先从少一杯含糖饮料、多走十分钟开始，稳定的小改变最有力量。", "watch"
    return "肥胖", "💪", "建议温和、持续地管理体重；如有基础疾病或明显不适，请咨询医生或营养师。", "high"


def advice(level, gender):
    if level == "偏瘦":
        return [
            ("🥣 饮食核心", "🍚 三餐 + 1–2 次加餐，先把规律吃饭做起来。<br>🥚 每餐加入蛋、奶、鱼、肉、豆类中的 1–2 种优质蛋白。<br>🥜 加餐可选坚果、酸奶、香蕉、全麦面包；不要只靠奶茶和甜点增重。<br>📈 每周观察一次体重，缓慢增加比突然暴食更稳妥。"),
            ("🍱 一日餐盘", "🌞 早餐：牛奶 / 豆浆 + 鸡蛋 + 全麦主食。<br>☀️ 午餐：米饭 + 鱼肉或鸡肉 + 两份蔬菜。<br>🌙 晚餐：面 / 杂粮饭 + 豆腐或瘦肉 + 菌菇蔬菜。<br>🍎 加餐：酸奶、水果、坚果三选一，感觉饱胀就减少份量。"),
            ("🏋️ 运动方案", "💪 每周 2–3 次力量训练：深蹲、臀桥、俯卧撑、弹力带划船各 2–3 组。<br>🚶 搭配轻松有氧，每次 20–30 分钟。<br>🎯 重点是保留肌肉，不用用大量跑步抵消进食。<br>🩺 体重持续下降、乏力或食欲异常时请咨询医生。"),
            ("🌙 生活节奏", "⏰ 固定起床和入睡时间，争取 7–9 小时睡眠。<br>💧 白天分次饮水，避免用咖啡或能量饮料顶替正餐。<br>🧡 每天记录一次‘吃饭 / 精力 / 心情’，找到影响食欲的原因。"),
        ]
    return [
        ("🥗 饮食核心", "🍽️ 进餐顺序：蔬菜 → 蛋白质 → 主食，先吃慢吃，七八分饱即可。<br>🥬 每餐至少一半是蔬菜，优先深色叶菜、菌菇、番茄。<br>🥚 蛋白质选鱼虾、鸡蛋、瘦肉、豆制品和奶。<br>🚫 少吃油炸、含糖饮料、甜点和酒；盐尽量控制在每日 5g 内，烹调油约 25–30g。"),
        ("🍱 一日餐盘", "🌞 早餐：无糖奶 / 豆浆 + 鸡蛋 + 全麦面包。<br>☀️ 午餐：半盘蔬菜 + 一掌心蛋白质 + 半拳到一拳主食。<br>🌙 晚餐：清淡蛋白质 + 蔬菜 + 适量杂粮主食，睡前 2–3 小时尽量不再进食。<br>🍎 想吃零食时：先喝水，优先水果、原味坚果或无糖酸奶。"),
        ("🏃 运动方案", "🚶 每周累计 150–300 分钟中等强度运动：快走、游泳、骑车都可以。<br>💪 每周 2–3 天抗阻训练：深蹲、臀桥、哑铃推举、弹力带划船。<br>⏱️ 久坐每 60 分钟起身 3–5 分钟，接水、拉伸、走动都算。<br>🌱 先从每天 20 分钟开始，稳定两周后再增加时长。"),
        ("🧘 心理与作息", "🌙 目标是 7–9 小时睡眠，尽量固定入睡和起床时间。<br>📝 想吃东西时先问自己：我是饿了、累了，还是在焦虑？<br>🌬️ 情绪上来时先做 3 分钟深呼吸、散步或伸展，再决定要不要吃。<br>👏 关注一周趋势，不因某一顿饭或某一天的体重责怪自己。"),
    ]


def risk_page(level):
    if level == "偏瘦":
        return ("🌿 体重过低的照顾提醒", "体重过低可能与营养摄入不足、肌肉量下降或潜在健康问题有关。可以关注食欲、疲劳感和近期体重变化，采用少量多餐、增加优质蛋白的方式温和调整；若体重持续下降或伴随不适，请及时咨询医生。", "需要留意：持续下降、乏力、食欲明显变化")
    if level == "正常":
        return ("🌈 继续守护你的健康", "BMI 在正常范围并不等于所有健康指标都正常。建议继续关注血压、血糖和血脂，保持规律运动与作息，让好状态稳稳延续。", "建议关注：血压、血糖、血脂")
    if level == "超重":
        return ("🔎 超重阶段的风险参照", "超重可能增加高血压、血糖异常、血脂异常、脂肪肝等代谢问题的发生风险。越早从饮食、运动和睡眠做小调整，越容易把变化控制在可管理的范围内；这不是对个人疾病的诊断。", "建议留意：血压、空腹血糖、血脂")
        return ("🧡 肥胖阶段的风险参照", "肥胖与高血压、2 型糖尿病、血脂异常、脂肪肝及心脑血管疾病等风险增加有关。建议在专业人士指导下制定循序渐进的体重管理计划；如已有慢性病或明显不适，请优先就医。", "建议留意：血压、血糖、血脂、肝功能及睡眠情况")


def gauge_html(bmi, level, emoji):
    # 成人 BMI 展示区间为 15–35；分类仍严格使用中国成人 BMI 口径。
    pct = max(0.0, min(1.0, (bmi - 15) / 20))
    angle = -135 + 270 * pct
    return f'''<div class="gauge-card">
        <div class="gauge-title">你的 BMI 身体质量指数</div>
        <div class="gauge">
          <div class="gauge-arc"></div>
          <div class="gauge-pointer" style="transform:translateX(-50%) rotate({angle:.1f}deg)"></div>
          <div class="gauge-center"><div class="gauge-number">{bmi:.1f}</div><div class="gauge-sub">BMI&nbsp; <span class="gauge-tag">{emoji} {level}</span></div></div>
          <span class="gauge-label l1">18.5</span><span class="gauge-label l2">24</span><span class="gauge-label l3">28</span>
        </div>
        <div class="gauge-scale"><span>偏瘦</span><span>正常</span><span>超重</span><span>肥胖</span></div>
    </div>'''


def main():
    init_state()
    pet_panel()
    st.markdown('<div class="brand"><div class="brand-mark">🌿</div><div><h1>轻盈 BMI</h1><small>把健康，变成每天都做得到的小事</small></div></div>', unsafe_allow_html=True)

    st.markdown(f'''<div class="hero"><div class="hero-copy"><div class="eyebrow">HEALTHY HABITS · 健康习惯</div><h2>今天的你，<br>值得被好好照顾。</h2><p>从一次 BMI 查询开始，发现身体发来的小信号，给自己一份温柔又具体的行动计划。</p><span class="pill">✨ 记录每一次轻盈变化</span></div><img src="{ASSET_DATA}" /></div>''', unsafe_allow_html=True)

    tab_check, tab_profile, tab_guide = st.tabs(["🌱 开始测量", "📈 个人中心", "📚 官方健康建议"])
    with tab_check:
        st.markdown('<div class="section-title">先认识一下今天的你</div><div class="section-sub">选择性别后，我们会给你更贴合的健康建议。成人 BMI 参考适用于 18 岁及以上人群。</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.2, 1], gap="medium")
        with c1:
            selected_gender = st.radio("你的性别（点击图标即可选择）", ["🧒🏻 男生", "👧🏻 女生"], horizontal=True, label_visibility="visible")
            gender = selected_gender.split(" ", 1)[1]
        with c2:
            age = st.number_input("年龄", min_value=1, max_value=120, value=25, step=1)

        st.markdown("#### 📏 输入身体数据")
        i1, i2 = st.columns(2)
        with i1:
            height = st.number_input("身高（米）｜例如：1.70", min_value=0.5, max_value=2.5, value=1.70, step=0.01, format="%.2f", help="请用米填写：170 厘米 = 1.70 米")
        with i2:
            weight = st.number_input("体重（千克）｜例如：60.0", min_value=10.0, max_value=300.0, value=60.0, step=0.1, format="%.1f", help="请用千克填写：60 斤约等于 30 千克")

        if st.button("✨ 查看我的 BMI", use_container_width=True):
            bmi = weight / (height ** 2)
            level, emoji, tip, tone = classify(bmi)
            previous = st.session_state.records[-1] if st.session_state.records else None
            delta = None if previous is None else bmi - previous["bmi"]
            st.session_state.current = {"bmi": bmi, "weight": weight, "level": level, "emoji": emoji, "tip": tip, "gender": gender, "age": age, "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
            st.session_state.records.append(st.session_state.current.copy())
            st.session_state.delta = delta

        if "current" in st.session_state:
            r = st.session_state.current
            delta = st.session_state.get("delta")
            left, right = st.columns([1.2, 1], gap="large")
            with left:
                st.markdown(gauge_html(r["bmi"], r["level"], r["emoji"]), unsafe_allow_html=True)
                st.markdown(f'<div class="result-box" style="margin-top:12px"><div class="label">轻盈小提醒</div><p style="margin:8px 0 0;opacity:.95;line-height:1.7">{r["tip"]}</p></div>', unsafe_allow_html=True)
                low_w, high_w = 18.5 * height ** 2, 23.9 * height ** 2
                a, b, c = st.columns(3)
                a.metric("健康体重下限", f"{low_w:.1f} kg")
                b.metric("健康体重上限", f"{high_w:.1f} kg")
                c.metric("本次体重", f"{weight:.1f} kg")
                st.caption("按中国成人 BMI 18.5–23.9 的参考区间换算；不适用于未成年人、孕期及特殊人群。")
            with right:
                st.markdown("#### 🧭 你的健康坐标")
                st.progress(min(r["bmi"] / 40, 1.0))
                st.caption("偏瘦 18.5　　正常 24　　超重 28　　肥胖")
                st.markdown('<div class="tip">BMI 是筛查参考，不是疾病诊断。建议结合血压、血糖、血脂、睡眠和日常精力综合观察。</div>', unsafe_allow_html=True)
                if delta is not None:
                    if delta < -0.1:
                        st.success(f"👍 比上一次下降 {abs(delta):.1f}，你的坚持正在发生变化！")
                    elif delta > 0.1:
                        st.info(f"🌤️ 比上一次上升 {delta:.1f}，别责怪自己，看看近期作息和饮食即可。")
                    else:
                        st.info("🌼 和上次差不多，稳定也是一种进步。")

            st.markdown("#### ✉️ 你的专属健康手册已送达")
            with st.expander("📨 点击打开专属健康手册 · 查看你的行动方案", expanded=True):
                st.markdown('<div class="envelope">💌 你的专属健康手册到了！<br><span style="font-size:12px;font-weight:500">点击上方绿色标题，逐页查看饮食、运动、作息和风险参照</span></div>', unsafe_allow_html=True)
                handbook = advice(r["level"], r["gender"])
                risk_title, risk_text, risk_watch = risk_page(r["level"])
                pages = [(title, text) for title, text in handbook] + [(risk_title, risk_text)]
                page_names = [f"第 {i + 1} 页 · {title.split(' ', 1)[-1]}" for i, (title, _) in enumerate(pages)]
                selected_page = st.radio("手册分页", page_names, horizontal=True, label_visibility="collapsed")
                page_index = page_names.index(selected_page)
                page_title, page_text = pages[page_index]
                st.markdown(f"### {page_title}")
                st.markdown(f'<div class="tip" style="font-size:15px;line-height:2">{page_text}</div>', unsafe_allow_html=True)
                if page_index == len(pages) - 1:
                    st.info(f"🩺 {risk_watch}\n\n以上是风险参照，不代表你已经患有相关疾病。")
                st.caption(f"{page_index + 1} / {len(pages)}　·　左右选择上方分页，逐页阅读你的行动建议")
                st.warning("⚠️ 以上是成人健康管理参考。孕期、未成年人、运动员或有慢性病者，请遵循专业人士建议。")

    with tab_profile:
        st.markdown('<div class="section-title">你的身体变化日记</div><div class="section-sub">每次测量都会留下一个小脚印，关注趋势，比盯着某一个数字更重要。</div>', unsafe_allow_html=True)
        records = st.session_state.records
        if not records:
            st.markdown('<div class="card history-empty">🌱 还没有测量记录<br><span class="metric-note">完成第一次测量后，这里会出现你的 BMI 趋势折线和鼓励徽章。</span></div>', unsafe_allow_html=True)
        else:
            df = pd.DataFrame(records)
            df["时间"] = pd.to_datetime(df["date"])
            f1, f2, f3, f4 = st.columns(4)
            with f1: view = st.radio("查看范围", ["最近", "今年", "近半年", "全部"], horizontal=True, label_visibility="collapsed")
            with f2: chart_metric = st.radio("指标", ["BMI", "体重"], horizontal=True, label_visibility="collapsed")
            if view == "今年": chart_df = df[df["时间"].dt.year == datetime.now().year]
            elif view == "近半年": chart_df = df[df["时间"] >= datetime.now() - timedelta(days=183)]
            elif view == "最近": chart_df = df.tail(8)
            else: chart_df = df
            if chart_df.empty: chart_df = df.tail(1)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            metric_key = {"BMI": "bmi", "体重": "weight"}[chart_metric]
            metric_data = chart_df.dropna(subset=[metric_key]).set_index("时间")[metric_key]
            st.line_chart(metric_data, color="#6958d8", height=300)
            mn, mx = chart_df[metric_key].min(), chart_df[metric_key].max()
            m1, m2, m3 = st.columns(3)
            unit = "" if chart_metric == "BMI" else " kg"
            m1.metric(f"最低 {chart_metric}", f"{mn:.1f}{unit}")
            m2.metric(f"最高 {chart_metric}", f"{mx:.1f}{unit}")
            m3.metric("测量次数", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("#### 🧡 最近记录")
            for idx, row in df.iloc[::-1].head(10).iterrows():
                prev = df.iloc[idx-1]["bmi"] if idx > 0 else None
                badge = "👍" if prev is not None and row["bmi"] < prev - .1 else ""
                st.markdown(f'<div class="card" style="padding:14px 18px;margin:8px 0"><b>{row["emoji"]} {row["level"]}</b>　BMI <b>{row["bmi"]:.1f}</b>　<span class="metric-note">{row["date"]} · {row["gender"]}</span> <span style="float:right;font-size:20px">{badge}</span></div>', unsafe_allow_html=True)
            if st.button("清空本地记录"):
                st.session_state.records = []
                st.rerun()

    with tab_guide:
        st.markdown('<div class="section-title">官方健康建议</div><div class="section-sub">把可靠的知识，变成今天就能做到的选择。</div>', unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown('<div class="card"><div style="font-size:30px">🥗</div><b>平衡膳食</b><p class="metric-note">食物多样、规律三餐，少油少盐，优先选择蔬菜、全谷物、奶豆和优质蛋白。</p><a href="https://www.nhc.gov.cn/wjw/c100378/202412/f3f58b54fbeb4c87b14164fac898bf08/files/1736390749000_59785.pdf" target="_blank">查看国家卫健委体重管理规范化流程 ↗</a></div>', unsafe_allow_html=True)
        with g2:
            st.markdown('<div class="card"><div style="font-size:30px">🚶</div><b>动起来</b><p class="metric-note">逐步达到每周 150–300 分钟中等强度身体活动，并加入抗阻训练。</p><a href="https://www.nhc.gov.cn/wjw/c100175/202005/7757e4f72e13402a97b42f785d7a335a.shtml" target="_blank">查看国家卫健委膳食与运动建议 ↗</a></div>', unsafe_allow_html=True)
        with g3:
            st.markdown('<div class="card"><div style="font-size:30px">😴</div><b>睡眠与压力</b><p class="metric-note">保持规律作息，减少情绪化进食，用散步、冥想或瑜伽给自己一点缓冲。</p><a href="https://www.nhc.gov.cn/cms-search/downFiles/5e20de34c0fe45bb9fcac0636b21ad98.pdf" target="_blank">查看居民体重管理核心知识 ↗</a></div>', unsafe_allow_html=True)
        st.caption("口径参考：国家卫生健康委《体重管理指导原则（2024年版）》、居民体重管理核心知识（2024年版）。本工具仅供健康管理参考。")


if __name__ == "__main__":
    main()
