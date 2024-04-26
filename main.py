import requests
import json
import streamlit as st

st.set_page_config(page_title="AI辅助教学", layout="centered", page_icon="🤖")

API_KEY = ""
SECRET_KEY = ""

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

def main(prompt):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + get_access_token()

    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


if __name__ == '__main__':
    user_input = st.chat_input("请输入你计划咨询的问题，按回车键提交！")
    if user_input is not None:
        progress_bar = st.empty()
        with st.spinner("内容已提交，文心一言4.0模型正在作答中！"):
            feedback = json.loads(main(user_input))
            if feedback.get("result"):
                feedback = feedback["result"]
                progress_bar.progress(100)
                st.session_state['chat_history'].append((user_input, feedback))
                for i in range(len(st.session_state["chat_history"])):
                    user_info = st.chat_message("user")
                    user_content = st.session_state["chat_history"][i][0]
                    user_info.write(user_content)

                    assistant_info = st.chat_message("assistant")
                    assistant_content = st.session_state["chat_history"][i][1]
                    assistant_info.write(assistant_content)

                with st.sidebar:
                    if st.sidebar.button("清除对话历史"):
                        st.session_state["chat_history"] = []

            elif feedback.get("error_msg"):
                st.error(feedback["error_msg"])
            else:
                st.info("对不起，我回答不了这个问题，请你更换一个问题，谢谢！")