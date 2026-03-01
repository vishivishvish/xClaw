import os;
from openai import OpenAI;

xai_api_key = "xai-W9iK1E5EuxxDmKG4AltX9jDr0T4OheH1GEje1vQWlhNvp9GrqgJnLLPhz7hENQuJQ9Ppp24EctlskI3O";

system_prompt = \
f"""
You are a workflow planning engine.
You must output STRICT JSON only.
No explanations. No markdown.
No text outside JSON.
""";

user_prompt = \
"""
Task:
Fix failing tests in a Python repository.

Available tools:
- run_tests
- fix_code
- verify

Return a workflow graph in this exact format:

{
  "nodes": ["node1", "node2"],
  "edges": [["node1", "node2"]]
}

Do not invent tools.
Only use provided tool names.
Return valid JSON only.
""";

client = OpenAI\
    (
        api_key = xai_api_key,
        base_url = "https://api.x.ai/v1"
    );

try:
    chat_completion = client.chat.completions.create\
    (
        model = "grok-code-fast-1",
        messages = \
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens = 1000
    );
    print(chat_completion.choices[0].message.content);

except Exception as e:
    print(f"Exception occurred: {e}");

