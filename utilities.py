import random
import json
##总结旧对话
def summarize_old_conversation_history(conversation_history):
    # 提取旧的对话历史
    old_messages = conversation_history[:-200]
    # 在这里添加总结算法
    # 提取每一轮对话的主题
    topics = [message['content'][:50] + '...' for message in old_messages]
    # 将主题转换为字符串
    summary = "\n".join(topics)
    return summary

##总结旧对话
def generate_personality():
    big_five_personality_language_style = {
        "开放探索型": "人格特質：富有想像力、好奇心強、寬容、獨立思考、喜歡新奇事物和冒險。言語風格：言辭富有創意，使用更多的抽象和複雜詞彙。喜歡談論新穎的觀點和想法，語言風格變化多端。常使用隱喻和比喻，喜歡表達個人見解和創意。",
        "尽责严谨型": "人格特質：有責任心、自律、可靠、計劃性強、目標導向、勤奮。言語風格：言辭謹慎、精確，常使用與計劃和目標相關的詞彙。注重細節，表達中常有結構性和邏輯性。喜歡使用「必須」、「需要」等表示責任和義務的詞語。",
        "外向社交型": "人格特質：精力充沛、健談、社交、樂觀、熱情、活躍。言語風格：言辭熱情洋溢，使用更多的正面情感詞彙。喜歡談論人際互動和社交活動，語速較快，聲音音量較高。經常主動發起對話，使用更多的「我」和「我們」這類第一人稱代詞。",
        "宜人合作型": "人格特質：友善、體貼、信賴他人、慷慨、樂於助人、合作性強。言語風格：言辭柔和、禮貌，常使用表示同情和關心的詞語。避免衝突，喜歡使用協調、支持和鼓勵性的語言。常使用「我們」、「大家」、「一起」等群體性詞彙。",
        "情绪敏感型": "人格特質：情緒易波動、容易緊張、焦慮、悲觀、自我意識強。言語風格：言辭中常帶有負面情緒詞彙，如擔憂、恐懼、悲傷。可能有較多的抱怨和自我批評，語調容易顯得緊張或不安。常使用「我覺得」、「我擔心」這類表達個人情感和感受的詞語。",
    }
    # 隨機為機器人選擇一個人格。
    selected_language_style_personality = random.choice(list(big_five_personality_language_style.items()))
    return selected_language_style_personality[1]


def load_cases(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    return cases
