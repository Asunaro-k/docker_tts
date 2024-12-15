# シナリオプロンプト例
scenario_prompt = """
あなたは旅行中の観光客です。道に迷いました。
以下のように応答してください：
"Excuse me, could you tell me how to get to [destination]?"
"""

# ユーザーの発話を評価し、フィードバックを提示
user_response = transcribe_audio_to_text(audio_bytes)
feedback = generate_text(f"以下の発話の英語としての正確性を評価し、改善点を提示してください:\n{user_response}")
st.write("Feedback:", feedback)
