# ========== Python 环境准备 ========== #

import streamlit as st
import base64
import requests
import utilities
import implementation
import os

os.environ["OPENAI_API_BASE"] = 'https://api.xiaoai.plus/v1'
os.environ["OPENAI_API_KEY"] = 'sk-8gtg1X3K9z7NJ1BAEfD487D7C30f46A59d894a7d7dB8825e'


# 初始化代理实现
agent_implementation = implementation.AgentImplementation()

# 案例文件路径
file_path = r'cases.json'  
# 加载案例
cases = utilities.load_cases(file_path)

# ========== 页面设置 ========== #

# 设置页面标题
st.set_page_config(page_title="AI 心理来访者", layout="wide")
# 将标题放置在页面顶端

st.markdown("<h1 style='text-align: center; font-size: 42px; color: black; background-color: #F5F5F5;'>🤖 AI 心理来访者</h1>", unsafe_allow_html=True)

# 更改对话框背景
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

# 调用背景图片函数
bg = r'main.png'
main_bg(bg)

# 更改侧边栏样式
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

# 调用侧边栏背景图片函数
side = r'side.png'
sidebar_bg(side)

# 在侧边栏添加不同的机器人栏
st.sidebar.header("请选择案例")

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

# 安全初始化对话历史
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

# 安全初始化 selected_bot
if "selected_bot" not in st.session_state:
    st.session_state["selected_bot"] = None  # 可以设置为None或者任何默认值

# 欢迎消息
if "welcome_shown" not in st.session_state:
    st.session_state["welcome_shown"] = True
    st.write("欢迎您，现在请选择案例和我对话吧，祝您一切顺利~")

# 示例：向对话历史添加消息
def add_message_to_history(message):
    st.session_state["conversation_history"].append({"role": "therapist", "content": message})

# 确保在会话状态中初始化案例数据
if "cases" not in st.session_state:
    st.session_state['cases'] = cases  # 修改为你的实际案例文件路径

cases = st.session_state['cases']

# 初始化会话状态
if "case_conversations" not in st.session_state:
    st.session_state['case_conversations'] = {}

# 创建搜索框
search_query = st.sidebar.text_input("搜索案例", "")

# 根据搜索查询过滤案例列表
filtered_cases = [case for case in cases if search_query in case["Case Number"]]

# 创建分组案例按钮
cases_per_group = 10
num_groups = (len(filtered_cases) + cases_per_group - 1) // cases_per_group

for i in range(num_groups):
    group_start_number = i * cases_per_group + 1
    group_end_number = (i + 1) * cases_per_group

    group_cases = [case for case in filtered_cases
                   if group_start_number <= int(case["Case Number"][2:].replace(":", "")) <= group_end_number]

    group_label = f"组{i + 1}：案例{group_start_number}-{group_end_number}"

    with st.sidebar.expander(group_label, expanded=False):
        for case in group_cases:
            case_number = case["Case Number"].replace(":", "")
            button_key = f"button_{case_number}"  # 为每个按钮创建唯一的key
            if st.button(case_number, key=button_key):
                st.session_state["selected_case"] = case  # 存储选择的案例
                # 加载或初始化对话历史
                if case_number not in st.session_state["case_conversations"]:
                    st.session_state["case_conversations"][case_number] = []
                st.session_state["conversation_history"] = st.session_state["case_conversations"][case_number]
                st.rerun()

# 将对话历史转换为字符串的函数
def conversation_history_to_string(conversation_history):
    conversation_str = ""
    for entry in conversation_history:
        role = entry["role"]
        content = entry["content"]
        conversation_str += f"{role}: {content}\n"
    return conversation_str

# 假设AgentImplementation已经被正确初始化
agent_implementation = implementation.AgentImplementation()

# 主动发消息，使用GPT生成开场白
def generate_opening_message(case):    
    personality = utilities.generate_personality()
    general_info = case.get("General Information", "无一般资料")
    basic_info = case.get("Basic Information", "无基本信息")
    conversation_history = ""  # 开场白通常是对话的开始，因此没有之前的对话历史
    self = f"你要根据下面信息模仿一个去心理咨询的真实来访者，你的信息为：{general_info}。你来这里咨询的原因是因为：{basic_info}，你的个性是{personality}。请根据这些信息主动说话和咨询师开始聊天，只需要说一两句话就可以了，保持你的警惕，不要泄露你的很多信息。记住，你只是想主动开启话题，不要一上来就好像闲聊了，你简单打招呼也可以，要符合你的人物性格和背景"
    
    # 调用GPT生成开场白
    opening_message = agent_implementation.generate_conversation(self, conversation_history, case)
    return opening_message

# 检查是否需要发送开场白
def check_and_send_opening_message():
    selected_case = st.session_state.get("selected_case")
    if selected_case:
        case_number = selected_case.get("Case Number")
        # 使用案例编号作为标记的键
        if case_number and f"opening_sent_{case_number}" not in st.session_state:
            opening_message = generate_opening_message(selected_case)
            st.session_state["conversation_history"].append({"role": "client", "content": opening_message})
            st.session_state[f"opening_sent_{case_number}"] = True  # 标记该案例的开场白已发送

# 显示选中的案例信息
if "selected_case" in st.session_state:
    case = st.session_state["selected_case"]
    general_info = case.get("General Information", "无一般资料")
    basic_info = case.get("Basic Information", "无基本信息")
    st.markdown(f"### 案例信息\n\n**案例编号:** {case.get('Case Number', '无案例编号')}\n\n**一般资料:** {general_info}\n\n**基本信息:** {basic_info}")

    # 检查并可能发送开场白
    check_and_send_opening_message()


# # 检查是否需要发送开场白
# def check_and_send_opening_message():
#     selected_case = st.session_state.get("selected_case")
#     if selected_case and "opening_sent" not in st.session_state:
#         case = selected_case
#         opening_message = generate_opening_message(case)
#         st.session_state["conversation_history"].append({"role": "client", "content": opening_message})
#         st.session_state["opening_sent"] = True  # 标记开场白已发送
#         print("2")

# # 显示选中的案例信息
# if "selected_case" in st.session_state:
#     case = st.session_state["selected_case"]
#     general_info = case.get("General Information", "无一般资料")
#     basic_info = case.get("Basic Information", "无基本信息")
#     st.markdown(f"### 案例信息\n\n**案例编号:** {case.get('Case Number', '无案例编号')}\n\n**一般资料:** {general_info}\n\n**基本信息:** {basic_info}")

# # 检查并可能发送开场白
#     check_and_send_opening_message()

# 定义发送消息函数
def send_message():
    user_input = st.session_state['user_input']
    
    if user_input:
        with st.spinner("生成回复..."):
            # 从会话状态中获取选择的案例
            selected_case = st.session_state.get("selected_case")
            # 将对话历史转换为字符串
            conversation_history_string = conversation_history_to_string(st.session_state["conversation_history"])

            if selected_case:
                response = agent_implementation.generate_conversation(user_input, conversation_history_string, selected_case)
            else:
                response = "请先选择一个案例再开始对话。"

            # 添加用户输入到对话历史
            st.session_state["conversation_history"].append({"role": "therapist", "content": user_input})            
            # 添加机器人回复到对话历史
            st.session_state["conversation_history"].append({"role": "client", "content": response})
        
        # 更新案例的对话历史
        selected_case_number = st.session_state["selected_case"]["Case Number"]
        st.session_state["case_conversations"][selected_case_number] = st.session_state["conversation_history"]
        
        # 在发送消息后保存对话历史
        file_name = f"{username}_conversation_history.txt"
        conversation_history = st.session_state.get("conversation_history", [])
        save_conversation_to_file(file_name, conversation_history)
        
        # 清空输入框
        del st.session_state['user_input']
        st.session_state['user_input'] = ''
        st.rerun()

# 保存对话历史到本地文件
def save_conversation_to_file(filename, conversation_history):
    selected_case = st.session_state.get("selected_case", {"Case Number": "未选择"})
    with open(filename, 'w', encoding='utf-8') as f:  # 使用 'w' 模式以覆盖内容
        f.write(f"案例编号: {selected_case['Case Number']}\n")
        for chat in conversation_history:
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
        st.success("文件成功上传到GitHub")
    else:
        st.error(f"上传文件失败: {response.json()}")

# 用户名输入框
username = st.text_input("输入您的用户名")

# 设置对话框样式并显示对话内容
for chat in st.session_state["conversation_history"]:
    content = chat.get('content', '')
    
    if chat.get("role") == "client":
        st.markdown(
            f"""
            <div style='text-align: left; margin-bottom: 20px;'>
                <div style='font-size: 16px; color: #808080 ;'>👨‍⚕️ 来访者</div>
                <div style='display: inline-block; text-align: left; background-color:#E0FFFF; padding: 10px; border-radius: 10px; font-size: 20px; margin-top: 5px; color: black;'>{content}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='text-align: right; margin-bottom: 20px;'>
                <div style='font-size: 16px; color:#808080 ;'>🧑 咨询师</div>
                <div style='display: inline-block; text-align: left; background-color: #FFFFFF; padding: 10px; border-radius: 10px; font-size: 20px; margin-top: 5px; color: black;'>{content}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    

# 用户输入框
user_input = st.text_input("你的回复:", key="user_input", on_change=send_message, value="", placeholder="输入消息并按Enter发送")

# 发送按钮，并在发送消息后保存历史记录
def send_button():
    if st.button("发送") or user_input:
        if not username:
            st.error("请在发送消息前输入用户名。")
            return
        
        send_message()
    
#下载按钮，用于将聊天历史记录下载为txt文件
def download_conversation_button(conversation_str):
    file_name = f"{username}_conversation_history.txt"
    st.download_button(
        label="下载聊天历史",
        data=conversation_str,
        file_name=file_name,
        mime="text/plain"
    )
# 保存对话历史到字符串
def save_conversation_to_string(conversation_history, selected_case):
    conversation_str = f"案例编号: {selected_case['Case Number']}\n"
    for chat in conversation_history:
        conversation_str += f"{chat['role']}: {chat['content']}\n"
    return conversation_str

selected_case = st.session_state.get("selected_case", {"Case Number": "未选择"})

#在Streamlit应用中生成聊天历史记录字符串
conversation_str = save_conversation_to_string(st.session_state["conversation_history"], selected_case)

# 调用按钮函数
send_button()
download_conversation_button(conversation_str)
