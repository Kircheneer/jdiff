import pdb
from collections import defaultdict
class Operator():    
    
    def __init__(self, referance_data, value_to_compare) -> None:
        
        self.referance_data_type = list(referance_data.keys())[0]
        self.referance_data_value = list(referance_data.values())[0]
        self.value_to_compare = value_to_compare

    
    def all_same(self):
        # [{'7.7.7.7': {'peerGroup': 'EVPN-OVERLAY-SPINE', 'vrf': 'default', 'state': 'Idle'}}, 
        # {'10.1.0.0': {'peerGroup': 'IPv4-UNDERLAY-SPINE', 'vrf': 'default', 'state': 'Idle'}}, 
        # {'10.2.0.0': {'peerGroup': 'IPv4-UNDERLAY-SPINE', 'vrf': 'default', 'state': 'Idle'}}, 
        # {'10.64.207.255': {'peerGroup': 'IPv4-UNDERLAY-MLAG-PEER', 'vrf': 'default', 'state': 'Idle'}}]
        list_of_values = list()
        result = list()

        for item in self.value_to_compare:
            for value in item.values():
                # Create a list for compare valiues.
                list_of_values.append(value)

        for element in list_of_values:
            if not element == list_of_values[0]:
                result.append(False)
            else:
                result.append(True)

        if self.referance_data_value and not all(result):
            return (False, self.value_to_compare)
        elif self.referance_data_value and all(result):
            return (True, self.value_to_compare)
        elif not self.referance_data_value and not all(result):
            return (True, self.value_to_compare)
        elif not self.referance_data_value and all(result):
            return (False, self.value_to_compare)

