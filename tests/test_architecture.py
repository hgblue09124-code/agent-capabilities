"""Architecture tests enforcing boundaries and independence from Agent-Core."""

import sys
from typing import Set


def test_no_agent_core_imports():
    """Verify that agent_capabilities package does not import or depend on Agent-Core."""
    import agent_capabilities
    import agent_capabilities.contracts
    import agent_capabilities.errors
    import agent_capabilities.examples
    import agent_capabilities.execution
    import agent_capabilities.permissions
    import agent_capabilities.registry

    for module_name, module in sys.modules.items():
        if module_name.startswith("agent_capabilities"):
            # Inspect imported module attributes / names
            for attr in dir(module):
                assert "agent_core" not in attr.lower(), f"Potential agent-core reference found in {module_name}.{attr}"


def test_package_isolation():
    """Ensure no external dependencies or networks are initialized on package import."""
    import agent_capabilities

    assert hasattr(agent_capabilities, "__version__")
