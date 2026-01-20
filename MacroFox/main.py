import keyboard
import time
import threading
import flet as ft
from flet_timer import Timer
import json
from pathlib import Path




# --- Constants ---
MATERIALS = ["Cloud_Vial", "Coconut", "Enzymes", "Glitter", "Glue", "Gumdrops", "Jelly_Beans", "Marshmallow_Bee", "Micro-Converter", "Oil", "Purple_Potion", "Stinger", "Super_Smoothie", "Sprinkler_Builder"]

MATERIAL_INFO = {
    "Cloud_Vial": "Summons a Cloud in the field you're standing in. Lasts for 3 minutes.",
    "Coconut": "Drops a huge Coconut into the field. Catch it to convert pollen to Honey Tokens.",
    "Enzymes": "Grants +10% Instant Conversion and x1.25 Conversion Rate for 10 minutes.",
    "Glitter": "Boosts the field you're standing in, granting +100% pollen for 15 minutes.",
    "Glue": "Grants x1.25 Bee Gather Pollen and Tools for 10 minutes.",
    "Gumdrops": "Use while standing in a field to cover flowers in goo. Goo grants bonus honey.",
    "Jelly_Beans": "Scatters various buff-granting beans on nearby flowers. Works best when shared.",
    "Marshmallow_Bee": "50% White Pollen, +50% Capacity, and +250% Conversion Rate for 30 minutes.",
    "Micro-Converter": "Instantly converts all Pollen in your bag to Honey.",
    "Oil": "Grants x1.2 Bee and Player Movespeed for 10 minutes.",
    "Purple_Potion": "Grants x1.25 Capacity, x1.25 Convert Rate At Hive, x1.5 Red Pollen, x1.5 Blue Pollen, x1.3 Bee Gather Pollen, and x1.3 Pollen From Tools for 15 minutes.",
    "Sprinkler_Builder": "Use while standing in flowers to place a Sprinkler.",
    "Stinger": "Grants your bees x1.5 attack for 30 seconds.",
    "Super_Smoothie": "Grants x1.5 Capacity, x1.6 Red Pollen, x1.6 Blue Pollen, x1.6 White Pollen, x1.4 Bee Gather Pollen, x1.4 Pollen From Tools, x2 Convert Rate, x1.5 Convert Rate At Hive, +12% Instant Conversion, +7% Critical Chance, x1.25 Bee Movespeed, and x1.25 Player Movespeed for 20 minutes.",
}

MATERIAL_TIMER = {"Cloud_Vial": 180, "Coconut": 1, "Enzymes": 600, "Glitter": 910, "Glue": 600, "Gumdrops": 1, "Jelly_Beans": 45, "Marshmallow_Bee": 1800, "Micro-Converter": 15, "Oil": 600, "Purple_Potion": 900, "Sprinkler_Builder": 5, "Stinger": 10, "Super_Smoothie": 1200}

PRESETS = {
    "Boost": ["Sprinkler_Builder", "Stinger", "Coconut", "Jelly_Beans", "Gumdrops", "Micro-Converter", "Glitter"],
}

# --- Theme Palettes ---
THEMES = {
    "light": {
        "BG": "#FFFFFF",
        "PANEL": "#F0F0F0",
        "SLOT_BG": "#E0E0E0",
        "FONT": "#212121",
        "PRIMARY": "#2196F3",
        "SUCCESS": "#73C277",
        "DANGER": "#F55A4E",
        "WARNING": "#FFC107",
        "HINT": "#616161",
        "THEME_MODE": ft.ThemeMode.LIGHT,
    },
    "dark": {
        "BG": "#121212",
        "PANEL": "#1E1E1E",
        "SLOT_BG": "#2A2A2A",
        "FONT": "#E0E0E0",
        "PRIMARY": "#4CAF50",
        "SUCCESS": "#66BB6A",
        "DANGER": "#EF5350",
        "WARNING": "#FFA726",
        "HINT": "#9E9E9E",
        "THEME_MODE": ft.ThemeMode.DARK,
    },
    "nothing": {
        "BG": "#000000",
        "PANEL": "#111111",
        "SLOT_BG": "#222222",
        "FONT": "#FFFFFF",
        "PRIMARY": "#D71922",
        "SUCCESS": "#2ECC71",
        "DANGER": "#E74C3C",
        "WARNING": "#F39C12",
        "HINT": "#AAAAAA",
        "THEME_MODE": ft.ThemeMode.DARK,
    },
    "pinky": {
        "BG": "#FFF9FB",
        "PANEL": "#FFE8F0",
        "SLOT_BG": "#FFDDEA",
        "FONT": "#C2185B",
        "PRIMARY": "#F06292",
        "SUCCESS": "#81C784",
        "DANGER": "#F48FB1",
        "WARNING": "#FFCC80",
        "HINT": "#CE93D8",
        "THEME_MODE": ft.ThemeMode.LIGHT,
    },
}

BORDER_RADIUS = 6


def format_time(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


def create_slot_content(mat, idx, disabled=False, on_cooldown=False, colors=None):
    if colors is None:
        colors = THEMES["light"]
    if mat:
        img = ft.Image(src=f"materials/{mat}.webp", width=46, height=46)
        content = img
    else:
        content = ft.Text(str(idx + 1), size=12, color=colors["HINT"])

    bgcolor = colors["SLOT_BG"]
    border = None
    if disabled:
        bgcolor = ft.Colors.with_opacity(0.2, colors["DANGER"])
        border = ft.Border.all(2, colors["DANGER"])
    elif on_cooldown:
        bgcolor = ft.Colors.with_opacity(0.2, colors["PRIMARY"])

    return ft.Container(width=60, height=60, border_radius=BORDER_RADIUS, bgcolor=bgcolor, border=border, alignment=ft.alignment.Alignment(0, 0), content=content, tooltip=(MATERIAL_INFO.get(mat, "") + " (Disabled)" if disabled else MATERIAL_INFO.get(mat, "") + " (On Cooldown)" if on_cooldown else MATERIAL_INFO.get(mat, "")) if mat else f"Slot {idx + 1}")


SETTINGS_PATH = Path.home() / "Documents" / "MacroFox" / "settings.json"


def load_settings():
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
                if data.get("theme") not in THEMES:
                    data["theme"] = "light"
                return data
        except:
            pass
    return {"theme": "light", "always_on_top": False}


def save_settings(data):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)


# --- Main App ---
def main(page: ft.Page):
    settings = load_settings()
    current_theme = settings.get("theme", "light")
    always_on_top = settings.get("always_on_top", False)

    page.window.icon = "icon.ico"
    page.title = "MacroFox"
    page.window.width = 820
    page.window.height = 480
    page.window.resizable = False
    page.padding = 14
    page.fonts = {"Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap"}
    page.theme = ft.Theme(font_family="Roboto")
    page.window.always_on_top = always_on_top
    page.window.maximizable = False

    # State
    slots = [None] * 7
    slot_disabled = [False] * 7
    slot_cooldown_end = [0] * 7
    material_to_slot = {}
    running = False
    pause_flag = False

    # UI refs
    timer_texts = []
    slot_containers = []
    left_panel_ref = ft.Ref[ft.Container]()
    hotbar_container_ref = ft.Ref[ft.Container]()
    info_container_ref = ft.Ref[ft.Container]()
    controls_container_ref = ft.Ref[ft.Container]()
    preset_dropdown_ref = ft.Ref[ft.Dropdown]()

    # Button refs
    apply_preset_btn_ref = ft.Ref[ft.Button]()
    save_preset_btn_ref = ft.Ref[ft.Button]()
    run_pause_btn_ref = ft.Ref[ft.Button]()
    stop_btn_ref = ft.Ref[ft.Button]()
    settings_btn_ref = ft.Ref[ft.Button]()

    preset_dir = Path.home() / "Documents" / "MacroFox"
    preset_dir.mkdir(parents=True, exist_ok=True)

    # Helper to get current colors
    def get_colors():
        return THEMES[current_theme]

    # Apply theme function — updates EVERYTHING
    def apply_theme(theme_name):
        nonlocal current_theme
        current_theme = theme_name
        colors = THEMES[theme_name]
        page.theme_mode = colors["THEME_MODE"]
        page.bgcolor = colors["BG"]

        # Update all slot displays
        for i in range(7):
            update_slot_display(i)

        # Update panel backgrounds
        if left_panel_ref.current:
            left_panel_ref.current.bgcolor = colors["PANEL"]
        if hotbar_container_ref.current:
            hotbar_container_ref.current.bgcolor = colors["PANEL"]
        if info_container_ref.current:
            info_container_ref.current.bgcolor = colors["PANEL"]
        if controls_container_ref.current:
            controls_container_ref.current.bgcolor = colors["PANEL"]

        # Update dropdown
        if preset_dropdown_ref.current:
            preset_dropdown_ref.current.bgcolor = colors["BG"]
            preset_dropdown_ref.current.color = colors["FONT"]

        # Rebuild material list
        material_list.controls.clear()
        for mat in MATERIALS:
            draggable = ft.Draggable(content=ft.Container(padding=8, border_radius=BORDER_RADIUS, bgcolor=colors["BG"], content=ft.Row([ft.Image(src=f"materials/{mat}.webp", width=70, height=70), ft.Column([ft.Text(mat.replace("_", " "), size=16, weight="bold", color=colors["FONT"]), ft.Text(MATERIAL_INFO[mat], size=10, color=colors["HINT"], width=160)], spacing=2, expand=True)], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START), tooltip=MATERIAL_INFO[mat]), data=mat)
            material_list.controls.append(draggable)

        # Update ALL buttons
        if apply_preset_btn_ref.current:
            apply_preset_btn_ref.current.style.bgcolor = colors["PRIMARY"]
            apply_preset_btn_ref.current.update()
        if save_preset_btn_ref.current:
            save_preset_btn_ref.current.style.bgcolor = colors["PRIMARY"]
            save_preset_btn_ref.current.update()
        if run_pause_btn_ref.current:
            if not running:
                run_pause_btn_ref.current.style.bgcolor = colors["SUCCESS"]
                run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PLAY_ARROW, size=20, color="#FFFFFF")
            elif pause_flag:
                run_pause_btn_ref.current.style.bgcolor = colors["SLOT_BG"]
                run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PLAY_ARROW, size=20, color=colors["FONT"])
            else:
                run_pause_btn_ref.current.style.bgcolor = colors["WARNING"]
                run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PAUSE, size=20, color="#FFFFFF")
            run_pause_btn_ref.current.update()
        if stop_btn_ref.current:
            stop_btn_ref.current.style.bgcolor = colors["DANGER"]
            stop_btn_ref.current.update()
        if settings_btn_ref.current:
            grey = ft.Colors.GREY_700 if theme_name != "nothing" else ft.Colors.GREY_900
            settings_btn_ref.current.style.bgcolor = grey
            settings_btn_ref.current.update()

        page.update()

    # Slot display logic
    def update_slot_display(idx):
        colors = get_colors()
        mat = slots[idx]
        disabled = slot_disabled[idx]
        on_cooldown = slot_cooldown_end[idx] > time.time()

        if mat is None:
            new_control = ft.DragTarget(content=create_slot_content(None, idx, disabled, on_cooldown, colors), data=str(idx), on_accept=lambda e, i=idx: on_slot_drop(e, i))
        else:
            inner = ft.Container(content=create_slot_content(mat, idx, disabled, on_cooldown, colors), on_click=lambda e, i=idx: toggle_slot_disabled(i), on_long_press=lambda e, i=idx: clear_slot(i))
            new_control = ft.Draggable(content=inner, data=mat, on_drag_complete=lambda e, i=idx: on_item_dragged_out(i))
        slot_containers[idx].content = new_control

        remaining = max(0, slot_cooldown_end[idx] - time.time())
        timer_texts[idx].value = format_time(remaining) if remaining > 0 else "–:–"
        timer_texts[idx].color = colors["DANGER"] if remaining > 0 else colors["HINT"]

    def clear_slot(idx):
        if slots[idx] is not None:
            mat = slots[idx]
            if mat in material_to_slot:
                del material_to_slot[mat]
            slots[idx] = None
            slot_disabled[idx] = False
            slot_cooldown_end[idx] = 0
            update_slot_display(idx)

    def toggle_slot_disabled(idx):
        if not running or slot_cooldown_end[idx] <= time.time():
            slot_disabled[idx] = not slot_disabled[idx]
            update_slot_display(idx)

    def on_slot_drop(e, target_idx):
        src = e.src
        if not src or not hasattr(src, "data"):
            return
        dragged_data = src.data

        if dragged_data in MATERIALS:
            mat = dragged_data
            if mat in material_to_slot:
                old_idx = material_to_slot[mat]
                if old_idx == target_idx:
                    return
                slots[old_idx] = None
                slot_disabled[old_idx] = False
                slot_cooldown_end[old_idx] = 0
                del material_to_slot[mat]
                update_slot_display(old_idx)

            if slots[target_idx] is not None:
                old_mat = slots[target_idx]
                if old_mat in material_to_slot:
                    del material_to_slot[old_mat]

            slots[target_idx] = mat
            slot_disabled[target_idx] = False
            slot_cooldown_end[target_idx] = 0
            material_to_slot[mat] = target_idx
            update_slot_display(target_idx)

        elif dragged_data.isdigit():
            source_idx = int(dragged_data)
            if source_idx == target_idx:
                return
            slots[source_idx], slots[target_idx] = slots[target_idx], slots[source_idx]
            slot_disabled[source_idx], slot_disabled[target_idx] = slot_disabled[target_idx], slot_disabled[source_idx]
            slot_cooldown_end[source_idx], slot_cooldown_end[target_idx] = slot_cooldown_end[target_idx], slot_cooldown_end[source_idx]

            material_to_slot.clear()
            for i, m in enumerate(slots):
                if m is not None:
                    material_to_slot[m] = i

            update_slot_display(source_idx)
            update_slot_display(target_idx)

    def on_item_dragged_out(idx):
        if slots[idx] is not None:
            mat = slots[idx]
            if mat in material_to_slot:
                del material_to_slot[mat]
            slots[idx] = None
            slot_disabled[idx] = False
            slot_cooldown_end[idx] = 0
            update_slot_display(idx)

    # Build initial UI
    for i in range(7):
        timer_texts.append(ft.Text("–:–", size=12))
        drag_target = ft.DragTarget(content=create_slot_content(None, i, False, False, THEMES[current_theme]), data=str(i), on_accept=lambda e, idx=i: on_slot_drop(e, idx))
        container = ft.Container(content=drag_target)
        slot_containers.append(container)

    hotbar = ft.Row([ft.Column([slot_containers[i], timer_texts[i]], spacing=4, alignment=ft.MainAxisAlignment.CENTER) for i in range(7)], spacing=8, alignment=ft.MainAxisAlignment.CENTER)

    material_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=440)

    BUTTON_HEIGHT = 48

    preset_dropdown = ft.Dropdown(
        ref=preset_dropdown_ref,
        width=180,
        height=BUTTON_HEIGHT,
        label="Select Preset",
        hint_text="Choose a preset",
        border=ft.InputBorder.OUTLINE,
        border_radius=8,
        border_width=2,
        menu_height=120,
        content_padding=10,
        text_style=ft.TextStyle(size=15, weight="w500"),
    )

    # Button creation helper
    def make_icon_button(icon, bgcolor, tooltip, on_click, ref):
        return ft.Button(ref=ref, content=ft.Icon(icon, size=20, color="#FFFFFF"), width=BUTTON_HEIGHT, height=BUTTON_HEIGHT, on_click=on_click, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=0, bgcolor=bgcolor), tooltip=tooltip)

    # Macro logic
    def run_macro():
        nonlocal running, pause_flag
        running = True
        pause_flag = False
        time.sleep(1.0)
        try:
            while running:
                if pause_flag:
                    time.sleep(0.1)
                    continue
                current_time = time.time()
                pressed_any = False
                for i in range(7):
                    if not running:
                        break
                    mat = slots[i]
                    if mat is None or slot_disabled[i]:
                        continue
                    if current_time >= slot_cooldown_end[i]:
                        keyboard.press_and_release(str(i + 1))
                        duration = MATERIAL_TIMER.get(mat, 1)
                        slot_cooldown_end[i] = current_time + duration
                        pressed_any = True
                time.sleep(0.1 if pressed_any else 0.5)
        finally:
            running = False
            pause_flag = False

    def ui_update_callback():
        colors = get_colors()
        current_time = time.time()
        for i in range(7):
            remaining = max(0, slot_cooldown_end[i] - current_time)
            timer_texts[i].value = format_time(remaining) if remaining > 0 else "–:–"
            timer_texts[i].color = colors["DANGER"] if remaining > 0 else colors["HINT"]
        try:
            page.update()
        except:
            pass

    ui_timer = Timer(callback=ui_update_callback, interval=0.1)

    def on_toggle_run_pause(e):
        nonlocal running, pause_flag
        colors = get_colors()
        if not running:
            threading.Thread(target=run_macro, daemon=True).start()
            ui_timer.start()
            run_pause_btn_ref.current.style.bgcolor = colors["WARNING"]
            run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PAUSE, size=20, color="#FFFFFF")
        elif running and not pause_flag:
            pause_flag = True
            run_pause_btn_ref.current.style.bgcolor = colors["SLOT_BG"]
            run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PLAY_ARROW, size=20, color=colors["FONT"])
        else:
            pause_flag = False
            run_pause_btn_ref.current.style.bgcolor = colors["WARNING"]
            run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PAUSE, size=20, color="#FFFFFF")
        run_pause_btn_ref.current.update()

    def on_stop(e):
        nonlocal running, pause_flag
        running = False
        pause_flag = False
        ui_timer.stop()
        for i in range(7):
            slot_cooldown_end[i] = 0
            update_slot_display(i)
        colors = get_colors()
        run_pause_btn_ref.current.style.bgcolor = colors["SUCCESS"]
        run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PLAY_ARROW, size=20, color="#FFFFFF")
        run_pause_btn_ref.current.update()

    def open_settings(e):
        colors = get_colors()
        always_on_top_setting = ft.Checkbox(label="Always on top", value=page.window.always_on_top, on_change=lambda ev: (setattr(page.window, "always_on_top", ev.control.value), save_settings({"theme": current_theme, "always_on_top": ev.control.value})), check_color="#FFFFFF", active_color=colors["PRIMARY"], label_style=ft.TextStyle(size=13, color=colors["FONT"]))

        theme_names = ["light", "dark", "nothing", "pinky"]
        theme_index = theme_names.index(current_theme)

        def on_theme_change(ev):
            new_theme = theme_names[int(ev.data)]
            apply_theme(new_theme)
            save_settings({"theme": new_theme, "always_on_top": page.window.always_on_top})

        theme_selector = ft.CupertinoSlidingSegmentedButton(
            selected_index=theme_index,
            thumb_color=colors["PRIMARY"],
            on_change=on_theme_change,
            padding=ft.Padding.symmetric(vertical=4, horizontal=10),
            controls=[
                ft.Text("Light"),
                ft.Text("Dark"),
                ft.Text("Nothing"),
                ft.Text("Pinky"),
            ],
        )

        def close_dlg(_):
            page.pop_dialog()

        close_btn = ft.Button("Close", on_click=close_dlg, height=36, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), bgcolor=colors["PRIMARY"], color="#FFFFFF"))

        settings_content = ft.Column([ft.Row([ft.Text("Settings", size=18, weight="bold", color=colors["FONT"])], alignment=ft.MainAxisAlignment.CENTER), ft.Divider(height=12, color=colors["SLOT_BG"]), always_on_top_setting, ft.Row([ft.Text("Theme:", size=13, color=colors["FONT"]), theme_selector], alignment=ft.MainAxisAlignment.START), ft.Divider(height=16, color=ft.Colors.TRANSPARENT), ft.Row([close_btn], alignment=ft.MainAxisAlignment.CENTER)], spacing=8, tight=True)

        settings_dialog = ft.AlertDialog(content=settings_content, content_padding=8, scrollable=True, shape=ft.RoundedRectangleBorder(radius=8), bgcolor=colors["BG"])

        page.show_dialog(settings_dialog)

    def apply_preset(e):
        name = preset_dropdown.value
        if not name:
            return
        if name in PRESETS:
            preset = PRESETS[name]
        else:
            preset_path = preset_dir / f"{name}.json"
            if not preset_path.exists():
                return
            try:
                with open(preset_path, "r") as f:
                    data = json.load(f)
                preset = data.get("slots", [])
            except:
                return

        material_to_slot.clear()
        for i in range(7):
            slots[i] = None
            slot_disabled[i] = False
            slot_cooldown_end[i] = 0

        for i, mat in enumerate(preset):
            if i < 7 and mat != "empty" and mat in MATERIALS:
                slots[i] = mat
                material_to_slot[mat] = i

        for i in range(7):
            update_slot_display(i)
        page.update()

    def save_preset(e):
        colors = get_colors()
        preset_name_field = ft.TextField(label="Preset Name", width=200, border_radius=6, border_color=colors["PRIMARY"], focused_border_color=colors["PRIMARY"], text_style=ft.TextStyle(size=14, color=colors["FONT"]), label_style=ft.TextStyle(size=13, color=colors["HINT"]))

        def close_dlg(_):
            page.pop_dialog()

        def confirm_save(_):
            name = preset_name_field.value
            if not name or not name.strip():
                return
            full_slots = [slots[i] if slots[i] is not None else "empty" for i in range(7)]
            data = {"name": name.strip(), "slots": full_slots}
            filepath = preset_dir / f"{name.strip()}.json"
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            load_presets()
            preset_dropdown.value = name.strip()
            preset_dropdown.update()
            page.pop_dialog()

        save_btn = ft.Button("Save", on_click=confirm_save, height=36, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), bgcolor=colors["PRIMARY"], color="#FFFFFF"))
        cancel_btn = ft.Button("Cancel", on_click=close_dlg, height=36, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), bgcolor=colors["SLOT_BG"], color=colors["FONT"]))

        save_content = ft.Column([ft.Row([ft.Text("Save Preset", size=18, weight="bold", color=colors["FONT"])], alignment=ft.MainAxisAlignment.CENTER), ft.Divider(height=12, color=colors["SLOT_BG"]), ft.Row([preset_name_field], alignment=ft.MainAxisAlignment.CENTER), ft.Row([cancel_btn, save_btn], alignment=ft.MainAxisAlignment.CENTER)], spacing=8, tight=True)

        save_dialog = ft.AlertDialog(content=save_content, content_padding=8, scrollable=False, shape=ft.RoundedRectangleBorder(radius=8), bgcolor=colors["BG"])
        page.show_dialog(save_dialog)

    def load_presets():
        options = [ft.dropdown.Option(name) for name in PRESETS]
        for file in preset_dir.glob("*.json"):
            options.append(ft.dropdown.Option(file.stem))
        preset_dropdown.options = options

    # Create buttons with refs
    apply_preset_btn = make_icon_button(ft.Icons.ARROW_OUTWARD_ROUNDED, THEMES[current_theme]["PRIMARY"], "Apply preset", apply_preset, apply_preset_btn_ref)
    save_preset_btn = make_icon_button(ft.Icons.SAVE, THEMES[current_theme]["PRIMARY"], "Save Preset", save_preset, save_preset_btn_ref)
    run_pause_btn = make_icon_button(ft.Icons.PLAY_ARROW, THEMES[current_theme]["SUCCESS"], "Start/Pause", on_toggle_run_pause, run_pause_btn_ref)
    stop_btn = make_icon_button(ft.Icons.STOP, THEMES[current_theme]["DANGER"], "Stop", on_stop, stop_btn_ref)
    settings_btn = make_icon_button(ft.Icons.SETTINGS, ft.Colors.GREY_700 if current_theme != "nothing" else ft.Colors.GREY_900, "Settings", open_settings, settings_btn_ref)

    def on_window_event(e):
        if e.data == "visible":
            for i in range(7):
                update_slot_display(i)
            page.update()

    page.on_window_event = on_window_event

    # Layout
    hotbar_container = ft.Container(ref=hotbar_container_ref, content=hotbar, padding=10, border_radius=8, margin=ft.margin.Margin(top=0, left=0, right=0, bottom=8))

    info_container = ft.Container(
        ref=info_container_ref,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(content=ft.Text("🚫 Long-press slot to clear\n💡 Single-click slot to disable it\n📁 All save files are stored at \nC:\Documents\MacroFox", size=11, color=THEMES[current_theme]["HINT"]), expand=True),
                        ft.Container(content=ft.Text("🦊 MacroFox v1.0\n\nThis macro is designed specifically for boosting by automating hotbar items usage", size=11, color=THEMES[current_theme]["HINT"]), expand=True),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=8,
        ),
        padding=10,
        border_radius=8,
        height=220,
        margin=ft.margin.Margin(top=0, left=0, right=0, bottom=8),
    )

    controls_container = ft.Container(
        ref=controls_container_ref,
        content=ft.Row([preset_dropdown, apply_preset_btn, save_preset_btn, settings_btn, run_pause_btn, stop_btn], spacing=8, alignment=ft.MainAxisAlignment.END),
        padding=10,
        border_radius=8,
        margin=ft.margin.Margin(top=0, left=0, right=0, bottom=8),
    )

    left_panel = ft.Container(ref=left_panel_ref, content=material_list, padding=6, border_radius=8, expand=False, width=280)

    page.add(
        ft.Column(
            [
                ft.Row([left_panel, ft.Column([hotbar_container, info_container, controls_container], expand=True, spacing=4)], expand=True, spacing=12),
            ],
            expand=True,
            spacing=0,
        )
    )

    # Initialize
    apply_theme(current_theme)
    load_presets()
    page.update()


ft.run(main, assets_dir="materials")
