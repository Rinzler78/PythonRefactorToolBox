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
}

for name, value in test_cases.items():
    input_value = value[0]
    expected_value = value[1]

    print(f"Test ({name}) : to_snake_case({input_value})")

    result = to_snake_case(input_value)

    print(f"\tExpected ({expected_value}) => {(result == expected_value)}")

    assert result == expected_value
