import pygame

class InputManager:
    def __init__(s, game):
        s.game = game

        s.actions_pressed = set()
        s.actions_just_pressed = set()
        s.actions_just_released = set()

        s.last_key_down = None

        # INITALIZING JOYSTICK
        pygame.joystick.init()
        s.joystick = {}
        s._detect_joysticks()

        # ANALOG DEADZONE THRESHOLD (PREVENTS STICK DRIFT)
        s.DEADZONE = 0.2
        
        # MOUSE CURSOR SPEED (Pixels per second)
        s.cursor_speed = 1200 

    def _trigger_action(s, action):
        """Helper method to trigger an action based on analog stick movement."""
        s.actions_pressed.add(action)
        s.actions_just_pressed.add(action)

    # QUERY METHODS FOR ACTION STATES
    def is_pressed(s, action): return action in s.actions_pressed
    def just_pressed(s, action): return action in s.actions_just_pressed
    def just_released(s, action): return action in s.actions_just_released

    def _detect_joysticks(s):
        """Detects and initializes connected joysticks."""
        s.joystick = {}
        for i in range(pygame.joystick.get_count()):
            js = pygame.joystick.Joystick(i)
            js.init()
            s.joystick[js.get_id()] = js
            print(f"Joystick {js.get_name()} (ID: {js.get_id()}) initialized.")

    def update(s, events):
        """Updates the state of the input manager."""
        s.actions_just_pressed.clear()
        s.actions_just_released.clear()

        kbd_config = s.game.controls_data.get('keyboard', {})
        key_to_action = {v: k for k, v in kbd_config.items()}

        pad_config = s.game.controls_data.get('gamepad', {})
        button_to_action = {v: k for k, v in pad_config.items()}

        # PROCESSING EVENT QUEUE (KEYBOARD AND GAMEPAD)
        for event in events:
            # HANDLING CONTROLLER CONNECTION/DISCONNECTION EVENTS
            if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
                s._detect_joysticks()

            # KEYBOARD INPUTS
            elif event.type == pygame.KEYDOWN:
                s.last_key_down = event.key
                if event.key in key_to_action:
                    action = key_to_action[event.key]
                    s.actions_pressed.add(action)
                    s.actions_just_pressed.add(action)

            elif event.type == pygame.KEYUP and event.key in key_to_action:
                action = key_to_action[event.key]
                s.actions_pressed.discard(action)
                s.actions_just_released.add(action)

            # GAMEPAD INPUTS
            elif event.type == pygame.JOYBUTTONDOWN and event.button in button_to_action:
                action = button_to_action[event.button]
                s.actions_pressed.add(action)
                s.actions_just_pressed.add(action)

            elif event.type == pygame.JOYBUTTONUP and event.button in button_to_action:
                action = button_to_action[event.button]
                s.actions_pressed.discard(action)
                s.actions_just_released.add(action)

        # PROCESSING ANALOG STICKS (POLLING AXIS VALUES FOR CONTINUOUS MOVEMENT)
        s._update_analog_axes()

    def get_last_key_down(s):
        key = s.last_key_down
        s.last_key_down = None  # Consume it once read
        return key

    def _update_analog_axes(s):
        for joy in s.joystick.values():
            
            # 1. LEFT STICK MOVEMENT (Axes 0 and 1)
            axis_x = joy.get_axis(0)
            axis_y = joy.get_axis(1)

            # HORIZONTAL MOVEMENT
            if axis_x < -s.DEADZONE:
                s._trigger_action('left')
            else:
                s.actions_pressed.discard('left')
                s.actions_just_released.discard('left')

            if axis_x > s.DEADZONE:
                s._trigger_action('right')
            else:
                s.actions_pressed.discard('right')
                s.actions_just_released.discard('right')

            # VERTICAL MOVEMENT
            if axis_y < -s.DEADZONE:
                s._trigger_action('up')
            else:
                s.actions_pressed.discard('up')
                s.actions_just_released.discard('up')

            if axis_y > s.DEADZONE:
                s._trigger_action('down')
            else:
                s.actions_pressed.discard('down')
                s.actions_just_released.discard('down')
                
            # 2. RIGHT STICK MOUSE CONTROL (Axes 2 and 3)
            # Check if joystick has enough axes (most standard gamepads have 4 to 6)
            if joy.get_numaxes() >= 4:
                right_axis_x = joy.get_axis(2)
                right_axis_y = joy.get_axis(3)
                
                move_x = 0
                move_y = 0
                
                # Apply deadzone
                if abs(right_axis_x) > s.DEADZONE:
                    move_x = right_axis_x
                if abs(right_axis_y) > s.DEADZONE:
                    move_y = right_axis_y
                    
                # If stick is being pushed outside deadzone
                if move_x != 0 or move_y != 0:
                    
                    # Get current system mouse position
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Calculate velocity based on stick tilt, cursor speed, and delta time
                    delta = s.game.delta_time
                    new_x = mouse_x + (move_x * s.cursor_speed * delta)
                    new_y = mouse_y + (move_y * s.cursor_speed * delta)
                    
                    # Set the new system mouse position
                    pygame.mouse.set_pos((int(new_x), int(new_y)))