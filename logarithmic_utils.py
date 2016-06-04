import math


def sum_logscale_list(input_list):
    """
    Given an input list of ints or floats that are log base 10,
    return the total sum of every element in that list,
    also in log base 10.
    """
    exponential_sum = 0
    for i in input_list:
        if i is not None:
            exponential_sum += math.pow(10, i)
    return math.log10(exponential_sum)
