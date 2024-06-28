import unittest

from python_refactor_tool_box.snake_case import to_snake_case


class TestSnakeCase(unittest.TestCase):

    def setUp(self):
        pass

    def setup_method(self, method):
        self.setUp()

    def test_normal_case(self):
        self.assertEqual(
            to_snake_case("ConvertirCetteChaine En_Snake-Case!"),
            "convertir_cette_chaine_en_snake_case!",
        )

    def test_single_word_lowercase(self):
        self.assertEqual(to_snake_case("simple"), "simple")

    def test_single_word_uppercase(self):
        self.assertEqual(to_snake_case("SIMPLE"), "simple")

    def test_mixed_case_with_spaces(self):
        self.assertEqual(
            to_snake_case("mixed CASE With SPACES"), "mixed_case_with_spaces"
        )

    def test_with_special_characters(self):
        self.assertEqual(
            to_snake_case("Special@Characters#Example!"), "special_characters_example!"
        )

    def test_numeric_and_alphabets(self):
        self.assertEqual(
            to_snake_case("Num3r1c4l and Alph4b3t!"), "num3r1c4l_and_alph4b3t!"
        )

    def test_leading_and_trailing_spaces(self):
        self.assertEqual(
            to_snake_case("  Leading and trailing spaces  "),
            "leading_and_trailing_spaces",
        )

    def test_hyphens_and_underscores(self):
        self.assertEqual(
            to_snake_case("hyphens-and_underscores"), "hyphens_and_underscores"
        )

    def test_consecutive_spaces(self):
        self.assertEqual(to_snake_case("consecutive    spaces"), "consecutive_spaces")

    def test_camel_case_with_digits(self):
        self.assertEqual(
            to_snake_case("CamelCase123WithDigits"), "camel_case123_with_digits"
        )

    def test_empty_string(self):
        self.assertEqual(to_snake_case(""), "")

    def test_spaces_only(self):
        self.assertEqual(to_snake_case("     "), "")

    def test_underscores_only(self):
        self.assertEqual(to_snake_case("_____"), "_____")

    def test_numbers_only(self):
        self.assertEqual(to_snake_case("123456"), "123456")

    def test_special_characters_only(self):
        self.assertEqual(to_snake_case("@#$%^&*()"), "@#$%^&*()")

    def test_mixed_case_with_underscores(self):
        self.assertEqual(
            to_snake_case("mixed_CASE_With_SPACES_and___underscores"),
            "mixed_case_with_spaces_and_underscores",
        )

    def test_single_character_lowercase(self):
        self.assertEqual(to_snake_case("a"), "a")

    def test_single_character_uppercase(self):
        self.assertEqual(to_snake_case("A"), "a")

    def test_consecutive_capitals(self):
        self.assertEqual(to_snake_case("CONSECUTIVECAPITALS"), "consecutivecapitals")

    def test_consecutive_numbers_and_letters(self):
        self.assertEqual(to_snake_case("abc123XYZ"), "abc123_xyz")

    def test_leading_numbers(self):
        self.assertEqual(to_snake_case("123LeadingNumbers"), "123_leading_numbers")

    def test_trailing_numbers(self):
        self.assertEqual(to_snake_case("TrailingNumbers123"), "trailing_numbers123")

    def test_none_case(self):
        self.assertEqual(to_snake_case(None), None)

    def test_double_underscore_init(self):
        self.assertEqual(to_snake_case("__init__"), "__init__")

    def test_double_underscore_Init(self):
        self.assertEqual(to_snake_case("__Init__"), "__init__")

    def test_double_underscore_INIT(self):
        self.assertEqual(to_snake_case("__INIT__"), "__init__")

    def test_double_underscore_INITok(self):
        self.assertEqual(to_snake_case("__INITok__"), "__ini_tok__")

    def test_double_underscore_INIT_ok(self):
        self.assertEqual(to_snake_case("__INIT_ok__"), "__init_ok__")

    def test_single_word_capitalized(self):
        self.assertEqual(to_snake_case("Toto"), "toto")

    def test_two_words_capitalized(self):
        self.assertEqual(to_snake_case("TotoTata"), "toto_tata")

    def test_three_words_capitalized(self):
        self.assertEqual(to_snake_case("TotoTataTiti"), "toto_tata_titi")

    def test_four_words_with_underscores(self):
        self.assertEqual(to_snake_case("Toto_Tata_Titi_Tata"), "toto_tata_titi_tata")

    def test_mixed_case_capitals(self):
        self.assertEqual(to_snake_case("TotoTATAtiti"), "toto_tat_atiti")

    def test_hello_world(self):
        self.assertEqual(to_snake_case("HelloWorld"), "hello_world")

    def test_xml_http_request(self):
        self.assertEqual(to_snake_case("XMLHttpRequest"), "xml_http_request")

    def test_get_http_response_code(self):
        self.assertEqual(to_snake_case("getHTTPResponseCode"), "get_http_response_code")

    def test_get_2_http_responses(self):
        self.assertEqual(to_snake_case("get2HTTPResponses"), "get2_http_responses")

    def test_get_http_2_responses(self):
        self.assertEqual(to_snake_case("getHTTP2Responses"), "get_http2_responses")

    def test_already_snake_case(self):
        self.assertEqual(to_snake_case("already_snake_case"), "already_snake_case")

    def test_this_is_a_test(self):
        self.assertEqual(to_snake_case("ThisIsATest"), "this_is_a_test")

    def test_single_A(self):
        self.assertEqual(to_snake_case("A"), "a")

    def test_double_AA(self):
        self.assertEqual(to_snake_case("AA"), "aa")

    def test_triple_AAA(self):
        self.assertEqual(to_snake_case("AAA"), "aaa")

    def test_mixed_case_aaaAAA(self):
        self.assertEqual(to_snake_case("aaaAAA"), "aaa_aaa")

    def test_hello_double_underscore_world(self):
        self.assertEqual(to_snake_case("Hello__World"), "hello_world")

    def test_hello_dash_world(self):
        self.assertEqual(to_snake_case("Hello-World"), "hello_world")

    def test_mj_is_a_boy_with_legs(self):
        self.assertEqual(to_snake_case("MJ_is_aBoyWith2Legs"), "mj_is_a_boy_with2_legs")
