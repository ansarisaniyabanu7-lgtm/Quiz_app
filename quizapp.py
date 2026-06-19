import os
import json
import streamlit as st
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

def fetch_questions(text_content, quiz_level):

    prompt = f"""
    You are an expert quiz generator. Based on the following text content, generate a quiz with 5 multiple-choice questions.
    The difficulty level should be: {quiz_level}.
    
    Provide the output strictly in a valid JSON format with the following structure:
    {{
        "mcqs": [
            {{
                "mcq": "Question text here?",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correct": "The exact correct option string here"
            }}
        ]
    }}
    Text content: {text_content}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    response_text = response.text.strip()
    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "").replace("```", "").strip()
    elif response_text.startswith("```"):
        response_text = response_text.replace("```", "").strip()
        
    try:
        data = json.loads(response_text)
        return data.get("mcqs", [])
    except Exception as e:
        st.error("Failed to parse quiz data. Please try again.")
        return []

def main():
    st.title("Quiz Generator App")

    text_content = st.text_area("Paste the text content here:")
    quiz_level = st.selectbox("Select quiz level:", ["Easy", "Medium", "Hard"])
    quiz_level = quiz_level.lower()

    if "questions" not in st.session_state:
        st.session_state.questions = None

    if st.button("Generate Quiz"):
        if text_content:
            with st.spinner("Generating quiz with Gemini..."):
                st.session_state.questions = fetch_questions(text_content=text_content, quiz_level=quiz_level)
        else:
            st.warning("Please paste some text content first!")

    if st.session_state.questions:
        with st.form("quiz_form"):
            selected_options = []
            correct_answers = []
            
            for i, question in enumerate(st.session_state.questions):
                st.subheader(f"Q{i+1}: {question['mcq']}")
                
                options = question['options']
                selected_option = st.radio(f"Choose option for Q{i+1}:", options, index=None, key=f"q_{i}")
                selected_options.append(selected_option)
                correct_answers.append(question['correct'])
            
            submit_quiz = st.form_submit_button("Submit Answers")
            
            if submit_quiz:
                st.header("Quiz Result:")
                marks = 0
                for i, (label, correct) in enumerate(zip(selected_options, correct_answers)):
                    if label == correct:
                        marks += 1
                        st.success(f"Q{i+1}: Correct! ")
                    else:
                        st.error(f"Q{i+1}: Incorrect. Correct answer was: {correct} ")
                
                st.info(f"Your total score: {marks} out of {len(st.session_state.questions)}")

if __name__ == "__main__":
    main()
    