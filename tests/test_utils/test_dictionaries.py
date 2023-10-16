import unittest

from utils.dictionaries import prune_dictionary_keys


class TestDictionariesHelpers(unittest.TestCase):
    def test_prune_dictionary_keys__removes_keys(self):
        input_dict = {
            "a": 1,
            "b": 2,
            "c": 3,
        }

        output_dict_1 = prune_dictionary_keys(input_dict, ["b"])
        self.assertDictEqual(
            output_dict_1,
            {
                "b": 2,
            },
        )

        output_dict_2 = prune_dictionary_keys(input_dict, [])
        self.assertDictEqual(
            output_dict_2,
            {},
        )

    def test_prune_dictionary_keys__does_not_modify_input(self):
        input_dict = {
            "a": 1,
            "b": 2,
            "c": 3,
        }
        prune_dictionary_keys(input_dict, [])
        self.assertDictEqual(
            input_dict,
            {
                "a": 1,
                "b": 2,
                "c": 3,
            },
        )
