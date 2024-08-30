def split_string_via_match(text, search_text):
    """
    text에서 search_text와 match가 발생할 시 매치된 텍스트 이전 텍스트, 매치된 텍스트, 매치된 텍스트 이후 텍스트를 반환
    match가 발생하지 않는 경우 None를 반환
    """
    match_pos = text.lower().find(search_text.lower())
    result = None

    if match_pos != -1:
        result = {
            "start": text[match_pos - 10 : match_pos],
            "match": text[match_pos : match_pos + len(search_text)],
            "end": text[match_pos + len(search_text) :],
        }

    return result
