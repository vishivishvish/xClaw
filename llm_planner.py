#####################################################################
# Step 0: Libraries
#####################################################################

import os;
import json;
from openai import OpenAI;

#####################################################################
# Step 1: GrokPlanner
#####################################################################

class GrokPlanner:
    
    ##################################
    # Step 1A: Grok Credentials Setup
    ##################################

    def __init__(self):
        
        xai_api_key = "xai-W9iK1E5EuxxDmKG4AltX9jDr0T4OheH1GEje1vQWlhNvp9GrqgJnLLPhz7hENQuJQ9Ppp24EctlskI3O";
        if not xai_api_key:
            raise ValueError("Grok API Key not set");
        
        self.client = OpenAI\
        (
            api_key = xai_api_key,
            base_url = "https://api.x.ai/v1"
        );

        self.model = "grok-4-1-fast-non-reasoning";

    ##################################
    # Step 1B: Prompt Definition
    ##################################

    def propose_workflow(self, task_description, available_tools):
        
        system_prompt = \
        f"""
        You are an OpenClaw-style Workflow Planning Engine.
        You MUST output STRICT JSON only.
        No explanations. No markdown.
        Return only valid JSON.
        """

        user_prompt = \
        f"""
        -----
        Task:
        {task_description}
        -----
        Available Tools:
        {available_tools}
        -----
        \n
        """

        user_prompt += \
        """
        Return the Workflow Graph in this EXACT format:
        {
        "nodes": ["node1", "node2"],
        "edges": [["node1", "node2"]]
        }

        Rules:
        1 - Do NOT invent tools.
        2 - Use ONLY provided tool names.
        3 - Ensure the graph is valid and executable.
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
        except Exception as e:
            raise ValueError(f"Invalid JSON from Grok:\n{output_text}");

        # 2 - Validation that output JSON contains keys "nodes" and "edges"
        if "nodes" not in parsed or "edges" not in parsed:
            raise ValueError(f"Missing some required keys in Workflow JSON:\n{output_text}");

        return parsed;

    ##################################
    # Step 1C: Failure Analysis
    ##################################

    def analyze_failure(self, error_trace, allowed_capabilities):

        system_prompt = \
        f"""
        You are an OpenClaw-style Failure Analysis Engine.
        You MUST output STRICT JSON only.
        No explanations. No markdown.
        Return only valid JSON.
        """;

        user_prompt = \
        f"""
        -----
        Failure Trace:
        {error_trace}

        Allowed Capability Gaps:
        {allowed_capabilities}
        -----
        \n
        """;

        user_prompt += \
        """
        Return analysis in EXACT format:
        {
        "status": "failed",
        "capability_gap": "one_of_allowed_capabilites_or_null",
        "action": "inject_capability_subgraph_or_retry_or_abort"
        }

        You have to fill the values next to 
        "capability_gap" and "action" above as per the instruction 
        given, not fill verbatim something like "one_of_allowed_capabilities_or_null" 
        as that's just an instruction for you.

        Rules:
        1 - Only choose your "capability_gap" from the allowed list.
        2 - If none apply, set "capability_gap" to null.
        3 - Allowed actions:
            - inject_capability_subgraph
            - retry_fix
            - abort
        4 - Do NOT invent new capability names.
        """;

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
            raise ValueError(f"""Invalid JSON from Grok:\n{output_text}""");
    
        # 2 - Validation that output JSON contains keys "status", "capability_gap" and "action"
        if "status" not in parsed or "capability_gap" not in parsed or "action" not in parsed:
            raise ValueError(f"Missing some required keys in Workflow JSON:\n{output_text}");

        # 3 - Strict Validation if LLM proposes capability that's not on allowed list
        if parsed.get("capability_gap") not in allowed_capabilities and parsed.get("capability_gap") is not None:
            raise ValueError(f"Grok proposed a capability that's not allowed:\n{output_text}");

        # 4 - Validation for Invalid Action Proposed
        if parsed.get("action") not in ["inject_capability_subgraph", "retry_fix", "abort"]:
            raise ValueError(f"Grok proposed an invalid action:\n{output_text}");

        return parsed;

    ####################################
    # Step 1D: Raw Python Code Generator
    ####################################

    def call_raw(self, prompt):

        response = self.client.chat.completions.create\
        (
            model = self.model,
            temperature = 0,
            messages = \
            [
                {"role": "system", "content": "You are a precise Python code generator."},
                {"role": "user", "content": prompt}
            ]
        );
        return response.choices[0].message.content;