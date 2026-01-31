# 🦊 MacroFox

# A hotbar automation tool for boosting efficiency in Bee Swarm Simualtor

![GitHub all releases](https://img.shields.io/github/downloads/GXX0T/MacroFox/total?style=for-the-badge&color=d71920&labelColor=000000&label=DOWNLOADS&logo=)

> [!TIP]
> Please leave me a star :3 ⭐

## Features
- Light / Dark / Nothing / Pinky themes
- Save and load presets
- Change Materials timers
- Disable slots with one click
- Settings saved between runs

## Installation
1. Download latest [`MacroFox.exe`](https://github.com/GXX0T/MacroFox/releases) from releases page
2. Run `MacroFox.exe`

> [!WARNING]
> Please report any bug you find by opening an issue

## Building
<details>
  <summary>
  
  </summary>
  You can build it yourself, it's open source:

```pip
pip install flet keyboard flet-timer
```

> flet (core framework)
>
> keyboard (for hotkey automation)
>
> flet-timer (for UI updates)

```console
pyinstaller --noconfirm --onefile --windowed --icon "C:\Users\YOUR_ICON_PATH" --name "MacroFox" --clean --add-data "C:\Users\YOUR_MATERIALS_PATH" --add-data "C:\Users\YOUR_BUILD_PATH." --hidden-import "flet, flet.core, flet.runtime, flet_timer"  "C:\Users\YOUR_EXPORT_PATH"
```

> I used `auto-py-to-exe` this time. You also can use `pyinstaller` or any other builder 
</details>


## Preview
> *may take a while to load gif*
>
![1](https://github.com/user-attachments/assets/f8b0bec9-9340-4849-a9ad-5ae5cc30c99f)
![2](https://github.com/user-attachments/assets/cae4d70e-dcbf-40a6-b941-460b26edf878)
![3](https://github.com/user-attachments/assets/7e0a7fb9-1ce3-40e5-8da3-49afeab4916a)
![4](https://github.com/user-attachments/assets/d1cb7ebe-b333-43f2-8efc-10b33a035492)
