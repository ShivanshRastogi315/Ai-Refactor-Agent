import streamlit as st
import requests

API_URL = "http://localhost:8000/api/refactor"

st.set_page_config(page_title="Auto Code Refactoring Agent", page_icon="✨", layout="wide")

st.title("✨ Autonomous Code Refactoring Agent")
st.markdown("Powered by Qwen2.5-Coder and FastAPI")

language = st.selectbox("Select Language", ["python", "c", "java"])
code_input = st.text_area("Paste your code here:", height=300)

if st.button("✨ Auto-Repair & Optimize"):
    if code_input:
        with st.spinner("Analyzing and Refactoring..."):
            try:
                response = requests.post(API_URL, json={"code": code_input, "language": language})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display the new agent logs
                    with st.expander("🕵️ Agent Thought Process & Sandbox Execution Logs", expanded=True):
                        for log in data["agent_logs"]:
                            if "✅" in log:
                                st.success(log)
                            elif "❌" in log:
                                st.error(log)
                            else:
                                st.write(log)
                                
                    st.subheader(f"Status: {data['final_status']}")
                    
                    st.subheader("Static Analysis Report")
                    if data["static_analysis_status"] == "passed":
                        st.success("Initial Static Analysis Passed!")
                    else:
                        st.warning("Initial Static Analysis found issues. The AI used this context.")
                        st.code(data["static_analysis_issues"], language="text")
                    
                    st.subheader("Refactored Code")
                    st.code(data["refactored_code"], language=language)
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is the FastAPI server running?")
    else:
        st.warning("Please enter some code first.")