import unittest

from benchmarking.simulation.utils import chunk


class TestUtils(unittest.TestCase):
    def test_chunk__returns_list_len_equal_to_num_threads(self):
        for num_threads in [1, 2, 4]:
            self.assertEqual(num_threads, len(chunk(12, num_threads)))

    def test_chunk__evenly_divisible(self):
        result = chunk(10, 2)
        self.assertListEqual([5, 5], result)

    def test_chunk__returns_correct_worker_array_when_num_runs_less_than_num_workers(self):
        for num_threads in [4, 5, 6, 29837]:
            chunk_array = chunk(4, num_threads)
            self.assertEqual(4, len(chunk_array))
            self.assertListEqual([1, 1, 1, 1], chunk_array)

    def test_chunk__not_evenly_divisible(self):
        result = chunk(10, 3)
        self.assertListEqual([4, 3, 3], result)

    def test_chunk__result_adds_to_num_runs(self):
        for num_runs in [1, 234, 9, 25]:
            self.assertEqual(num_runs, sum(chunk(num_runs, 7)))

    def test_chunk__rejects_invalid_args(self):
        self.assertRaises(ValueError, lambda: chunk(0, 12))
        self.assertRaises(ValueError, lambda: chunk(-1, 12))
        self.assertRaises(ValueError, lambda: chunk(12, 0))
        self.assertRaises(ValueError, lambda: chunk(0, -1))
