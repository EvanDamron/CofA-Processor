import unittest
import os

class TestOCRAccuracy(unittest.TestCase):
    def setUp(self):
        """Setup relative file paths for reference and output files."""
        self.test_dir = os.path.dirname(__file__)  # Get the folder where this test script is located
        self.reference_file = os.path.join(self.test_dir, "Raw_Material_Correct.txt")
        self.output_file = os.path.join(self.test_dir, "Raw_Material_Output.txt")

    def test_ocr_output_matches_reference(self):
        with open(self.reference_file, 'r', encoding='utf-8') as ref, \
             open(self.output_file, 'r', encoding='utf-8') as out:
            reference_text = ref.read().strip()
            output_text = out.read().strip()

        self.assertEqual(reference_text, output_text, "OCR output does not match reference text.")
        print("Test Passed: OCR output matches reference text.")
if __name__ == "__main__":
    unittest.main()
