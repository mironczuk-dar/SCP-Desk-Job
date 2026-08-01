import pygame


class InputManager:
    def __init__(self, game):
        self.game = game

        # --- ACTION STATES TRACKING ---
        self.actions_pressed = set()
        self.actions_just_pressed = set()
        self.actions_just_released = set()

        self.last_key_down = None

        # --- INITIALIZING JOYSTICKS ---
        pygame.joystick.init()
        self.joysticks = {}
        self._detect_joysticks()

        # ANALOG DEADZONE THRESHOLD (PREVENTS STICK DRIFT)
        self.DEADZONE = 0.2

        # TRACK D-PAD HAT STATES TO AVOID REPEAT TRIGGER ISSUES
        self.hat_states = {'up': False, 'down': False, 'left': False, 'right': False}

    def _trigger_action(self, action):
        """Helper method to trigger an action based on analog stick movement."""
        self.actions_pressed.add(action)
        self.actions_just_pressed.add(action)

    # --- QUERY METHODS FOR ACTION STATES ---
    def is_pressed(self, action):
        return action in self.actions_pressed

    def just_pressed(self, action):
        return action in self.actions_just_pressed

    def just_released(self, action):
        return action in self.actions_just_released

    def _detect_joysticks(self):
        """Detects and initializes connected joysticks."""
        self.joysticks = {}
        for i in range(pygame.joystick.get_count()):
            js = pygame.joystick.Joystick(i)
            js.init()
            # Pygame 2.x uses get_instance_id() for safe device tracking
            self.joysticks[js.get_instance_id()] = js
            print(f"Joystick {js.get_name()} (ID: {js.get_instance_id()}) initialized.")

    def update(self, events):
        """Updates the state of the input manager."""
        self.actions_just_pressed.clear()
        self.actions_just_released.clear()

        # --- CONFIG MAPPINGS ---
        kbd_config = self.game.controls_data.get('keyboard', {})
        key_to_action = {v: k for k, v in kbd_config.items()}

        pad_config = self.game.controls_data.get('gamepad', {})
        button_to_action = {v: k for k, v in pad_config.items()}

        # Map standard mouse clicks (left click = 1, right click = 3)
        mouse_config = self.game.controls_data.get('mouse', {1: 'action_a', 3: 'action_b'})
        mouse_to_action = {v: k for k, v in mouse_config.items()}

        # --- PROCESSING EVENT QUEUE ---
        for event in events:
            # Handling Controller Connections/Disconnections
            if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
                self._detect_joysticks()

            # Keyboard Inputs
            elif event.type == pygame.KEYDOWN:
                self.last_key_down = event.key
                if event.key in key_to_action:
                    action = key_to_action[event.key]
                    self.actions_pressed.add(action)
                    self.actions_just_pressed.add(action)

            elif event.type == pygame.KEYUP and event.key in key_to_action:
                action = key_to_action[event.key]
                self.actions_pressed.discard(action)
                self.actions_just_released.add(action)

            # Gamepad Button Inputs (Standard SDL Buttons)
            elif event.type == pygame.JOYBUTTONDOWN and event.button in button_to_action:
                action = button_to_action[event.button]
                self.actions_pressed.add(action)
                self.actions_just_pressed.add(action)

            elif event.type == pygame.JOYBUTTONUP and event.button in button_to_action:
                action = button_to_action[event.button]
                self.actions_pressed.discard(action)
                self.actions_just_released.add(action)

            # Gamepad D-Pad (Hat) Motion
            elif event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value

                directions = {
                    'up': hat_y == 1,
                    'down': hat_y == -1,
                    'left': hat_x == -1,
                    'right': hat_x == 1
                }

                for dir_name, active in directions.items():
                    was_active = self.hat_states[dir_name]
                    if active and not was_active:
                        self.actions_pressed.add(dir_name)
                        self.actions_just_pressed.add(dir_name)
                    elif not active and was_active:
                        self.actions_pressed.discard(dir_name)
                        self.actions_just_released.add(dir_name)
                    self.hat_states[dir_name] = active

            # Virtual Mouse / Trackpad Clicks
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in mouse_to_action:
                action = mouse_to_action[event.button]
                self.actions_pressed.add(action)
                self.actions_just_pressed.add(action)

            elif event.type == pygame.MOUSEBUTTONUP and event.button in mouse_to_action:
                action = mouse_to_action[event.button]
                self.actions_pressed.discard(action)
                self.actions_just_released.add(action)

        # --- PROCESSING ANALOG STICKS ---
        self._update_analog_axes()

    def get_last_key_down(self):
        key = self.last_key_down
        self.last_key_down = None  # Consume it once read
        return key

    def _update_analog_axes(self):
        """Polls Left Stick for continuous grid movement. Right stick is handled natively by the daemon."""
        for joy in self.joysticks.values():

            # 1. LEFT STICK MOVEMENT (Axes 0 and 1)
            axis_x = joy.get_axis(0)
            axis_y = joy.get_axis(1)

            # HORIZONTAL MOVEMENT
            if axis_x < -self.DEADZONE:
                self._trigger_action('left')
            else:
                self.actions_pressed.discard('left')

            if axis_x > self.DEADZONE:
                self._trigger_action('right')
            else:
                self.actions_pressed.discard('right')

            # VERTICAL MOVEMENT
            if axis_y < -self.DEADZONE:
                self._trigger_action('up')
            else:
                self.actions_pressed.discard('up')

            if axis_y > self.DEADZONE:
                self._trigger_action('down')
            else:
                self.actions_pressed.discard('down')