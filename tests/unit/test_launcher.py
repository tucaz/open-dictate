import subprocess
import sys
import unittest
from unittest.mock import patch

from src import launcher


class LauncherTests(unittest.TestCase):
    def test_build_tray_command_uses_frozen_executable(self):
        with patch.object(sys, "executable", r"C:\app\open-dictate.exe"):
            with patch.object(sys, "frozen", True, create=True):
                self.assertEqual(
                    launcher.build_tray_command(),
                    [r"C:\app\open-dictate.exe", launcher.INTERNAL_TRAY_COMMAND],
                )

    def test_build_tray_command_prefers_pythonw_for_source_runs(self):
        with patch.object(sys, "executable", r"C:\Python312\python.exe"):
            with patch.object(sys, "frozen", False, create=True):
                with patch("src.launcher.Path.exists", return_value=True):
                    self.assertEqual(
                        launcher.build_tray_command(),
                        [r"C:\Python312\pythonw.exe", "-m", "src", launcher.INTERNAL_TRAY_COMMAND],
                    )

    def test_launch_tray_process_uses_detached_popen_settings(self):
        with patch.object(sys, "executable", r"C:\Python312\python.exe"):
            with patch.object(sys, "frozen", False, create=True):
                with patch("src.launcher.Path.exists", return_value=True):
                    with patch("src.launcher.subprocess.Popen") as mock_popen:
                        launcher.launch_tray_process(cwd=r"C:\workspace")

        args, kwargs = mock_popen.call_args
        self.assertEqual(
            args[0],
            [r"C:\Python312\pythonw.exe", "-m", "src", launcher.INTERNAL_TRAY_COMMAND],
        )
        self.assertEqual(kwargs["cwd"], r"C:\workspace")
        self.assertIs(kwargs["stdin"], subprocess.DEVNULL)
        self.assertIs(kwargs["stdout"], subprocess.DEVNULL)
        self.assertIs(kwargs["stderr"], subprocess.DEVNULL)
        self.assertTrue(kwargs["close_fds"])
        self.assertIn("creationflags", kwargs)
        self.assertIn("startupinfo", kwargs)


if __name__ == "__main__":
    unittest.main()
