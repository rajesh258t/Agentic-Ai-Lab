import streamlit as st
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

import streamlit as st
from query_executor import run_query

# your simple SQL generator
def generate_sql(user_query):
    query = user_query.lower()

    if "top" in query and "student" in query:
        return "SELECT * FROM students ORDER BY marks DESC LIMIT 3;"
    
    elif "highest marks" in query:
        return "SELECT * FROM students ORDER BY marks DESC LIMIT 1;"
    
    elif "all students" in query:
        return "SELECT * FROM students;"
    
    elif "cse students" in query:
        return "SELECT * FROM students WHERE branch='CSE';"
    
    else:
        return "SELECT * FROM students;"


# UI
st.set_page_config(page_title="AskDB", layout="wide")

st.title("🧠 AskDB - Text to SQL System")

st.sidebar.header("📊 Database Info")
st.sidebar.write("Table: students")
st.sidebar.write("Columns: id, name, marks, branch")

user_query = st.text_input("💬 Enter your question:")

if st.button("Generate & Run"):
    if user_query:
        sql = generate_sql(user_query)

        st.subheader("🔍 Generated SQL")
        st.code(sql, language="sql")

        result = run_query(sql)

        st.subheader("📈 Result")
        st.dataframe(result)