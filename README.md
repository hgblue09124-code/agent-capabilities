# agent-capabilities

Supplemental capability and adapter layer for **Agent-Core**.

---

## 1. Overview & Architectural Boundary

`agent-capabilities` defines and implements the infrastructure required for external capabilities and modules (e.g. GitHub, Browser, Filesystem, Communication) to be safely discovered, validated, invoked, observed, and evolved independently of the agent kernel.

### Strict Architectural Boundaries
- **Agent-Core** retains full authority over:
  - Identity, memory, cognition, reasoning, planning, strategy, policy, and autonomy.
- **agent-capabilities** provides:
  - Stable capability contracts, discovery registry, invocation boundary (dispatcher), permission validation, lifecycle rules, and execution record events.

```text
Agent-Core (Kernel / Authority)
    │
    │ Capability Contract / Invocation Boundary
    ▼
agent-capabilities (Hardened Framework v1)
    │
    ├── Echo capability (Framework proof)
    ├── GitHub capability (Future module)
    ├── Browser capability (Future module)
    └── Filesystem capability (Future module)
```

---

## 2. Framework v1 Hardening Summary

- **Observer Exception Semantics:** Observer listener errors are captured explicitly without silently swallowing exceptions or crashing capability execution.
- **True Immutability:** `CapabilityContext` and `CapabilityMetadata` enforce immutable data structures (`frozenset`, `tuple`, `MappingProxyType`) preventing capabilities from mutating context permissions, metadata, or cancellation settings.
- **Coherent Lifecycle Rules:** Execution requires `CapabilityStatus.ENABLED`. Unready states (`REGISTERED`, `AVAILABLE`) raise `CapabilityNotReadyError`, and `DISABLED` raises `CapabilityDisabledError`. Capabilities can be safely disabled and re-enabled.
- **Contract & Permission Boundary Validation:** Strict constructor input validation and immutable permission checking reject malformed requests or permission escalation attempts.
- **Zero Agent-Core Dependencies:** Operates strictly as a independent supplemental layer.

---

## 3. Usage Example

```python
from agent_capabilities.contracts import CapabilityContext, CapabilityRequest
from agent_capabilities.execution import CapabilityDispatcher
from agent_capabilities.examples import EchoCapability
from agent_capabilities.registry import CapabilityRegistry

# 1. Initialize registry and dispatcher
registry = CapabilityRegistry()
dispatcher = CapabilityDispatcher(registry)

# 2. Register & enable capability
echo_cap = EchoCapability()
registry.register(echo_cap)
registry.enable("echo")

# 3. Formulate immutable request & context
context = CapabilityContext(request_id="req-001", caller="agent-core")
request = CapabilityRequest(
    capability_id="echo",
    action="echo",
    input={"message": "Hello from Agent-Core!"},
)

# 4. Dispatch request
result = dispatcher.dispatch(request, context=context)

if result.success:
    print("Output:", result.output)
else:
    print("Error:", result.error)
```

---

## 4. CI / Quality Gates

Run complete test suite and package build:

```bash
pytest
python -m build
```
