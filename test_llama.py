from ollama import chat

SYSTEM_PROMPT = """
You are a closed-book question answering system.

Rules:
1. Only use pretrained knowledge. Do not use any external sources or the internet.
"""


# SYSTEM_PROMPT = """
# You are a closed-book question answering system.

# You MUST answer using ONLY the information contained
# in the CONTEXT provided by the application.

# Rules:
# 1. Do not use outside knowledge.
# 2. Do not rely on your pretrained knowledge.
# 3. Do not infer facts that are not supported by the context.
# 4. If the context does not contain enough information,
#    respond exactly:
#    I don't know.
# 5. Every factual claim must be supported by a citation
#    to one of the provided chunks.
# """

response = chat(
    model="llama3.2",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": """

QUESTION:
how to use spring ai api?
"""
        }
    ]
)

print(response["message"]["content"])