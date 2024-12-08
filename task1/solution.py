import unittest
from typing import Callable


def strict(func: Callable):
    # wrap passed function with type checking 
    def check_wrapper(*args):
        anotations: dict = func.__annotations__   # kw dictionary of args and their annotations 
        anotations.pop('return', 'no return type') # remove anotation for return type if it excists

        start_i = len(args) - len(anotations)     # idx of 1-st anotated arg (some leading args might be without annotation)
        for i, anot_type in enumerate(anotations.values()):
            if not isinstance(args[start_i + i], anot_type):
                raise TypeError()     # tell about type missmatch
         
        return func(*args)  # run passed in function if all is OK


    # return modified function
    return check_wrapper



@strict
def sum_two(a: int, b: int) -> int:
    return a + b

@strict
def sum_three(a: int, b: float, c: int) -> float:
    ''' 2nd param is float '''
    return a + b + c

@strict
def sum_three_mixed_anot(a, b: float, c: int) -> float:
    ''' 1st arg has no annotation, while rest - have '''
    return a + b + c


class TestStrictDecorator(unittest.TestCase):
    
    def test_correct_types(self):
        self.assertEqual(sum_two(1, 2), 3) 

    def test_correct_types_sum_three(self):
        self.assertEqual(sum_three(1, 2.7, 3), 6.7)

    def test_correct_types_sum_three_mixed_anot(self):
        self.assertEqual(sum_three_mixed_anot(True, 2.7, 3), 6.7)

    def test_incorrect_types(self):
        with self.assertRaises(TypeError):
            sum_two("1", 2)  
    
    def test_incorrect_types2(self):
        with self.assertRaises(TypeError):
            sum_two(1, 2.4)  

    def test_incorrect_types3(self):
        with self.assertRaises(TypeError):
            sum_two(False, 2.4)  

    def test_incorrect_types_sum_three(self):
        with self.assertRaises(TypeError):
            sum_three(1, 2, 3)

if __name__ == '__main__':
    unittest.main()