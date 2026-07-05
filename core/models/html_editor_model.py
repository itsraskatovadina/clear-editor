from typing import List


class TagCompletionsModel:
    def __init__(self, tags: List[str] = None):
        self._tags: List[str] = tags or [
            "p", "b", "div", "span", "a", "ul", "li",
            "h1", "h2", "h3", "h4", "h5", "h6",
            "table", "tr", "td",
        ]

    @property
    def tags(self) -> List[str]:
        return list(self._tags)

    def is_valid_tag(self, name: str) -> bool:
        return name in self._tags

    def add(self, name: str):
        if name and name not in self._tags:
            self._tags.append(name)

    def remove(self, name: str):
        if name in self._tags:
            self._tags.remove(name)
