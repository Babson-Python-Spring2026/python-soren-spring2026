# refernce code for structure and reference point
'''
class Box:
    def __init__(self, value):
        self.value = value
    def add_one(self):
        self.value += 1

my_int = Box(5)
print(my_int.value)
'''

'''
STI commentary

State:
The variables that must be tracked are: longest_increasing_run(length of the run), longest_decreasing_run(length of the run), num_increasing_runs(count of the increasing runs),
num_decreasing_runs(count of decreasing runs), and technically longest_run_values(what the run contains) but that can be determined at the end

Transitions:
When a run continues the count increases for length. This must happen while not duplicating or repeating the 
previous items of the run. When a run ends it must be tested for the longest.

Invariants:
The input must include integers, the input must be a list, for a run to qualify it must be 2 numbers or longers,
runs must be increasing or decreasing they cannot be equal, the values of longest run should also be the length
of the of the longest run

'''

# actual code

def analyze_runs(nums):
    """
    Analyze maximal contiguous increasing and decreasing runs in a list of integers.

    A run is:
    - maximal and contiguous
    - strictly increasing or strictly decreasing
    - allowed to share a turning-point value with an adjacent run
    - at least length 2

    Returns:
        dict | None
    """
    # invariants are that inputs must be integers in lists
    if not isinstance(nums, list):
        print("Error: input must be a list of integers.")
        return None

    if any(not isinstance(x, int) for x in nums):
        print("Error: all elements in the input list must be integers.")
        return None

    # invariant: runs must be 2 or more numbers to count as runs
    if len(nums) < 2:
        return {
            "longest_increasing_run": 0,
            "longest_decreasing_run": 0,
            "num_increasing_runs": 0,
            "num_decreasing_runs": 0,
            "longest_run_values": []
        }

    # this is a way to record state
    increasing_runs = []
    decreasing_runs = []

    i = 0
    n = len(nums)

    # this is a transition counting increasing and decreasing runs
    while i < n - 1:
        if nums[i + 1] > nums[i]:
            start = i
            while i < n - 1 and nums[i + 1] > nums[i]:
                i += 1
            increasing_runs.append(nums[start:i + 1])

        elif nums[i + 1] < nums[i]:
            start = i
            while i < n - 1 and nums[i + 1] < nums[i]:
                i += 1
            decreasing_runs.append(nums[start:i + 1])

        else:
            i += 1

    longest_increasing_run = max((len(run) for run in increasing_runs), default=0)
    longest_decreasing_run = max((len(run) for run in decreasing_runs), default=0)

    # sets the state for edge cases/if they are not entries of a certain level
    longest_run_values = []
    longest_run_length = 0

    # updates/transitions state of longest_run_length and longest_run_values
    for run in increasing_runs + decreasing_runs:
        if len(run) > longest_run_length:
            longest_run_length = len(run)
            longest_run_values = run

    # returns final state
    return {
        "longest_increasing_run": longest_increasing_run,
        "longest_decreasing_run": longest_decreasing_run,
        "num_increasing_runs": len(increasing_runs),
        "num_decreasing_runs": len(decreasing_runs),
        "longest_run_values": longest_run_values
    }

nums = [3, 5, 7, 2, 1, 4]
print(analyze_runs(nums))