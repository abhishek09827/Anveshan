# Anveshan - Work In progress

You're building a tool that answers one question a developer asks constantly while building AI agents:

"Why did my agent do that?"

When an AI agent runs - whether it's a RAG pipeline, a ReAct loop, a multi-agent crew - it produces traces. A trace is the full record of everything that happened: which LLM was called, with what prompt, what it returned, which tool was invoked, how long each step took, whether anything errored.
The problem today is that these traces exist - OpenTelemetry already captures them - but they're unreadable. They come out as raw JSON. You can't see the shape of what happened, you can't tell if the LLM hallucinated, you can't compare two runs. You're debugging blind.
This project is the lens between raw traces and human understanding.

May include:
1.  Codex JSONL adapter 
