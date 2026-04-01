# MASTER INSTRUCTIONS FOR GITHUB COPILOT AGENT — IEEE THESIS PROGRESS REPORT GENERATION

You are working on a Master's Thesis project involving quantum computing using the Qiskit framework and IBM Quantum hardware. Your task is to generate a Progress Report 1 in strict IEEE conference paper format using the Overleaf template provided in the "IEEE_Conference_Template_1" folder.

You MUST follow these instructions exactly. Do not make assumptions, do not fabricate results, and do not generate placeholder or fictional scientific claims.

---

## PRIMARY OBJECTIVE

Generate a complete Progress Report 1 (1000–1500 words) in IEEE LaTeX format, fully compatible with the Overleaf IEEE template provided in the folder "IEEE_Conference_Template_1".

The report must strictly follow the grading criteria:

• Completeness
• Clarity
• Alignment with thesis objectives and syllabus

---

## MANDATORY SOURCE FILES — USE ONLY THESE

You MUST extract information exclusively from the following project files and folders:

1. prevWork folder
   → Use for Related Work section
   → Extract literature review and contextual scientific background

2. Qiskit.ipynb
   → This is the PRIMARY source of experimental methodology
   → Extract:

   * Implemented quantum circuits
   * Algorithms used
   * Simulation and hardware execution setup
   * IBM Quantum usage
   * Benchmarking methods
     → DO NOT invent experiments not present in notebook

3. results folder
   → Use for Results and Analysis section
   → Extract:

   * Graphs
   * Experimental data
   * Observed performance metrics
     → DO NOT generate fictional or estimated data

4. README.md
   → Use for:

   * Project overview
   * Objectives
   * Current progress summary
   * Research goals

5. PDF-Template4Report
   → Use only as reference for structure and clarity expectations

6. IEEE_Conference_Template_1
   → This MUST be used as the LaTeX template
   → Final output must be fully compatible with Overleaf IEEE format

---

## ABSOLUTE PROHIBITIONS

You MUST NOT:

• Fabricate experimental results
• Simulate fake IBM Quantum outputs
• Invent datasets
• Invent performance metrics
• Invent literature references not present in prevWork folder
• Modify scientific meaning of existing results

If information is missing, state clearly:

"Further experimental validation is ongoing."

---

## REQUIRED IEEE STRUCTURE

You MUST generate LaTeX code structured exactly like this:

• Title
• Authors
• Abstract
• Keywords

• I. Introduction

* Background
* Research problem
* Thesis objective

• II. Related Work

* Based strictly on prevWork folder

• III. Methodology

* Based strictly on Qiskit.ipynb
* Explain quantum circuits
* Explain algorithms
* Explain IBM Quantum usage

• IV. Experimental Setup

* Explain simulation vs real hardware execution
* Explain benchmarking methodology

• V. Results and Analysis

* Use ONLY data from results folder
* Interpret actual outcomes

• VI. Discussion

* Progress achieved
* Challenges encountered
* Limitations

• VII. Conclusion and Future Work

* Next research steps
* Planned improvements

---

## OUTPUT FORMAT REQUIREMENTS

You MUST output:

• Fully functional IEEE LaTeX (.tex)
• Overleaf-ready
• No syntax errors
• No placeholders like "TODO"
• No pseudocode in report
• Fully formatted IEEE sections

---

## WRITING STYLE REQUIREMENTS

Use STRICT academic tone:

DO:

• Use formal scientific language
• Use evidence-based statements
• Use passive voice where appropriate
• Be precise and technical

DO NOT:

• Use conversational tone
• Use personal pronouns like "I", "we"
• Use vague claims

---

## NOTEBOOK EXECUTION RULES (CRITICAL)

If modifying or extending Qiskit.ipynb:

You MUST:

• Write code that runs on real IBM Quantum hardware
• Use Qiskit Runtime API
• Do NOT fabricate outputs
• Leave execution cells ready for runtime execution
• Do NOT insert fake output cells

---

## FINAL OUTPUT REQUIREMENT

Output ONLY:

• Complete IEEE LaTeX source code
• Compatible with Overleaf template
• Ready for compilation

DO NOT output explanations, comments, or analysis outside LaTeX file.

---

END OF INSTRUCTIONS
