import keyboard
import time
import threading
import flet as ft
from flet_timer import Timer
import json
from pathlib import Path

# try:
#     from precise_tracker import PrecisionTracker
#     PRECISION_TRACKING_AVAILABLE = True
# except Exception:
#     PRECISION_TRACKING_AVAILABLE = False

from constants import (
    MATERIALS, MATERIAL_INFO, MATERIAL_TIMER, PRESETS, THEMES, BORDER_RADIUS,
    APP_VERSION, UPDATE_LOG, APP_TIPS
)
from utils import format_time, load_settings, save_settings, load_custom_timers, save_custom_timers
from ui_components import get_image_src, create_slot_content, make_icon_button
# from assets_b64 import APP_ICON_B64

# --- Paths ---
SETTINGS_PATH = Path.home() / "Documents" / "MacroFox" / "Settings" / "settings.json"
CUSTOM_TIMER_PATH = Path.home() / "Documents" / "MacroFox" / "Settings" / "custom_timers.json"
preset_dir = Path.home() / "Documents" / "MacroFox" / "Preset"

# --- Load timers ---
custom_timers = load_custom_timers()
EFFECTIVE_MATERIAL_TIMER = {k: custom_timers.get(k, v) for k, v in MATERIAL_TIMER.items()}

# --- Main App ---
def main(page: ft.Page):
    settings = load_settings()
    current_theme = settings.get("theme", "light")
    always_on_top = settings.get("always_on_top", False)
    # track_precision = settings.get("track_precision", False) and PRECISION_TRACKING_AVAILABLE
    # precision_interval = settings.get("precision_interval", 0.25)

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
    precision_tracker = None

    # UI refs
    timer_texts = []
    slot_containers = []
    left_panel_ref = ft.Ref[ft.Container]()
    hotbar_container_ref = ft.Ref[ft.Container]()
    info_container_ref = ft.Ref[ft.Container]()
    controls_container_ref = ft.Ref[ft.Container]()
    preset_dropdown_ref = ft.Ref[ft.Dropdown]()

    apply_preset_btn_ref = ft.Ref[ft.Button]()
    save_preset_btn_ref = ft.Ref[ft.Button]()
    run_pause_btn_ref = ft.Ref[ft.Button]()
    stop_btn_ref = ft.Ref[ft.Button]()
    settings_btn_ref = ft.Ref[ft.Button]()

    preset_dir.mkdir(parents=True, exist_ok=True)

    def get_colors():
        return THEMES[current_theme]
    # --- WIP ---
    # def _start_precision_tracker():
    #     nonlocal precision_tracker
    #     if not PRECISION_TRACKING_AVAILABLE or not track_precision:
    #         return
    #     if precision_tracker is None:
    #         def on_warn(remaining):
    #             page.snack_bar = ft.SnackBar(
    #                 ft.Text(f"Precision expires in {int(remaining)}s!"),
    #                 bgcolor=get_colors()["WARNING"]
    #             )
    #             page.snack_bar.open = True
    #             page.update()
    #
    #         threshold = 0.9 - (precision_interval - 0.25) * (0.05 / 0.75)
    #         threshold = max(0.90, min(0.975, threshold))
    #
    #         precision_tracker = PrecisionTracker(
    #             callback_on_expire=on_warn,
    #             check_interval=precision_interval,
    #             # match_threshold=threshold
    #         )
    #         precision_tracker.start()
    #         print(f"[Main] Started PrecisionTracker @ {precision_interval}s, threshold={threshold:.3f}")

    # def _stop_precision_tracker():
    #     nonlocal precision_tracker
    #     if precision_tracker:
    #         precision_tracker.stop()
    #         precision_tracker = None
    #         print("[Main] Stopped PrecisionTracker")

    def apply_theme(theme_name):
        nonlocal current_theme
        current_theme = theme_name
        colors = THEMES[theme_name]
        page.theme_mode = ft.ThemeMode.LIGHT if colors["THEME_MODE"] == "light" else ft.ThemeMode.DARK
        page.bgcolor = colors["BG"]

        for i in range(7):
            update_slot_display(i)

        if left_panel_ref.current:
            left_panel_ref.current.bgcolor = colors["PANEL"]
        if hotbar_container_ref.current:
            hotbar_container_ref.current.bgcolor = colors["PANEL"]
        if info_container_ref.current:
            info_container_ref.current.bgcolor = colors["PANEL"]
        if controls_container_ref.current:
            controls_container_ref.current.bgcolor = colors["PANEL"]

        if preset_dropdown_ref.current:
            preset_dropdown_ref.current.bgcolor = colors["BG"]
            preset_dropdown_ref.current.color = colors["FONT"]

        material_list.controls.clear()
        for mat in MATERIALS:
            src = get_image_src(mat)
            img_widget = ft.Image(src=src, width=70, height=70) if src else ft.Text("?", size=24)
            draggable = ft.Draggable(
                content=ft.Container(
                    padding=8,
                    border_radius=BORDER_RADIUS,
                    bgcolor=colors["BG"],
                    content=ft.Row([
                        img_widget,
                        ft.Column([
                            ft.Text(mat.replace("_", " "), size=16, weight="bold", color=colors["FONT"]),
                            ft.Text(MATERIAL_INFO[mat], size=10, color=colors["HINT"], width=160)
                        ], spacing=2, expand=True)
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START),
                    tooltip=MATERIAL_INFO[mat]
                ),
                data=mat
            )
            material_list.controls.append(draggable)

        btn_refs_and_icons = [
            (apply_preset_btn_ref, ft.Icons.ARROW_OUTWARD_ROUNDED, "Apply preset"),
            (save_preset_btn_ref, ft.Icons.SAVE, "Save Preset"),
            (run_pause_btn_ref, None, "Start/Pause"),
            (stop_btn_ref, ft.Icons.STOP, "Stop"),
            (settings_btn_ref, ft.Icons.SETTINGS, "Settings")
        ]

        for ref, icon, tooltip in btn_refs_and_icons:
            if ref.current:
                if ref == run_pause_btn_ref:
                    if not running:
                        ref.current.style.bgcolor = colors["SUCCESS"]
                        ref.current.content = ft.Icon(ft.Icons.PLAY_ARROW, size=20, color="#FFFFFF")
                    elif pause_flag:
                        ref.current.style.bgcolor = colors["SLOT_BG"]
                        ref.current.content = ft.Icon(ft.Icons.PLAY_ARROW, size=20, color=colors["FONT"])
                    else:
                        ref.current.style.bgcolor = colors["WARNING"]
                        ref.current.content = ft.Icon(ft.Icons.PAUSE, size=20, color="#FFFFFF")
                elif ref == settings_btn_ref:
                    grey = ft.Colors.GREY_700 if theme_name != "nothing" else ft.Colors.GREY_900
                    ref.current.style.bgcolor = grey
                else:
                    ref.current.style.bgcolor = colors["PRIMARY"]
                ref.current.update()

        page.update()

    def update_slot_display(idx):
        colors = get_colors()
        mat = slots[idx]
        disabled = slot_disabled[idx]
        on_cooldown = slot_cooldown_end[idx] > time.time()

        if mat is None:
            new_control = ft.DragTarget(
                content=create_slot_content(None, idx, disabled, on_cooldown, colors),
                data=str(idx),
                on_accept=lambda e, i=idx: on_slot_drop(e, i)
            )
        else:
            inner = ft.Container(
                content=create_slot_content(mat, idx, disabled, on_cooldown, colors),
                on_click=lambda e, i=idx: toggle_slot_disabled(i),
                on_long_press=lambda e, i=idx: clear_slot(i)
            )
            new_control = ft.Draggable(
                content=inner,
                data=mat,
                on_drag_complete=lambda e, i=idx: on_item_dragged_out(i)
            )
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
        drag_target = ft.DragTarget(
            content=create_slot_content(None, i, False, False, THEMES[current_theme]),
            data=str(i),
            on_accept=lambda e, idx=i: on_slot_drop(e, idx)
        )
        container = ft.Container(content=drag_target)
        slot_containers.append(container)

    hotbar = ft.Row([
        ft.Column([slot_containers[i], timer_texts[i]], spacing=4, alignment=ft.MainAxisAlignment.CENTER)
        for i in range(7)
    ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)

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

    def run_macro():
        nonlocal running, pause_flag
        running = True
        pause_flag = False
        time.sleep(1.0)
        try:
            # if PRECISION_TRACKING_AVAILABLE and track_precision:
            #     _start_precision_tracker()
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
                        duration = EFFECTIVE_MATERIAL_TIMER.get(mat, 1)
                        slot_cooldown_end[i] = current_time + duration
                        pressed_any = True
                time.sleep(0.1 if pressed_any else 0.5)
        finally:
            running = False
            pause_flag = False
            # _stop_precision_tracker()

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

    # --- Hotkeys ---
    def start_macro_hotkey():
        nonlocal running, pause_flag
        if not running:
            threading.Thread(target=run_macro, daemon=True).start()
            ui_timer.start()
            # Update UI button state
            colors = get_colors()
            run_pause_btn_ref.current.style.bgcolor = colors["WARNING"]
            run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PAUSE, size=20, color="#FFFFFF")
            run_pause_btn_ref.current.update()

    def toggle_pause_hotkey():
        nonlocal running, pause_flag
        if not running:
            return
        colors = get_colors()
        pause_flag = not pause_flag
        if pause_flag:
            run_pause_btn_ref.current.style.bgcolor = colors["SLOT_BG"]
            run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PLAY_ARROW, size=20, color=colors["FONT"])
        else:
            run_pause_btn_ref.current.style.bgcolor = colors["WARNING"]
            run_pause_btn_ref.current.content = ft.Icon(ft.Icons.PAUSE, size=20, color="#FFFFFF")
        run_pause_btn_ref.current.update()

    def stop_macro_hotkey():
        nonlocal running, pause_flag
        if not running:
            return
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
        # _stop_precision_tracker()

    keyboard.add_hotkey('f1', start_macro_hotkey, suppress=True)
    keyboard.add_hotkey('f2', toggle_pause_hotkey, suppress=True)
    keyboard.add_hotkey('f3', stop_macro_hotkey, suppress=True)

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
        # _stop_precision_tracker()

    def open_settings(e):
        colors = get_colors()

        always_on_top_val = page.window.always_on_top
        always_on_top_checkbox = ft.Checkbox(
            label="Always on top",
            value=always_on_top_val,
            check_color="#FFFFFF",
            active_color=colors["PRIMARY"],
            label_style=ft.TextStyle(size=13, color=colors["FONT"])
        )

        # track_precision_val = track_precision
        # precision_interval_val = precision_interval

        # if PRECISION_TRACKING_AVAILABLE:
        #     track_precision_checkbox = ft.Checkbox(
        #         label="Track Precision Buff",
        #         value=track_precision_val,
        #         check_color="#FFFFFF",
        #         active_color=colors["PRIMARY"],
        #         label_style=ft.TextStyle(size=13, color=colors["FONT"])
        #     )
        #
        #     interval_slider_ref = ft.Ref[ft.Slider]()
        #
        #     def on_interval_change(e):
        #         val = float(e.control.value)
        #         e.control.label = f"{val:.2f}s"
        #         e.control.update()
        #
        #     interval_slider = ft.Slider(
        #         ref=interval_slider_ref,
        #         min=0.1,
        #         max=1.0,
        #         divisions=18,
        #         value=precision_interval_val,
        #         label=f"{precision_interval_val:.2f}s",
        #         on_change=on_interval_change,
        #         thumb_color=colors["PRIMARY"],
        #         active_color=colors["PRIMARY"],
        #         inactive_color=colors["HINT"],
        #         width=200,
        #     )
        #
        #     performance_warn = ft.Text(
        #         "⚠️ Lower intervals use more CPU/GPU",
        #         size=11,
        #         color=colors["DANGER"],
        #         text_align=ft.TextAlign.CENTER,
        #     )
        # else:
        #     track_precision_checkbox = None
        #     interval_slider = None
        #     performance_warn = None

        theme_names = ["light", "dark", "nothing", "pinky"]
        theme_index = theme_names.index(current_theme)
        theme_selector = ft.CupertinoSlidingSegmentedButton(
            selected_index=theme_index,
            thumb_color=colors["PRIMARY"],
            on_change=lambda ev: None,
            padding=ft.Padding.symmetric(vertical=4, horizontal=10),
            controls=[ft.Text(t.capitalize()) for t in theme_names],
        )

        timer_fields = {}
        timer_grid = ft.Column(spacing=6)

        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        for row_mats in chunks(MATERIALS, 4):
            row_items = []
            for mat in row_mats:
                current = EFFECTIVE_MATERIAL_TIMER.get(mat, MATERIAL_TIMER.get(mat, 1))
                field = ft.TextField(
                    value=str(current),
                    width=70,
                    height=32,
                    text_align=ft.TextAlign.RIGHT,
                    input_filter=ft.NumbersOnlyInputFilter(),
                    border_radius=5,
                    dense=True,
                    content_padding=4,
                    text_style=ft.TextStyle(size=11, color=colors["FONT"]),
                    bgcolor=colors["BG"],
                    border_color=colors["HINT"],
                )
                timer_fields[mat] = field
                src = get_image_src(mat)
                img_widget = ft.Image(src=src, width=28, height=28) if src else ft.Text("?", size=16)
                row_items.append(
                    ft.Container(
                        ft.Column([
                            img_widget,
                            field,
                        ], spacing=2, alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        width=80,
                        alignment=ft.alignment.Alignment(0, 0),
                    )
                )
            while len(row_items) < 4:
                row_items.append(ft.Container(width=80))
            timer_grid.controls.append(ft.Row(row_items, spacing=8, alignment=ft.MainAxisAlignment.START))

        def save_and_close(_):
            # nonlocal track_precision, precision_interval, precision_tracker

            new_always_on_top = always_on_top_checkbox.value
            new_theme = theme_names[theme_selector.selected_index]
            setattr(page.window, "always_on_top", new_always_on_top)

            data_to_save = {"theme": new_theme, "always_on_top": new_always_on_top}

            # if PRECISION_TRACKING_AVAILABLE:
            #     new_track = track_precision_checkbox.value
            #     new_interval = round(interval_slider.value, 2)
            #     data_to_save["track_precision"] = new_track
            #     data_to_save["precision_interval"] = new_interval
            #
            #     track_precision = new_track
            #     precision_interval = new_interval
            #
            #     if running:
            #         _stop_precision_tracker()
            #         if new_track:
            #             _start_precision_tracker()

            save_settings(data_to_save)

            if new_theme != current_theme:
                apply_theme(new_theme)

            new_timer_data = {}
            for mat, field in timer_fields.items():
                try:
                    val = int(field.value)
                    if val > 0:
                        new_timer_data[mat] = val
                except ValueError:
                    pass
            save_custom_timers(new_timer_data)
            global custom_timers, EFFECTIVE_MATERIAL_TIMER
            custom_timers = load_custom_timers()
            EFFECTIVE_MATERIAL_TIMER = {k: custom_timers.get(k, v) for k, v in MATERIAL_TIMER.items()}

            page.pop_dialog()
            page.snack_bar = ft.SnackBar(ft.Text("Settings saved!"), bgcolor=colors["SUCCESS"])
            page.snack_bar.open = True
            page.update()

        def reset_timers(_):
            for mat, field in timer_fields.items():
                field.value = str(MATERIAL_TIMER.get(mat, 1))
            page.update()

        reset_btn = ft.Button(
            "Reset Timers", on_click=reset_timers,
            height=30, style=ft.ButtonStyle(bgcolor=colors["SLOT_BG"], color=colors["FONT"],
                                            shape=ft.RoundedRectangleBorder(radius=6))
        )

        save_close_btn = ft.Button(
            "Save & Close", on_click=save_and_close,
            height=36,
            style=ft.ButtonStyle(bgcolor=colors["PRIMARY"], color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=6))
        )

        settings_content_controls = [
            ft.Row(
                [
                    ft.Text("⚙️ Settings", size=18, weight="bold", color=colors["FONT"]),
                    save_close_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Divider(height=12, color=colors["SLOT_BG"]),
            always_on_top_checkbox,
            ft.Row([ft.Text("Theme:", size=13, color=colors["FONT"]), theme_selector],
                   alignment=ft.MainAxisAlignment.START),
        ]

        # if PRECISION_TRACKING_AVAILABLE:
        #     precision_row = ft.Row(
        #         [
        #             track_precision_checkbox,
        #             interval_slider,
        #         ],
        #         alignment=ft.MainAxisAlignment.START,
        #         vertical_alignment=ft.CrossAxisAlignment.CENTER,
        #         spacing=10,
        #     )
        #     settings_content_controls.extend([
        #         precision_row,
        #         performance_warn,
        #     ])

        settings_content_controls.extend([
            ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
            ft.Row([
                ft.Text("Material Cooldowns (sec)", size=14, weight="bold", color=colors["FONT"]),
                reset_btn
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(timer_grid, padding=ft.Padding.only(top=6)),
            ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
        ])

        settings_content = ft.Column(
            settings_content_controls,
            spacing=10, tight=True, scroll=ft.ScrollMode.AUTO, height=520
        )

        dialog = ft.AlertDialog(
            content=settings_content,
            content_padding=12,
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=colors["PANEL"]
        )
        page.show_dialog(dialog)

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

        save_content = ft.Column([
            ft.Row([ft.Text("Save Preset", size=18, weight="bold", color=colors["FONT"])], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=12, color=colors["SLOT_BG"]),
            ft.Row([preset_name_field], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([cancel_btn, save_btn], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=8, tight=True)

        save_dialog = ft.AlertDialog(content=save_content, content_padding=8, scrollable=False, shape=ft.RoundedRectangleBorder(radius=8), bgcolor=colors["BG"])
        page.show_dialog(save_dialog)

    def load_presets():
        options = [ft.dropdown.Option(name) for name in PRESETS]
        for file in preset_dir.glob("*.json"):
            options.append(ft.dropdown.Option(file.stem))
        preset_dropdown.options = options

    # Create buttons
    colors = get_colors()
    apply_preset_btn = make_icon_button(ft.Icons.ARROW_OUTWARD_ROUNDED, colors["PRIMARY"], "Apply preset", apply_preset, apply_preset_btn_ref)
    save_preset_btn = make_icon_button(ft.Icons.SAVE, colors["PRIMARY"], "Save Preset", save_preset, save_preset_btn_ref)
    run_pause_btn = make_icon_button(ft.Icons.PLAY_ARROW, colors["SUCCESS"], "Start/Pause", on_toggle_run_pause, run_pause_btn_ref)
    stop_btn = make_icon_button(ft.Icons.STOP, colors["DANGER"], "Stop", on_stop, stop_btn_ref)
    settings_btn = make_icon_button(ft.Icons.SETTINGS, ft.Colors.GREY_700 if current_theme != "nothing" else ft.Colors.GREY_900, "Settings", open_settings, settings_btn_ref)

    def on_window_event(e):
        if e.data == "visible":
            for i in range(7):
                update_slot_display(i)
            page.update()

    page.on_window_event = on_window_event

    hotbar_container = ft.Container(ref=hotbar_container_ref, content=hotbar, padding=10, border_radius=8, margin=ft.margin.Margin(top=0, left=0, right=0, bottom=8))

    info_container = ft.Container(
        ref=info_container_ref,
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text(
                        "\n".join(APP_TIPS),
                        size=11,
                        color=colors["HINT"]
                    ),
                    expand=True
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"🦊 MacroFox {APP_VERSION}", size=11, weight=ft.FontWeight.BOLD, color=colors["HINT"]),
                        ft.Text("This macro is designed specifically for boosting by automating hotbar items usage\n",
                                size=11, color=colors["HINT"]),
                        ft.Text("Update Log:", size=11, weight=ft.FontWeight.BOLD, color=colors["HINT"]),
                        ft.Container(
                            content=ft.ListView(
                                controls=[
                                    ft.Text(f"• {log}", size=11, color=colors["HINT"])
                                    for log in UPDATE_LOG
                                ],
                                auto_scroll=False,
                                padding=0,
                                spacing=2,
                            ),
                            height=80,
                            expand=False,
                        ),
                    ], spacing=4),
                    expand=True,
                ),
            ], spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], spacing=8),
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
        ft.Column([
            ft.Row([left_panel, ft.Column([hotbar_container, info_container, controls_container], expand=True, spacing=4)], expand=True, spacing=12),
        ], expand=True, spacing=0)
    )

    apply_theme(current_theme)
    load_presets()
    page.update()


ft.run(main)