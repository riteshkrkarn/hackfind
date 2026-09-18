from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

SourceKind = Literal["html", "json", "tavily"]


class SourceDefinition(BaseModel):
    """Config for a pluggable source — no new Python file required."""

    name: str = Field(..., min_length=1, max_length=64)
    kind: SourceKind
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class HtmlSourceConfig(BaseModel):
    list_url: str
    link_selector: str = "a[href]"
    title_selector: Optional[str] = None
    base_url: Optional[str] = None
    skip_substrings: list[str] = Field(
        default_factory=lambda: ["login", "signup", "register", "javascript:"]
    )
    min_title_length: int = 4
    max_items: int = 40


class JsonSourceConfig(BaseModel):
    list_url: str
    items_path: str = ""  # dotted path into JSON; empty = root list
    title_key: str = "title"
    url_key: str = "url"
    id_key: Optional[str] = "id"
    description_key: Optional[str] = "description"
    max_items: int = 50


class TavilySourceConfig(BaseModel):
    query: str = "upcoming hackathons for students apply deadline"
    max_results: int = 15
    search_depth: Literal["basic", "advanced"] = "basic"
    include_domains: list[str] = Field(default_factory=list)
    topic: str = "general"
