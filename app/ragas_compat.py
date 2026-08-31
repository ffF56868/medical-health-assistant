"""Compatibility helpers for RAGAS 0.2.15 with LangChain 1.x.

RAGAS 0.2.15 imports the old LangChain Community Vertex AI classes only to
decide whether an LLM supports multiple completions. LangChain Community 0.4
removed those classes in favor of the standalone integration package. This
application uses OpenAI, so lightweight placeholders preserve the old type
checks without changing the active LangChain/Milvus dependency set.
"""

from __future__ import annotations

import sys
from types import ModuleType


def enable_ragas_langchain_compatibility() -> None:
    """Make the retired Vertex AI import paths available before importing RAGAS."""
    try:
        from langchain_community.chat_models.vertexai import ChatVertexAI  # noqa: F401
    except ModuleNotFoundError:
        import langchain_community.chat_models as chat_models

        module_name = "langchain_community.chat_models.vertexai"
        vertex_module = sys.modules.get(module_name)
        if vertex_module is None:
            vertex_module = ModuleType(module_name)
            vertex_module.ChatVertexAI = type("ChatVertexAI", (), {})
            sys.modules[module_name] = vertex_module
        setattr(chat_models, "vertexai", vertex_module)

    import langchain_community.llms as llms

    if not hasattr(llms, "VertexAI"):
        llms.VertexAI = type("VertexAI", (), {})
