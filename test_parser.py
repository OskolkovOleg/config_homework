import pytest
import os
import sys
from lark import Lark, exceptions

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config_parser import ConfigTransformer, to_xml, prettify_xml


@pytest.fixture
def parser():
    with open('grammar.lark', 'r', encoding='utf-8') as f:
        grammar = f.read()
    return Lark(grammar, start='start', parser='lalr')


def test_single_comment(parser):
    text = "-- комментарий\ntest: 42;"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert result is not None


def test_multi_comment(parser):
    text = "%{ многострочный\nкомментарий %}\nvalue: 10;"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert result is not None


def test_positive_number(parser):
    text = "num: +123;"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert ('const', 'num', 123) in result


def test_negative_number(parser):
    text = "num: -456;"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert ('const', 'num', -456) in result


def test_zero(parser):
    text = "zero: 0;"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert ('const', 'zero', 0) in result


def test_simple_dict(parser):
    text = "([key: 100])"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert len(result) == 1


def test_dict_multiple_pairs(parser):
    text = "([a: 1, b: 2, c: 3])"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    expr = result[0]
    assert expr[0] == 'expr'


def test_nested_dict(parser):
    text = "([outer: 1, nested: ([inner: 2])])"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert result is not None


def test_const_declaration(parser):
    text = "my_const: 777;"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert ('const', 'my_const', 777) in result


def test_const_reference(parser):
    text = "val: 100;\nref: ${val};"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert ('const', 'ref', 100) in result


def test_const_in_dict(parser):
    text = "port: 8080;\nconfig: ([server_port: ${port}]);"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert result is not None


def test_undefined_const_error(parser):
    text = "ref: ${undefined};"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    with pytest.raises(ValueError):
        transformer.transform(tree)


def test_name_with_underscore(parser):
    text = "test_name: 42;"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert ('const', 'test_name', 42) in result


def test_complex_config(parser):
    text = """
    -- веб-сервер
    port: 8080;
    timeout: 30;
    
    %{ многострочный комментарий %}
    
    server: ([
        host: 127,
        port: ${port},
        settings: ([
            timeout: ${timeout},
            retry: 3
        ])
    ]);
    """
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert len(result) == 3


def test_xml_generation(parser):
    text = "test: 42;"
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    xml_root = to_xml(result)
    xml_string = prettify_xml(xml_root)
    assert '<config>' in xml_string
    assert 'test' in xml_string
    assert '42' in xml_string


def test_example_webserver(parser):
    with open('examples/webserver.conf', 'r', encoding='utf-8') as f:
        text = f.read()
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert result is not None


def test_example_database(parser):
    with open('examples/database.conf', 'r', encoding='utf-8') as f:
        text = f.read()
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert result is not None


def test_example_game(parser):
    with open('examples/game.conf', 'r', encoding='utf-8') as f:
        text = f.read()
    tree = parser.parse(text)
    transformer = ConfigTransformer()
    result = transformer.transform(tree)
    assert result is not None
