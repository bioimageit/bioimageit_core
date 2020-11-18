from bioimageit_core.metadata.exceptions import MetadataQueryError


def query_list_single(search_list: list, query: str) -> list:
    """query internal function

    Search if the query is on the search_list

    Parameters
    ----------
    search_list
        data search list (list of SearchContainer)
    query
        String query with the key=value format. No 'AND', 'OR'...

    Returns
    -------
    list
        list of selected SearchContainer

    """

    selected_list = list()

    if 'name' in query:
        split_query = query.split('=')
        if len(split_query) != 2:
            raise MetadataQueryError(
                'Error: the query ' + query +
                ' is not correct. Must be (key<=value)'
            )
        value = split_query[1]
        for i in range(len(search_list)):
            if value in search_list[i].name():
                selected_list.append(search_list[i])
        return selected_list

    if "<=" in query:
        split_query = query.split('<=')
        if len(split_query) != 2:
            raise MetadataQueryError(
                'Error: the query ' + query +
                ' is not correct. Must be (key<=value)'
            )
        key = split_query[0]
        value = float(split_query[1].replace(' ', ''))
        for i in range(len(search_list)):
            if (
                search_list[i].is_tag(key)
                and float(search_list[i].tag(key).replace(' ', '')) <= value
            ):
                selected_list.append(search_list[i])

    elif ">=" in query:
        split_query = query.split('>=')
        if len(split_query) != 2:
            raise MetadataQueryError(
                'Error: the query ' + query +
                ' is not correct. Must be (key>=value)'
            )
        key = split_query[0]
        value = split_query[1]
        for i in range(len(search_list)):
            if search_list[i].is_tag(key) and \
                    float(search_list[i].tag(key)) >= float(
                value
            ):
                selected_list.append(search_list[i])
    elif "=" in query:
        split_query = query.split('=')
        if len(split_query) != 2:
            raise MetadataQueryError(
                'Error: the query ' + query +
                ' is not correct. Must be (key=value)'
            )
        key = split_query[0]
        value = split_query[1]
        for i in range(len(search_list)):
            if search_list[i].is_tag(key) and search_list[i].tag(key) == value:
                selected_list.append(search_list[i])
    elif "<" in query:
        split_query = query.split('<')
        if len(split_query) != 2:
            raise MetadataQueryError(
                'Error: the query ' + query +
                ' is not correct. Must be (key<value)'
            )
        key = split_query[0]
        value = split_query[1]
        for i in range(len(search_list)):
            if search_list[i].is_tag(key) and \
                    float(search_list[i].tag(key)) < float(
                value
            ):
                selected_list.append(search_list[i])
    elif ">" in query:
        split_query = query.split('>')
        if len(split_query) != 2:
            raise MetadataQueryError(
                'Error: the query ' + query +
                ' is not correct. Must be (key>value)'
            )
        key = split_query[0]
        value = split_query[1]
        for i in range(len(search_list)):
            if search_list[i].is_tag(key) and \
                    float(search_list[i].tag(key)) > float(
                value
            ):
                selected_list.append(search_list[i])

    return selected_list
