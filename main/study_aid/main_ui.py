import streamlit as st
from llm_initializer import agent
from llm_initializer import generate_quiz_data

# -----------------------------
# Backend quiz logic
# -----------------------------
def generate_quiz_questions():
    # Replace with real generator
    mcq, shorts = generate_quiz_data()
    return mcq, shorts

# Chatbot logic
def ask_chatbot(question: str):
    response = agent.invoke({"question": question})
    return response["answer"]


# -----------------------------
# Streamlit UI Setup
# -----------------------------
st.set_page_config(page_title="Smart Tutor", layout="centered")

# Session state initialization
for key, default in {
    "page": "home",
    "quiz_index": 0,
    "quiz_questions": [],
    "show_answer": False,
    "chat_response": "",
    "quiz_type": None,
    "short_answers": {}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------------
# Home Page
# -----------------------------
if st.session_state.page == "home":
    st.title("📘 Welcome!")
    st.subheader("Choose a mode:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Quiz"):
            st.session_state.page = "quiz"
            mcq, short = generate_quiz_questions()
            st.session_state.mcq_questions = mcq
            st.session_state.short_questions = short
            st.session_state.quiz_type = None
    with col2:
        if st.button("💬 Chat"):
            st.session_state.page = "chat"

# -----------------------------
# Quiz Page
# -----------------------------
elif st.session_state.page == "quiz":
    if st.session_state.quiz_type is None:
        st.subheader("Choose quiz type:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 MCQ"):
                st.session_state.quiz_type = "mcq"
                st.session_state.quiz_questions = st.session_state.mcq_questions
                st.session_state.quiz_index = 0
                st.session_state.show_answer = False
                st.rerun()
        with col2:
            if st.button("✍️ Short Answer"):
                st.session_state.quiz_type = "short"
                st.session_state.quiz_questions = st.session_state.short_questions
                st.session_state.quiz_index = 0
                st.session_state.show_answer = False
                st.rerun()
        st.stop()

    questions = st.session_state.quiz_questions
    index = st.session_state.quiz_index

    if index >= len(questions):
        st.success("✅ Quiz complete!")
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.session_state.quiz_type = None
        st.stop()

    current_q = questions[index]
    st.markdown(f"**Q{index + 1}: {current_q['question']}**")

    if st.session_state.quiz_type == "mcq":
        selected = st.radio("Choose your answer:", current_q["options"], key=f"q{index}")

        if not st.session_state.show_answer:
            if st.button("Submit"):
                st.session_state.show_answer = True
                st.rerun()

        if st.session_state.show_answer:
            correct = current_q["answer"]
            if selected == correct:
                st.success(f"✅ Correct! The answer is: {correct}")
            else:
                st.error(f"❌ Incorrect. The correct answer is: {correct}")

            if st.button("Next Question"):
                st.session_state.quiz_index += 1
                st.session_state.show_answer = False
                st.rerun()

    elif st.session_state.quiz_type == "short":
        user_answer = st.text_input("Your answer:", key=f"short_q{index}")

        if not st.session_state.show_answer:
            if st.button("Submit"):
                st.session_state.short_answers[index] = user_answer
                st.session_state.show_answer = True
                st.rerun()

        if st.session_state.show_answer:
            correct = current_q["answer"]
            st.info(f"✅ Model Answer: {correct}")

            if st.button("Next Question"):
                st.session_state.quiz_index += 1
                st.session_state.show_answer = False
                st.rerun()

    if st.button("Quit"):
        st.session_state.page = "home"
        st.session_state.quiz_type = None

# -----------------------------
# Chat Page
# -----------------------------
elif st.session_state.page == "chat":
    st.subheader("🧑‍🏫 Talk to a Revolutionary")

    user_input = st.text_input("Ask a question:")

    if st.button("Ask"):
        if user_input.strip():
            st.session_state.chat_response = ask_chatbot(user_input)

    if st.session_state.chat_response:
        st.markdown(f"**Answer:** {st.session_state.chat_response}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Continue"):
            st.session_state.chat_response = ""
            st.rerun()
    with col2:
        if st.button("Quit"):
            st.session_state.page = "home"
