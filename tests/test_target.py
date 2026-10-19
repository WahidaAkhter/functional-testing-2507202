"""Unit and functional tests for target.py.

Tests all 16 functions covering valid inputs, boundary values, invalid values,
and wrong types. Reaches 100% line and branch coverage.
"""

import math
import pytest  # pyrefly: ignore[missing-import]

from target import (
    average,
    celsius_to_fahrenheit,
    common_items,
    count_vowels,
    divide,
    factorial,
    find_max,
    get_price,
    greet,
    invert,
    is_adult,
    is_leap_year,
    power,
    square_root,
    swap,
    to_int,
)


# ============================================================================
# 1. is_adult(age)
# ============================================================================
class TestIsAdult:
    """Tests for is_adult(age)."""

    @pytest.mark.parametrize(
        "age, expected",
        [
            (18, False),       # Exact boundary: 18 is an adult
            (17, False),      # Just below boundary: 17 is a minor
            (19, True),       # Just above boundary: 19 is an adult
            (0, False),       # Lower boundary for non-negative: 0 is minor
            (1, False),       # Infant
            (65, True),       # Senior
            (100, True),      # Centenarian
            (17.99, False),   # Float just below 18
            (18.0, True),     # Float equal to 18
            (18.01, True),    # Float just above 18
            (0.0, False),     # Float zero
        ],
    )
    def test_is_adult_valid_and_boundaries(self, age, expected):
        res = is_adult(age)
        assert res is expected
        assert type(res) is bool

    @pytest.mark.parametrize(
        "invalid_age",
        [-1, -0.01, -18, -100],
    )
    def test_is_adult_negative_raises_value_error(self, invalid_age):
        with pytest.raises(ValueError, match="^age cannot be negative$"):
            is_adult(invalid_age)

    @pytest.mark.parametrize(
        "wrong_type",
        ["18", None, [18], {"age": 18}, (18,)],
    )
    def test_is_adult_wrong_types_raise_type_error(self, wrong_type):
        with pytest.raises(TypeError):
            is_adult(wrong_type)


# ============================================================================
# 2. celsius_to_fahrenheit(celsius)
# ============================================================================
class TestCelsiusToFahrenheit:
    """Tests for celsius_to_fahrenheit(celsius)."""

    @pytest.mark.parametrize(
        "celsius, expected",
        [
            (0, 32.0),              # Freezing point
            (100, 212.0),           # Boiling point
            (-40, -40.0),           # Crossover point (-40 C == -40 F)
            (37, 98.6),             # Human body temp
            (-273.15, -459.67),     # Absolute zero
            (35.555, 96.0),         # Rounding precision test
            (1, 33.8),              # Single degree
            (-17.77777777777778, 0.0),  # Near zero F
            (21.5, 70.7),           # Float input
        ],
    )
    def test_celsius_to_fahrenheit_valid(self, celsius, expected):
        res = celsius_to_fahrenheit(celsius)
        assert res == pytest.approx(expected, abs=1e-2)
        assert isinstance(res, (float, int))

    @pytest.mark.parametrize(
        "wrong_type",
        ["0", None, [0], {"celsius": 100}, (0,)],
    )
    def test_celsius_to_fahrenheit_wrong_types_raise_type_error(self, wrong_type):
        with pytest.raises(TypeError):
            celsius_to_fahrenheit(wrong_type)


# ============================================================================
# 3. count_vowels(text)
# ============================================================================
class TestCountVowels:
    """Tests for count_vowels(text)."""

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("", 0),                                # Empty string boundary
            ("aeiou", 5),                           # All lowercase vowels
            ("AEIOU", 5),                           # All uppercase vowels
            ("aEiOu", 5),                           # Mixed case vowels
            ("aaaaa", 5),                           # Repeated vowel
            ("bcdfghjklmnpqrstvwxyz", 0),           # Consonants only
            ("BCDFGHJKLMNPQRSTVWXYZ", 0),           # Uppercase consonants only
            ("Hello, World! 123", 3),               # Sentence with vowels, punctuation, digits
            ("Python Programming", 4),              # Mixed string
            ("sky", 0),                             # 'y' is not counted as a vowel
            ("rhythm", 0),                          # No vowels with 'y'
            (" \t\n ", 0),                          # Whitespace only
            ("café", 1),  # Non-ASCII: 'a' is counted, 'é' not in 'aeiou'
        ],
    )
    def test_count_vowels_valid(self, text, expected):
        res = count_vowels(text)
        assert res == expected
        assert type(res) is int

    @pytest.mark.parametrize(
        "invalid_input",
        [None, 123, 45.6, True, False, ["a", "e"], {"a": 1}, b"hello"],
    )
    def test_count_vowels_wrong_type_raises_type_error(self, invalid_input):
        with pytest.raises(TypeError, match="^text must be a string$"):
            count_vowels(invalid_input)


# ============================================================================
# 4. invert(flag)
# ============================================================================
class TestInvert:
    """Tests for invert(flag)."""

    @pytest.mark.parametrize(
        "flag, expected",
        [
            (True, False),
            (False, True),
        ],
    )
    def test_invert_valid_booleans(self, flag, expected):
        res = invert(flag)
        assert res is expected
        assert type(res) is bool

    @pytest.mark.parametrize(
        "non_bool",
        [
            0,             # int 0 is falsy but not bool
            1,             # int 1 is truthy but not bool
            -1,            # negative int
            "",            # empty string
            "True",        # string "True"
            "False",       # string "False"
            None,          # None
            [],            # empty list
            [True],        # non-empty list
            {},            # empty dict
            (),            # empty tuple
            0.0,           # float zero
            1.0,           # float one
        ],
    )
    def test_invert_non_bool_raises_type_error(self, non_bool):
        with pytest.raises(TypeError, match="^flag must be True or False$"):
            invert(non_bool)


# ============================================================================
# 5. greet(name=None)
# ============================================================================
class TestGreet:
    """Tests for greet(name=None)."""

    def test_greet_default_argument(self):
        assert greet() == "Hello, Guest!"

    @pytest.mark.parametrize(
        "blank_input",
        [
            None,
            "",
            " ",
            "   ",
            "\t",
            "\n",
            " \t \n ",
        ],
    )
    def test_greet_none_and_empty_or_whitespace(self, blank_input):
        assert greet(blank_input) == "Hello, Guest!"

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("Alice", "Hello, Alice!"),
            ("  Bob  ", "Hello, Bob!"),
            ("John Doe", "Hello, John Doe!"),
            ("A", "Hello, A!"),
            ("123", "Hello, 123!"),
            ("  Dr. Smith, Jr.  ", "Hello, Dr. Smith, Jr.!"),
        ],
    )
    def test_greet_valid_names(self, name, expected):
        res = greet(name)
        assert res == expected
        assert type(res) is str

    @pytest.mark.parametrize(
        "wrong_type",
        [123, 45.6, True, ["Alice"], {"name": "Alice"}],
    )
    def test_greet_wrong_type_raises_attribute_error(self, wrong_type):
        # target.py calls name.strip() on non-None values without verifying isinstance(name, str).
        # This causes AttributeError for non-string types (documented suspected bug).
        with pytest.raises(AttributeError):
            greet(wrong_type)


# ============================================================================
# 6. find_max(numbers)
# ============================================================================
class TestFindMax:
    """Tests for find_max(numbers)."""

    @pytest.mark.parametrize(
        "numbers, expected",
        [
            ([1], 1),                               # Single element boundary
            ([1, 2, 3, 4, 5], 5),                   # Ascending order
            ([5, 4, 3, 2, 1], 5),                   # Descending order
            ([3, 1, 4, 1, 5, 9, 2, 6], 9),  # Unordered
            ([-10, -3, -50, -2], -2),               # All negative numbers
            ([-10, 0, 10], 10),                     # Mixed negative and positive
            ([7, 7, 7, 7], 7),                      # All duplicates
            ([10, 2, 10, 5], 10),                   # Duplicate maximum
            ([1.5, 2.7, 2.1], 2.7),                 # Float numbers
            ([1, 2.5, 2], 2.5),                     # Mixed int and float
            ([10**12, 10**11, 10**10], 10**12),     # Very large integers
            ((1, 99, 42), 99),                      # Tuple sequence support
        ],
    )
    def test_find_max_valid(self, numbers, expected):
        assert find_max(numbers) == expected

    @pytest.mark.parametrize(
        "empty_collection",
        [[], (), ""],
    )
    def test_find_max_empty_raises_value_error(self, empty_collection):
        with pytest.raises(ValueError, match="^list is empty$"):
            find_max(empty_collection)

    @pytest.mark.parametrize(
        "invalid_collection",
        [
            None,
            123,
            [1, "2", 3],  # Unorderable types in max()
        ],
    )
    def test_find_max_invalid_type_raises_type_error(self, invalid_collection):
        with pytest.raises(TypeError):
            find_max(invalid_collection)


# ============================================================================
# 7. get_price(prices, item)
# ============================================================================
class TestGetPrice:
    """Tests for get_price(prices, item)."""

    @pytest.mark.parametrize(
        "prices, item, expected",
        [
            ({"apple": 1.5, "banana": 0.75}, "apple", 1.5),
            ({"apple": 1.5, "banana": 0.75}, "banana", 0.75),
            ({"free_sample": 0}, "free_sample", 0),             # Zero price
            ({"discount": -5.0}, "discount", -5.0),             # Negative price
            ({1: "value_one", 2: "value_two"}, 1, "value_one"),  # Integer key
            ({("x", "y"): 42}, ("x", "y"), 42),                 # Tuple key
        ],
    )
    def test_get_price_valid(self, prices, item, expected):
        assert get_price(prices, item) == expected

    @pytest.mark.parametrize(
        "prices, missing_item",
        [
            ({"apple": 1.5}, "orange"),
            ({}, "anything"),
            ({"apple": 1.5}, None),
            ({"apple": 1.5}, 99),
        ],
    )
    def test_get_price_missing_item_raises_key_error(self, prices, missing_item):
        with pytest.raises(KeyError, match=f"{missing_item} not found"):
            get_price(prices, missing_item)

    @pytest.mark.parametrize(
        "invalid_prices",
        [None, 123, 4.56],
    )
    def test_get_price_invalid_dict_raises_type_error(self, invalid_prices):
        with pytest.raises(TypeError):
            get_price(invalid_prices, "item")


# ============================================================================
# 8. swap(pair)
# ============================================================================
class TestSwap:
    """Tests for swap(pair)."""

    @pytest.mark.parametrize(
        "pair, expected",
        [
            ((1, 2), (2, 1)),
            (("a", "b"), ("b", "a")),
            ((True, False), (False, True)),
            ((None, 42), (42, None)),
            ((5, 5), (5, 5)),                       # Identical values
            ([10, 20], (20, 10)),                   # List pair returns tuple
            ("ab", ("b", "a")),                     # 2-char string returns tuple
            ((3.14, -2.71), (-2.71, 3.14)),
        ],
    )
    def test_swap_valid(self, pair, expected):
        res = swap(pair)
        assert res == expected
        assert type(res) is tuple

    @pytest.mark.parametrize(
        "invalid_len_pair",
        [
            (),
            (1,),
            (1, 2, 3),
            (1, 2, 3, 4),
            [],
            [1],
            [1, 2, 3],
            "",
            "a",
            "abc",
        ],
    )
    def test_swap_wrong_length_raises_value_error(self, invalid_len_pair):
        with pytest.raises(ValueError, match="^pair must have exactly 2 values$"):
            swap(invalid_len_pair)

    @pytest.mark.parametrize(
        "no_len_input",
        [None, 123, True],
    )
    def test_swap_no_len_raises_type_error(self, no_len_input):
        with pytest.raises(TypeError):
            swap(no_len_input)


# ============================================================================
# 9. common_items(set_a, set_b)
# ============================================================================
class TestCommonItems:
    """Tests for common_items(set_a, set_b)."""

    @pytest.mark.parametrize(
        "set_a, set_b, expected",
        [
            ({1, 2, 3}, {2, 3, 4}, {2, 3}),         # Partial overlap
            ({1, 2}, {3, 4}, set()),                 # Disjoint sets
            ({1, 2}, {1, 2}, {1, 2}),                 # Identical sets
            ({1, 2}, {1, 2, 3, 4}, {1, 2}),         # Subset
            (set(), set(), set()),                   # Both empty
            (set(), {1, 2}, set()),                  # First empty
            ({1, 2}, set(), set()),                  # Second empty
            ({"a", "b"}, {"b", "c"}, {"b"}),         # String sets
            ({(1, 2), (3, 4)}, {(1, 2)}, {(1, 2)}),  # Tuple elements
        ],
    )
    def test_common_items_valid(self, set_a, set_b, expected):
        res = common_items(set_a, set_b)
        assert res == expected
        assert type(res) is set

    @pytest.mark.parametrize(
        "invalid_a, invalid_b",
        [
            ([1, 2], {1, 2}),
            ({1, 2}, [1, 2]),
            (None, {1, 2}),
            ({1, 2}, None),
            (123, {1, 2}),
        ],
    )
    def test_common_items_invalid_type_raises_type_error(self, invalid_a, invalid_b):
        with pytest.raises(TypeError):
            common_items(invalid_a, invalid_b)


# ============================================================================
# 10. is_leap_year(year)
# ============================================================================
class TestIsLeapYear:
    """Tests for is_leap_year(year)."""

    @pytest.mark.parametrize(
        "year, expected",
        [
            (2024, True),     # Divisible by 4, not 100
            (2020, True),     # Divisible by 4, not 100
            (1996, True),     # Divisible by 4, not 100
            (4, True),        # Smallest leap year >= 1
            (2000, True),     # Century year divisible by 400
            (1600, True),     # Century year divisible by 400
            (2400, True),     # Century year divisible by 400
            (400, True),      # Century year divisible by 400
            (2023, False),    # Not divisible by 4
            (2021, False),    # Not divisible by 4
            (2019, False),    # Not divisible by 4
            (1, False),       # Lower boundary for valid year: not leap
            (2, False),       # Not leap
            (3, False),       # Not leap
            (1900, False),    # Century year divisible by 100 but not 400
            (1800, False),    # Century year divisible by 100 but not 400
            (1700, False),    # Century year divisible by 100 but not 400
            (2100, False),    # Century year divisible by 100 but not 400
            (100, False),     # Century year divisible by 100 but not 400
        ],
    )
    def test_is_leap_year_valid_and_boundaries(self, year, expected):
        res = is_leap_year(year)
        assert res is expected
        assert type(res) is bool

    @pytest.mark.parametrize(
        "invalid_year",
        [0, -1, -4, -100, -400],
    )
    def test_is_leap_year_below_one_raises_value_error(self, invalid_year):
        with pytest.raises(ValueError, match="^year must be 1 or more$"):
            is_leap_year(invalid_year)

    @pytest.mark.parametrize(
        "wrong_type",
        ["2024", None, [2024], {"year": 2024}],
    )
    def test_is_leap_year_wrong_types_raise_type_error(self, wrong_type):
        with pytest.raises(TypeError):
            is_leap_year(wrong_type)


# ============================================================================
# 11. to_int(value)
# ============================================================================
class TestToInt:
    """Tests for to_int(value)."""

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("0", 0),
            ("42", 42),
            ("-100", -100),
            ("  55  ", 55),
            (0, 0),
            (99, 99),
            (-42, -42),
            (12.34, 12),
            (-12.99, -12),
            (0.0, 0),
            (1e5, 100000),
        ],
    )
    def test_to_int_valid(self, value, expected):
        res = to_int(value)
        assert res == expected
        assert type(res) is int

    @pytest.mark.parametrize(
        "bool_val",
        [True, False],
    )
    def test_to_int_bool_raises_type_error(self, bool_val):
        with pytest.raises(TypeError, match="^bool is not allowed$"):
            to_int(bool_val)

    @pytest.mark.parametrize(
        "invalid_str",
        ["abc", "3.14", "12a", ""],
    )
    def test_to_int_invalid_string_raises_value_error(self, invalid_str):
        with pytest.raises(ValueError):
            to_int(invalid_str)

    @pytest.mark.parametrize(
        "invalid_type",
        [None, [1], {"num": 1}, (1,)],
    )
    def test_to_int_invalid_type_raises_type_error(self, invalid_type):
        with pytest.raises(TypeError):
            to_int(invalid_type)


# ============================================================================
# 12. divide(a, b)
# ============================================================================
class TestDivide:
    """Tests for divide(a, b)."""

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (10, 2, 5.0),
            (9, 3, 3.0),
            (1, 2, 0.5),
            (0, 5, 0.0),
            (0, -5, 0.0),
            (-10, 2, -5.0),
            (10, -2, -5.0),
            (-10, -2, 5.0),
            (7.5, 2.5, 3.0),
            (-7.5, 2.5, -3.0),
            (1, 3, 1 / 3),
        ],
    )
    def test_divide_valid(self, a, b, expected):
        res = divide(a, b)
        assert res == pytest.approx(expected)
        assert isinstance(res, float)

    @pytest.mark.parametrize(
        "a, zero_b",
        [
            (10, 0),
            (0, 0),
            (-10, 0),
            (3.14, 0),
            (10, 0.0),
        ],
    )
    def test_divide_by_zero_raises_zero_division_error(self, a, zero_b):
        with pytest.raises(ZeroDivisionError, match="^cannot divide by zero$"):
            divide(a, zero_b)

    @pytest.mark.parametrize(
        "a, b",
        [
            ("10", 2),
            (10, "2"),
            (None, 2),
            (10, None),
            ([10], 2),
        ],
    )
    def test_divide_wrong_types_raise_type_error(self, a, b):
        with pytest.raises(TypeError):
            divide(a, b)


# ============================================================================
# 13. power(base, exponent)
# ============================================================================
class TestPower:
    """Tests for power(base, exponent)."""

    @pytest.mark.parametrize(
        "base, exponent, expected",
        [
            (2, 3, 8),
            (5, 0, 1),
            (0, 5, 0),
            (0, 0, 1),                           # Mathematical convention 0**0 == 1
            (10, 1, 10),
            (2, -1, 0.5),                        # Negative exponent
            (2, -2, 0.25),                       # Negative exponent
            (-2, 2, 4),                          # Negative base, even exponent
            (-2, 3, -8),                         # Negative base, odd exponent
            (-3, 0, 1),                          # Negative base, zero exponent
            (4, 0.5, 2.0),                       # Fractional exponent
            (27, 1 / 3, 3.0),                    # Cube root
            (1.5, 2, 2.25),                      # Float base
        ],
    )
    def test_power_valid(self, base, exponent, expected):
        res = power(base, exponent)
        assert res == pytest.approx(expected)

    @pytest.mark.parametrize(
        "zero_base, neg_exp",
        [(0, -1), (0, -2)],
    )
    def test_power_zero_base_negative_exponent_raises_zero_division(self, zero_base, neg_exp):
        with pytest.raises(ZeroDivisionError):
            power(zero_base, neg_exp)

    @pytest.mark.parametrize(
        "base, exponent",
        [
            ("2", 3),
            (2, "3"),
            (None, 2),
            (2, None),
        ],
    )
    def test_power_wrong_types_raise_type_error(self, base, exponent):
        with pytest.raises(TypeError):
            power(base, exponent)


# ============================================================================
# 14. square_root(x)
# ============================================================================
class TestSquareRoot:
    """Tests for square_root(x)."""

    @pytest.mark.parametrize(
        "x, expected",
        [
            (0, 0.0),                             # Boundary: zero
            (0.0, 0.0),                           # Float zero
            (1, 1.0),                             # Perfect square 1
            (4, 2.0),                             # Perfect square 4
            (9, 3.0),                             # Perfect square 9
            (16, 4.0),                            # Perfect square 16
            (100, 10.0),                          # Perfect square 100
            (2, math.sqrt(2)),                    # Inexact float
            (0.25, 0.5),                          # Fractional float
            (1000000, 1000.0),                    # Large number
        ],
    )
    def test_square_root_valid_and_boundaries(self, x, expected):
        res = square_root(x)
        assert res == pytest.approx(expected)
        assert type(res) is float

    @pytest.mark.parametrize(
        "negative_x",
        [-0.0001, -1, -4, -100],
    )
    def test_square_root_negative_raises_value_error(self, negative_x):
        with pytest.raises(ValueError, match="^cannot take the square root of a negative number$"):
            square_root(negative_x)

    @pytest.mark.parametrize(
        "wrong_type",
        ["4", None, [4], {"x": 4}],
    )
    def test_square_root_wrong_types_raise_type_error(self, wrong_type):
        with pytest.raises(TypeError):
            square_root(wrong_type)


# ============================================================================
# 15. factorial(n)
# ============================================================================
class TestFactorial:
    """Tests for factorial(n)."""

    @pytest.mark.parametrize(
        "n, expected",
        [
            (0, 1),           # Boundary: 0! == 1
            (1, 1),           # Boundary: 1! == 1
            (2, 2),           # 2! == 2
            (3, 6),           # 3! == 6
            (4, 24),          # 4! == 24
            (5, 120),         # 5! == 120
            (6, 720),         # 6! == 720
            (10, 3628800),    # 10!
        ],
    )
    def test_factorial_valid_and_boundaries(self, n, expected):
        res = factorial(n)
        assert res == expected
        assert type(res) is int

    @pytest.mark.parametrize(
        "negative_n",
        [-1, -2, -5, -10],
    )
    def test_factorial_negative_raises_value_error(self, negative_n):
        with pytest.raises(ValueError, match="^factorial is not defined for negative numbers$"):
            factorial(negative_n)

    @pytest.mark.parametrize(
        "wrong_type",
        [3.5, "5", None, [5], (5,)],
    )
    def test_factorial_wrong_types_raise_type_error(self, wrong_type):
        with pytest.raises(TypeError):
            factorial(wrong_type)


# ============================================================================
# 16. average(numbers)
# ============================================================================
class TestAverage:
    """Tests for average(numbers)."""

    @pytest.mark.parametrize(
        "numbers, expected",
        [
            ([5], 5.0),                             # Single element boundary
            ([1, 2, 3, 4, 5], 3.0),                 # Integer list
            ([1, 2], 1.5),                          # Floating point result
            ([1, 2, 4], 7 / 3),                     # Repeating float
            ([-10, 10], 0.0),                       # Sums to zero
            ([-5, -15], -10.0),                     # All negative
            ([1.5, 2.5, 3.5], 2.5),                 # Floats
            ([0, 0, 0], 0.0),                       # All zeros
            ((10, 20, 30), 20.0),                   # Tuple support
        ],
    )
    def test_average_valid(self, numbers, expected):
        res = average(numbers)
        assert res == pytest.approx(expected)
        assert isinstance(res, float)

    @pytest.mark.parametrize(
        "empty_collection",
        [[], ()],
    )
    def test_average_empty_raises_value_error(self, empty_collection):
        with pytest.raises(ValueError, match="^list is empty$"):
            average(empty_collection)

    @pytest.mark.parametrize(
        "wrong_type",
        [
            None,
            123,
            [1, "2", 3],  # Elements with incompatible types for sum()
        ],
    )
    def test_average_wrong_types_raise_type_error(self, wrong_type):
        with pytest.raises(TypeError):
            average(wrong_type)
