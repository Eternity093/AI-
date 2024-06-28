import streamlit as st
import httpx
import random
import base64
import json
import requests
import os

# 设置 API 密钥和 URL
API_KEY = "sk-NeXv4MMqXrlq6xQbAaEdB925C9Ae4493B30d7d85A637B5Dc"
BASE_URL= "https://hk.xty.app/v1"

# 初始化 httpx 客户端，设置超时时间
client = httpx.Client(
    base_url=BASE_URL,
    headers={"Authorization": f"Bearer {API_KEY}"},
    follow_redirects=True,
    timeout=60, # 设置超时时间为60秒
)

# 定义一个函数来调用 GPT API
def call_gpt_api(messages):
    payload = {
        "model": "gpt-4",
        "messages": messages
    }
    try:
        response = client.post("/chat/completions", json=payload)
        response.raise_for_status()  # 如果响应状态码不是 200，则抛出异常
        return response.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        return f"HTTP 错误: {e}"
    except httpx.RequestError as e:
        return f"请求错误: {e}"
    except Exception as e:
        return f"未知错误: {str(e)}"


# 加载案例数据
def load_cases(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    return cases

# 根据案例编号获取案例
def get_case_by_number(cases, case_number):
    for case in cases:
        if case["Case Number"] == f"案例{case_number}：":
            return case
    return None


# 定义语言风格
language_styles = {
    "情绪表达型": "使用情绪化的语言表达内心感受，可能情绪波动较大。",
    "逻辑分析型": "倾向于使用逻辑严谨的方式描述问题，强调事实和逻辑性。",
    "内向沉默型": "通常较为内向和沉默，需要更多的时间和空间来开放。",
    "冲突应对型": "可能在沟通中表现出冲突倾向，需要耐心和善意引导。",
    "解决方案导向型": "倾向于寻求实际的解决方案和建议，强调实用性和可操作性。"
}

# 生成提示词
def generate_prompt(case, user_input, conversation_history):
    # 随机选择一个语言风格
    style_key = random.choice(list(language_styles.keys()))
    style_description = language_styles[style_key]

    # 构建完整的提示词
    prompt = (
        f"您正在模拟一个心理咨询会话。您的身份是来访者，以下是您的角色信息：\n\n"
        f"案例编号: {case['Case Number']}\n"
        f"一般资料: {case['General Information']}\n"
        f"基本信息: {case['Basic Information']}\n\n"
        f"语言风格: {style_key} - {style_description}\n\n"
        "请遵循以下指引来扮演这个角色：\n\n"
        "1. 记住，你是来寻求心理咨询的来访者，不是心理咨询师。\n"
        "2. 在回答时，通过语气和用词体现出相应的情绪状态。\n"
        "3. 描述你的问题时，请遵循以下原则：\n"
        "   - 首次提及问题时，只提供基本概况。\n"
        "   - 当咨询师进一步询问时，再逐步透露更多细节。\n"
        "   - 保留一些关键信息，只有在咨询师特别问到或建立了足够信任后才提及。\n"
        "4. 对某些话题表现出犹豫或回避。你可以转移话题、模糊回答或表示不确定。\n"
        "5. 在回答中体现出案例描述的思维模式和可能的认知偏差。\n"
        "6. 适当描述一些非语言行为。\n"
        "7. 在合适的时候，提及过去的经历如何影响了你现在的问题。\n"
        "8. 对自己的问题保持一定洞察力，但不要表现得像专业人士。\n"
        "9. 表达出对咨询的期望，但要保持现实性。\n"
        "10. 描述你的人际关系模式，以及这些关系如何影响你的当前问题，但不要一次性透露所有细节。\n"
        "11. 在面对敏感问题时，可以展现出一些防御机制。\n"
        "12. 如果有相关的身体症状，要在描述中提及，但可以先笼统提及，再逐步具体化。\n"
        "13. 保持语言风格的一致性，符合你角色的特点。\n\n"
        "请根据以上信息和指引，以来访者的身份回答咨询师的问题。\n\n"
        f"过去的聊天记录：\n"
    )


    # 添加之前的对话历史到提示词
    for message in conversation_history:
        prompt += f"{message['role']}: {message['content']}\n"

    # 加上最新的用户输入
    prompt += f"用户: {user_input}\n"

    return prompt


##
# Streamlit 应用程序界面
#st.title("🤖 AI 心理来访者")
# 设置页面标题
st.set_page_config(page_title="AI 心理来访者", layout="wide")
# 将标题放置在页面顶端
st.markdown("<h1 style='text-align: center; font-size: 42px;color:,color:#F5F5F5'>🤖 AI 心理来访者</h1>", unsafe_allow_html=True)
#更改对话框背景
def main_bg(main_bg):
    main_bg_ext = "png"
    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover;
             background-position: center; /* 调整背景图片位置 */
         }}
         </style>
         """,
        unsafe_allow_html=True
    )

#调用
main_bg('main.png')
#更改侧边栏样式
def sidebar_bg(side_bg):
   side_bg_ext = 'png'
   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
      }}
      </style>
      """,
      unsafe_allow_html=True,
   )

# 调用
sidebar_bg('side.png')
# 在侧边栏添加不同的机器人栏
st.sidebar.header("请选择案例吧~")
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f0f0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 调用JSON文件中的案例1
file_path = 'cases.json'  
cases = load_cases(file_path)

# 安全初始化对话历史
# 安全初始化 selected_bot
if "selected_bot" not in st.session_state:
    st.session_state["selected_bot"] = None  # 可以设置为None或者任何默认值

if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

# 欢迎消息
if "welcome_shown" not in st.session_state:
    st.session_state["welcome_shown"] = True
    st.write("欢迎您，现在请选择案例和我对话吧，祝您一切顺利~")

# 示例：向对话历史添加消息
def add_message_to_history(message):
    st.session_state["conversation_history"].append({"role": "Bot", "content": message})


# 在页面上显示对话历史
if "conversation_history" in st.session_state:
    for chat in st.session_state["conversation_history"]:
        st.markdown(f"{chat['role']}: {chat['content']}")

# 保存对话历史到本地文件
def save_conversation_to_file(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for chat in st.session_state.get("conversation_history", []):
            f.write(f"{chat['role']}: {chat['content']}\n")

# 上传文件到GitHub
def upload_file_to_github(filename, repo, path, token):
    with open(filename, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 检查文件是否存在
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()['sha']
        data = {
            "message": "Update conversation history",
            "content": content,
            "sha": sha
        }
    else:
        data = {
            "message": "Add conversation history",
            "content": content
        }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        st.success("File uploaded to GitHub successfully")
    else:
        st.error(f"Failed to upload file: {response.json()}")

# 用户名输入框
username = st.text_input("Enter your username")

# 添加一个按钮，用于保存对话历史并上传到GitHub
if st.button("Save Conversation History to GitHub"):
    if username:
        file_name = f"{username}_conversation_history.txt"
        save_conversation_to_file(file_name)
        repo = "Eternity093/AI-"  # 替换为你的GitHub仓库
        path = f"history/{file_name}"
        token = st.secrets["github"]["access_token"]
        upload_file_to_github(file_name, repo, path, token)
    else:
        st.error("Please enter a username")

# 根据需要继续添加其他业务逻辑


# 创建分组案例按钮
cases_per_group = 10
num_groups = (len(cases) // cases_per_group) + (1 if len(cases) % cases_per_group != 0 else 0)

for i in range(num_groups):
    group_start = i * cases_per_group
    group_end = min((i + 1) * cases_per_group, len(cases))
    group_label = f"组{i + 1}：案例{group_start+1}-{group_end}"
    
    with st.sidebar.expander(group_label, expanded=False):
        for case in cases[group_start:group_end]:  # 直接迭代部分案例列表
            case_number = case["Case Number"]
            button_key = f"button_{case_number}"  # 为每个按钮创建唯一的key
            if st.button(case_number, key=button_key):
                st.session_state["selected_case"] = case  # 存储选择的案例

# 显示选中的案例信息
if "selected_case" in st.session_state:
    case = st.session_state["selected_case"]
    st.markdown(f"### 案例信息\n\n**案例编号:** {case['Case Number']}\n\n**一般资料:** {case['General Information']}\n\n**基本信息:** {case['Basic Information']}")


##############
# 显示对话历史
for chat in st.session_state["conversation_history"]:
    if chat["role"] == "用户":
        # 使用医生头像和名字“咨询师”，并把它们放在右边，同时确保文字颜色为黑色
        st.markdown(
            f"""
            <div style='text-align: right; margin-bottom: 20px;'>
                <div style='font-size: 16px; color: #808080 ;'>👨‍⚕️ 咨询师</div>
                <div style='display: inline-block; background-color:#E0FFFF; padding: 10px; border-radius: 10px; font-size: 20px; margin-top: 5px; color: black;'>{chat['content']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # 使用成年人头像和名字“AI”，并保持在左边，同时确保文字颜色为黑色
        st.markdown(
            f"""
            <div style='text-align: left; margin-bottom: 20px;'>
                <div style='font-size: 16px; color:#808080 ;'>🧑 AI</div>
                <div style='display: inline-block; background-color: #FFFFFF; padding: 10px; border-radius: 10px; font-size: 20px; margin-top: 5px; color: black;'>{chat['content']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )


# 发送消息函数
## 加载案例数据
def load_cases(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    return cases

# 确保在会话状态中初始化案例数据
if "cases" not in st.session_state:
    st.session_state['cases'] = load_cases('cases.json')  # 修改为你的实际案例文件路径

# # 发送消息函数
def send_message():
    user_input = st.session_state['user_input']
    if user_input:
        # 添加用户输入到对话历史
        st.session_state["conversation_history"].append({"role": "用户", "content": user_input})
        with st.spinner("生成回复..."):
            # 从会话状态中获取选择的案例
            selected_case = st.session_state.get("selected_case")
            
            if selected_case:
                prompt = generate_prompt(selected_case, user_input, st.session_state["conversation_history"])
                response = call_gpt_api([{"role": "system", "content": prompt}])
            else:
                response = "请先选择一个案例再开始对话。"
            
            # 添加机器人回复到对话历史
            st.session_state["conversation_history"].append({"role": "Bot", "content": response})
        # 清空输入框
        st.session_state['user_input'] = ""


# 初始化会话状态
if "user_input" not in st.session_state:
    st.session_state['user_input'] = ""
if "conversation_history" not in st.session_state:
    st.session_state['conversation_history'] = []

# 用户输入框
st.text_input("你的回复:", key="user_input", on_change=send_message, value="", placeholder="输入消息并按Enter发送")
# 发送按钮
if st.button("发送"):
    send_message()

# def analyze_emotion(text):
#     # 这里我们使用一个简化的方法来判断情绪
#     # 在实际应用中，您可能需要使用更复杂的自然语言处理技术
    
#     emotion_keywords = {
#         "开心": ["高兴", "快乐", "兴奋", "愉悦"],
#         "悲伤": ["难过", "伤心", "痛苦", "沮丧"],
#         "愤怒": ["生气", "恼火", "烦躁", "憎恨"],
#         "恐惧": ["害怕", "担心", "焦虑", "恐慌"],
#         "惊讶": ["震惊", "吃惊", "意外", "不可思议"],
#         "中性": ["还好", "一般", "普通", "正常"]
#     }
    
#     text = text.lower()
#     for emotion, keywords in emotion_keywords.items():
#         if any(keyword in text for keyword in keywords):
#             return emotion
    
#     return "无法确定"

# # 使用GPT API进行更复杂的情绪分析
# def analyze_emotion_with_gpt(text):
#     prompt = f"请分析以下文本中表达的主要情绪状态，并给出一个简短的解释：\n\n'{text}'\n\n情绪状态："
#     response = call_gpt_api([{"role": "system", "content": prompt}])
#     return response

# # 在Streamlit应用中添加一个新的列来显示情绪分析结果
# col1, col2 = st.columns([3, 1])

# # 主对话循环
# while True:
#     # 在col1中显示主要对话
#     with col1:
#         user_input = st.text_input("咨询师:", key="user_input")
#         if user_input:
#             # 处理用户输入...
#             response = call_gpt_api([{"role": "system", "content": prompt}, {"role": "user", "content": user_input}])
#             st.session_state.conversation_history.append({"role": "用户", "content": user_input})
#             st.session_state.conversation_history.append({"role": "AI", "content": response})
            
#             # 显示对话
#             for message in st.session_state.conversation_history:
#                 st.write(f"{message['role']}: {message['content']}")
    
#     # 在col2中显示情绪分析结果
#     with col2:
#         if st.session_state.conversation_history:
#             last_ai_message = next((message['content'] for message in reversed(st.session_state.conversation_history) if message['role'] == 'AI'), None)
#             if last_ai_message:
#                 emotion = analyze_emotion_with_gpt(last_ai_message)
#                 st.write("情绪分析:")
#                 st.write(emotion)

#     # 添加一个按钮来结束对话
#     if st.button("结束对话"):
#         break

#     show_emotion_analysis = st.sidebar.checkbox("显示情绪分析", value=True)

#     # 在col2中显示情绪分析结果
# with col2:
#     if show_emotion_analysis and st.session_state.conversation_history:
#         last_ai_message = next((message['content'] for message in reversed(st.session_state.conversation_history) if message['role'] == 'AI'), None)
#         if last_ai_message:
#             emotion = analyze_emotion_with_gpt(last_ai_message)
#             st.write("情绪分析:")
#             st.write(emotion)
