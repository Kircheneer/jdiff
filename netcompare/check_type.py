"""CheckType Implementation."""
from typing import Mapping, Tuple, List, Dict, Any
from .evaluator import diff_generator, parameter_evaluator, regex_evaluator
from .runner import extract_values_from_output
from pydantic import BaseModel, ValidationError, validator



class CheckType:
    """Check Type Class."""
    # class Validation(BaseModel):
    #     def __init__(self, value_to_compare): 
    #         self.valid_options = (
    #             "all-same",
    #             "is-equal",
    #             "not-equal",
    #             "contains",
    #             "not-contains",
    #             "is-gt",
    #             "is-lt",
    #             "in-range",
    #             "not-range",
    #             "is-in",
    #             "not-in"
    #         )
    #         self.bools = ("all-same")
    #         self.fiter = (
    #             "is-in", 
    #             "not-in",
    #             "in-range",
    #             "not-range"
    #         )
    #         self.numbers = ("is-gt","is-lt")
    #         self.strings = ("contains", "not-contains")
    #         self.value_to_compare = value_to_compare

    # my_check = CheckType.init(*args)

    def __init__(self, *args):
        """Check Type init method."""
        self.validate(*args)

    def validate(*args):
        pass
        
    @staticmethod
    def init(*args):
        """Factory pattern to get the appropriate CheckType implementation.

        Args:
            *args: Variable length argument list.
        """
        check_type = args[0]
        if check_type == "exact_match":
            return ExactMatchType(*args)
        if check_type == "tolerance":
            return ToleranceType(*args)
        if check_type == "parameter_match":
            return ParameterMatchType(*args)
        if check_type == "regex":
            return RegexType(*args)
        if check_type == "operator":
            return OperatorType(*args)
        raise NotImplementedError

    @staticmethod
    def get_value(output: Mapping, path: str, exclude: List = None) -> Any:
        """Return the value contained into a Mapping for a defined path."""
        return extract_values_from_output(output, path, exclude)

    def evaluate(self, reference_value: Any, value_to_compare: Any) -> Tuple[Dict, bool]:
        """Return the result of the evaluation and a boolean True if it passes it or False otherwise.

        This method is the one that each CheckType has to implement.

        Args:
            reference_value: Can be any structured data or just a simple value.
            value_to_compare: Similar value as above to perform comparison.

        Returns:
            tuple: Dictionary representing check result, bool indicating if differences are found.
        """
        self.validate_reference_value(reference_value, value_to_compare)
        self.hook_evaluate()

    def hook_evaluate():
        raise NotImplementedError

    def validate_reference_value(reference_value, value_to_compare):
        raise NotImplementedError


class ExactMatchType(CheckType):
    """Exact Match class docstring."""

    def hook_evaluate(self, reference_value: Any, value_to_compare: Any) -> Tuple[Dict, bool]:
        """Returns the difference between values and the boolean."""
        diff = diff_generator(reference_value, value_to_compare)
        return diff, not diff

    def validate_reference_value(reference_value, value_to_compare):
        if type(reference_value) != type(value_to_compare):
            raise ValueError

    def validate(*args):
        if len(args) > 1:
            raise ValueError


class ToleranceType(CheckType):
    """Tolerance class docstring."""
    def validate(*args):
        """Tolerance init method."""
        try:
            tolerance = args[1]
        except IndexError as error:
            raise f"Tolerance parameter must be defined as float at index 1. You have: {args}" from error

        if not any(isinstance(tolerance, int), isinstance(tolerance, float)):
            raise ValueError

    def evaluate(self, reference_value: Mapping, value_to_compare: Mapping) -> Tuple[Dict, bool]:
        """Returns the difference between values and the boolean. Overwrites method in base class."""
        diff = diff_generator(reference_value, value_to_compare)
        diff = self._get_outliers(diff)
        return diff, not diff

    def _get_outliers(self, diff: Mapping) -> Dict:
        """Return a mapping of values outside the tolerance threshold."""
        result = {
            key: {sub_key: values for sub_key, values in obj.items() if not self._within_tolerance(**values)}
            for key, obj in diff.items()
        }
        return {key: obj for key, obj in result.items() if obj}

    def _within_tolerance(self, *, old_value: float, new_value: float) -> bool:
        """Return True if new value is within the tolerance range of the previous value."""
        max_diff = old_value * self.tolerance_factor
        return (old_value - max_diff) < new_value < (old_value + max_diff)


class ParameterMatchType(CheckType):
    """Parameter Match class implementation."""

    def evaluate(self, reference_value: Mapping, value_to_compare: Mapping) -> Tuple[Dict, bool]:
        """Parameter Match evaluator implementation."""
        try:
            parameter = value_to_compare[1]
        except IndexError as error:
            raise f"Evaluating parameter must be defined as dict at index 1. You have: {value_to_compare}" from error
        if not isinstance(parameter, dict):
            raise TypeError("check_option must be of type dict()")

        diff = parameter_evaluator(reference_value, parameter)
        return diff, not diff


class RegexType(CheckType):
    """Regex Match class implementation."""

    def evaluate(self, reference_value: Mapping, value_to_compare: Mapping) -> Tuple[Mapping, bool]:
        """Regex Match evaluator implementation."""
        # Assert that check parameters are at index 1.
        try:
            parameter = value_to_compare[1]
        except IndexError as error:
            raise IndexError(
                f"Evaluating parameter must be defined as dict at index 1. You have: {value_to_compare}"
            ) from error

        # Assert that check parameters are at index 1.
        if not all([isinstance(parameter, dict)]):
            raise TypeError("check_option must be of type dict().")

        # Assert that check option has 'regex' and 'mode' dict keys.
        if "regex" not in parameter and "mode" not in parameter:
            raise KeyError(
                "Regex check-type requires check-option. Example: dict(regex='.*UNDERLAY.*', mode='no-match')."
            )

        # Assert that check option has 'regex' and 'mode' dict keys.\
        if parameter["mode"] not in ["match", "no-match"]:
            raise ValueError(
                "Regex check-type requires check-option. Example: dict(regex='.*UNDERLAY.*', mode='no-match')."
            )

        diff = regex_evaluator(reference_value, parameter)
        return diff, not diff


class OperatorType(CheckType):
    """Operator class implementation."""




    # elif parameter_key in iter:
    #     #"in", "not-in", "in-range", "not-range" requires an iterable
    #     if not isinstance(parameter_value, list) or not isinstance(parameter_value, tuple):
    #         raise ValueError(f"Range check-option {iter} must have value of type list or tuple. i.e: dict(not-in=('Idle', 'Down')")
    #     # "in-range", "not-range" requires int or floar where value at index 0 is lower than value at index 1
    #     if "range" in parameter_key:
    #         if not (isinstance(parameter_value[0], int) or isinstance(parameter_value[0], float)) and not (isinstance(parameter_value[1], float) or isinstance(parameter_value[1], int)):
    #             raise ValueError(f"Range check-option {iter} must have value of type list or tuple with items of type float or int. i.e: dict(not-range=(70000000, 80000000)")
    #         if not parameter_value[0] < parameter_value[1]:
    #             raise ValueError(f"'range' and 'not-range' must have value at index 0 lower than value at index 1. i.e: dict(not-range=(70000000, 80000000)")
    #     else:
    #         # "is-in", "not-in" requires iterable of strings
    #         for item in parameter_value.values():
    #             if not isinstance(item, str):
    #                 raise ValueError(f"'is-in' and 'not-in' must be an iterable of strings. i.e: dict(is-in=(Idle, Down)")

    # elif parameter_key in numbers:
    #     if not isinstance(parameter_value, float) or not isinstance(parameter_value, int):
    #         raise ValueError(f"Range check-option {numbers} must have value of type float or int. i.e: dict(is-lt=80000000)")

    # elif parameter_key in strings:
    #     if not isinstance(parameter_value, str):
    #         raise ValueError(f"Range check-option {strings} must have value of type string. i.e: dict(contains='EVPN')")


    def evaluate(self, reference_value: Mapping, value_to_compare: Mapping) -> Tuple[Mapping, bool]:
        """Operator evaluator implementation."""

        # Assert that check parameters are at index 1.
        try:
            parameter = value_to_compare[1]
        except IndexError as error:
            raise IndexError(
                f"Evaluating parameter must be defined as dict at index 1. You have: {value_to_compare}"
            ) from error

        parameter: list
        @validator('parameter')
        def parameter_must_be_dict(cls, v):
            if not isinstance(v, list):
                raise TypeError("check-option must be of type dict().")
            return parameter
        
        # parameter_key = list(parameter.keys())[0]
        # parameter_value = list(parameter.values())[0]

        # parameter_key: list
        # parameter_value: list
        # @validator(parameter_key)
        # def check_option_must_be_legal_option(parameter_key):
        #     if parameter_key not in self.valid_options:
        #         raise KeyError(
        #             f"Range check-type requires one of the following check-option: {self.valid_options}"
        #         )

        # # Assert data type for each range option.
        # if parameter_key in bools:
        #     # "all-same" requires boolean True or False
        #     if not isinstance(parameter_value, bool):
        #         raise ValueError(f"Range check-option {bools} must have value of type bool. i.e: dict(all-same=True)")
        
# TODO: compare is no longer the entry point, we should use the libary as:
#   check_type_info = "regex"
#   options = {"regex": ".*UNDERLAY.*", "mode": "no-match"}
#   netcompare_check = CheckType.init(check_type_info, options)
#   pre_result = netcompare_check.get_value(pre_obj, path)
#   post_result = netcompare_check.get_value(post_obj, path)
#   netcompare_check.evaluate(pre_result, post_result)
#
# def compare(
#     pre_obj: Mapping, post_obj: Mapping, path: Mapping, type_info: Iterable, options: Mapping
# ) -> Tuple[Mapping, bool]:
#     """Entry point function.

#     Returns a diff object and the boolean of the comparison.
#     """

#     type_info = type_info.lower()

#     try:
#         type_obj = CheckType.init(type_info, options)
#     except Exception:
#         # We will be here if we can't infer the type_obj
#         raise

#     return type_obj.evaluate(pre_obj, post_obj, path)
