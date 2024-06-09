import re


def to_snake_case(name):
    # If the input is None or an empty string, return it as is
    if not name:
        return name

    # Remove leading and trailing whitespace
    name = name.strip()

    # If the resulting string is empty, return it
    if not name:
        return name

    # Replace hyphens and multiple spaces with underscores
    # Remove special characters
    name = re.sub(r"[-\s]+", "_", name)
    name = re.sub(r"[^\w\s]", "", name)

    # If the resulting string is empty after removing special characters, return it
    if not name:
        return name

    words = []
    word_len = len(name)
    start_index = 0
    end_index = 0

    # Process the string to extract words based on case and digits
    while start_index < word_len:
        if name[start_index].isdigit():
            while end_index < word_len and name[end_index].isdigit():
                end_index += 1
        elif name[start_index].islower():
            while end_index < word_len and (
                name[end_index].islower() or name[end_index].isdigit()
            ):
                end_index += 1
        elif name[start_index].isupper():
            while end_index < word_len and (
                name[end_index].isupper() or name[end_index].isdigit()
            ):
                end_index += 1
            if (end_index - start_index) > 1 and end_index < word_len:
                while end_index > start_index and name[end_index].islower():
                    end_index -= 1
            else:
                while end_index < word_len and (
                    name[end_index].islower() or name[end_index].isdigit()
                ):
                    end_index += 1
        else:
            end_index += 1

        extracted_name = name[start_index:end_index]

        if extracted_name != "_":
            words.append(extracted_name)

        start_index = end_index

    # Convert extracted words to lowercase and join them with underscores
    name = "_".join([word.lower() for word in words])

    return name
