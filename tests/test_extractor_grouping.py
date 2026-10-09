import unittest

from extractor import _group_declaration_pages, extract_casillas, extract_header


class DeclarationPageGroupingTests(unittest.TestCase):
    def test_groups_pages_by_declaration_identity(self):
        pages = [
            "RUC 20123456789\nRazon Social Empresa Uno Periodo 202311\n"
            "Numero de Orden 1001\nTipo de Declaracion Original",
            "RUC 20123456789\nRazon Social Empresa Uno Periodo 202311\n"
            "Numero de Orden 1001\nTipo de Declaracion Original\n108 180.00",
            "RUC 20123456789\nRazon Social Empresa Uno Periodo 202312\n"
            "Numero de Orden 1002\nTipo de Declaracion Original",
            "RUC 20123456789\nRazon Social Empresa Uno Periodo 202312\n"
            "Numero de Orden 1002\nTipo de Declaracion Original\n108 250.00",
        ]

        grouped = _group_declaration_pages(pages)
        records = [
            {**extract_header(text), **extract_casillas(text)}
            for text in grouped
        ]

        self.assertEqual([record['Periodo'] for record in records], ['202311', '202312'])
        self.assertEqual([record['108'] for record in records], [180.0, 250.0])


if __name__ == '__main__':
    unittest.main()