# SCP Desk Job

**Version:** 1.0 (Alpha)

**Repository:** [mironczuk-dar/SCP-Desk-Job](https://github.com/mironczuk-dar/SCP-Desk-Job.git)

> This developer guide outlines the architecture, setup, and contribution workflow for **SCP Desk Job**. Currently built upon a robust "Default Pygame Project" template, this application features a state-driven UI, dynamic asset loading, and built-in managers for audio, inputs, and achievements.

---

## Table of Contents

1. Introduction
2. Quick Start
   - Windows
   - Linux
3. Project Structure
4. Core Architecture
5. Running the Game
6. Dependencies
7. Contribution Workflow

---

## 1. Introduction

**SCP Desk Job** is a Pygame-based application designed with a scalable, state-driven architecture. The project is modularized to cleanly separate game loop management, UI rendering, input handling (keyboard and gamepad), and data persistence. 

It handles dynamic aspect-ratio scaling (rendering to a fixed virtual resolution and scaling to the display), seamless background asset loading, and extensive user customization via JSON configuration files.

---

## 2. Quick Start

The project provides dedicated startup scripts to handle environment setup and dependency management automatically.

### Windows

Use the bundled Windows script:

```bat
[RUN]_WINDOWS.bat

```

What it does:

* Uses the embedded Python runtime (if configured) or system Python.
* Checks for an internet connection to update the repository via Git.
* Installs or upgrades required Python packages.
* Launches `src/main.py`.

### Linux

Use the Linux startup script:

```bash
./[RUN]_LINUX.sh

```

What it does:

* Checks for a system `python3` installation.
* Creates a local `.venv` (virtual environment) to isolate dependencies.
* Installs or upgrades dependencies from `requirements.txt`.
* Launches the application via `src/main.py`.

---

## 3. Project Structure

The repository is organized into the following primary directories to maintain a clean codebase:

```text
SCP-Desk-Job/
├── assets/              # Graphics, fonts, and icon assets
├── audio/               # Sound effects and music tracks
├── data/                # Persistent JSON configurations (controls, themes, saves)
├── src/                 # Main application source code
│   ├── Machines/        # Background workers (e.g., multithreaded asset loading)
│   ├── Managers/        # Core service classes (State, Audio, Input, Achievements)
│   ├── States/          # UI and Game states (Start Menu, Options, Extras, Gameplay)
│   ├── Tools/           # Helper utilities for JSON loading and color processing
│   ├── UI_elements/     # Reusable UI widgets (Buttons, Sliders, Option Tabs)
│   ├── settings.py      # Global constants, file paths, and default configurations
│   └── main.py          # Application entry point and main game loop
├── requirements.txt     # Python package dependencies
├── [RUN]_WINDOWS.bat    # Windows startup script
└── [RUN]_LINUX.sh       # Linux startup script

```

---

## 4. Core Architecture

The game relies on several centralized managers mapped out in `src/main.py`:

* **StateManager (`Managers/state_manager.py`):** Routes logic and rendering to the active screen (e.g., Main Menu, Options, Gameplay). It handles UI focus and transitions between states.
* **InputManager (`Managers/input_manager.py`):** Abstracts hardware inputs. It maps raw keyboard presses and gamepad inputs (buttons, analog sticks) to unified string-based "actions" (e.g., `up`, `action_a`). It also includes deadzone handling and analog cursor control.
* **AudioManager (`Managers/audio_manager.py`):** Centralizes music and sound effect playback, linked directly to the user's volume settings.
* **AchievementManager (`Managers/achievement_manager.py`):** Tracks player progress and triggers UI popups when milestones are reached.
* **Virtual Resolution System:** The game renders to a consistent internal 16:9 resolution (`WINDOW_WIDTH` x `WINDOW_HEIGHT`) and mathematically scales up or down to fit the user's display, preserving aspect ratio with letterboxing/pillarboxing.

---

## 5. Running the Game

### Recommended Flow

1. Open a terminal in the root directory.
2. On Windows: run `[RUN]_WINDOWS.bat`
3. On Linux: run `./[RUN]_LINUX.sh`

### Direct Launch (Development)

If you are debugging and already have your Python environment activated, run:

```bash
python src/main.py

```

*Note: Make sure your working directory is the repository root so relative paths to `data/` and `assets/` resolve correctly.*

---

## 6. Dependencies

Dependencies are listed in `requirements.txt`. The primary engines driving this project are:

* `pygame` or `pygame-ce` (Community Edition is recommended for better performance and modern features)

The initialization scripts handle the installation of these requirements automatically.

---

## 7. Contribution Workflow

### Recommended Process

1. Fork the repository.
2. Clone your fork locally.
3. Create a feature branch (`git checkout -b feature/new-ui-element`).
4. Make your changes. Ensure you update `settings.py` or JSON defaults if you add new controls or themes.
5. Test your changes thoroughly using the provided platform run scripts.
6. Commit and push your work.
7. Open a Pull Request with a clear description of your changes.

### Coding Guidelines

* Keep UI logic strictly inside the `UI_elements/` folder and State routing inside `States/`.
* Never poll `pygame.key.get_pressed()` directly in a UI element; always query the `InputManager`.
* Ensure new assets (audio, images) are properly registered in the multithreaded `Machines/asset_importing_machine.py`.

```

```