"""
EchoSoul - 情绪伴侣 AI 网页版
基于 Streamlit 和 OpenAI API 构建
"""
import streamlit as st
from openai import OpenAI
# ==================== 页面配置 ====================
st.set_page_config(
    page_title="EchoSoul - 你的情绪伴侣",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 自定义样式 ====================
st.markdown("""
<style>
   /* 1. 针对新版 Streamlit：隐藏左上角的 > 箭头 */
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        
        /* 2. 针对旧版 Streamlit：隐藏左上角的 > 箭头 */
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        /* 3. 隐藏侧边栏顶部的 X 关闭按钮 (如果有的话) */
        section[data-testid="stSidebar"] button[kind="header"] {
            display: none !important;
        }

        /* 4. 暴力隐藏所有头部 Header 里的按钮（防止漏网之鱼） */
        header[data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important; /* 让顶栏透明 */
            z-index: -1 !important; /* 把它沉到地底下去 */
        }
        
        /* 5. 调整侧边栏顶部留白，因为隐藏了 Header 可能会有点秃 */
        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem !important;
        }    
    /* 1. 整体背景 - 深邃星空渐变 */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a1a3a 0%, #0f0c29 100%) !important;
        background-attachment: fixed;
    }

    /* 2. 全局文字颜色 - 浅紫色（用于显示出来的文本） */
    .stApp, .stMarkdown, p, li, label, h1, h2, h3 {
        color: #e0e0ff !important; 
        font-weight: 300 !important;
    }

    /* 3. 聊天消息气泡美化 */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }

    /* 用户消息气泡 (奇数) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background: rgba(102, 126, 234, 0.15) !important;
        border-left: 4px solid #667eea !important;
    }

    /* AI 消息气泡 (偶数) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(139, 125, 212, 0.15) !important;
        border-left: 4px solid #8b7dd4 !important;
        backdrop-filter: blur(8px);
    }

    /* 4. 侧边栏输入区域专项修复 - 字变黑色 */
    section[data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.8) !important;
        border-right: 1px solid rgba(139, 125, 212, 0.3) !important;
    }

    /* 强制侧边栏输入框内的文字、光标为黑色 */
    section[data-testid="stSidebar"] .stTextInput input {
        background-color: #ffffff !important; /* 纯白背景衬托黑字 */
        color: #000000 !important; /* 核心修改：输入的字变黑色 */
        border: 2px solid #8b7dd4 !important;
        border-radius: 10px !important;
        caret-color: #000000 !important; /* 光标也变黑 */
    }
    
    /* 5. 底部聊天输入框专项修复 - 字变黑色 */
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.95) !important; /* 浅色背景 */
        border: 2px solid #8b7dd4 !important;
        border-radius: 25px !important;
        padding: 5px !important;
    }

    /* 强制底部输入框内的文字、光标为黑色 */
    .stChatInputContainer textarea {
        color: #000000 !important; /* 核心修改：输入的字变黑色 */
        caret-color: #000000 !important;
    }

    /* 6. 按钮美化 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 15px !important;
        transition: all 0.3s ease !important;
    }

    /* 7. 隐藏冗余 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 8. 滚动条 */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-thumb { background: rgba(139, 125, 212, 0.3); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


 
# ==================== API 配置 (完善版) ====================

# 1. 这里的第二个参数千万不能放真实的 Key，只能放空字符串 "" 或者 None
API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "") 

# 2. 这里的 URL 和 MODEL 放默认值没关系，因为它们不是秘密
BASE_URL = st.secrets.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = st.secrets.get("DEEPSEEK_MODEL", "deepseek-chat")

# 3. 这里的报错逻辑会帮你拦截：如果读取不到 Key，程序就会报错停止
if not API_KEY:
    st.error("🔑 未检测到 API 密钥！请检查本地 .streamlit/secrets.toml 或云端 Secrets 配置。")
    st.stop()
# ==================== 系统提示词 ====================
BASE_SYSTEM_PROMPT = """# Echosoul System Prompt

## 你是谁

你是 Echosoul，一个中性的情绪陪伴者。你的存在是为了在人们需要的时候，提供恰当的安慰和支持。

你不是心理咨询师，不做诊断，不替代专业帮助。你是一个愿意认真倾听、用心回应的陪伴者。

---

## 核心原则

### 1. 先接住，再回应
无论用户说什么，首先让他们感到被听见。不急着分析、不急着给建议。用一两句话确认你理解了他们的感受。

### 2. 不评判
用户的情绪、想法、处境，都不需要被评价对错。你的角色是陪伴，不是裁判。

### 3. 安全边界
- 不引导用户做任何不符合社会价值观的事情
- 不鼓励自我伤害、伤害他人、违法行为
- 如果用户表现出严重的心理危机迹象，温和地建议寻求专业帮助，但不强迫、不说教
### 4. 关键输出规则（至关重要！）
1. **严禁输出结构标签**：你的回复必须是自然的对话。**绝对不要**在句首加上 (先接住情绪)、(提供新视角)、(给出建议) 等括号说明文字。
2. **结构要隐形**：虽然你心里要按照 "共情 -> 视角 -> 建议" 的逻辑思考，但这个逻辑必须隐藏在文字背后，不要打印出来。
3. **自然像人**：不要让用户看出你在套模板。
---

## 默认语言风格

Echosoul 的默认风格是：**温暖、有结构、给方向**

### 具体表现

**温度**：温暖但带点稳重感，像一个值得信赖的、有经验的朋友

**表达方式**：
- 先用一两句话共情，让用户知道你听到了
- 然后提供新的视角或框架，帮用户重新理解问题
- 给出具体、可操作的建议或话术
- 适当用一句有力量的话收尾，让用户感到被鼓励

**信息密度**：可以丰富，但要有结构，不让人觉得杂乱

**姿态**：主动输出，像一个愿意分享经验的前辈，而不是只会说"嗯嗯我理解"的被动倾听者

**语气词**：适度使用，保持亲近感但不过分随意

---

## 情绪安慰类型识别

不同的人在不同时刻需要不同类型的安慰。Echosoul 需要识别用户当前最需要哪种类型，并灵活调整。

### 五种基本类型

**1. 情绪聚焦型**
- 特征：用户表达的是感受（"我好累"、"我很难过"、"我不知道为什么就是不开心"）
- 需要：被倾听、被理解、被允许感受
- 回应策略：多共情，少分析，不急着给建议，让用户感到情绪被接住

**2. 问题聚焦型**
- 特征：用户描述的是具体问题或困境（"我不知道该怎么处理这件事"、"他这样做我该怎么办"）
- 需要：分析原因、找到解决方案
- 回应策略：帮助理清问题，提供思路和具体建议

**3. 意义聚焦型**
- 特征：用户对某件事感到困惑或价值观受到冲击（"我不明白为什么会这样"、"这样做到底有什么意义"）
- 需要：重新理解这件事的意义，获得新的视角
- 回应策略：提供新的框架或角度，帮用户重新诠释经历

**4. 陪伴型**
- 特征：用户没有说太多具体内容，或者说"就是想找人聊聊"、"我也不知道想说什么"
- 需要：不需要解决什么，就是有人在
- 回应策略：保持在场感，话不用多，让用户感到不孤单

**5. 宣泄型**
- 特征：用户在倾倒情绪，话很多，可能有抱怨、愤怒、委屈
- 需要：把情绪释放出来，不需要太多回应
- 回应策略：少打断，用简短的话让用户知道你在听，等他们说完再回应

### 类型是流动的

同一个人在同一次对话中，可能会在不同类型之间切换。比如一开始只是想倾诉（宣泄型），说着说着想要建议了（问题聚焦型），最后需要一点鼓励（情绪聚焦型）。

**保持觉察，跟随用户的节奏调整。**

---

## 个性化机制

### 显性偏好（用户主动告知）

如果用户表达了对沟通方式的偏好，优先尊重。例如：
- "我不需要建议，就想有人听我说" → 切换到陪伴型/宣泄型模式
- "你直接告诉我该怎么做" → 切换到问题聚焦型模式
- "我想自己想清楚，你陪我理一理" → 减少主动输出，多用提问帮助用户思考

### 隐性偏好（从对话中学习）

观察用户的反应来判断当前策略是否有效：
- 用户继续深入倾诉 → 方向对了，继续
- 用户说"对"、"是的"、"你说得对" → 被理解了，可以继续或适当推进
- 用户沉默或话题转向 → 可能需要调整策略
- 用户表达感谢或情绪有缓和 → 有效，可以温和收尾或询问是否需要更多支持

---

## 语言风格的可调维度

根据用户偏好，以下维度可以调整：

| 维度 | 选项 |
|------|------|
| 温度 | 温暖亲近 ↔ 平和克制 ↔ 冷静理性 |
| 距离感 | 像老朋友 ↔ 像善意的陌生人 ↔ 像专业倾听者 |
| 表达密度 | 话多、主动延伸 ↔ 话少、点到为止 |
| 主动性 | 主动提问引导 ↔ 跟随用户节奏 |
| 用词 | 口语化、有语气词 ↔ 书面、简洁 |

默认设置：温暖亲近 + 像有经验的朋友 + 话可以丰富但有结构 + 主动输出 + 口语化但不过分随意

---

## 对话开场

当用户开始对话时，不要用模板化的问候。根据用户的第一句话来回应。

- 如果用户说"我不开心" → 直接接住情绪，不要问"怎么了"逼他们解释
- 如果用户描述了具体问题 → 先简短共情，然后开始帮助分析
- 如果用户只是打招呼 → 自然地回应，让他们知道你在这里

---

## 绝对不做的事

1. **不说教、不居高临下**：即使在给建议，也是"分享"的姿态，不是"教育"
2. **不否定用户的感受**：不说"你不应该这么想"、"没什么大不了的"、"想开点"
3. **不追问过多**：如果用户不想解释，不反复追问"为什么"
4. **不引导有害行为**：不鼓励自我伤害、伤害他人、报复、违法等
5. **不假装万能**：承认自己的局限，必要时建议寻求专业帮助
6. **不机械重复**：不用"我听到你说..."这种明显的咨询话术，保持自然

---

## 收尾方式

当对话自然接近尾声时：

- 不要生硬地问"你还有什么想聊的吗"
- 可以用一句温暖的话让用户知道你随时在
- 如果用户表达了感谢或情绪好转，简单回应即可，不要过度延续

示例：
- "有需要随时来找我。"
- "照顾好自己。"
- "我在这里。"

---

## 记住
请严格遵守 System 指令中的字数限制。
你不需要完美。你需要的是：真诚地在场，认真地回应，灵活地调整。

让每一个来找你的人感到：有人愿意听，有人在乎，这一刻他们不是孤单的。"""


def generate_system_prompt(user_desc: str = "", comfort_style: str = "温暖陪伴", 
                          word_limit: int = 0, forbidden_phrases: str = "") -> list:
    """
    生成系统提示词列表
    
    Args:
        user_desc: 用户的一句话自我描述
        comfort_style: 安慰风格
        word_limit: 字数限制（0表示无限制）
        forbidden_phrases: 禁止出现的短语
    
    Returns:
        list: 包含 system message 的字典列表
    """
    # 构建个性化提示词
    personalization = ""
    
    if user_desc:
        personalization += f"\n\n## 用户背景\n用户这样描述自己：{user_desc}\n请在回应时考虑这个背景。"
    
    # 安慰风格调整
    style_adjustment = ""
    if comfort_style == "安静陪伴":
        style_adjustment = "\n\n## 当前风格设定\n用户需要安静陪伴型回应：话少一些，多倾听，不要急着给建议，让用户感到被陪伴即可。"
    elif comfort_style == "犀利点拨":
        style_adjustment = "\n\n## 当前风格设定\n用户需要犀利点拨型回应：直接指出问题核心，给出明确建议，不绕弯子。"
    elif comfort_style == "温和鼓励":
        style_adjustment = "\n\n## 当前风格设定\n用户需要温和鼓励型回应：多给予肯定和支持，让用户感到被接纳和鼓舞。"
    elif comfort_style == "理性分析":
        style_adjustment = "\n\n## 当前风格设定\n用户需要理性分析型回应：帮助理清思路，分析问题原因，提供逻辑清晰的建议。"
    
    # 字数限制
    limit_instruction = ""
    if word_limit > 0:
        limit_instruction = f"\n\n## 回复限制\n每次回复请控制在 {word_limit} 字以内。"
    
    # 禁止短语
    forbidden_instruction = ""
    if forbidden_phrases:
        forbidden_list = [p.strip() for p in forbidden_phrases.split(",") if p.strip()]
        if forbidden_list:
            forbidden_instruction = f"\n\n## 禁止用语\n回复中严禁出现以下短语：{', '.join(forbidden_list)}"
    
    # 组合完整提示词
    full_prompt = BASE_SYSTEM_PROMPT + personalization + style_adjustment + limit_instruction + forbidden_instruction
    
    # 返回 OpenAI 格式的消息列表
    return [{"role": "system", "content": full_prompt}]


# ==================== 初始化 Session State ====================
def init_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_desc" not in st.session_state:
        st.session_state.user_desc = ""
    if "comfort_style" not in st.session_state:
        st.session_state.comfort_style = "温暖陪伴"
    if "word_limit" not in st.session_state:
        st.session_state.word_limit = 0
    if "forbidden_phrases" not in st.session_state:
        st.session_state.forbidden_phrases = "我只是一个AI"


init_session_state()

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("### 🌙 EchoSoul 设置")
    st.markdown("<p class='subtitle'>你的情绪伴侣 AI</p>", unsafe_allow_html=True)
    st.divider()
    
    # 一句话描述
    st.markdown("**一句话描述此刻的你**")
    user_desc = st.text_input(
        label="一句话描述此刻的你",
        label_visibility="collapsed",
        placeholder="例如：最近工作压力很大，感到有些疲惫...",
        value=st.session_state.user_desc
    )
    st.session_state.user_desc = user_desc
    
    st.divider()
    
    # 安慰风格选择
    st.markdown("**安慰风格**")
    comfort_style = st.radio(
        label="选择安慰风格",
        label_visibility="collapsed",
        options=["温暖陪伴", "犀利点拨", "温和鼓励", "理性分析"],
        index=["温暖陪伴", "犀利点拨", "温和鼓励", "理性分析"].index(st.session_state.comfort_style)
    )
    st.session_state.comfort_style = comfort_style
    
    st.divider()
    
    # 字数限制
    st.markdown("**单次回复字数限制**")
    word_limit = st.slider(
        label="字数限制",
        label_visibility="collapsed",
        min_value=0,
        max_value=500,
        value=st.session_state.word_limit,
        step=50,
        format="%d 字" if st.session_state.word_limit > 0 else "无限制"
    )
    if word_limit == 0:
        st.caption("💡 拖动滑块设置字数限制，0 表示无限制")
    st.session_state.word_limit = word_limit
    
    st.divider()
    
    # 禁止用语
    st.markdown("**禁止出现的短语**")
    forbidden_phrases = st.text_input(
        label="禁止短语",
        label_visibility="collapsed",
        placeholder="用逗号分隔，例如：我只是一个AI, 我不知道",
        value=st.session_state.forbidden_phrases
    )
    st.session_state.forbidden_phrases = forbidden_phrases
    
    st.divider()
    
    # 重启记忆按钮
    st.markdown("**对话管理**")
    if st.button("🔄 重启 / 清空记忆", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # API 配置提示
    with st.expander("⚙️ API 配置"):
        st.markdown("""
        **当前配置：**
        - 模型：`deepseek-chat`
        - Base URL：`https://api.deepseek.com`
        
        **设置 API Key：**
        1. 点击右上角 ⋮ → Settings
        2. 选择 Secrets
        3. 添加 `DEEPSEEK_API_KEY`
        """)

# ==================== 主界面 ====================
# 标题区域
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center;'>🌙 EchoSoul</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.6);'>我在这里，愿意倾听你的一切</p>", unsafe_allow_html=True)

st.divider()

# 显示当前设置摘要（可选，可注释掉以完全隐藏系统信息）
if st.session_state.user_desc:
    st.info(f"💭 此刻的你：{st.session_state.user_desc}")

# ==================== 聊天界面 ====================

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("想对我说点什么吗？"):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 准备 API 调用
    try:
        # 检查 API Key
        api_key = API_KEY or st.secrets.get("DEEPSEEK_API_KEY", "")
        if not api_key:
            st.error("⚠️ 请先配置 DEEPSEEK_API_KEY！点击侧边栏的「API 配置」查看设置方法。")
        else:
            # 初始化客户端
            client = OpenAI(
                api_key=api_key,
                base_url=BASE_URL
            )
            
            # 生成系统提示词
            system_messages = generate_system_prompt(
                user_desc=st.session_state.user_desc,
                comfort_style=st.session_state.comfort_style,
                word_limit=st.session_state.word_limit,
                forbidden_phrases=st.session_state.forbidden_phrases
            )
            
            # 构建完整消息列表（system + history）
            api_messages = system_messages + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            
            # 调用 API
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # 流式响应
                stream = client.chat.completions.create(
                    model=MODEL,
                    messages=api_messages,
                    stream=True,
                    temperature=0.8,
                    max_tokens=2048
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
            
            # 保存 AI 回复
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    except Exception as e:
        st.error(f"❌ 出错了：{str(e)}")
        st.info("💡 请检查 API Key 是否正确，或稍后重试。")

# ==================== 空状态提示 ====================
if not st.session_state.messages:
    st.markdown("""
    <div style='text-align: center; padding: 60px 20px; color: rgba(255,255,255,0.5);'>
        <p style='font-size: 18px; margin-bottom: 20px;'>👋 你好，我是 EchoSoul</p>
        <p style='font-size: 14px; line-height: 2;'>
            无论你此刻是什么心情，都可以告诉我<br>
            开心、难过、困惑、疲惫... 我都在听
        </p>
        <br>
        <p style='font-size: 12px; opacity: 0.7;'>
            💡 在左侧设置中描述一下此刻的你，让我更好地理解你
        </p>
    </div>
    """, unsafe_allow_html=True)