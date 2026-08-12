from query_executor import run_query

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


if __name__ == "__main__":
    q = input("Enter your question: ")
    
    sql = generate_sql(q)
    print("\nGenerated SQL:\n", sql)

    result = run_query(sql)
    print("\nResult:\n", result)