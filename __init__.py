import os
import subprocess
import sys

from PoorMansHeadless import FakeHeadless
from ctrlchandler import set_console_ctrl_handler
from touchtouch import touch
from ctypes_window_info import get_window_infos, user32, windll
from hackyargparser import add_sysargv
from kthread_sleep import sleep
from suicideproc import commit_suicide

from fast_ctypes_screenshots import (
    ScreenshotOfWindow,
)
from ctypes import wintypes
from ast import literal_eval
from vidgear.gears import WriteGear
import keyboard as key_b
from subprocess_alive import is_process_alive

windll.shcore.SetProcessDpiAwareness(2)

user32.GetForegroundWindow.argtypes = ()
user32.GetForegroundWindow.restype = wintypes.HWND
user32.ShowWindow.argtypes = wintypes.HWND, wintypes.BOOL
user32.ShowWindow.restype = wintypes.BOOL
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE
creationflags = subprocess.CREATE_NO_WINDOW
invisibledict = {
    "startupinfo": startupinfo,
    "creationflags": creationflags,
    "start_new_session": True,
}


def resize_window(hwnd: int, position: tuple):
    user32.MoveWindow(hwnd, *position, True)


def comsu(s, writer):
    writer.close()
    if s:
        s.quit_headless_mode()
    commit_suicide()


def failsafe_kill(s, writer):
    try:
        writer.close()
        if s:
            s.quit_headless_mode()
    except Exception:
        pass
    commit_suicide()


@add_sysargv
def take_screenshots(
    headless: int | bool = 0,
    videofile: str | None = None,
    windowpos: tuple | None = None,
    hwnd: int | None = None,
    framerate: int = 30,
    params: tuple = (("-vcodec", "libx264"), ("-crf", 0), ("-preset", "ultrafast")),
    killhotkey: str = "ctrl+alt+e",
    use_client: int | bool = 0,
    resizebefore: int | bool = 0,
):
    if use_client:
        suffix = "_client"
    else:
        suffix = "_win"
    s = None
    try:
        output_params = dict(params)
    except Exception:
        output_params = dict(literal_eval("".join(list(params))))

    if resizebefore:
        resize_window(hwnd, position=windowpos)
        sleep(2)
    for w in get_window_infos(hwnd=hwnd):
        startofwindowx, startofwindowy, sizeofwindow_width, sizeofwindow_height = (
            getattr(w, f"coords{suffix}")[0],
            getattr(w, f"coords{suffix}")[2],
            getattr(w, f"dim{suffix}")[0],
            getattr(w, f"dim{suffix}")[1],
        )
    if headless:
        s = FakeHeadless(hwnd)
        s.start_headless_mode(
            width=windowpos[2], height=windowpos[3], distance_from_taskbar=1
        )
    videofile = os.path.normpath(videofile.strip("\"' "))
    touch(videofile)
    try:
        os.remove(videofile)
    except Exception as fe:
        print(fe)
    writer = WriteGear(
        output=videofile, compression_mode=True, logging=True, **output_params
    )
    set_console_ctrl_handler(returncode=1, func=comsu, s=s, writer=writer)
    if killhotkey:
        key_b.add_hotkey(killhotkey, lambda: failsafe_kill(s, writer))
    co = 0
    validsize = 0
    try:
        with ScreenshotOfWindow(
            hwnd=hwnd, client=False, ascontiguousarray=True
        ) as screenshots_window:
            for frame in screenshots_window:
                if co == 0:
                    validsize = frame.size
                    co = +1
                try:
                    if frame.size != validsize:
                        for w in get_window_infos(hwnd=hwnd):
                            if getattr(w, f"dim{suffix}") != (
                                sizeofwindow_width,
                                sizeofwindow_height,
                            ):
                                print(
                                    getattr(w, f"dim{suffix}"),
                                    sizeofwindow_width,
                                    sizeofwindow_height,
                                )
                                startofwindowx_startofwindowy = (
                                    getattr(w, f"coords{suffix}")[0],
                                    getattr(w, f"coords{suffix}")[2],
                                )
                                resize_window(
                                    hwnd,
                                    position=startofwindowx_startofwindowy
                                    + (sizeofwindow_width, sizeofwindow_height),
                                )
                                break
                    else:
                        writer.write(frame)
                        if framerate > 0:
                            sleep(1 / framerate * 0.9)
                except Exception as fe:
                    print(fe)
    except KeyboardInterrupt:
        pass


def start_recording(
    videofile: str,
    hwnd: int,
    windowpos: tuple | None = None,  # startx, starty, width, height
    headless: int | bool = 0,
    framerate: int = 0,
    params: tuple = (("-vcodec", "libx264"), ("-crf", 0), ("-preset", "ultrafast")),
    killhotkey: str = "ctrl+alt+e",
    use_client: int | bool = 0,
) ->None:
    r"""
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

    """
    if use_client:
        suffix = "_client"
    else:
        suffix = "_win"
    resizebefore = 1
    if not windowpos:
        resizebefore = 0
        for w in get_window_infos(hwnd=hwnd):
            windowpos = (
                getattr(w, f"coords{suffix}")[0],
                getattr(w, f"coords{suffix}")[2],
                getattr(w, f"dim{suffix}")[0],
                getattr(w, f"dim{suffix}")[1],
            )
    wholec = [
        __file__,
        "--headless",
        str(headless),
        "--videofile",
        str(videofile),
        "--windowpos",
        str(windowpos),
        "--hwnd",
        str(hwnd),
        "--framerate",
        str(framerate),
        "--params",
        str(params),
        "--killhotkey",
        str(killhotkey),
        "--use_client",
        str(use_client),
        "--resizebefore",
        str(resizebefore),
    ]
    cmd = subprocess.list2cmdline(wholec)
    wholecommand = f'start "" "{sys.executable}" {cmd}'
    print(wholecommand)
    p = subprocess.Popen(
        wholecommand,
        shell=True,
        env=os.environ.copy(),
        cwd=os.getcwd(),
        **invisibledict,
    )
    while is_process_alive(p.pid):
        sleep(1)


if __name__ == "__main__":
    take_screenshots()
