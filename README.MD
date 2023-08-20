# records multiple (background) windows using ctypes and ffmpeg - Windows only

### pip install schirmshots

### Tested against Windows 10 / Python 3.10 / Anaconda 

```python

Customizable Recording Parameters - The function allows you to specify various recording parameters, such as the
output video file path, the target window's handle (HWND), the window's position and dimensions,
whether to run in headless mode, desired frame rate, compression parameters, and more.
This level of customization gives you fine-grained control over the recording process.

Headless Mode - If the headless parameter is set to true, the function utilizes the FakeHeadless class to run in
headless mode. This means that it hides the window that is being recorded. This can be advantageous for automation and background tasks.

Hotkey Termination - The function supports a hotkey combination (killhotkey)
to terminate the recording process. This provides an easy and user-friendly way to stop the recording if needed.

Error Handling - The code includes error handling for various scenarios, such as removing an existing video
file before starting the recording and handling exceptions that might arise during the recording process.
This helps ensure a smoother execution even in the presence of unexpected issues.

Dynamic Window Resizing - The code includes functionality to dynamically resize the target window before recording,
which can be useful if you want to ensure a specific window size for the recording. If you resize the window,
the frames won't be recorded, and the window will automatically be resized to the dimensions from the beginning, and the recording
will go on. However, you can move the window during the recording

External Process Management - The code manages external processes, like launching a subprocess which starts a main
process (completely independent) for every recording
and ensuring it runs in the background. That means you can record multiple windows at once and use all your CPUs

Start recording video of a specific window using specified parameters.

Args:
	videofile (str): The path to the output video file.
	hwnd (int): The handle of the target window to be recorded.
	windowpos (tuple, optional): The position and dimensions of the window as a tuple (startx, starty, width, height).
		If None, the window's position and dimensions will not be altered before recording.
	headless (int | bool, optional): Set to 1 or True to run in headless mode (hides the window that is being recorded), 0 or False otherwise.
	framerate (int, optional): The approximate desired recording frame rate. Default is 0 (no specific framerate).
	params (tuple, optional): Additional parameters for video compression, as a tuple of tuples.
		Default is (("-vcodec", "libx264"), ("-crf", 0), ("-preset", "ultrafast")).
	killhotkey (str, optional): The hotkey combination to terminate the recording. Default is "ctrl+alt+e" - can be used multiple times.
	use_client (int | bool, optional): Set to 1 or True to use the client area of the window, 0 or False otherwise.

Returns:
	None

Example:
	from schirmshots import start_recording # needs to be in a file - not directly from the console - make sure that ffmpeg is installed

	start_recording(
		headless = 0,
		videofile= f'c:\\myvideofile2.mkv',
		windowpos=None,# (0,0,640,480),
		hwnd=3477668,
		framerate = 30,
		params = (("-vcodec", "libx264"), ("-crf", 0), ("-preset", "slow")),
		killhotkey='ctrl+alt+e',
	)
```
