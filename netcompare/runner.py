#!/ur/bin/env python3
import re
import jmespath
from typing import Mapping, List, Union
from .utils.jmspath_parsers import jmspath_value_parser, jmspath_refkey_parser
from .utils.filter_parsers import exclude_filter
from .utils.refkey import keys_cleaner, keys_values_zipper, associate_key_of_my_value
from .utils.flatten import flatten_list
import pdb

def extract_values_from_output(value: Mapping, path: Mapping, exclude: List) -> Union[Mapping, List, int, str, bool]:
    """Return data from output depending on the check path. See unit text for complete example.

    Args:
        path: "result[0].vrfs.default.peerList[*].[$peerAddress$,prefixesReceived]",
        value: {
            "jsonrpc": "2.0",
            "id": "EapiExplorer-1",
            "result": [
                {
                "vrfs": {
                    "default": {
                    "peerList": [
                        { ...
        exclude: ["interfaceStatistics", "interfaceCounters"]

    Return:
        [{'7.7.7.7': {'prefixesReceived': 101}}, {'10.1.0.0': {'prefixesReceived': 120}}, ...
    """
    # Get the wanted values to be evaluated if jmspath expression is defined, otherwise
    # use the entire output if jmespath is not defined in check. This cover the "raw" diff type.
    if path:
        value = jmespath.search(jmspath_value_parser(path), value)

    # Exclude filter implementation.
    if exclude:
        exclude_filter(value, exclude)


    # check if list of lists
    if not any(isinstance(i, list) for i in value):
        raise TypeError(
            "Catching value must be defined as list in jmespath expression i.e. result[*].state -> result[*].[state]. You have {}'.".format(
                path
            )
        )

    for element in value:
        for item in element:
            if isinstance(item, dict):
                raise TypeError(
                    'Must be list of lists i.e. [["Idle", 75759616], ["Idle", 75759620]]. You have {}\'.'.format(
                        value
                    )
                )
            elif isinstance(item, list):
                flatten_list(value)
                break
    
    if path:
        paired_key_value = associate_key_of_my_value(jmspath_value_parser(path), value)
    else:
        paired_key_value = value

    pdb.set_trace()
    if path and re.search(r"\$.*\$", path):
        wanted_reference_keys = jmespath.search(jmspath_refkey_parser(path), value)
        list_of_reference_keys = keys_cleaner(wanted_reference_keys)
        return keys_values_zipper(list_of_reference_keys, paired_key_value)
    else:
        return paired_key_value
