from app.analysis.parser_prototype import parse_python_source


def test_parse_python_source_segments_functions_and_methods_without_execution():
    source = """
def outer(value):
    def inner(item):
        return item + 1
    return inner(value)


class Formatter:
    def render(self, data):
        if data:
            return str(data)
        return ""


async def collect(items):
    return [item async for item in items]
"""

    result = parse_python_source(source)

    assert result.syntax_valid is True
    assert result.syntax_failure is None
    assert result.tree is not None
    assert [segment.qualified_name for segment in result.segments] == [
        "outer",
        "outer.inner",
        "Formatter.render",
        "collect",
    ]
    assert [segment.kind for segment in result.segments] == [
        "function",
        "function",
        "method",
        "function",
    ]


def test_parse_python_source_returns_syntax_failure_details():
    source = """
def broken(
    return 1
"""

    result = parse_python_source(source)

    assert result.syntax_valid is False
    assert result.tree is None
    assert result.segments == ()
    assert result.syntax_failure is not None
    assert result.syntax_failure.line is not None
    assert result.syntax_failure.column is not None
