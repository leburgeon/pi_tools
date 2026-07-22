from registry import register_tool


@register_tool("weather", "Returns the weather at the location of your IP")
def weather() -> str:
    return "Ooo there be some clouds or some shit"
