#################################################################################################
# Stages Completed
# Stage 1: Workflow DAG Spine
# Stage 2: Execution Engine Layer
# Stage 3: Agentic Initial Workflow DAG
# Stage 4: Agentic Capability Gap Detection & Mutation Proposal
# Stage 5: Agentic Local Knowledge Selection Tool
# Stage 6: Agentic Function Extraction & Sandbox Validation
#################################################################################################

#####################################################################
# Step 0: Libraries
#####################################################################

import os;
import uuid;
import random;
import datetime;
import traceback;
from collections import defaultdict;
from llm_planner import GrokPlanner;
from knowledge_agent import KnowledgeSelectionAgent;
print("# Step 0: Libraries Imported");

#####################################################################
# Step 1: Tool Registry
#####################################################################

class ToolRegistry:
    
    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = func

    def execute(self, name, context):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered.")
        return self.tools[name](context)

print("# Step 1: Tool Registry created");

#####################################################################
# Step 2: Execution Engine
#####################################################################

class ExecutionEngine:
    
    def __init__(self, graph, tool_registry):
        self.graph = graph
        self.registry = tool_registry
        self.context = \
            {
            "capability_gap": None
            }

    def run(self):
        
        print("\nStarting execution loop...\n")

        while True:
            executable = self.graph.get_next_executable_nodes()

            if not executable:
                print("No more executable nodes.")
                break

            for node_id in executable:
                node = self.graph.nodes[node_id]

                print(f"Executing node: {node_id}")
                node.status = "running"

                try:
                    result = self.registry.execute(node_id, self.context)

                    # This was initially hardcoded in earlier iterations
                    # Now it is being dynamically analyzed by the LLM (Grok)

                    # if result.get("status") == "failed":
                    #    node.status = "failed"
                    #    self.context["capability_gap"] = result.get("capability_gap")
                    #    print(f"Node {node_id} failed.")
                    #    return "failure"

                    ##################################################

                    if result.get("status") == "failed":

                        node.status = "failed";
                        error_trace = result.get("error_trace");

                        # Now newly saving this error_trace so that the Knowledge Tool can access it 
                        self.context["last_error_trace"] = error_trace;

                        planner = self.context["planner"];
                        allowed_capabilities = ["nested_json_schema_validation"];
                    
                        print("\n[LLM] Analyzing failure trace via Grok...");
                        print(f"[LLM] Error Trace: {error_trace}");

                        analysis = planner.analyze_failure\
                        (
                            error_trace, allowed_capabilities
                        );
                    
                        print("[LLM] Failure analysis response:");
                        print(analysis);
                        print("-" * 60);

                        self.context["analysis"] = analysis;
                    
                        return "failure";

                    ##################################################                    

                    node.status = "complete"

                except Exception as e:
                    node.status = "failed"
                    print(f"Execution error in {node_id}: {e}")
                    return "failure"

        return "complete"

print("# Step 2: Execution Engine created");

#####################################################################
# Step 3: Mock Tool Implementations
#####################################################################

def run_tests_tool(context):
    print("Running tests...")
    return {"status": "success"}

# The initial fix_code_tool was hardcoded upto a fixed capability_gap in earlier iterations
# Now it is first a random selection among 2 possibilities upto the error_trace

# def fix_code_tool(context):
#    print("Attempting to fix code...");
    
#    # Simulate capability gap
#    return \
#        {
#        "status": "failed",
#        "capability_gap": "nested_schema_validation"
#        };

#####################################################################

def fix_code_tool(context):

    print("Attempting to fix code...");

    failure_templates = \
        [
            {
            "raw_error": "ValueError: Missing required nested field: server.port",
            "structured_failure": \
                """
                ## Failure Report
                Failure Category: Configuration Schema Validation Error
                Failure Type: Missing Nested Field
                Error Message: Missing required nested field: server.port

                ## Context
                - A nested configuration dictionary is being validated.
                - A required nested key 'server.port' is missing.
                - The system likely lacks recursive schema validation logic.

                ## Keywords
                nested
                schema
                configuration
                recursive validation
                missing field
                dictionary
                """
            },
            {
            "raw_error": "TypeError: Field server.port must be integer, got string",
            "structured_failure": \
                """
                ## Failure Report
                Failure Category: Configuration Schema Validation Error
                Failure Type: Nested Field Type Mismatch
                Error Message: Field server.port must be integer, got string

                ## Context
                - A nested configuration dictionary is being validated.
                - Field 'server.port' exists but has incorrect type.
                - The system likely lacks type checking during recursive schema traversal.
                
                ## Keywords
                nested
                schema
                configuration
                recursive validation
                type mismatch
                integer validation
                dictionary
                """
            }
        ];

    selected = random.choice(failure_templates);

    print(f"[TOOL] Simulated Raw Error: {selected['raw_error']}");

    return \
        {
        "status": "failed",
        "raw_error": selected["raw_error"],
        "error_trace": selected["structured_failure"],
        };

#####################################################################

def verify_tool(context):
    print("Verifying final result...")
    return {"status": "success"}

# The read_local_knowledge_tool() was initially hardcoded
# That has now been replaced by LLM-driven Local Knowledge Selection

# def read_local_knowledge_tool(context):
#     print("Reading local knowledge base...")
#     return {"status": "success"}

#####################################################################

def read_local_knowledge_tool(context):
    
    print("\n" + "="*70);
    print("KNOWLEDGE RETRIEVAL PHASE");
    print("="*70);
    
    failure_trace = context.get("analysis", {}).get("failure_trace");
    if not failure_trace:
        failure_trace = context.get("last_error_trace");

    knowledge_dir = "knowledge_base";
    if not os.path.exists(knowledge_dir):
        raise FileNotFoundError("knowledge_base folder not found");

    files = [f for f in os.listdir(knowledge_dir) if f.endswith(".md")];
    if not files:
        raise ValueError("No markdown files found in knowledge_base");

    file_summaries = [];
    for filename in files:
        filepath = os.path.join(knowledge_dir, filename);
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read();
        summary_section = "";
        lines = content.splitlines();
        capture = False;
        for line in lines:
            if line.strip().startswith("Summary:"):
                capture = True;
                summary_section += line + "\n";
                continue;
    
            if capture:
                if line.strip() == "":
                    break;
                summary_section += line + "\n";
    
        file_summaries.append\
        (
            f"Filename: {filename}\n{summary_section}\n"
        )

    structured_input = "\n".join(file_summaries);

    print("\nAvailable Knowledge Files:\n");
    print(structured_input);

    selector = KnowledgeSelectionAgent();
    selection = selector.select_relevant_file(failure_trace, structured_input);
    selected_file = selection.get("selected_file");
    if selected_file not in files:
        raise ValueError(f"Invalid File selected by Grok: {selected_file}");
    print(f"\nLLM Selected File: {selected_file}");

    full_path = os.path.join(knowledge_dir, selected_file);
    with open(full_path, "r", encoding="utf-8") as f:
        full_content = f.read();
    
    context["selected_knowledge_file"] = selected_file;
    context["selected_knowledge_content"] = full_content;

    return {"status": "success"}

#####################################################################
    
    # This was initially a hardcoded success response in earlier iterations
    # Now we are defining an actual sandbox experiment tool 
    
# def sandbox_experiment_tool(context):
    # print("Running sandbox experiment...")
    # return {"status": "success"}

#####################################################################

def sandbox_experiment_tool(context):

    print("\n--- SANDBOX VALIDATION PHASE ---");

    structured_failure = context.get("last_error_trace");
    knowledge_content = context.get("selected_knowledge_content");
    knowledge_file = context.get("selected_knowledge_file");

    if not structured_failure or not knowledge_content:
        return {"status": "failed", "error": "Missing knowledge context for sandbox experiment"};

    planner = context["planner"];

    # Step 1 - Ask Grok to extract and adapt function

    prompt = \
    f"""
    You are an expert software engineer.
    Your job is to extract a reusable capability / function from the provided knowledge content.
    
    ---
    Failure Context:
    {structured_failure}
    ---
    Knowledge Content:
    {knowledge_content}
    ---

    Task:
    Extract and adapt a Python function that resolves the failure.

    Rules:
    - Return ONLY valid Python code.
    - No Markdown.
    - No explanation.
    - You must define a function named:
    validate_nested_schema(data, schema)
    - Function must handle:
      - Missing nested fields.
      - Type mismatches.
    - Must be self-contained.
    """;

    print("[LLM] Requesting function extraction...");

    response = planner.call_raw(prompt);
    generated_code = response.strip();

    print("\n[LLM Generated Code]\n");
    print(generated_code);

    # Step 2 - Sandbox Execution

    # Step 3 - Build Structured Skill Object

    ## WIP - More Code Coming ## 


#####################################################################

def approval_gate_tool(context):
    print("Awaiting human approval...")
    approval = input("Approve new skill? (y/n): ")
    if approval.lower() == "y":
        return {"status": "success"}
    return {"status": "failed"}

def register_skill_tool(context):
    print("Registering new skill into registry...")
    return {"status": "success"}

print("# Step 3: Mock Tool Implementations completed");

#####################################################################
# Step 4: Node Model
#####################################################################

class Node:
    def __init__(self, node_id, node_type, metadata = None):
        self.id = node_id;
        self.type = node_type;
        self.metadata = metadata or {};
        self.status = "pending"; 
        # This can toggle between pending | running | complete | failed

    def __repr__(self):
        return f"Node(id={self.id}, type={self.type}, status={self.status})";

print("# Step 4: Node Model Defined");

#####################################################################
# Step 5: Workflow Graph
#####################################################################

class WorkflowGraph:
    def __init__(self):
        self.nodes = {};
        self.edges = defaultdict(list); # from_node -> [to_nodes]
        self.reverse_edges = defaultdict(list); # to_node -> [from_nodes]

    ##################################
    # Step 5A: Node & Edge Management
    ##################################

    def add_node(self, node):
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists");
        self.nodes[node.id] = node;

    def add_edge(self, from_node, to_node):
        if from_node not in self.nodes or to_node not in self.nodes:
            raise ValueError("Both nodes must exist before adding an edge");
        self.edges[from_node].append(to_node);
        self.reverse_edges[to_node].append(from_node);
    
    def remove_edge(self, from_node, to_node):
        if to_node in self.edges[from_node]:
            self.edges[from_node].remove(to_node);
        if from_node in self.reverse_edges[to_node]:
            self.reverse_edges[to_node].remove(from_node);
    
    print("# Step 5A: Node & Edge Management Done");

    ##################################
    # Step 5B: Execution Helpers
    ##################################

    def get_next_executable_nodes(self):
        """
        A node is executable if:
        - status == "pending"
        - all parents are "complete"
        """
        executable = [];
        for node_id, node in self.nodes.items():
            if node.status != "pending":
                continue;

            parents = self.reverse_edges[node_id];
            if all(self.nodes[p].status == "complete" for p in parents):
                executable.append(node_id);

        return executable;

    def mark_complete(self, node_id):
        self.nodes[node_id].status = "complete";

    def mark_failed(self, node_id):
        self.nodes[node_id].status = "failed";

    print("# Step 5B: Execution Helpers Created");

    ##################################
    # Step 5C: Subgraph Injection
    ##################################

    def inject_subgraph_after(self, after_node_id, subgraph_nodes, subgraph_edges):
        
        """
        Injects a subgraph after `after_node_id`
        Rewires outgoing edges of after_node to the entry node of the subgraph
        """
        if after_node_id not in self.nodes:
            raise ValueError("after_node_id does not exist");

        # Capture original outgoing edges
        original_children = list(self.edges[after_node_id]);

        # Remove existing outgoing edges
        for child in original_children:
            self.remove_edge(after_node_id, child);

        # Add subgraph nodes
        for node in subgraph_nodes:
            self.add_node(node);

        # Add subgraph edges
        for from_node, to_node in subgraph_edges:
            self.add_edge(from_node, to_node);

        # Connect after_node to subgraph entry
        entry_node_id = subgraph_nodes[0].id;
        self.add_edge(after_node_id, entry_node_id);

        # Find subgraph exit node(s)
        subgraph_node_ids = {node.id for node in subgraph_nodes};
        exit_nodes = \
            [
                node_id for node_id in subgraph_node_ids \
                if not any(child in subgraph_node_ids for child in self.edges[node_id])
            ];

        # Reconnect exit nodes to original children
        for exit_node in exit_nodes:
            for child in original_children:
                self.add_edge(exit_node, child);

    print("# Step 5C: Subgraph Injection Functionality Defined");

    ##################################
    # Step 5D: Graph Printing
    ##################################

    def print_graph(self):
        
        print("\nCurrent Workflow Graph:");

        printed_edges = set();
        terminal_nodes = [];

        for node_id in self.nodes:
            children = self.edges[node_id];
            status = self.nodes[node_id].status;
            
            if children:
                for child in children:
                    print(f"[{node_id} ({status})] --> [{child} ({self.nodes[child].status})]");
                    printed_edges.add(child);
            else:
                terminal_nodes.append(node_id);
        
        for node_id in terminal_nodes:
            if node_id not in printed_edges:
                print(f"[{node_id} ({self.nodes[node_id].status})]");
        
        print("-" * 50);

    print("# Step 5D: Graph Printing Functionality Defined");

#####################################################################
# Step 6: Hardcoded Test Simulation
#####################################################################

def simulate_workflow():
    
    graph = WorkflowGraph();
    registry = ToolRegistry();

    # Register initial tools
    registry.register("run_tests", run_tests_tool);
    registry.register("fix_code", fix_code_tool);
    registry.register("verify", verify_tool);

    # The initial graph was manually hardcoded in earlier iterations
    # Now it is being dynamically created by the LLM (Grok)

    # graph.add_node(Node("run_tests", "tool")); graph.add_node(Node("fix_code", "tool"));
    # graph.add_edge("run_tests", "fix_code");
    # graph.add_node(Node("verify", "tool"));
    # graph.add_edge("fix_code", "verify");

    # Dynamic Workflow Graph Creation below between the # lines

    ###############################################################

    planner = GrokPlanner();

    task_description = "Fix failing tests in a Python repository.";
    available_tools = ["run_tests", "fix_code", "verify"];

    print("\n[LLM] Requesting dynamic workflow generation from Grok...\n");

    workflow_json = planner.propose_workflow\
    (
        task_description,
        available_tools
    );

    print("[LLM] Workflow proposal received:");
    print(workflow_json);
    print("-" * 60);

    # Building the graph dynamically with an LLM (Grok)
    for node_name in workflow_json["nodes"]:
        graph.add_node(Node(node_name, "tool"));
    for edge in workflow_json["edges"]:
        graph.add_edge(edge[0], edge[1]);

    ###############################################################

    graph.print_graph();

    engine = ExecutionEngine(graph, registry);
    engine.context["planner"] = planner;
    
    print("\n" + "="*70);
    print("EXECUTION PHASE");
    print("="*70);
    
    result = engine.run();
    analysis = engine.context.get("analysis");

    print("\n[ENGINE] Mutation decision validated.");
    print(f"[ENGINE] Proposed Capability Gap: {analysis['capability_gap']}");
    print(f"[ENGINE] Proposed Action: {analysis['action']}");
    print("-" * 60);

    # Older "if" condition - before dynamic LLM capabilities
    # if result == "failure" and engine.context["capability_gap"]:

    if result == "failure" and analysis and analysis["action"] == "inject_capability_subgraph":

        print("\n" + "="*70);
        print("STRUCTURAL MUTATION PHASE");
        print("="*70);

        print("\nCapability gap detected. Injecting acquisition subgraph...\n");

        # Mark fix_code as structurally handled
        graph.nodes["fix_code"].status = "complete"; 

        # Register new tools
        registry.register("read_local_knowledge", read_local_knowledge_tool);
        registry.register("sandbox_experiment", sandbox_experiment_tool);
        registry.register("approval_gate", approval_gate_tool);
        registry.register("register_skill", register_skill_tool);

        sub_nodes = \
            [
            Node("read_local_knowledge", "tool"),
            Node("sandbox_experiment", "tool"),
            Node("approval_gate", "control"),
            Node("register_skill", "tool"),
            ];

        sub_edges = \
            [
            ("read_local_knowledge", "sandbox_experiment"),
            ("sandbox_experiment", "approval_gate"),
            ("approval_gate", "register_skill"),
            ];

        graph.inject_subgraph_after("fix_code", sub_nodes, sub_edges);

        graph.print_graph();

        print("\nResuming execution...\n");
        engine = ExecutionEngine(graph, registry);

        print("\n" + "="*70);
        print("RESUMED EXECUTION");
        print("="*70);

        engine.run();

    print("\nFinal Graph State:");
    graph.print_graph();

print("# Step 6: Hardcoded Test Simulation Created");
    
#####################################################################
# Entry Point
#####################################################################

if __name__ == "__main__":
    simulate_workflow();