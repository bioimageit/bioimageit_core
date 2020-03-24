from bioimagepy.metadata.containers import SearchContainer

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
    
    if "<=" in query:
        splitted_query = query.split('<=')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key<=value)' )
        key = splitted_query[0]
        value = float(splitted_query[1])   
        for i in range(len(search_list)):
            if float(search_list[i].tag(key)) <= float(value):
                selected_list.append(search_list[i]) 

    elif ">=" in query:
        splitted_query = query.split('>=')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key>=value)' )
        key = splitted_query[0]
        value = splitted_query[1]   
        for i in range(len(search_list)):
            if float(search_list[i].tag(key)) >= float(value):
                selected_list.append(search_list[i])
    elif "=" in query:
        splitted_query = query.split('=')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key=value)' )
        key = splitted_query[0]
        value = splitted_query[1]  
        for i in range(len(search_list)):
            if search_list[i].tag(key) == value:
                selected_list.append(search_list[i])
    elif "<" in query:
        splitted_query = query.split('<')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key<value)' )
        key = splitted_query[0]
        value = splitted_query[1]   
        for i in range(len(search_list)):
            if float(search_list[i].tag(key)) < float(value):
                selected_list.append(search_list[i])
    elif ">" in query:            
        splitted_query = query.split('>')
        if len(splitted_query) != 2:
            print('Error: the query ' + query + ' is not correct. Must be (key>value)' )
        key = splitted_query[0]
        value = splitted_query[1]   
        for i in range(len(search_list)):
            if float(search_list[i].tag(key)) > float(value):
                selected_list.append(search_list[i])

    return selected_list   
    