import re


def to_snake_case(name):
    if not name:
        return name

    name = name.strip()

    if not name:
        return name

    name = re.sub("-", "_", name)
    name = re.sub("  ", " ", name)
    name = re.sub(" ", "_", name)
    name = re.sub("__", "_", name)
    name = re.sub(r"[^\w\s]", "", name)

    if not name:
        return name

    words = []
    word_len = len(name)
    start_index = 0
    end_index = 0

    while start_index < word_len:
        if name[start_index].isdigit():
            while end_index < word_len and name[end_index].isdigit():
                end_index += 1
        elif name[start_index].islower():
            while (end_index < word_len) and (
                name[end_index].islower() or name[end_index].isdigit()
            ):
                end_index += 1
        elif name[start_index].isupper():
            while (end_index < word_len) and (
                name[end_index].isupper() or name[end_index].isdigit()
            ):
                end_index += 1

            if (end_index - start_index) > 1:
                if end_index < word_len:
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

        if end_index == word_len:
            break

        start_index = end_index

    for i in range(len(words)):
        word = words[i]

        new_word = ("_" if i > 0 else "") + word.lower()
        name = name.replace(word, new_word)

    name = "_".join([word.lower() for word in words])
    return name
