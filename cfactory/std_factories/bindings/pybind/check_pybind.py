from illuminate.code_models.parse_object import ParseObject
from illuminate.code_models.variable import VariableObject
from illuminate.code_models.function_param import FunctionParamObject
from illuminate.code_models.function import FunctionObject
from illuminate.code_models.enumeration import EnumObject
from illuminate.code_models.member_function import MemberFunctionObject
from illuminate.code_models.member import MemberObject
from illuminate.code_models.class_object import ClassObject

import illuminate.pybind.pybind_opt as po

opt_dict = {
        MemberFunctionObject: po.FunctionOpt,
        FunctionObject: po.FunctionOpt,
        FunctionParamObject: po.FunctionParamOpt,
        VariableObject: po.VariableOpt,
        MemberObject: po.VariableOpt,
        EnumObject: po.EnumOpt,
        ClassObject: po.ClassOpt
}


def check_pybind_opt(obj: ParseObject) -> ParseObject:
    print(obj.get_name() + ' check_pybind_opt')
    try:
        check = obj.pybind
    except:
        obj.pybind = opt_dict[type(obj)]()
    return obj

def check_opt(func):

    def _check_opt(ctx, parse_obj, *args, **kwargs):
        print(parse_obj.get_name() + ' check_opt')
        checked = check_pybind_opt(parse_obj)
        return func(parse_obj)

    return _check_opt
