# Ingestion Report

## Document

- Document ID: `d2d98440-2efd-489f-bb8b-ead7b6f45ece`
- Filename: `2604.17091v1.pdf`
- Title: GenericAgent: A Token-Efficient Self-Evolving LLM Agent via Contextual Information Density Maximization (V1.0)
- Author: Shenzhen Aquaintelling Technology Fudan University
- Source Type: `scientific_paper`
- Trust Level: `verified`
- Parser: `pymupdf+grobid`
- Parser Version: `1.28.0`
- Created At: `2026-07-07 21:23:34.562490+00:00`

## Extraction Metrics

- Total Pages in PDF: 47
- Extracted Pages: 47
- Skipped Pages: 0
- Total Characters: 153426
- Average Characters/Page: 3264.38
- Section Blocks: 90

## Section Blocks

| # | Section | Pages | Characters | Preview |
|---|---|---|---:|---|
| 1 | abstract | 1 | 1323 | ABSTRACT Long-horizon large language model (LLM) agents are fundamentally limited by context. As interactions become longer, tool descriptio... |
| 2 | introduction | 1 | 6135 | Introduction Introduction The recent emergence of agentic systems such as Claude Code [1] , OpenAI Codex [2] , and OpenClaw [3] marks a qual... |
| 3 | genericagent | 1-47 | 25 | GenericAgent GenericAgent... |
| 4 | design_principles | 3 | 6122 | Design Principles Design Principles Context information density is all a self-evolving LLM agent needs. The performance of LLM-based agents... |
| 5 | tool_minimality | 4 | 1856 | Tool Minimality Tool Minimality To maximize context information density before task execution begins, GA constrains its tool design to the m... |
| 6 | hierarchical_memory | 5 | 1843 | Hierarchical Memory Hierarchical Memory To continuously maintain context information density during task execution, GA adopts a systematic a... |
| 7 | self_evolution_as_experience_consolidation | 5 | 2755 | Self-Evolution as Experience Consolidation Self-Evolution as Experience Consolidation To enable context information density to improve conti... |
| 8 | context_truncation_and_compression | 6 | 1769 | Context Truncation and Compression Context Truncation and Compression Many agent frameworks rely on extended context windows of up to 1M tok... |
| 9 | overview_of_genericagent | 7 | 2165 | Overview of GenericAgent Overview of GenericAgent Guided by the principles above, we develop GenericAgent, a general-purpose self-evolving L... |
| 10 | core_components_of_genericagent | 1-47 | 302 | Core Components of GenericAgent Core Components of GenericAgent Building on the principles established in Section 2.1, we describe how GA re... |
| 11 | minimal_atomic_toolset | 7 | 2197 | Minimal Atomic Toolset Minimal Atomic Toolset GA's toolset adheres to a minimalist design: a small set of atomic primitives that can be comp... |
| 12 | capability_boundaries_and_execution_control | 8 | 2647 | Capability boundaries and execution control. Capability boundaries and execution control. GA enforces a clear permission hierarchy via the i... |
| 13 | hierarchical_memory_architecture | 8 | 4634 | Hierarchical Memory Architecture Hierarchical Memory Architecture To maximize context information density during task execution, GA organize... |
| 14 | self_evolution_capability_in_ga | 9 | 1039 | Self-Evolution Capability in GA Self-Evolution Capability in GA GA implements self-evolution as an explicit and transparent process rather t... |
| 15 | how_the_evolutionary_trajectory_is_maintained_failure_escalation | 10 | 1031 | How the evolutionary trajectory is maintained: failure escalation. How the evolutionary trajectory is maintained: failure escalation. To pre... |
| 16 | context_truncation_and_compression | 10 | 3153 | Context Truncation and Compression Context Truncation and Compression The underlying model that GA relies on operates within a finite contex... |
| 17 | stage_3_message_eviction | 1-47 | 1570 | Stage 3: Message eviction. Stage 3: Message eviction. When a new message causes the total history length (C H ) to exceed the character budg... |
| 18 | auxiliary_tool_schema_elision | 1-47 | 578 | Auxiliary: tool-schema elision. Auxiliary: tool-schema elision. When using the text-protocol path, if a tool's definition hasn't changed fro... |
| 19 | from_minimal_architecture_to_emergent_capabilities | 1-47 | 101 | From Minimal Architecture to Emergent Capabilities From Minimal Architecture to Emergent Capabilities... |
| 20 | minimal_architecture | 11 | 1825 | Minimal Architecture Minimal Architecture GenericAgent exhibits architectural minimality in two dimensions: code minimality and interface mi... |
| 21 | compositional_capabilities | 1-47 | 504 | Compositional Capabilities Compositional Capabilities A recurring pattern in agent framework design is to introduce dedicated subsystems for... |
| 22 | subagent_dispatch | 1-47 | 886 | Subagent Dispatch. Subagent Dispatch. Once the agent can be invoked programmatically via CLI, subagents follow naturally. To handle complex... |
| 23 | reflect_mode | 1-47 | 1664 | Reflect Mode. Reflect Mode. Similarly, once the CLI can be invoked programmatically, daemon-like behavior emerges naturally. GA's Reflect Mo... |
| 24 | autonomous_exploration_capability | 12 | 2288 | Autonomous Exploration Capability Autonomous Exploration Capability In real long-horizon environments, relying solely on user interaction to... |
| 25 | exploration_task_generation | 1-47 | 1596 | Exploration Task Generation. Exploration Task Generation. A core question in autonomous exploration is determining what to explore. When no... |
| 26 | execution_and_consolidation | 1-47 | 1274 | Execution and Consolidation. Execution and Consolidation. Each autonomous task proceeds through a fixed sequence: context loading (retrieve... |
| 27 | exploration_quality_assessment | 1-47 | 1757 | Exploration Quality Assessment. Exploration Quality Assessment. The second core question is evaluating exploration quality. After each batch... |
| 28 | evaluation | 14 | 226 | Evaluation Evaluation In this section, we evaluate the GenericAgent to systematically analyze its system behavior, resource management, and... |
| 29 | task_completion_and_token_efficiency | 1-47 | 232 | Task Completion and Token Efficiency: Task Completion and Token Efficiency: We measure overall success rates and token consumption across di... |
| 30 | tool_use_efficiency | 1-47 | 210 | Tool-Use Efficiency: Tool-Use Efficiency: We analyze the minimal atomic-tool design to assess how a restricted tool space impacts the abilit... |
| 31 | memory_system_effectiveness | 1-47 | 230 | Memory System Effectiveness: Memory System Effectiveness: We investigate the memory management mechanisms to examine their function in long-... |
| 32 | self_evolution_capability | 1-47 | 251 | Self-Evolution Capability: Self-Evolution Capability: We evaluate the self-evolution pipeline to observe the process and effects of compress... |
| 33 | web_browsing_capability | 1-47 | 221 | Web Browsing Capability: Web Browsing Capability: We use open-ended web tasks to test the framework's end-to-end navigation, multi-hop retri... |
| 34 | task_completion_and_token_efficiency | 1-47 | 654 | Task completion and token efficiency Task completion and token efficiency This section evaluates the fundamental execution capability and re... |
| 35 | setup | 15 | 693 | Setup Setup Baseline. To contextualize the performance of GA, we establish a comparative evaluation against three representative agent syste... |
| 36 | benchmark | 1-47 | 1151 | Benchmark. Benchmark. The evaluation is conducted on three distinct benchmarks to assess distinct facets of agent capabilities under complex... |
| 37 | results | 1-47 | 15 | Results Results... |
| 38 | ga_consistently_achieves_state_of_the_art_or_highly_competitive_task_completion_rates | 15 | 856 | GA consistently achieves state-of-the-art or highly competitive task completion rates. GA consistently achieves state-of-the-art or highly c... |
| 39 | tool_use_efficiency | 16 | 656 | Tool-use efficiency Tool-use efficiency This section evaluates the impact of tool space design on an agent's operational efficiency and prob... |
| 40 | setup | 16 | 596 | Setup Setup Baseline. All compared systems use the same backbone model, Claude Sonnet 4.6. We evaluate three representative agents: (1) GA,... |
| 41 | atomic_tool_generalization | 1-47 | 651 | Atomic Tool Generalization Atomic Tool Generalization GA can solve complex long-horizon tasks through compositions of atomic tools rather th... |
| 42 | ga_reduces_token_overhead_while_preserving_task_performance | 17 | 619 | GA reduces token overhead while preserving task performance. GA reduces token overhead while preserving task performance. Although it matche... |
| 43 | tool_usage_distribution | 1-47 | 1029 | Tool Usage Distribution Tool Usage Distribution Tool usage is highly concentrated in a few high-frequency tools, while the remaining long-ta... |
| 44 | memory_system_effectiveness | 18 | 695 | Memory System Effectiveness Memory System Effectiveness This section evaluates the architectural design and operational impact of GA's hiera... |
| 45 | continuous_efficiency_improvement | 1-47 | 67 | Continuous Efficiency Improvement Continuous Efficiency Improvement... |
| 46 | setup | 1-47 | 1486 | Setup. Setup. To evaluate whether the Condensed Memory framework enables GA to improve through continuous real-world use, we assess the perf... |
| 47 | effectiveness_of_condensed_memory | 1-47 | 929 | Effectiveness of Condensed memory Effectiveness of Condensed memory Setup. To examine whether retaining only decision-critical rules yields... |
| 48 | results_filtered_high_density_memory_provides_optimal_behavioral_guidance_while_drastically_minimizing_contextual_burden | 19 | 1027 | Results. Filtered, high-density memory provides optimal behavioral guidance while drastically minimizing contextual burden. Results. Filtere... |
| 49 | long_term_fact_retention | 19 | 1853 | Long-Term Fact Retention Long-Term Fact Retention Setup. This experiment examines whether GA has long term factual memory and whether it can... |
| 50 | context_explosion_prevention | 20 | 483 | Context Explosion Prevention Context Explosion Prevention Setup. To evaluate whether GA can prevent memory explosion under long term use and... |
| 51 | results | 1-47 | 659 | Results. Results. Hierarchical retrieval strictly isolates idle memory from the active prompt, eliminating the risk of context explosion. As... |
| 52 | self_evolution_capability | 20 | 761 | Self-Evolution Capability Self-Evolution Capability This section evaluates the framework's capacity for self-evolution, specifically its abi... |
| 53 | setup | 21 | 362 | Setup Setup Baseline. To rigorously evaluate the cross-task generalization of the self-evolution mechanism, we establish a direct comparison... |
| 54 | iteration_wise_efficiency_trajectory | 1-47 | 1050 | Iteration-Wise Efficiency Trajectory Iteration-Wise Efficiency Trajectory The nine-round trajectory shows a phase transition from high-entro... |
| 55 | most_of_the_efficiency_gain_comes_from_eliminating_repeated_reasoning_cycles_rather_than_merely_shortening_individual_responses | 22 | 1071 | Most of the efficiency gain comes from eliminating repeated reasoning cycles rather than merely shortening individual responses. Most of the... |
| 56 | cross_task_efficiency_gains | 1-47 | 2963 | Cross-Task Efficiency Gains Cross-Task Efficiency Gains GA's self-evolving memory mechanism consistently improves efficiency across tasks ra... |
| 57 | web_browsing_capability | 1-47 | 687 | Web Browsing Capability Web Browsing Capability This section evaluates the agent's capability to navigate, search, and reason within open-en... |
| 58 | setup | 23 | 307 | Setup Setup Baseline. We compare GA against OpenClaw to contrast their architectural approaches in handling highly dynamic environments. To... |
| 59 | benchmark | 1-47 | 753 | Benchmark. Benchmark. We evaluate web browsing proficiency across three diverse benchmarks, ranging from atomic interactions to open-ended r... |
| 60 | metrics | 1-47 | 384 | Metrics. Metrics. Performance is evaluated using a normalized Score (0-1). The scoring protocols are tailored to each benchmark: automatic e... |
| 61 | results | 1-47 | 581 | Results Results GA consistently outperforms the baseline in web navigation and reasoning while operating at a fraction of the token cost. As... |
| 62 | ga_s_multi_stage_compression_pipeline_provides_an_advantage_in_long_horizon_multi_hop_web_search_tasks | 1-47 | 1218 | GA's multi-stage compression pipeline provides an advantage in long-horizon, multi-hop web search tasks. GA's multi-stage compression pipeli... |
| 63 | discussion | 24 | 328 | Discussion Discussion We highlight key findings from the development of GenericAgent that we believe are broadly relevant to the design of l... |
| 64 | context_information_density_is_a_structural_constraint_for_all_llm_based_agent_systems | 24 | 3776 | Context information density is a structural constraint for all LLM-based agent systems. Context information density is a structural constrai... |
| 65 | permissions_define_the_ceiling_of_agent_capability | 25 | 2136 | Permissions define the ceiling of agent capability. Permissions define the ceiling of agent capability. What an agent can perceive, what it... |
| 66 | related_work | 1-47 | 803 | Related Work Related Work 5 Prior work on autonomous LLM agents has advanced several ingredients of long-horizon execution, including action... |
| 67 | llm_based_agent_systems_and_action_interfaces | 25 | 1967 | LLM-Based Agent Systems and Action Interfaces LLM-Based Agent Systems and Action Interfaces LLM agents have evolved from prompt-level reason... |
| 68 | memory_and_context_management | 26 | 1642 | Memory and Context Management Memory and Context Management A second line of work studies how agents retain only behaviorally useful informa... |
| 69 | self_evolution_and_experience_distillation | 26 | 1655 | Self-Evolution and Experience Distillation Self-Evolution and Experience Distillation Research on self-evolving agents asks how repeated exe... |
| 70 | conclusion | 27 | 1608 | Conclusion Conclusion We present GenericAgent (GA), a self-evolving general-purpose LLM agent built around a single design principle: contex... |
| 71 | web_browsing_visualization | 1-47 | 206 | Web Browsing Visualization Web Browsing Visualization Figure 6 provides a visual comparison of token consumption and normalized performance... |
| 72 | case_studies | 34 | 1296 | Case Studies Case Studies We present four representative cases corresponding to the main evaluation dimensions. For readability, the cases a... |
| 73 | case_a1_tool_use_api_procurement_workflow | 1-47 | 585 | Case A1. Tool Use: API Procurement Workflow Case A1. Tool Use: API Procurement Workflow Purpose and Task Setup Purpose: to examine whether G... |
| 74 | case_a2_memory_dangerous_goods_hazard_classification | 1-47 | 652 | Case A2. Memory: Dangerous-Goods Hazard Classification Case A2. Memory: Dangerous-Goods Hazard Classification Purpose and Task Setup Purpose... |
| 75 | inputs_sds_label_text_handling_storage_guidance_transportation_requirements_disposal_guidance | 1-47 | 257 | Inputs: -SDS label text -handling/storage guidance -transportation requirements -disposal guidance Inputs: -SDS label text -handling/storage... |
| 76 | artifact_1_condensed_memory | 1-47 | 4240 | Artifact 1: Condensed Memory Artifact 1: Condensed Memory Required rules: 1. First validate product_id. It must be resolvable and follow for... |
| 77 | observed_outcome | 38 | 495 | Observed Outcome Observed Outcome The memory ablation becomes visually intuitive once the three variants are shown side by side. The condens... |
| 78 | case_a3_self_evolution_github_pr_research | 1-47 | 87 | Case A3. Self-Evolution: GitHub PR Research Case A3. Self-Evolution: GitHub PR Research... |
| 79 | purpose_and_task_setup | 38 | 4104 | Purpose and Task Setup Purpose and Task Setup Purpose: to examine whether repeated execution can be distilled into reusable assets, we provi... |
| 80 | observed_outcome | 1-47 | 361 | Observed Outcome Observed Outcome LangChain verification case (2026-04-08): python3 github_pr_analyzer.py langchain-ai/langchain -doc-url ht... |
| 81 | case_a4_web_browsing_browsecomp_zh_reasoning_chain | 1-47 | 1809 | Case A4. Web Browsing: BrowseComp-ZH Reasoning Chain Case A4. Web Browsing: BrowseComp-ZH Reasoning Chain Purpose and Task Setup Purpose: to... |
| 82 | case_b1_cross_device_control_mobile_food_ordering_via_adb | 1-47 | 970 | Case B1. Cross-Device Control: Mobile Food Ordering via ADB Case B1. Cross-Device Control: Mobile Food Ordering via ADB Purpose and Task Set... |
| 83 | case_b3_autonomous_operation_unsupervised_overnight_session | 1-47 | 1112 | Case B3. Autonomous Operation: Unsupervised Overnight Session Case B3. Autonomous Operation: Unsupervised Overnight Session Purpose and Task... |
| 84 | artifact_1_autonomous_task_inventory_rounds_125_140 | 1-47 | 111 | Artifact 1: Autonomous Task Inventory (Rounds 125-140+) Artifact 1: Autonomous Task Inventory (Rounds 125-140+)... |
| 85 | category_1_system_security_audit | 1-47 | 719 | Category 1 --System Security Audit: Category 1 --System Security Audit: -Scanned all listening ports on the host machine. -Discovered a stoc... |
| 86 | category_4_environment_hygiene | 1-47 | 328 | Category 4 --Environment Hygiene: Category 4 --Environment Hygiene: -Audited the Python environment: found 294 installed packages occupying... |
| 87 | observed_outcome | 1-47 | 876 | Observed Outcome Observed Outcome Over approximately 15+ autonomous rounds, GA performed system security auditing, created three reusable ut... |
| 88 | case_b4_remote_infrastructure_ssh_based_file_server_deployment | 1-47 | 888 | Case B4. Remote Infrastructure: SSH-Based File Server Deployment Case B4. Remote Infrastructure: SSH-Based File Server Deployment Purpose an... |
| 89 | artifact_1_execution_trace | 1-47 | 55 | Artifact 1: Execution Trace Artifact 1: Execution Trace... |
| 90 | observed_outcome | 1-47 | 713 | Observed Outcome Observed Outcome In this session, GA completed the full DevOps workflow: SSH connection, dependency installation on the rem... |

## Page Summary

| Page | Characters |
|---:|---:|
| 1 | 3241 |
| 2 | 4608 |
| 3 | 4377 |
| 4 | 2967 |
| 5 | 4754 |
| 6 | 2746 |
| 7 | 4600 |
| 8 | 5129 |
| 9 | 4381 |
| 10 | 4317 |
| 11 | 3616 |
| 12 | 4149 |
| 13 | 4289 |
| 14 | 3934 |
| 15 | 3240 |
| 16 | 3378 |
| 17 | 4034 |
| 18 | 3217 |
| 19 | 3852 |
| 20 | 3220 |
| 21 | 3743 |
| 22 | 4153 |
| 23 | 4257 |
| 24 | 4191 |
| 25 | 4661 |
| 26 | 4543 |
| 27 | 1299 |
| 28 | 3933 |
| 29 | 4280 |
| 30 | 506 |
| 31 | 2821 |
| 32 | 1015 |
| 33 | 1683 |
| 34 | 2126 |
| 35 | 2505 |
| 36 | 2171 |
| 37 | 2231 |
| 38 | 3025 |
| 39 | 2065 |
| 40 | 2255 |
| 41 | 2921 |
| 42 | 2831 |
| 43 | 2920 |
| 44 | 2965 |
| 45 | 2581 |
| 46 | 2761 |
| 47 | 935 |