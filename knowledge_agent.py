import os;
import json;
from openai import OpenAI;

class KnowledgeSelectionAgent:

    def __init__(self):

        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            raise ValueError("Grok API Key not set");

        self.client = OpenAI\
        (
            api_key = api_key,
            base_url = "https://api.x.ai/v1"
        );

        self.model = "grok-4-1-fast-non-reasoning";

    def select_relevant_file(self, failure_trace, file_summaries):

        system_prompt = \
        f"""
        You are an OpenClaw-style Knowledge Selection Agent.
        Select the file whose content directly addresses the root cause of the failure.
        You MUST output STRICT JSON only.
        No explanations. No markdown.
        Return only valid JSON.
        """;

        user_prompt = \
        f"""
        -----
        Failure Trace:
        {failure_trace}
        -----
        Available Knowledge  Files (with summaries):
        {file_summaries}
        -----
        \n
        """;

        user_prompt += \
        """
        Return response in EXACT format:
        {
        "selected_file": "filename.md" <- replace filename.md with whatever the exact file name is
        }

        Rules:
        1 - Select ONLY ONE file. ONLY ONE.
        2 - The filename MUST exactly match one from the list.
        3 - Do NOT invent filenames.
        """

        response = self.client.chat.completions.create\
        (
            model = self.model,
            temperature = 0,
            messages = \
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        );
        output_text = response.choices[0].message.content.strip();

        # 1 - Validation that output is actually a JSON
        try:
            parsed = json.loads(output_text);
        except Exception:
            raise ValueError(f"Invalid JSON from Grok:\n{output_text}");

        # 2 - Validation that output JSON contains key "selected_files"
        if "selected_file" not in parsed:
            raise ValueError(f"Missing 'selected_files' required key in JSON:\n{output_text}");

        return parsed;

# print("All good - knowledge_agent ready to be used as a module");