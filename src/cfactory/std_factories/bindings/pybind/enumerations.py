

class ReturnValuePolicy(object):

    TAKE_OWNERSHIP = 0
    COPY = 1
    MOVE = 2
    REFERENCE = 2
    REFERENCE_INTERNAL = 3
    AUTOMATIC = 4
    AUTOMATIC_REFERENCE = 5


value_policy_map = {
    ReturnValuePolicy.TAKE_OWNERSHIP : "return_value_policy::take_ownership",
    ReturnValuePolicy.COPY: "return_value_policy::copy",
    ReturnValuePolicy.MOVE: "return_value_policy::move",
    ReturnValuePolicy.REFERENCE: "return_value_policy::reference",
    ReturnValuePolicy.REFERENCE_INTERNAL: "return_value_policy::reference_internal",
    ReturnValuePolicy.AUTOMATIC: "return_value_policy::automatic",
    ReturnValuePolicy.AUTOMATIC_REFERENCE: "return_value_policy::automatic_reference"
    }
