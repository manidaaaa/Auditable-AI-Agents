# 02. Component diagram

**Notation:** UML component  
**Project:** Auditable AI Agents

## What it shows

The modules, the layer each belongs to, and what depends on what. Arrows point from the user of a module to the module it uses. `domain` and `core` have no file, network or console access.

## Diagram

```mermaid
flowchart TB
  subgraph app["app layer - side effects"]
    run_demo["run_demo.py"]
    chain_client["chain_client.py"]
    logstore["logstore.py"]
    ollama_llm["ollama_llm.py"]
    anthropic_llm["anthropic_llm.py"]
  end
  subgraph domain["domain layer - pure functions"]
    agent["agent.py"]
    audit["audit.py"]
    merkle["merkle.py"]
    chain["chain.py"]
  end
  subgraph core["core layer"]
    hashing["hashing.py"]
  end
  subgraph contracts["contracts"]
    anchor["AuditAnchor.sol"]
  end
  subgraph external["external services"]
    hardhat["Hardhat node<br/>local chain"]
    ollama["Ollama server<br/>qwen3:8b"]
    anthropic["Anthropic API<br/>optional, needs key"]
  end
  run_demo --> agent
  run_demo --> audit
  run_demo --> chain_client
  run_demo --> logstore
  run_demo --> ollama_llm
  run_demo --> anthropic_llm
  chain_client --> audit
  chain_client --> hardhat
  logstore --> chain
  agent --> chain
  audit --> chain
  audit --> merkle
  chain --> hashing
  hardhat -. hosts .-> anchor
  chain_client -. "web3 calls" .-> anchor
  ollama_llm --> ollama
  anthropic_llm --> anthropic
```

![Component diagram](images/02-component.png)

## Where it comes from

`src/core`, `src/domain`, `src/app` and `contracts/`. Dotted arrows: the contract runs inside the Hardhat node and is called through web3.
