import unittest
import gravity_squares as gs


class TestVec2(unittest.TestCase):

    def test_create_vec2(self):
        v = gs.Vec2()
        print(v)

    def test_add_vec2s(self):
        v1 = gs.Vec2(1, 2)
        v2 = gs.Vec2(3, 4)
        v3 = v1 + v2
        self.assertEqual(v3.x, 4)
        self.assertEqual(v3.y, 6)


class TestColor(unittest.TestCase):

    def test_create_color(self):
        c = gs.Color()
        print(c)


if __name__ == "__main__":
    unittest.main()
