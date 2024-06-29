import unittest

from Code.texture_manager import (DMSValidator, InvalidSpriteError,
                                  SpriteValidationError)


class TestTextureFolders(unittest.TestCase):
    def setUp(self):
        self.dms_validator = DMSValidator('Sprites')

    def test_validate_all_dms_folders(self):
        try:
            result = self.dms_validator.validate_all_dms()
            self.assertTrue(result)
        
        except (SpriteValidationError, InvalidSpriteError) as e:
            self.fail(f"validate_all_dms raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
