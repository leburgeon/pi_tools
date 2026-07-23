

from registry import register_tool


@register_tool(name="tool", help_text="Tool help")
def tool() -> list[str]:
    return ["This is actually just the template"]