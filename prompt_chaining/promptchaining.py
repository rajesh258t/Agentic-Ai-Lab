import ollama


MODEL = "qwen3:8b"


# -------------------------------------------------
# Ollama helper
# -------------------------------------------------

def ask_llm(prompt):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# -------------------------------------------------
# Step 1: Extract important information
# -------------------------------------------------

def extract_key_points(text):

    prompt = f"""
You are an information extraction system.

Read the following text and extract the most important information.

Return:
1. Main topic
2. Important facts
3. Important numbers or dates
4. Important conclusions

Do not add information that is not present in the text.

TEXT:
{text}
"""

    return ask_llm(prompt)


# -------------------------------------------------
# Step 2: Convert key points into structured summary
# -------------------------------------------------

def create_structured_summary(key_points):

    prompt = f"""
You are a professional summarization system.

Using the extracted information below, create a structured summary.

Use these sections:

- Overview
- Key Points
- Important Details
- Conclusion

Keep the information accurate and remove unnecessary repetition.

EXTRACTED INFORMATION:
{key_points}
"""

    return ask_llm(prompt)


# -------------------------------------------------
# Step 3: Generate final concise summary
# -------------------------------------------------

def create_final_summary(structured_summary):

    prompt = f"""
You are a final summarization assistant.

Convert the structured summary below into a concise,
easy-to-understand final summary.

Requirements:
- 1 short introductory paragraph
- 4 to 6 bullet points
- Mention important facts and numbers
- Do not introduce new information
- Keep the language simple

STRUCTURED SUMMARY:
{structured_summary}
"""

    return ask_llm(prompt)


# -------------------------------------------------
# Main Prompt Chaining Pipeline
# -------------------------------------------------

def summarize(text):

    print("\n========== STEP 1: KEY POINT EXTRACTION ==========\n")

    key_points = extract_key_points(text)

    print(key_points)


    print("\n========== STEP 2: STRUCTURED SUMMARY ==========\n")

    structured_summary = create_structured_summary(key_points)

    print(structured_summary)


    print("\n========== STEP 3: FINAL SUMMARY ==========\n")

    final_summary = create_final_summary(structured_summary)

    print(final_summary)


    return final_summary


# -------------------------------------------------
# Example
# -------------------------------------------------

text = """
Artificial intelligence is rapidly transforming software development.
Modern AI coding assistants can generate code, explain programming
concepts, detect bugs and help developers understand large codebases.

Large language models such as Qwen, Llama and GPT can be integrated
into development environments and applications. Local models are
particularly useful when privacy is important because data can remain
on the user's computer.

However, AI-generated code still requires human review. Developers
must verify security, performance and correctness before deploying
AI-generated solutions.

Organizations are increasingly combining AI with traditional software
engineering practices. This creates new roles such as AI engineer,
LLM engineer and AI platform engineer. Knowledge of Python, APIs,
databases, cloud platforms and DevOps is becoming increasingly useful
for these roles.
"""


summarize(text)