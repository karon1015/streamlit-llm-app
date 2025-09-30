# === セル1: ライブラリ準備 (手順メモ) ===
# 以下をターミナルで事前に実行してライブラリをインストールしてください
# pip install langchain==0.3.0 langchain-openai streamlit==1.24.0 python-dotenv
# === セル2: 必要ライブラリの読み込みとLLM初期化 ===

import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
load_dotenv()



# --- LLM初期化 ---
llm = ChatOpenAI(
    model="gpt-4o-mini",   # Lesson8に合わせたモデルを使用
    temperature=0.7
)
# === セル3: 専門家プロファイル定義 ===

# ラジオボタンで選択できる専門家のプロファイルを定義
EXPERT_PROFILES = {
    "A": "あなたはキャリアコーチです。相談者のキャリアパスやスキルアップについて、前向きで具体的なアドバイスをしてください。",
    "B": "あなたは栄養士です。相談者の食生活や健康を考慮し、バランスのとれた食事改善の提案をしてください。"
}
# === セル4: プロンプトテンプレート & チェーン定義 ===

# プロンプトテンプレートを定義
prompt = ChatPromptTemplate.from_messages([
    ("system", "{expert_profile}"),
    ("human", "{user_input}")
])

# チェーンを定義（プロンプト → LLM → 出力整形）
qa_chain = prompt | llm | StrOutputParser()
# === セル5: 回答生成関数の定義 ===

def generate_answer(user_text: str, expert_choice: str) -> str:
    """
    入力テキストとラジオボタンでの選択値を受け取り、
    LLMからの回答を文字列として返す関数
    """
    try:
        # 選択された専門家プロファイルを取得
        expert_profile = EXPERT_PROFILES.get(expert_choice)
        if expert_profile is None:
            return "エラー: 選択した専門家プロファイルが見つかりません。"

        # チェーンに入力を渡して実行
        result = qa_chain.invoke({
            "expert_profile": expert_profile,
            "user_input": user_text
        })

        return result
    
    except Exception as e:
        # 例外発生時には簡潔なエラー文を返す
        return f"回答の取得に失敗しました: {str(e)}"
# === セル6: Streamlit UI部分 ===

# アプリタイトルと概要
st.title("専門家Q&Aアプリ")
st.write("このアプリでは、入力したテキストに対して、選択した専門家（キャリアコーチ／栄養士）が回答します。")
st.write("ラジオボタンで専門家を選び、質問を入力して送信してください。")

# ラジオボタンで専門家を選択
expert_choice = st.radio(
    "専門家を選択してください：",
    options=["A", "B"],
    format_func=lambda x: "キャリアコーチ" if x == "A" else "栄養士"
)

# 入力フォーム
user_text = st.text_area("質問を入力してください：")

# 送信ボタン
if st.button("送信"):
    if user_text.strip() == "":
        st.warning("質問を入力してください。")
    else:
        with st.spinner("回答生成中..."):
            answer = generate_answer(user_text, expert_choice)
        
        # 結果を表示
        if answer.startswith("エラー") or answer.startswith("回答の取得に失敗しました"):
            st.error(answer)
        else:
            st.success("回答結果")
            st.write(answer)
