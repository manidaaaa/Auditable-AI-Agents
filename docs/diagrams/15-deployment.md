# 15. Deployment diagram

**Notation:** UML deployment  
**Project:** Auditable AI Agents

## What it shows

What runs where during development and the demo. Everything runs on one laptop; the two cloud services are optional or only used for pushing code.

## Diagram

```mermaid
flowchart LR
  subgraph laptop["Laptop - Apple M5 Pro, 24 GB"]
    subgraph py["Python 3.14 process (.venv)"]
      app["src/ app, domain, core<br/>tests and scripts"]
    end
    subgraph node["Node.js 26.5 process"]
      hh["Hardhat node<br/>local Ethereum chain"]
      sc["AuditAnchor contract"]
    end
    subgraph ol["Ollama server process"]
      model["qwen3:8b model, about 5 GB"]
    end
    files[("Files: JSONL logs,<br/>contract artifacts, documents")]
  end
  gh["GitHub repository<br/>Auditable-AI-Agents"]
  api["Anthropic API<br/>optional, needs an API key"]
  app -- "JSON-RPC over HTTP, local port" --> hh
  hh --- sc
  app -- "HTTP, port 11434" --> model
  app -- "read and write" --> files
  app -. "HTTPS, optional" .-> api
  files -. "git push over HTTPS" .-> gh
```

![Deployment diagram](images/15-deployment.png)

## Where it comes from

`local_chain()` starts the Hardhat node on a free local port for each demo run; `make_ollama_llm` talks to `127.0.0.1:11434`. The Anthropic adapter is unit-tested but has not been run live.
