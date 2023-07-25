# Mouse Click Recorder

This program allows you to record mouse clicks and scrolls, and save their positions to a JSON file. You can also take a screenshot of the mouse position when recording a click.
## Requirements

- Python 3.x
- Dependencies: `pyautogui`, `pywinauto`, `keyboard`, `pynput`, `PIL`

## Installation

1. Clone the repository or download the program files.
2. Install the required dependencies by running the following command:


## Usage
1. Import the MouseClickRecorder class: `from mouse_click_recorder import MouseClickRecorder`
2. Create a new MouseClickRecorder instance: `recorder = MouseClickRecorder()`
3. Call the `record()` method on the recorder object to start recording mouse clicks and scrolls. The recording can be stopped by pressing the "Esc" key.
4. The recorded positions will be saved to a JSON file called positions.json.
### Example usage

#### Recording mouse clicks and scrolls
```python
    from mouse_click_recorder import MouseClickRecorder
    recorder = MouseClickRecorder()
    recorder.record()
```


#### replay mouse clicks and scrolls
```python
    import Record_mouse_click as MC
    helper = MC.MouseClickRecorder()
    helper.move_mouse(json.load(open('positions.json'))) # import a list of positions
```

## Methods
### `record()`

Starts recording mouse clicks and scrolls. The recording can be stopped by pressing the "Esc" key. The recorded positions will be saved to a JSON file called positions.json.

### `convert_position(position, from_size, to_size)`

Converts a mouse position from one screen size to another.

#### Parameters:

* `position(x, y).`: The mouse position to convert.
* `from_size(width, height)`: The size of the original screen.
* `to_size(width, height)`: The size of the target screen.
#### Returns:

* The converted mouse position, in the format (x, y).

### `move_mouse(positions)`
Moves the mouse to the recorded positions.

#### Parameters:

* positions (list): A list of positions to move the mouse to. Each position should be a dictionary with the keys "type" (either "click" or "scroll"), "position" (the position to move to, in the format (x, y)), and "wheel_dist" (the distance to scroll, if the type is "scroll").

### `save_positions()`
Saves the recorded positions to a JSON file called positions.json.
