"""Windows Virtual Key Codes mapping."""

from typing import Optional, Tuple, List


class KeyCodes:
    """Windows Virtual Key Codes and parsing utilities."""

    # Windows Virtual Key Codes
    VK_LBUTTON = 0x01  # Left mouse button
    VK_RBUTTON = 0x02  # Right mouse button
    VK_CANCEL = 0x03  # Control-break processing
    VK_MBUTTON = 0x04  # Middle mouse button
    VK_XBUTTON1 = 0x05  # X1 mouse button
    VK_XBUTTON2 = 0x06  # X2 mouse button
    VK_BACK = 0x08  # BACKSPACE key
    VK_TAB = 0x09  # TAB key
    VK_CLEAR = 0x0C  # CLEAR key
    VK_RETURN = 0x0D  # ENTER key
    VK_SHIFT = 0x10  # SHIFT key
    VK_CONTROL = 0x11  # CTRL key
    VK_MENU = 0x12  # ALT key
    VK_PAUSE = 0x13  # PAUSE key
    VK_CAPITAL = 0x14  # CAPS LOCK key
    VK_ESCAPE = 0x1B  # ESC key
    VK_SPACE = 0x20  # SPACEBAR
    VK_PRIOR = 0x21  # PAGE UP key
    VK_NEXT = 0x22  # PAGE DOWN key
    VK_END = 0x23  # END key
    VK_HOME = 0x24  # HOME key
    VK_LEFT = 0x25  # LEFT ARROW key
    VK_UP = 0x26  # UP ARROW key
    VK_RIGHT = 0x27  # RIGHT ARROW key
    VK_DOWN = 0x28  # DOWN ARROW key
    VK_SELECT = 0x29  # SELECT key
    VK_PRINT = 0x2A  # PRINT key
    VK_EXECUTE = 0x2B  # EXECUTE key
    VK_SNAPSHOT = 0x2C  # PRINT SCREEN key
    VK_INSERT = 0x2D  # INS key
    VK_DELETE = 0x2E  # DEL key
    VK_HELP = 0x2F  # HELP key
    VK_0 = 0x30  # 0 key
    VK_1 = 0x31  # 1 key
    VK_2 = 0x32  # 2 key
    VK_3 = 0x33  # 3 key
    VK_4 = 0x34  # 4 key
    VK_5 = 0x35  # 5 key
    VK_6 = 0x36  # 6 key
    VK_7 = 0x37  # 7 key
    VK_8 = 0x38  # 8 key
    VK_9 = 0x39  # 9 key
    VK_A = 0x41  # A key
    VK_B = 0x42  # B key
    VK_C = 0x43  # C key
    VK_D = 0x44  # D key
    VK_E = 0x45  # E key
    VK_F = 0x46  # F key
    VK_G = 0x47  # G key
    VK_H = 0x48  # H key
    VK_I = 0x49  # I key
    VK_J = 0x4A  # J key
    VK_K = 0x4B  # K key
    VK_L = 0x4C  # L key
    VK_M = 0x4D  # M key
    VK_N = 0x4E  # N key
    VK_O = 0x4F  # O key
    VK_P = 0x50  # P key
    VK_Q = 0x51  # Q key
    VK_R = 0x52  # R key
    VK_S = 0x53  # S key
    VK_T = 0x54  # T key
    VK_U = 0x55  # U key
    VK_V = 0x56  # V key
    VK_W = 0x57  # W key
    VK_X = 0x58  # X key
    VK_Y = 0x59  # Y key
    VK_Z = 0x5A  # Z key
    VK_LWIN = 0x5B  # Left Windows key
    VK_RWIN = 0x5C  # Right Windows key
    VK_APPS = 0x5D  # Applications key
    VK_SLEEP = 0x5F  # Computer Sleep key
    VK_NUMPAD0 = 0x60  # Numeric keypad 0 key
    VK_NUMPAD1 = 0x61  # Numeric keypad 1 key
    VK_NUMPAD2 = 0x62  # Numeric keypad 2 key
    VK_NUMPAD3 = 0x63  # Numeric keypad 3 key
    VK_NUMPAD4 = 0x64  # Numeric keypad 4 key
    VK_NUMPAD5 = 0x65  # Numeric keypad 5 key
    VK_NUMPAD6 = 0x66  # Numeric keypad 6 key
    VK_NUMPAD7 = 0x67  # Numeric keypad 7 key
    VK_NUMPAD8 = 0x68  # Numeric keypad 8 key
    VK_NUMPAD9 = 0x69  # Numeric keypad 9 key
    VK_MULTIPLY = 0x6A  # Multiply key
    VK_ADD = 0x6B  # Add key
    VK_SEPARATOR = 0x6C  # Separator key
    VK_SUBTRACT = 0x6D  # Subtract key
    VK_DECIMAL = 0x6E  # Decimal key
    VK_DIVIDE = 0x6F  # Divide key
    VK_F1 = 0x70  # F1 key
    VK_F2 = 0x71  # F2 key
    VK_F3 = 0x72  # F3 key
    VK_F4 = 0x73  # F4 key
    VK_F5 = 0x74  # F5 key
    VK_F6 = 0x75  # F6 key
    VK_F7 = 0x76  # F7 key
    VK_F8 = 0x77  # F8 key
    VK_F9 = 0x78  # F9 key
    VK_F10 = 0x79  # F10 key
    VK_F11 = 0x7A  # F11 key
    VK_F12 = 0x7B  # F12 key
    VK_F13 = 0x7C  # F13 key
    VK_F14 = 0x7D  # F14 key
    VK_F15 = 0x7E  # F15 key
    VK_F16 = 0x7F  # F16 key
    VK_F17 = 0x80  # F17 key
    VK_F18 = 0x81  # F18 key
    VK_F19 = 0x82  # F19 key
    VK_F20 = 0x83  # F20 key
    VK_F21 = 0x84  # F21 key
    VK_F22 = 0x85  # F22 key
    VK_F23 = 0x86  # F23 key
    VK_F24 = 0x87  # F24 key
    VK_NUMLOCK = 0x90  # NUM LOCK key
    VK_SCROLL = 0x91  # SCROLL LOCK key
    VK_LSHIFT = 0xA0  # Left SHIFT key
    VK_RSHIFT = 0xA1  # Right SHIFT key
    VK_LCONTROL = 0xA2  # Left CONTROL key
    VK_RCONTROL = 0xA3  # Right CONTROL key
    VK_LMENU = 0xA4  # Left ALT key
    VK_RMENU = 0xA5  # Right ALT key

    # Name to VK code mapping
    NAME_TO_VK = {
        # Letters
        "a": VK_A, "b": VK_B, "c": VK_C, "d": VK_D, "e": VK_E,
        "f": VK_F, "g": VK_G, "h": VK_H, "i": VK_I, "j": VK_J,
        "k": VK_K, "l": VK_L, "m": VK_M, "n": VK_N, "o": VK_O,
        "p": VK_P, "q": VK_Q, "r": VK_R, "s": VK_S, "t": VK_T,
        "u": VK_U, "v": VK_V, "w": VK_W, "x": VK_X, "y": VK_Y,
        "z": VK_Z,
        # Numbers
        "0": VK_0, "1": VK_1, "2": VK_2, "3": VK_3, "4": VK_4,
        "5": VK_5, "6": VK_6, "7": VK_7, "8": VK_8, "9": VK_9,
        # Function keys
        "f1": VK_F1, "f2": VK_F2, "f3": VK_F3, "f4": VK_F4,
        "f5": VK_F5, "f6": VK_F6, "f7": VK_F7, "f8": VK_F8,
        "f9": VK_F9, "f10": VK_F10, "f11": VK_F11, "f12": VK_F12,
        "f13": VK_F13, "f14": VK_F14, "f15": VK_F15, "f16": VK_F16,
        "f17": VK_F17, "f18": VK_F18, "f19": VK_F19, "f20": VK_F20,
        "f21": VK_F21, "f22": VK_F22, "f23": VK_F23, "f24": VK_F24,
        # Special keys
        "space": VK_SPACE, "spacebar": VK_SPACE,
        "return": VK_RETURN, "enter": VK_RETURN,
        "tab": VK_TAB,
        "escape": VK_ESCAPE, "esc": VK_ESCAPE,
        "delete": VK_DELETE, "del": VK_DELETE,
        "insert": VK_INSERT, "ins": VK_INSERT,
        "home": VK_HOME,
        "end": VK_END,
        "prior": VK_PRIOR, "pageup": VK_PRIOR, "page_up": VK_PRIOR,
        "next": VK_NEXT, "pagedown": VK_NEXT, "page_down": VK_NEXT,
        "left": VK_LEFT,
        "right": VK_RIGHT,
        "up": VK_UP,
        "down": VK_DOWN,
        # Modifier keys
        "shift": VK_SHIFT, "leftshift": VK_LSHIFT, "rightshift": VK_RSHIFT,
        "ctrl": VK_CONTROL, "control": VK_CONTROL, "leftctrl": VK_LCONTROL, "rightctrl": VK_RCONTROL,
        "alt": VK_MENU, "menu": VK_MENU, "leftalt": VK_LMENU, "rightalt": VK_RMENU,
        "win": VK_LWIN, "windows": VK_LWIN, "leftwin": VK_LWIN, "rightwin": VK_RWIN,
        "command": VK_LWIN, "cmd": VK_LWIN,
        "capital": VK_CAPITAL, "capslock": VK_CAPITAL, "caps_lock": VK_CAPITAL,
        "back": VK_BACK, "backspace": VK_BACK,
        # Numpad
        "numpad0": VK_NUMPAD0, "numpad1": VK_NUMPAD1, "numpad2": VK_NUMPAD2,
        "numpad3": VK_NUMPAD3, "numpad4": VK_NUMPAD4, "numpad5": VK_NUMPAD5,
        "numpad6": VK_NUMPAD6, "numpad7": VK_NUMPAD7, "numpad8": VK_NUMPAD8,
        "numpad9": VK_NUMPAD9,
    }

    # VK code to name mapping (reverse, with preferred names)
    VK_TO_NAME = {v: k for k, v in NAME_TO_VK.items()}

    @classmethod
    def parse(cls, input_str: str) -> Optional[Tuple[int, List[str]]]:
        """
        Parse a hotkey string like 'ctrl+f5' or 'alt+space'.
        
        Returns:
            Tuple of (vk_code, modifiers) or None if invalid
        """
        parts = input_str.lower().split("+")
        parts = [p.strip() for p in parts]
        
        if not parts:
            return None
        
        # Last part is the key
        key_name = parts[-1]
        vk_code = cls.NAME_TO_VK.get(key_name)
        
        if vk_code is None:
            return None
        
        # Everything before is modifiers
        modifiers = parts[:-1]
        valid_modifiers = ["ctrl", "control", "alt", "menu", "shift", "win", "windows", "cmd", "command"]
        
        for mod in modifiers:
            if mod not in valid_modifiers:
                return None
        
        return (vk_code, modifiers)

    @classmethod
    def describe(cls, key_code: int, modifiers: List[str]) -> str:
        """
        Create a human-readable description of a hotkey.
        
        Args:
            key_code: Windows VK code
            modifiers: List of modifier names
        
        Returns:
            Human-readable string like 'ctrl+f5'
        """
        key_name = cls.VK_TO_NAME.get(key_code, f"key(0x{key_code:02X})")
        
        if not modifiers:
            return key_name
        
        return "+".join(modifiers + [key_name])

    @classmethod
    def is_modifier_key(cls, vk_code: int) -> bool:
        """Check if a key code is a modifier key."""
        return vk_code in (
            cls.VK_SHIFT, cls.VK_CONTROL, cls.VK_MENU, cls.VK_LWIN, cls.VK_RWIN,
            cls.VK_LSHIFT, cls.VK_RSHIFT, cls.VK_LCONTROL, cls.VK_RCONTROL,
            cls.VK_LMENU, cls.VK_RMENU
        )
