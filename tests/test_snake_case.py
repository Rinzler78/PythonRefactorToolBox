import unittest

from python_refactor_toolbox.snake_case import to_snake_case


class TestSnakeCase(unittest.TestCase):

    def setUp(self):
        pass

    def setup_method(self, method):
        self.setUp()

    def test_to_snake_case(self):
        names = {
            None: None,
            "__init__": "__init__",
            "__Init__": "__init__",
            "__INIT__": "__init__",
            "__INITok__": "__ini_tok__",
            "__INIT_ok__": "__init_ok__",
            "Toto": "toto",
            "TotoTata": "toto_tata",
            "TotoTataTiti": "toto_tata_titi",
            "Toto_Tata_Titi_Tata": "toto_tata_titi_tata",
            "TotoTATAtiti": "toto_tat_atiti",
            "HelloWorld": "hello_world",
            "XMLHttpRequest": "xml_http_request",
            "getHTTPResponseCode": "get_http_response_code",
            "get2HTTPResponses": "get2_http_responses",
            "getHTTP2Responses": "get_http2_responses",
            "already_snake_case": "already_snake_case",
            "ThisIsATest": "this_is_a_test",
            "A": "a",
            "AA": "aa",
            "AAA": "aaa",
            "aaaAAA": "aaa_aaa",
            "Hello__World": "hello_world",
            "Hello-World": "hello_world",
            "MJ_is_aBoyWith2Legs": "mj_is_a_boy_with2_legs",
        }

        for name, expected in names.items():
            self.assertEqual(to_snake_case(name), expected)
