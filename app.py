import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
from ai_engine import analyze_message, get_friendly_error

st.set_page_config(
    page_title="好好说 - 高情商家校沟通助手",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 注入治愈系风格及全新升级组件的 CSS（包含彻底隐藏 Streamlit 官方黑边与水印）
st.markdown("""
<style>
    /* 1. 彻底隐藏 Streamlit 官方顶部黑栏与右下角管理图标 */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    [data-testid="stStatusWidget"], #stDecoration, .stAppViewer, div[data-testid="stToolbar"] {
        display: none !important;
    }

    /* 2. 主页面背景与字体设置 */
    .stApp {
        background-color: #FBF9F2 !important;
        font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
        color: #2C3E50 !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .app-header {
        text-align: center;
        padding: 15px 0 10px 0;
    }
    .app-title {
        color: #2E4A3B;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .app-subtitle {
        color: #7F8C8D;
        font-size: 14px;
        margin-top: 4px;
    }
    
    .stTextArea label, .stTextInput label, .stSelectbox label {
        color: #2C3E50 !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }

    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #2C3E50 !important;
        border: 1px solid #EAE8E0 !important;
        border-radius: 12px !important;
        font-size: 15px !important;
    }
    
    div.stButton > button {
        background-color: #94C668 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border-radius: 25px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 12px rgba(148, 198, 104, 0.3) !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #82B555 !important;
        transform: translateY(-1px);
    }

    button[data-baseweb="tab"] {
        color: #7F8C8D !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        background-color: transparent !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2E4A3B !important;
        font-weight: 800 !important;
        border-bottom-color: #94C668 !important;
        border-bottom-width: 3px !important;
    }

    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #EAE8E0 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        margin-bottom: 12px;
    }
    [data-testid="stExpander"] summary {
        background-color: #FFFFFF !important;
        color: #2C3E50 !important;
        border-radius: 14px !important;
    }
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary div {
        color: #2C3E50 !important;
        font-weight: 700 !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: #FFFFFF !important;
        color: #34495E !important;
        border-top: 1px solid #F0EFE9;
        border-bottom-left-radius: 14px;
        border-bottom-right-radius: 14px;
        padding: 16px !important;
    }

    .stAlert {
        background-color: #FFFDF0 !important;
        border: 1px solid #F5E6A3 !important;
        border-radius: 14px !important;
    }
    .stAlert p {
        color: #8A6D3B !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }
    
    .chat-timestamp { font-size: 11px; color: #95A5A6; margin-bottom: 4px; }
    .chat-bubble-teacher {
        background-color: #FFFFFF;
        border-left: 5px solid #70A1FF;
        padding: 14px 18px; border-radius: 16px; margin-bottom: 12px;
        font-size: 15px; color: #2C3E50; box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .chat-bubble-parent {
        background-color: #F0F9EB;
        border-left: 5px solid #94C668;
        padding: 14px 18px; border-radius: 16px; margin-bottom: 12px;
        font-size: 15px; color: #2C3E50; box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .reply-card-box {
        background-color: #FBFDF9;
        border: 1.5px solid #D6E8C5;
        padding: 18px; border-radius: 16px; margin-bottom: 12px;
        font-size: 16px; font-weight: 600; color: #2C3E50 !important;
        line-height: 1.6;
        box-shadow: 0 4px 12px rgba(148, 198, 104, 0.08);
    }
    .psychology-box {
        background-color: #FFFDF4;
        border: 1px dashed #F3E5AB;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 14px;
        font-size: 14px;
        color: #8C6D1F;
    }
    .risk-alert-box {
        background-color: #FFF5F5;
        border: 1px solid #FEB2B2;
        padding: 14px 16px;
        border-radius: 14px;
        margin-bottom: 16px;
        color: #C53030;
        font-size: 14px;
        font-weight: 600;
    }
    .wx-tip-bar {
        background-color: #E6F9EE;
        color: #065F2C;
        padding: 10px 14px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 14px;
        text-align: center;
    }
    .tag-badge {
        background-color: #E2E8F0;
        color: #475569;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        margin-left: 6px;
    }
</style>
""", unsafe_allow_html=True)

def render_mobile_copy_button(text_to_copy: str, button_text: str = "📋 一键复制到微信", key: str = "copy_btn"):
    escaped_text = text_to_copy.replace("\\", "\\\\").replace("`", "\\`").replace('"', '\\"').replace("\n", "\\n")
    html_code = f"""
    <div style="margin: 8px 0 16px 0;">
        <button id="btn_{key}" onclick="copyText_{key}()" style="
            background-color: #94C668; color: white; border: none; padding: 12px 16px; 
            font-size: 15px; border-radius: 25px; cursor: pointer; font-weight: 700;
            box-shadow: 0 4px 12px rgba(148, 198, 104, 0.3); width: 100%;
        ">{button_text}</button>
        <div id="tip_{key}" style="color: #94C668; font-size: 13px; text-align: center; margin-top: 6px; display: none; font-weight: 700;">
            ✅ 已成功复制，可直接切换到微信粘贴发给老师
        </div>
    </div>
    <script>
    function copyText_{key}() {{
        const text = `{escaped_text}`;
        navigator.clipboard.writeText(text).then(function() {{
            const tip = document.getElementById('tip_{key}');
            tip.style.display = 'block';
            setTimeout(function() {{ tip.style.display = 'none'; }}, 2500);
        }}).catch(function(err) {{ alert('复制失败，请手动长按复制。'); }});
    }}
    </script>
    """
    components.html(html_code, height=65)

st.markdown("""
<div class='app-header'>
    <div class='app-title'>🌿 好好说</div>
    <div class='app-subtitle'>高情商家校沟通助手</div>
</div>
""", unsafe_allow_html=True)

# 初始化 Session State
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "parent_reply_recorded" not in st.session_state:
    st.session_state.parent_reply_recorded = False
if "run_mode" not in st.session_state:
    st.session_state.run_mode = "真实 AI 模式"
if "draft_teacher_msg" not in st.session_state:
    st.session_state.draft_teacher_msg = ""
if "refine_mode" not in st.session_state:
    st.session_state.refine_mode = "正常"


# ==================== 后台管理（侧边栏隔离） ====================
with st.sidebar:
    st.markdown("### ⚙️ 后台系统设置")
    run_mode_choice = st.radio(
        "选择运行模式",
        ["真实 AI 模式", "本地模拟模式"],
        index=0 if st.session_state.run_mode == "真实 AI 模式" else 1
    )
    if run_mode_choice != st.session_state.run_mode:
        st.session_state.run_mode = run_mode_choice
        st.success(f"已切换为：{run_mode_choice}")

    st.divider()
    st.markdown("### 💾 数据备份与恢复")
    if st.session_state.conversation_history:
        backup_data = json.dumps(st.session_state.conversation_history, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 下载 JSON 备份文件",
            data=backup_data,
            file_name=f"家校沟通备份_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    if st.button("🔄 清空当前对话历史", use_container_width=True):
        st.session_state.conversation_history = []
        if "analysis_result" in st.session_state:
            del st.session_state.analysis_result
        st.session_state.parent_reply_recorded = False
        st.session_state.refine_mode = "正常"
        st.success("已成功清空所有对话历史。")
        st.rerun()


# ==================== 家校沟通前台（主界面） ====================

# 微信端提示条
st.markdown("""
<div class='wx-tip-bar'>
    💬 提示：点击复制后，可直接粘贴至微信发给老师，沟通更顺畅。
</div>
""", unsafe_allow_html=True)

# 带情境标签的历史对话展示
if st.session_state.conversation_history:
    st.markdown("### 💬 历史对话脉络")
    for chat in st.session_state.conversation_history:
        role_name = "👩‍🏫 老师" if chat["role"] == "teacher" else "🧑‍🦰 我（家长）"
        bubble_class = "chat-bubble-teacher" if chat["role"] == "teacher" else "chat-bubble-parent"
        time_str = chat.get("timestamp", "")
        tag_name = chat.get("tag", "日常沟通")
        st.markdown(f"""
        <div class='{bubble_class}'>
            <div class='chat-timestamp'>⏰ {time_str} <span class='tag-badge'>#{tag_name}</span></div>
            <strong>{role_name}：</strong>{chat['content']}
        </div>
        """, unsafe_allow_html=True)
    st.divider()

is_first_turn = len(st.session_state.conversation_history) == 0

if is_first_turn:
    st.markdown("##### 💡 常见老师消息快捷填入（可选）")
    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        if st.button("📝 上课走神", use_container_width=True):
            st.session_state.draft_teacher_msg = "今天孩子上课注意力不太集中，提醒了几次，希望家长在家也关注一下。"
            st.rerun()
    with col_q2:
        if st.button("✍️ 作业潦草", use_container_width=True):
            st.session_state.draft_teacher_msg = "最近作业完成得比较敷衍，字迹潦草，希望家长多盯一下签字。"
            st.rerun()
    with col_q3:
        if st.button("🌟 表现表扬", use_container_width=True):
            st.session_state.draft_teacher_msg = "今天课堂上表现特别积极，进步很大，特此表扬！"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("第一步：输入沟通内容")
    
    input_teacher_message = st.text_area(
        "老师发来的消息", 
        value=st.session_state.draft_teacher_msg, 
        placeholder="请粘贴老师发来的微信消息……", 
        height=100
    )
    st.session_state.draft_teacher_msg = input_teacher_message

    parent_position = st.text_area("家长自己的想法（选填）", placeholder="例如：我想表达配合，但也想顺便问下孩子在学校的状态。", height=65)
    context = st.text_area("补充背景（选填）", placeholder="例如：孩子四年级，最近比较贪玩。", height=60)
else:
    st.subheader(f"🔄 继续分析（第 {len(st.session_state.conversation_history)//2 + 1} 轮）")
    input_teacher_message = st.text_area("老师接下来的最新回复", placeholder="把老师新发来的消息粘贴在这里……", height=100)
    parent_position = ""
    context = ""

analyze_btn_text = "🚀 开始首轮分析" if is_first_turn else "💡 结合前文分析最新回复"
if st.button(analyze_btn_text, type="primary", use_container_width=True):
    if not input_teacher_message.strip():
        st.warning("请先输入老师的消息。")
    else:
        with st.spinner("正在结合上下文分析，生成口语化回复……"):
            if st.session_state.run_mode == "本地模拟模式":
                result = {
                    "teacher_analysis": {
                        "surface_meaning": "老师接收到了上轮反馈，并提出了下一步跟进要求。",
                        "message_categories": ["沟通跟进", "行为反馈"],
                        "issue_points": [{
                            "topic": "沟通跟进",
                            "teacher_feedback": input_teacher_message.strip(),
                            "information_type": "后续跟进事项",
                            "evidence": input_teacher_message.strip(),
                            "unknowns": []
                        }],
                        "facts": ["老师作出了后续回应。"],
                        "teacher_evaluations": [],
                        "explicit_request": "请配合后续安排",
                        "possible_intentions": ["希望保持沟通一致性"],
                        "unknowns": [],
                        "risk_level": "普通"
                    },
                    "communication_strategy": {
                        "strategy": "cooperate",
                        "reason": "多轮沟通中先保持回应的连贯性与礼貌。",
                        "suggestion": "确认接收信息并给予明确反馈。"
                    },
                    "replies": {
                        "natural": "好嘞老师！收到您的提醒啦，今晚回去我好好跟他聊聊，辛苦您费心啦！",
                        "rational": "好的老师，收到。那请问他今天是哪个环节没听懂呀？我们在家好针对性辅导一下。",
                        "principled": "好的老师，感谢您关注。这事儿我先跟孩子了解下情况哈，晚点再给您反馈。"
                    }
                }
            else:
                try:
                    result = analyze_message(
                        teacher_message=input_teacher_message,
                        parent_position=parent_position,
                        context=context,
                        conversation_history=st.session_state.conversation_history
                    )
                except Exception as e:
                    import traceback
                    st.error(get_friendly_error(str(e)))
                    with st.expander("开发调试信息"):
                        st.code(traceback.format_exc())
                    st.stop()

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        current_msg = input_teacher_message.strip()
        
        # 自动提取分类作为情境标签
        cats = result.get("teacher_analysis", {}).get("message_categories", ["日常沟通"])
        chat_tag = cats[0] if cats else "日常沟通"

        if not st.session_state.conversation_history or st.session_state.conversation_history[-1].get("content") != current_msg:
            st.session_state.conversation_history.append({
                "role": "teacher",
                "content": current_msg,
                "timestamp": now_str,
                "tag": chat_tag
            })

        st.session_state.analysis_result = result
        st.session_state.parent_reply_recorded = False
        st.session_state.draft_teacher_msg = ""
        st.session_state.refine_mode = "正常"
        st.rerun()

# 展示分析结果
if "analysis_result" in st.session_state:
    result = st.session_state.analysis_result
    st.divider()
    st.subheader("第二步：沟通分析与回复方案")

    # 智能沟通雷达与风险预警
    risk_lvl = result["teacher_analysis"].get("risk_level", "普通")
    if risk_lvl in ["较高", "紧急", "严重"]:
        st.markdown(f"""
        <div class='risk-alert-box'>
            ⚠️ <b>沟通雷达预警：</b> 当前老师的消息情绪或要求较严格（风险评估：{risk_lvl}）。建议采用柔性承接、避免文字误会，必要时可约线下沟通。
        </div>
        """, unsafe_allow_html=True)

    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["💬 最新回复方案", "🔍 老师意图剖析", "⚖️ 沟通策略建议"])

    with sub_tab1:
        replies = result["replies"]
        
        # 一键语气微调按钮组
        st.markdown("##### 🪄 一键调整回复风格")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            if st.button("🌱 正常语气", use_container_width=True):
                st.session_state.refine_mode = "正常"
                st.rerun()
        with col_m2:
            if st.button("💬 更口语化", use_container_width=True):
                st.session_state.refine_mode = "口语"
                st.rerun()
        with col_m3:
            if st.button("✂️ 更简短精炼", use_container_width=True):
                st.session_state.refine_mode = "简短"
                st.rerun()

        # 动态切换风格文本
        nat_text = replies.get('natural', '')
        rat_text = replies.get('rational', '')
        pri_text = replies.get('principled', '')

        if st.session_state.refine_mode == "口语":
            nat_text = "哎呀老师，真不好意思！" + nat_text
            rat_text = "老师您好，想跟您确认下：" + rat_text
            pri_text = "老师，这事儿我了解下哈：" + pri_text
        elif st.session_state.refine_mode == "简短":
            nat_text = "收到老师！今晚一定督促他改好。"
            rat_text = "收到，请问具体是哪个环节呢？"
            pri_text = "感谢老师提醒，我先核实下情况。"

        st.markdown(f"""
        <div class='psychology-box'>
            💡 <b>老师这段话的言外之意：</b><br>
            {result['teacher_analysis'].get('surface_meaning', '希望家长能共同配合引导孩子')}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"#### 🍃 方案一：自然得体 【当前风格：{st.session_state.refine_mode}】")
        st.markdown(f"<div class='reply-card-box'>{nat_text}</div>", unsafe_allow_html=True)
        render_mobile_copy_button(nat_text, "📋 复制【自然得体】", "btn_natural")

        st.markdown("#### 🔍 方案二：理性询问")
        st.markdown(f"<div class='reply-card-box'>{rat_text}</div>", unsafe_allow_html=True)
        render_mobile_copy_button(rat_text, "📋 复制【理性询问】", "btn_rational")

        st.markdown("#### ⚖️ 方案三：有原则表达")
        st.markdown(f"<div class='reply-card-box'>{pri_text}</div>", unsafe_allow_html=True)
        render_mobile_copy_button(pri_text, "📋 复制【有原则表达】", "btn_principled")

        st.divider()
        st.markdown("#### ✏️ 确定最终发送给老师的回复")
        reply_options = {
            "自然得体": nat_text,
            "理性询问": rat_text,
            "有原则表达": pri_text,
            "自己编辑": nat_text
        }
        selected_reply = st.selectbox("选择或微调方案", options=list(reply_options.keys()))
        draft = st.text_area("实际发送内容", value=reply_options[selected_reply], height=95)

        if draft.strip():
            render_mobile_copy_button(draft.strip(), "🟢 一键复制自定义内容", "btn_custom_draft")

        if st.button("📌 确认已发送，存入历史记录", type="primary", disabled=st.session_state.parent_reply_recorded, use_container_width=True):
            if not draft.strip():
                st.warning("请先填写发送内容。")
            else:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.conversation_history.append({
                    "role": "parent",
                    "content": draft.strip(),
                    "timestamp": now_str,
                    "tag": "家长回复"
                })
                st.session_state.parent_reply_recorded = True
                st.success("✅ 已存入沟通历史！")
                st.rerun()

    with sub_tab2:
        analysis = result["teacher_analysis"]
        st.markdown("### 老师这段话的深度剖析")
        with st.expander("① 消息类型与表面意思", expanded=True):
            st.write("分类：", ", ".join(analysis.get("message_categories", [])))
            st.write("表面意思：", analysis.get("surface_meaning", ""))
        with st.expander("② 老师反馈的具体问题", expanded=False):
            for i, issue in enumerate(analysis.get("issue_points", []), 1):
                st.markdown(f"**问题 {i}：{issue.get('topic')}**")
                st.write("反馈：", issue.get("teacher_feedback"))
        with st.expander("③ 要求与风险评估", expanded=False):
            st.write("明确要求：", analysis.get("explicit_request"))
            st.info(f"风险等级：{analysis.get('risk_level', '普通')}")

    with sub_tab3:
        strategy = result["communication_strategy"]
        st.markdown("### 建议沟通策略")
        strategy_names = {
            "cooperate": "配合沟通", "clarify": "先询问核实", "correct": "澄清事实",
            "disagree": "理性表达不同意见", "protect": "优先保护孩子权益", "normal": "普通沟通"
        }
        st.success(strategy_names.get(strategy.get("strategy"), "普通沟通"))
        st.markdown("#### 为什么这样建议")
        st.write(strategy.get("reason", ""))
        st.markdown("#### 具体建议")
        st.write(strategy.get("suggestion", ""))
