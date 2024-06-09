from src.python_refactor_toolbox.snake_case import to_snake_case

test_cases = {
    "normal_case": (
        "ConvertirCetteChaine En_Snake-Case!",
        "convertir_cette_chaine_en_snake_case",
    ),
    "single_word_lowercase": ("simple", "simple"),
    "single_word_uppercase": ("SIMPLE", "simple"),
    "mixed_case_with_spaces": ("mixed CASE With SPACES", "mixed_case_with_spaces"),
    "with_special_characters": (
        "Special@Characters#Example!",
        "special_characters_example",
    ),
    "numeric_and_alphabets": ("Num3r1c4l and Alph4b3t!", "num3r1c4l_and_alph4b3t"),
    "leading_and_trailing_spaces": (
        "  Leading and trailing spaces  ",
        "leading_and_trailing_spaces",
    ),
    "hyphens_and_underscores": ("hyphens-and_underscores", "hyphens_and_underscores"),
    "consecutive_spaces": ("consecutive    spaces", "consecutive_spaces"),
    "camel_case_with_digits": ("CamelCase123WithDigits", "camel_case123_with_digits"),
    "empty_string": ("", ""),
    "spaces_only": ("     ", ""),
    "underscores_only": ("_____", ""),
    "numbers_only": ("123456", "123456"),
    "special_characters_only": ("@#$%^&*()", ""),
    "mixed_case_with_underscores": (
        "mixed_CASE_With_SPACES_and___underscores",
        "mixed_case_with_spaces_and_underscores",
    ),
    "single_character_lowercase": ("a", "a"),
    "single_character_uppercase": ("A", "a"),
    "consecutive_capitals": ("CONSECUTIVECAPITALS", "consecutivecapitals"),
    "consecutive_numbers_and_letters": ("abc123XYZ", "abc123_xyz"),
    "leading_numbers": ("123LeadingNumbers", "123_leading_numbers"),
    "trailing_numbers": ("TrailingNumbers123", "trailing_numbers123"),
    "none_case": (None, None),
    "double_underscore_init": ("__init__", "init"),
    "double_underscore_Init": ("__Init__", "init"),
    "double_underscore_INIT": ("__INIT__", "init"),
    "double_underscore_INITok": ("__INITok__", "ini_tok"),
    "double_underscore_INIT_ok": ("__INIT_ok__", "init_ok"),
    "single_word_capitalized": ("Toto", "toto"),
    "two_words_capitalized": ("TotoTata", "toto_tata"),
    "three_words_capitalized": ("TotoTataTiti", "toto_tata_titi"),
    "four_words_with_underscores": ("Toto_Tata_Titi_Tata", "toto_tata_titi_tata"),
    "mixed_case_capitals": ("TotoTATAtiti", "toto_tat_atiti"),
    "hello_world": ("HelloWorld", "hello_world"),
    "xml_http_request": ("XMLHttpRequest", "xml_http_request"),
    "get_http_response_code": ("getHTTPResponseCode", "get_http_response_code"),
    "get_2_http_responses": ("get2HTTPResponses", "get2_http_responses"),
    "get_http_2_responses": ("getHTTP2Responses", "get_http2_responses"),
    "already_snake_case": ("already_snake_case", "already_snake_case"),
    "this_is_a_test": ("ThisIsATest", "this_is_a_test"),
    "single_A": ("A", "a"),
    "double_AA": ("AA", "aa"),
    "triple_AAA": ("AAA", "aaa"),
    "mixed_case_aaaAAA": ("aaaAAA", "aaa_aaa"),
    "hello_double_underscore_world": ("Hello__World", "hello_world"),
    "hello_dash_world": ("Hello-World", "hello_world"),
    "mj_is_a_boy_with_legs": ("MJ_is_aBoyWith2Legs", "mj_is_a_boy_with2_legs"),
}

for name, value in test_cases.items():
    input_value = value[0]
    expected_value = value[1]
    result = to_snake_case(input_value)

    print(
        f"Test ({name}) : to_snake_case({input_value}) : {(result == expected_value)}"
    )
    print(f"-Expected : ({expected_value})")
    print(f"-Result : ({result})")

    assert result == expected_value
