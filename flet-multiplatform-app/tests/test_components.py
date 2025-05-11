import unittest
from src.components.common.app_card import AppCard
from src.components.common.custom_buttons import primary_button, secondary_button
from src.components.common.loading_skeleton import create_skeleton

class TestComponents(unittest.TestCase):

    def test_app_card(self):
        card = AppCard("Test Title", "Test Description", "https://example.com/image.jpg")
        self.assertIsNotNone(card)
        self.assertEqual(card.title, "Test Title")
        self.assertEqual(card.description, "Test Description")
        self.assertEqual(card.image_url, "https://example.com/image.jpg")

    def test_primary_button(self):
        button = primary_button("Click Me", lambda: None)
        self.assertIsNotNone(button)
        self.assertEqual(button.text, "Click Me")

    def test_secondary_button(self):
        button = secondary_button("Click Me Too", lambda: None)
        self.assertIsNotNone(button)
        self.assertEqual(button.text, "Click Me Too")

    def test_loading_skeleton(self):
        skeleton = create_skeleton()
        self.assertIsNotNone(skeleton)
        self.assertEqual(len(skeleton.controls), 3)  # Assuming 3 skeleton items are created

if __name__ == '__main__':
    unittest.main()