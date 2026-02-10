import flet as ft
from constants import MATERIALS, MATERIAL_INFO, THEMES, BORDER_RADIUS
from assets_b64 import MATERIAL_IMAGES

def get_image_src(mat):
    if mat in MATERIAL_IMAGES:
        return f"data:image/webp;base64,{MATERIAL_IMAGES[mat]}"
    return None

def create_slot_content(mat, idx, disabled=False, on_cooldown=False, colors=None):
    if colors is None:
        colors = THEMES["light"]
    if mat:
        src = get_image_src(mat)
        if src:
            img = ft.Image(src=src, width=46, height=46)
            content = img
        else:
            content = ft.Text("?", size=16, color=colors["HINT"])
    else:
        content = ft.Text(str(idx + 1), size=12, color=colors["HINT"])

    bgcolor = colors["SLOT_BG"]
    border = None
    if disabled:
        bgcolor = ft.Colors.with_opacity(0.2, colors["DANGER"])
        border = ft.Border.all(2, colors["DANGER"])
    elif on_cooldown:
        bgcolor = ft.Colors.with_opacity(0.2, colors["PRIMARY"])

    tooltip_text = ""
    if mat:
        base = MATERIAL_INFO.get(mat, "")
        if disabled:
            tooltip_text = base + " (Disabled)"
        elif on_cooldown:
            tooltip_text = base + " (On Cooldown)"
        else:
            tooltip_text = base
    else:
        tooltip_text = f"Slot {idx + 1}"

    return ft.Container(
        width=60,
        height=60,
        border_radius=BORDER_RADIUS,
        bgcolor=bgcolor,
        border=border,
        alignment=ft.alignment.Alignment(0, 0),
        content=content,
        tooltip=tooltip_text
    )

def make_icon_button(icon, bgcolor, tooltip, on_click, ref):
    return ft.Button(
        ref=ref,
        content=ft.Icon(icon, size=20, color="#FFFFFF"),
        width=48,
        height=48,
        on_click=on_click,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=0, bgcolor=bgcolor),
        tooltip=tooltip
    )