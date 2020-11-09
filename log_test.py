import re

table_function = ['head', 'tail', 'shape', 'info', 'describe', 'value_counts', 'columns', 'index', 'dtype', 'values', 'loc', 'iloc', 'isin',
                  'isnull', 'notnull', 'dropna', 'fillna', 'quantile', 'mean']
chart_function = ['plot', 'show', 'figure', 'grid', 'hist', 'scatter', 'bar', 'line',
                  'title', 'legend', 'xlabel', 'ylabel', 'xscale']
agg_function = ['groupby', 'filter', 'pivot']
read_function = ['read_csv']
variable_function = ['tolist', 'append']
log_list = []
def_list = [] # 사용자 정의 함수명 list

def save_log(log):
    """
    log_list 에 정의한 operator format log를 적재하는 함수
    :param log: operator format log
    """
    if log is not None:
        log_list.append(log)

def show_log_list():
    """
    log_list 에 정의한 operator format log를 적재하는 함수
    :return: log_list 내에 적재한 log print
    """
    for log in log_list:
        print (log)

def get_import(log):
    """
    'import' 단어가 포함된 log를 parsing

    :param log: trace log
    :return: Import(create_var, import_name)
    :Args:
        create_var : 분석을 위해 변경한 import name
        import_name : import name
    """
    split_log_list = re.findall(r"[\S']+", log)
    import_index = -1
    as_index = -1
    create_var = None

    for i, split_log in enumerate(split_log_list):
        if split_log == 'import':
            import_index = i
        if split_log == 'as':
            as_index = i

    if as_index > -1:
        import_name = split_log_list[import_index+1:as_index][0]
        create_var = split_log_list[as_index + 1:][0]
    else:
        import_name = split_log_list[import_index + 1:][0]

    return "Import({0},{1})".format(create_var, import_name)

def handle_def(log):
    """
    'def' 단어가 포함된 log를 parsing

    :param log: trace log
    """
    split_log = re.findall(r"[\S']+", log)
    def_name = ""
    for str in split_log[1]:
        if str == '(':
            break
        def_name = def_name + str

    def_list.append(def_name)

def get_read_function(stan_var, func_name, param, create_var):
    """
    파일을 read하여 변수에 저장하는 함수
    TODO. 추후 csv.reader, from_csv, .. 와 같은 다른 function도 파악할 예정

    :param stan_var:
    :param func_name:
    :param param:
    :param create_var: 파일 데이터를 저장할 변수
    :return: CSV(create_var, stan_var, func_name, parameter)
    :Args:
        create_var : 생성된 변수명
        stan_var : function 대상 변수명
        func_name : 적용할 function명
        param : function parameter
    """

    return "CSV({0},{1},{2},{3})".format(create_var, stan_var, func_name, param)

def get_variable(create_var, values, stan_var=None):
    """
    대입 연산자('=')을 사용하여 변수를 생성할 때 function 수행 결과를 저장하지 않는 경우

    :param create_var:
    :param values:
    :param stan_var:
    :return: Variable(create_var, stan_var, values)
    :Args:
        create_var : 생성된 변수명
        stan_var : function 대상 변수명
        values : 변수에 저장할 데이터
    """
    valid = True

    if stan_var:
        index = values.find(stan_var+'.')
        if index > -1:
            values = values[index+len(stan_var+'.'):]

    # values 에 def(사용자 정의 함수)가 쓰이는 경우
    for i, def_name in enumerate(def_list):
        if def_name in values:
            valid = False
            break

    if valid:
        return "Variable({0},{1},{2})".format(create_var, stan_var, values)

def get_table_function(stan_var, func_name, param, create_var=None):
    """
    table function 수행 결과를 저장하는 함수
    table function은 해당하는 데이터를 table 형태로 화면상에 보여주는 것을 말함

    :param stan_var:
    :param func_name:
    :param param:
    :param create_var:
    :return: Table(create_var, stan_var, func_name, parameter)
    :Args:
        create_var : 생성한 변수명, 없을 경우 None
        stan_var : function 대상 변수명
        func_name : 적용할 function 명
        param_list : function parameter
    """
    param_list = []

    if param == '':
        param_list.append('')
    else:
        index = param.find(",")
        if index > 0:
            param_list = param.split(",")
        else:
            param_list.append(param)

    return "Table({0},{1},{2},{3})".format(create_var, stan_var, func_name, param_list)

def get_chart_function(stan_var, func_name, param, create_var=None):
    """
    chart function 수행결과를 저장하는 함수
    chart function은 해당하는 데이터를 chart 형태로 화면상에 보여주는 것을 말함

    :param stan_var:
    :param func_name:
    :param param:
    :param create_var:
    :return: Chart(create_var, stan_var, func_name, parameter)
    :Args:
        create_var : 생성한 변수명, 없을 경우 None
        stan_var : function 대상 변수명
        func_name : 적용할 function 명
        param_list : function parameter
    """
    param_list = []

    if param == '':
        param_list.append('')
    else:
        index = param.find(",")
        if index > 0:
            param_list = param.split(",")
        else:
            param_list.append(param)

    return "Chart({0},{1},{2},{3})".format(create_var, stan_var, func_name, param_list)

def get_groupby_function(create_var, stan_var, param_list):
    """
    groupby function 수행결과를 저장하는 함수
    추후 groupby와 관련된 매개변수를 지정하여 세부적으로 log로 저장할 예정

    :param create_var:
    :param stan_var:
    :param param_list:
    :return: Groupby(create_var, stan_var, parameter)
    :Args:
        create_var : 생성한 변수명, 없을 경우 None
        stan_var : function 대상 변수명
        param_list : function parameter
    """
    return "Groupby({0},{1},{2})".format(create_var, stan_var, param_list)


def get_filter_function(create_var, stan_var, param_list):
    """
    filter function 수행결과를 저장하는 함수
    추후 filter와 관련된 매개변수를 지정하여 세부적으로 log로 저장할 예정

    :param create_var:
    :param stan_var:
    :param param_list:
    :return: Filter(create_var, stan_var, parameter)
    :Args:
        create_var : 생성한 변수명, 없을 경우 None
        stan_var : function 대상 변수명
        param_list : function parameter
    """
    return "Filter({0},{1},{2})".format(create_var, stan_var, param_list)


def get_pivot_function(create_var, stan_var, param_list):
    """
    pivot function 수행결과를 저장하는 함수
    추후 pivot과 관련된 매개변수를 지정하여 세부적으로 log로 저장할 예정

    :param create_var:
    :param stan_var:
    :param param_list:
    :return: Pivot(create_var, stan_var, parameter)
    :Args:
        create_var : 생성한 변수명, 없을 경우 None
        stan_var : function 대상 변수명
        param_list : function parameter
    """
    return "Pivot({0},{1},{2})".format(create_var, stan_var, param_list)

def get_agg_function(stan_var, func_name, param, create_var=None):
    """
    agg function 수행결과를 저장하는 함수
    agg function은 여러 행 또는 테이블 전체 행으로부터 하나의 결과값을 반환하는 함수를 말함
    agg function에 맞는 log로 반환

    :param stan_var:
    :param func_name:
    :param param:
    :param create_var:
    :return: Agg(create_var, stan_var, func_name, parameter)
    :Args:
        create_var : 생성한 변수명, 없을 경우 None
        stan_var : function 대상 변수명
        func_name : 적용할 function 명
        parameter : function parameter
    """
    param_list = []

    if param == '':
        param_list.append('')
    else:
        index = param.find(",")
        if index > 0:
            param_list = param.split(",")
        else:
            param_list.append(param)

    agg_function = ""

    # agg function 확인
    agg_function = agg_func_dic = {
        "groupby" : lambda create_var, stan_var, func_name, param_list: get_groupby_function(create_var, stan_var, param_list),
        "filter": lambda create_var, stan_var, func_name, param_list: get_filter_function(create_var, stan_var, param_list),
        "pivot": lambda create_var, stan_var, func_name, param_list: get_pivot_function(create_var, stan_var, param_list)
    }[func_name](create_var, stan_var, func_name, param_list)

    if agg_function:
        return agg_function
    else:
        print("**WARNING : 파악하지 못한 agg_function")
        print('해당 function 처리 필요 : ', func_name, '\n')
        return "Agg({0},{1},{2})".format(create_var, stan_var, func_name, param_list)

def get_variable_function(stan_var, func_name, param, create_var):
    """
    function 수행결과를 통해 변수가 변경되는 경우

    :param stan_var:
    :param func_name:
    :param param:
    :param create_var:
    :return: Variable(create_var, stan_var, func_name, parameter)
    :Args:
        create_var : 생성한 변수명, 없을 경우 None
        stan_var : function 대상 변수명
        func_name : 적용할 function 명
        parameter : function parameter
    """
    param_list = []

    if param == '':
        param_list.append('')
    else:
        index = param.find(",")
        if index > 0:
            param_list = param.split(",")
        else:
            param_list.append(param)

    return "Variable({0},{1},{2},{3})".format(create_var, stan_var, func_name, param_list)

def search_operator(stan_var, func_name, param, create_var=None):
    """
    function이 해당하는 type을 파악하는 함수
    미리 정의된 function 리스트(table, chart, agg, ..)를 통해 type을 확인하며 미확인된 function은 지속적으로 추가할 예정

    :param stan_var:
    :param func_name:
    :param param:
    :param create_var:
    :return: operator format 에 맞는 log
    """
    res = ""
    operation_flag = False

    # read_function search
    if not operation_flag:
        for read_func in read_function:
            if func_name == read_func:
                res = get_read_function(stan_var, func_name, param, create_var)

                # search
                operation_flag = True
                break
    # table_function search
    if not operation_flag:
        for table_func in table_function:
            if func_name == table_func:
                res = get_table_function(stan_var, func_name, param, create_var)

                # search
                operation_flag = True
                break
    # chart_function search
    if not operation_flag:
        for chart_func in chart_function:
            if func_name == chart_func:
                res = get_chart_function(stan_var, func_name, param, create_var)

                # search
                operation_flag = True
                break
    # agg_function search
    if not operation_flag:
        for agg_func in agg_function:
            if func_name == agg_func:
                res = get_agg_function(stan_var, func_name, param, create_var)

                # search
                operation_flag = True
                break
    # variable_function search
    if not operation_flag:
        for variable_func in variable_function:
            if func_name == variable_func:
                create_var = stan_var
                res = get_variable_function(stan_var, func_name, param, create_var)

                # search
                operation_flag = True
                break

    # 파악하지 못한 function 파악
    if not operation_flag:
        print("**WARNING : 파악하지 못한 function")
        print('해당 function 처리 필요 : ', func_name, '\n')

    return res