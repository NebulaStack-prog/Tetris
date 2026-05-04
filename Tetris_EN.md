## Part 1. Main Document.

### 1. Title and Basic Information.

• **Name:** Tetris

• **Purpose:** Project No. 7. Product.

• **Project Phase:** Phase I.

• **Technology Stack:** Python (Pygame library).

• **Project Status:** Fully completed.

### 2. Brief Project Description.

Tetris is a classic arcade game created in Python using the Pygame library.

The player controls falling shapes, arranging them into solid horizontal lines to earn points.

In this version of the project, the following interface and logic elements are implemented: main menu, help screen, next piece preview system, and best score saving.

The project represents a fully functional version of the game with a rich user interface and well-designed game logic.

### 3. Clear Project Goals.

• Create a working version of the game “Tetris” with intuitive controls.

• Implement core gameplay mechanics: spawning shapes, their falling, rotation, movement, and removal (when a line is filled).

• Implement an application state system (menu, game, help).

• Add a next piece preview system.

• Implement a scoring system and best score saving.

• Ensure correct handling of collisions with field boundaries and other shapes.

• Ensure stable game performance with a fixed frame rate.

• Demonstrate an approach to developing game applications with a user interface.

### 4. Project Components.

• The project consists of one executable file that includes all components:

• tetris.py – the main script containing all game code, including game logic, interface, and state management system.

### 5. User Guide.

**5.1. Launch:**

• Make sure the Pygame library is installed (pip install pygame).

• Run the script using Python (for example, via PyCharm).

**5.2. Game Objective:**

• Fill horizontal lines with falling shapes to earn points.

• The game ends if a new shape cannot spawn on the field (the top boundary is reached), after which the game returns to the menu. The best score is saved.

**5.3. Controls:**

• **LEFT ARROW (←):** move the active shape to the left.

• **RIGHT ARROW (→):** move the active shape to the right.

• **DOWN ARROW (↓):** accelerate the fall of the active shape.

• **UP ARROW (↑):** rotate the active shape 90 degrees clockwise.

• **ESC:** return to the main menu.

• **Mouse:** interaction with buttons in the menu and help screen.

**5.4. Interface:**

• Main menu with Play and Help buttons and Best score.

• Help screen with control descriptions.

• Game field of size 11x21 cells.

• Top panel displaying:

* current score (Score)
* best score (Best)
* next shape (Next)

• Black cells with gray elements represent empty space.

• Colored cells represent placed or falling shapes.

• Filling a line awards 10 points.

## Part 2. Technical Document.

### 1. Development Goals.

• The main goal was to create an extended model of the classic Tetris game to reinforce Python programming skills and working with the Pygame library.

• Additionally, the project aims to study user interface construction, application state management, and file system operations (data saving).

• Tasks included working with matrices (game field), handling user input, implementing collision systems, time intervals, and basic game loop architecture.

### 2. Technologies Used.

• **Programming Language:** Python

• **Graphics Library:** Pygame

• **Standard Libraries:** random (for shape generation), copy (for copying shape objects), json file handling (saving records).

### 3. Project Architecture.

• The project is implemented as a monolithic application with elements of a finite state machine.

• Main loop: “while game:”.

• Logic is divided into states: menu – main menu, game – gameplay, help – help screen.

• Each frame performs: event handling, state updates, game logic checks, rendering.

### 4. Project Structure.

• Initialization: setting up Pygame, creating the window, fonts, buttons, and game parameters.

• Global variables: grid, det, det_choice, next_det_choice, color, score, best_score, state, and others.

• Game loop: the main loop where state management and game logic occur.

• Functions:

* **draw_menu()** – menu rendering.

* **draw_help()** – help screen.

* **draw_panel()** – top panel.

* **draw_cell()** – cell outline rendering.

* **CanMove()** – movement validation.

* **get_next_figure()** – shape generation.

* **reset_game()** – game reset.

* **save_best_score(), load_best_score()** – record handling.

• Arrays:

* **grid** – game field.

* **details** – shape templates.

* **det** – transformed shapes.

### 5. Key System Components.

• **Game field (grid):** a three-dimensional list where each element contains: cell status (0 - empty, 1 - occupied), Rect object, color.

• **Shapes:** represented as coordinates, converted into pygame.Rect objects, selected randomly.

• **Next shape system:** implemented via next_det_choice and next_color, displayed on the panel.

• **Collision system:** boundary checks and occupied cell checks.

• **Rotation system:** rotation around a central point (with coordinates (0;0)), using a shift system (similar to wall kick).

### 6. User Interface Implementation.

• The interface is fully implemented using Pygame tools.

• Main elements: application window, menu buttons, game field, top panel, text elements.

• Rendering is performed every frame using pygame.draw and pygame.font functions.

### 7. Development Process.

• Development was carried out step by step:

* creation of the base game window.
  implementation of the grid.

* adding shapes and their movement.

* implementing collisions.

* adding rotation.

* implementing line clearing.

* adding menu and interface.

* adding next shape system.

* implementing best score saving.

### 8. Main Challenges and Solutions.

• **(1)** Challenge: correct rotation of shapes near walls and blocks.

Solution: a shift system during rotation and a function to check shift validity were implemented.

• **(2)** Challenge: correct line clearing and color preservation.

Solution: copying both cell status and color.

• **(3)** Challenge: application state management.

Solution: introducing a state variable and switching logic.

• **(4)** Challenge: instant freezing of a shape after touching the bottom or another shape.

• Solution: after contact, a timer starts during which the shape can still be moved and rotated, if possible.

### 9. Current Project Limitations.

• No difficulty levels.

• No полноценного Game Over screen.

• The code remains monolithic (no modular structure).

• No sound effects.

### 10. Possible Improvements and Development Plans.

• Code refactoring (splitting into modules and classes).

• Adding difficulty levels and increasing speed.

• Adding sound effects.

• Implementing a Game Over screen.

• Adding additional mechanics (for example, higher points for clearing multiple lines at once).
