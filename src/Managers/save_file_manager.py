import json
import os
from copy import deepcopy
from datetime import datetime

from Manifests.savefile_manifest import DEFAULT_SAVE_FILE_MANIFEST
from settings import SAVE_FILE_SLOT_COUNT, SAVE_FILES_DATA_PATH
from Tools.data_loading_tools import save_data


class SaveFileManager:
    """Manage up to three persistent save slots for the singleplayer menu."""

    def __init__(self, game):
        self.game = game
        os.makedirs(SAVE_FILES_DATA_PATH, exist_ok=True)
        self.slots = []
        self.refresh_slots()

    def get_slot_file_path(self, slot_id):
        return os.path.join(SAVE_FILES_DATA_PATH, f"save_file{slot_id}.json")

    def _build_slot_data(self, slot_id, data=None):
        slot_data = deepcopy(DEFAULT_SAVE_FILE_MANIFEST)
        if isinstance(data, dict):
            slot_data.update(data)

        slot_data['slot_id'] = slot_id
        slot_data['name'] = slot_data.get('name') or f"Save Slot {slot_id}"
        slot_data['date_created'] = slot_data.get('date_created') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        slot_data['upgrades'] = slot_data.get('upgrades') or []
        return slot_data

    def load_slot(self, slot_id):
        path = self.get_slot_file_path(slot_id)
        if not os.path.exists(path):
            return None

        try:
            with open(path, 'r', encoding='utf-8') as save_file:
                payload = json.load(save_file)
        except (json.JSONDecodeError, OSError):
            payload = None

        if not isinstance(payload, dict):
            return None

        slot_data = self._build_slot_data(slot_id, payload)
        self._update_slot_cache(slot_id, slot_data)
        return slot_data

    def create_slot(self, slot_id, name=None, data=None):
        slot_data = self._build_slot_data(slot_id, data or {})
        if name:
            slot_data['name'] = name

        save_data(slot_data, self.get_slot_file_path(slot_id))
        self._update_slot_cache(slot_id, slot_data)
        return slot_data

    def save_slot(self, slot_id, data):
        slot_data = self._build_slot_data(slot_id, data)
        save_data(slot_data, self.get_slot_file_path(slot_id))
        self._update_slot_cache(slot_id, slot_data)
        return slot_data

    def delete_slot(self, slot_id):
        path = self.get_slot_file_path(slot_id)
        if os.path.exists(path):
            os.remove(path)
        self._update_slot_cache(slot_id, None)
        return True

    def get_all_slots(self):
        slots = []
        for slot_id in range(1, SAVE_FILE_SLOT_COUNT + 1):
            slot_data = self.load_slot(slot_id)
            if slot_data is None:
                slots.append({
                    'slot_id': slot_id,
                    'is_empty': True,
                    'data': None,
                    'rect': None,
                    'is_hovered': False
                })
            else:
                slots.append({
                    'slot_id': slot_id,
                    'is_empty': False,
                    'data': slot_data,
                    'rect': None,
                    'is_hovered': False
                })

        self.slots = slots
        return self.slots

    def refresh_slots(self):
        return self.get_all_slots()

    def _update_slot_cache(self, slot_id, slot_data):
        for slot in self.slots:
            if slot['slot_id'] == slot_id:
                if slot_data is None:
                    slot['is_empty'] = True
                    slot['data'] = None
                else:
                    slot['is_empty'] = False
                    slot['data'] = slot_data
                return

        if slot_data is not None:
            self.slots.append({
                'slot_id': slot_id,
                'is_empty': False,
                'data': slot_data,
                'rect': None,
                'is_hovered': False
            })
