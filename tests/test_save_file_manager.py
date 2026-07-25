import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from Managers.save_file_manager import SaveFileManager
from States.save_file_wizzard import SaveFileWizzard


class SaveFileManagerTests(unittest.TestCase):
    def test_create_and_load_slot_for_three_save_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('Managers.save_file_manager.SAVE_FILES_DATA_PATH', tmpdir), \
                 patch('Managers.save_file_manager.SAVE_FILE_SLOT_COUNT', 3):
                manager = SaveFileManager(game=type('GameStub', (), {})())

                slots = manager.get_all_slots()
                self.assertEqual(len(slots), 3)
                self.assertTrue(all(slot['is_empty'] for slot in slots))

                created = manager.create_slot(1, name='Alpha Run')
                self.assertEqual(created['name'], 'Alpha Run')
                self.assertTrue(os.path.exists(os.path.join(tmpdir, 'save_file1.json')))

                loaded = manager.load_slot(1)
                self.assertEqual(loaded['name'], 'Alpha Run')
                self.assertEqual(loaded['slot_id'], 1)

    def test_wizard_saves_form_data_to_slot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('Managers.save_file_manager.SAVE_FILES_DATA_PATH', tmpdir), \
                 patch('Managers.save_file_manager.SAVE_FILE_SLOT_COUNT', 3):
                game = SimpleNamespace()
                game.state_manager = SimpleNamespace(set_state=lambda name: None)
                game.save_file_manager = SaveFileManager(game)

                wizard = SaveFileWizzard(game)
                wizard.slot_id = 2
                wizard.form_data = {'name': 'Ada', 'occupation': 'Researcher', 'notes': 'First run'}
                wizard.save_current_slot()

                saved = game.save_file_manager.load_slot(2)
                self.assertEqual(saved['name'], 'Ada')
                self.assertEqual(saved['occupation'], 'Researcher')
                self.assertEqual(saved['notes'], 'First run')


if __name__ == '__main__':
    unittest.main()
