import sys
import argparse
from lark import Lark, Transformer, exceptions
import xml.etree.ElementTree as ET
from xml.dom import minidom


class ConfigTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.constants = {}

    def start(self, items):
        return items

    def statement(self, items):
        return items[0]

    def const_decl(self, items):
        name = str(items[0])
        value = items[1]
        self.constants[name] = value
        return ('const', name, value)

    def const_ref(self, items):
        name = str(items[0])
        if name not in self.constants:
            raise ValueError(f"Константа '{name}' не определена")
        return self.constants[name]

    def expression(self, items):
        return ('expr', items[0])

    def dict(self, items):
        return ('dict', items)

    def pair(self, items):
        name = str(items[0])
        value = items[1]
        return (name, value)

    def value(self, items):
        return items[0]

    def number(self, items):
        return int(items[0])

    def NAME(self, token):
        return str(token)


def to_xml(data):
    root = ET.Element('config')
    
    for item in data:
        if isinstance(item, tuple):
            if item[0] == 'const':
                const_elem = ET.SubElement(root, 'constant')
                const_elem.set('name', item[1])
                if isinstance(item[2], tuple) and item[2][0] == 'dict':
                    dict_elem = dict_to_xml(item[2])
                    const_elem.append(dict_elem)
                else:
                    const_elem.text = str(item[2])
            elif item[0] == 'expr':
                expr_value = item[1]
                if isinstance(expr_value, tuple) and expr_value[0] == 'dict':
                    root.append(dict_to_xml(expr_value))
                else:
                    value_elem = ET.SubElement(root, 'value')
                    value_elem.text = str(expr_value)
    
    return root


def dict_to_xml(dict_tuple):
    dict_elem = ET.Element('dictionary')
    for pair in dict_tuple[1]:
        pair_elem = ET.SubElement(dict_elem, 'pair')
        pair_elem.set('key', pair[0])
        if isinstance(pair[1], tuple) and pair[1][0] == 'dict':
            pair_elem.append(dict_to_xml(pair[1]))
        else:
            pair_elem.text = str(pair[1])
    return dict_elem


def prettify_xml(elem):
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def main():
    parser = argparse.ArgumentParser(description='Конфигурационный транслятор')
    parser.add_argument('-i', '--input', required=True, help='Входной файл')
    parser.add_argument('-o', '--output', required=True, help='Выходной файл XML')
    args = parser.parse_args()

    with open('grammar.lark', 'r', encoding='utf-8') as f:
        grammar = f.read()

    lark_parser = Lark(grammar, start='start', parser='lalr')

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()

        tree = lark_parser.parse(input_text)
        transformer = ConfigTransformer()
        result = transformer.transform(tree)

        xml_root = to_xml(result)
        xml_string = prettify_xml(xml_root)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(xml_string)

        print(f"Трансляция завершена: {args.output}")

    except exceptions.LarkError as e:
        print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Файл не найден: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
