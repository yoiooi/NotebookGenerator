import re
from log_test import save_log, show_log_list, search_operator, get_import, handle_def, get_variable

# 일단 하나의 trace 파일에 대해 log를 적재하는 것을 테스트
# 추후 trace 파일들에 대해 log를 적재할 예정
f = open('lesson2_poll_data_inclass_as_is_trace', 'r') # iris_data_trace, cars_trace
line = f.readline()
index = ""
str = ""

def valid_stan_var(stan_var):
    """
    function의 적용 대상이 되는 변수의 유효성을 판단하여 반환

    :param stan_var:
    :return: valid_stan_var
    """
    # STEP 1. [] 유효성 판단
    # 뒤에서부터 파악, '[' 은 -1, ']' 은 +1을 하면서 음수가 되는 순간 split
    num = 0
    if stan_var is None:
        index = - 1
        return stan_var
    else :
        index = len(stan_var) - 1

    while index > -1:
        character = stan_var[index]

        if num < 0:
            stan_var = stan_var[index + 2:]
            break

        if character == '[':
            num = num - 1
        elif character == ']':
            num = num + 1

        index = index - 1


    # STEP 2. 공백 제거
    stan_var = stan_var.lstrip()

    return stan_var

def valid_func_name(func_list):
    """
    function name의 유효성을 확인하여 유효한 function name만 반환

    :param func_list:
    :return: valid_func_list
    """
    valid_func_list = []

    for func in func_list:
        # STEP 1. func name에 '.' 포함 유무 판단
        if any(c in func for c in '.'):
            # 유효하지 않은 경우
            continue

        # STEP 2. func name에 ' '(공백) 포함 유무 판단
        if len(func) != len(''.join(func.split())):
            # 유효하지 않은 경우
            continue

        valid_func_list.append(func)

    return valid_func_list

def valid_param(func_list, values):
    '''
    function parameter의 유효성을 확인하여 유효한 parameter만 반환

    :param func_list: ex) ['append', 'mean']
    :param values: ex) '.append(group.mean())'
    :return: valid_param_list ex) ['group.mean()', '']
    '''
    param_list = []

    for func in func_list:
        # STEP 1. values에 func 일치하는 위치 찾기
        func_index = values.find(func)

        append_param = False
        open_parent_flag = False # '(' 괄호 확인시 True
        parent_count = 0
        param_start = -1
        param_end = -1
        # STEP 2. func_index 부터 '(' 또는 ')' 가 있는 지점을 찾아 param apppend
        for i in range(func_index, len(values), 1):
            # param을 찾은 경우
            if open_parent_flag == True and parent_count == 0:
                param_list.append(values[param_start+1:param_end])
                append_param = True
                break

            if values[i] == '(':
                open_parent_flag = True
                if parent_count == 0:
                    param_start = i
                parent_count = parent_count + 1
                continue
            if values[i] == ')':
                if parent_count == 1:
                    param_end = i
                parent_count = parent_count - 1
                continue
        # param을 찾은 경우
        if not append_param and open_parent_flag and parent_count == 0:
            param_list.append(values[param_start + 1:param_end])

    return param_list

def valid_func(values_list):
    """
    function 형태가 맞는지 확인

    :param values_list:
    :return: function 유무 (True/False)
    """
    check = True
    # function 명으로 숫자가 올 수 없음
    if values_list[1].isdigit():
        check = False

    return check

def construct_func_set(func, param):
    """
    nested function 형태를 해결하기 위해 func_set 형태로 반환
    func_set은 func_dic로 구성 즉, {(stan_var, func_name) : param}

    case 1. param이 function을 갖고 있지 않는 경우,
    - {(stan_var, func_name) : param}
    case 2. param이 function을 갖고 있는 nested function일 경우,
    - {(stan_var1, func_name_1) : param_1, (stan_var2, func_name_2) : param_2}
    - ex) input - ['append', 'mean'], ['group.mean()', '']
          reverse_input - ['mean', 'append'], ['', 'group.mean()']
          output - {(group, mean) : '', (None, append) : group.mean()}

    :param func:
    :param param:
    :return: func_set
    """
    func_set = {}

    # nested function의 경우 안 쪽부터 변환해야 하므로 거꾸로 func_set을 구성
    if len(func) == len(param):
        func.reverse()
        param.reverse()

        # stan_var 파악
        for i, v in enumerate(func):
            cur_func_name = v
            stan_var = None
            # func_name이 param 중에 있는지 확인
            for j, v in enumerate(param):
                index = param[j].find(cur_func_name)
                # 있다면 .func_name 앞 부분을 stan_var로 set
                if index > -1:
                    stan_var = param[j][:index-1].lstrip()
                    break

            func_set.update({(stan_var, func[i]):param[i]})
    else:
        raise Exception("func과 param의 길이가 맞지 않음")

    return func_set

def get_values_list(values):
    """
    function chaining 형태를 해결하기 위해 func_set 기준으로 values 구분

    :param values: ex) .append(group.mean()).groupby(price['year'])
    :return: values_list ex) [.append(group.mean()), .groupby(price['year'])]
    """
    dot_list = []
    values_list = []

    # STEP 1. 함수 단위로 구분하기 위해 '.' 위치 파악
    for match in re.finditer('\.', values):
        dot_list.append(match.start())

    # STEP 2. 함수 형태를 이루고 있는지 확인
    finish_index = -1
    for i, v in enumerate(dot_list):
        # parameter에 있는 함수는 고려하지 않음
        if v < finish_index:
            continue

        start_index = dot_list[i]
        end_index = -1
        open_parent_flag = False # '(' 괄호 확인시 True
        func_check = False
        parent_count = 0
        for i in range(start_index, len(values), 1):
            # 함수인 경우
            if open_parent_flag and parent_count == 0:
                func_check = True
                end_index = i
                break
            # 괄호 확인
            if values[i] == '(':
                open_parent_flag = True
                parent_count = parent_count + 1
                continue
            if values[i] == ')':
                parent_count = parent_count - 1
                if i == len(values)-1:
                    func_check = True
                    end_index = i+1
                continue

        if func_check and parent_count == 0:
            values_list.append(values[start_index:end_index])
            finish_index = end_index

    return values_list

def divide_values(values):
    """
    values(line에서 대입 연산자를 제외한 부분)를 parsing하여 stan_var, values, func_set_list로 구분하여 반환

    func_set_list는 func_set list로 구성 즉, [{func_name : param}, {func_name : param}, ..]
    func_set은 key-func_name, value-param 로 구성된 dictionary로 구성 func_dic 로 구성 즉, {func_name : param}

    case 1. function이 없을 경우
    - stan_var, values, []
    case 2. 단일 function일 경우,
    - stan_var, [{func_name : param}]
    case 3. 여러 function일 경우,
    case 3-1. chaining
    - stan_var, [{func_name_1 : param_1}, {func_name_2 : param_2}]
    case 3-2. nested function일 경우,
    - stan_var [{func_name_1 : param_1, func_name_2 : param_2}, {func_name_3 : param_3}]

    :param values:
    :return: stan_var, values, func_set_list
    :Args:
        stan_var : function or 데이터 대상 변수명
        values : stan_var에 적용할 데이터
        func_set_list : func_set list
    """
    stan_var = None
    origin_values = values
    func_set_list = []

    # STEP 1. function 유무 확인
    func_flag = True

    stan_var_index = values.find('.')
    if stan_var_index > -1:
        stan_var = values[:stan_var_index]
        values_list = get_values_list(values[stan_var_index:].rstrip())

        # '.' 적용 변수(stan_var)의 유효성을 판단함으로써 func 유무 파악
        for i, v in enumerate(stan_var):
            if v == '(':
                stan_var = None
                func_flag = False
                values = origin_values
                break
        # values_list 에 대한 function 유효성 파악
        if len(values_list) > 0:
            if not valid_func(values_list[0]):
                stan_var = None
                func_flag = False
                values = origin_values
    else:
        func_flag = False

    # STEP 2. 후보군 유효성 파악
    stan_var = valid_stan_var(stan_var)

    # STEP 3-1. function이 있을 경우 (case 2,3,4) 처리
    if func_flag:
        for values in values_list:
            func_pattern = '\.(.*?)\('

            # STEP 4. pattern을 통해 func 후보군 추출 및 유효성 파악
            func_list = re.findall(func_pattern, values)
            func_list = valid_func_name(func_list)

            # STEP 5. func_list, valuse을 통해 param_list 추출
            param_list = valid_param(func_list, values)

            # STEP 6. func_set 구성
            func_set = construct_func_set(func_list, param_list)
            func_set_list.append(func_set)

        return stan_var, values, func_set_list
    else:
        # STEP 3-2. function이 없을 경우 (case 1) 처리
        return stan_var, values, func_set_list

while line:
    # STEP 1. valid log 파악
    log_pattern = '.py(.*?)\:'

    # STEP 1-1. ~~~.py(num): format 인지 파악
    if len(re.findall(log_pattern, line)) == 0:
        line = f.readline()
        continue

    # STEP 1-2. 조건문(if) or 반복문(for 문)인지 파악
    if line.find(" if ") > -1 or line.find(" for ") > -1 or line.find(" return ") > -1:
        line = f.readline()
        continue

    # STEP 2. line number 관련 정보 제거
    colon_index = line.find(':')
    line = line[colon_index + 1:]

    # STEP 3. 대입 연산자('=') 유무 파악하여 create_var 결정
    # 만약 대입 연산자('=')가 있다면 그 위치 전에 괄호가 없어야 유효
    assign_index = line.find('=')
    assign = True

    if assign_index > -1:
        for i in range(assign_index-1, 0, -1):
            if line[i] == '(':
                assign = False
                continue

    if assign_index > -1 and assign:
        assign_valid = True
    else:
        assign_valid = False

    # STEP 4. search_operation func 인자(create_var, stan_var, func, param) 파악
    # STPE 4-1. create_var, values로 구분
    import_check = False
    def_check = False
    # 대입 연산자('=')가 있는 경우
    if assign_valid:
        create_var = line[:assign_index].strip()
        values = line[assign_index+1:].strip()
    # 대입 연산자('=')가 없는 경우
    else:
        # import 인지 확인
        import_index = line.find('import')
        if import_index > -1:
            import_check = True

        # def(사용자 정의 함수) 인지 확인
        def_index = line.find('def')
        if def_index > -1:
            def_check = True

        create_var = None
        values = line

    # STEP 4-2. values를 stan_var, func_set_list로 구분
    stan_var, values, func_set_list = divide_values(values)

    # STEP 5. func_set 단위로 search_operator func call[반복]
    # STEP 5-1. func_set이 없는 경우
    if not func_set_list:
        if import_check:
            res = get_import(line)
        elif def_check:
            res = handle_def(line)
        else:
            res = get_variable(create_var, values.rstrip(), stan_var)
        # STEP 6. save log call
        save_log(res)
    # STEP 5-2. func_set이 있는 경우
    else:
        for i, func_set in enumerate(func_set_list):
            res = ""
            nested_flag = False
            for key, value in func_set.items():
                cur_stan_var = key[0]
                # cur_stan_var가 None이면 stan_var로 변경
                if not cur_stan_var:
                    cur_stan_var = stan_var
                cur_func_name = key[1]
                # nested function인 경우cur_param을  그 전 func_set으로 변경
                if not nested_flag:
                    cur_param = value
                    nested_flag = True
                else:
                    cur_param = res
                res = search_operator(cur_stan_var, cur_func_name, cur_param, create_var)
            # STEP 6. save log call
            if res:
                save_log(res)

    line = f.readline()
f.close()

# log 확인
print("\n*****show log list call*****")
show_log_list()