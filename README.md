# agent-capabilities

Independent, modular capability layer for **Agent-Core**.

---

## 1. Overview

`agent-capabilities` defines and implements the infrastructure required for external capabilities and modules (e.g. GitHub, Browser, Filesystem, Communication) to be safely discovered, validated, invoked, observed, and evolved independently of the agent kernel.

### Architectural Analogy
- **Agent-Core** = kernel
- **agent-capabilities** = device/module ecosystem

---

## 2. Architectural Boundary & Non-Negotiables

Preserve strict separation between core reasoning and capability execution:

```text
Agent-Core (kernel)
    │
    │ capability contract / invocation boundary
    ▼
agent-capabilities (framework v1)
    │
    ├── Echo capability (framework proof)
    ├── GitHub capability (future)
    ├── Browser capability (future)
    ├── Filesystem capability (future)
    └── Communication capability (future)
```

### What this repository IS NOT:
- Not an agent brain/kernel
- Not a memory or state container
- Not an identity or philosophy manager
- Not a strategy learning system
- Not an autonomous agent cognition engine

The framework communicates through explicit, typed contracts and interfaces. It has zero hard dependencies on `agent-core`.

---

## 3. Current Framework Status

**Version:** `v1.0.0` (Framework Foundation Only)

- [x] **Capability Contracts** (`Capability`, `CapabilityMetadata`, `CapabilityRequest`, `CapabilityResult`, `CapabilityContext`)
- [x] **Lifecycle Management** (`REGISTERED` -> `AVAILABLE` -> `ENABLED` -> `DISABLED`)
- [x] **Capability Registry** (Thread-safe registration, lookup, lifecycle transitions)
- [x] **Invocation Boundary / Dispatcher** (Input validation, lifecycle checks, permission boundary, execution)
- [x] **Permission Boundary** (Explicit permission declaration and runtime enforcement)
- [x] **Typed Error Model** (`CapabilityError`, `CapabilityNotFoundError`, `PermissionDeniedError`, etc.)
- [x] **Lightweight Observability** (`ExecutionRecord` events emitted per invocation)
- [x] **Proof-of-Concept Capability** (`EchoCapability`)

> **Note:** Concrete external capabilities such as GitHub, Browser, Filesystem, Coding, and Communication modules are future extensions. Only `EchoCapability` is implemented as a framework proof in v1.

---

## 4. Architecture & Workflow

When a request is dispatched, the capability pipeline executes as follows:

```text
CapabilityRequest
   │
   ▼
1. Context Resolution & ID Assignment
   │
   ▼
2. Capability Lookup (Registry)
   │
   ▼
3. Lifecycle Check (Status != DISABLED)
   │
   ▼
4. Supported Action Check
   │
   ▼
5. Permission Boundary Check (Required vs Granted Permissions)
   │
   ▼
6. Input Validation (capability.validate)
   │
   ▼
7. Execution (capability.execute)
   │
   ▼
8. Observability Event Emission (ExecutionRecord)
   │
   ▼
CapabilityResult
```

---

## 5. Usage Example

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

# 3. Formulate request & context
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

## 6. Running Tests & Quality Gates

### Run Test Suite
```bash
pytest
```

All 27 unit and architecture tests verify:
- Registry operations (register, lookup, list, unregister, duplicate prevention)
- Lifecycle transition enforcement
- Invocation boundary pipeline & validation
- Permission checking (no self-elevation, missing permissions rejected)
- Typed error handling
- Output determinism
- Architectural boundary (no Agent-Core imports)
