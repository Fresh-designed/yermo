"""Geometría del gráfico de flujo. El SVG se dibuja en `metrics/_flow_chart.html`."""
from math import ceil

WIDTH = 860
HEIGHT = 280
LEFT = 34
RIGHT = 12
TOP = 14
BOTTOM = 30


def _axis_ticks(peak):
    """Marcas enteras y redondas del eje: paso 1, 2, 5, 10, 20, 50… con 4 tramos como mucho."""
    peak = max(peak, 4)
    magnitude = 1
    while True:
        for step in (magnitude, 2 * magnitude, 5 * magnitude):
            if peak <= step * 4:
                return list(range(0, ceil(peak / step) * step + 1, step))
        magnitude *= 10


def build_flow_chart(flow):
    """Líneas de usuarios activos, registros y eliminaciones sobre un solo eje."""
    series = [
        {"key": "active", "label": "Usuarios activos", "css": "s-active"},
        {"key": "registers", "label": "Registros", "css": "s-register"},
        {"key": "deletes", "label": "Eliminaciones", "css": "s-delete"},
    ]
    peak = max((row[s["key"]] for row in flow for s in series), default=0)
    tick_values = _axis_ticks(peak)
    ceiling = tick_values[-1]
    plot_w = WIDTH - LEFT - RIGHT
    plot_h = HEIGHT - TOP - BOTTOM
    step_x = plot_w / max(len(flow) - 1, 1)

    def x(index):
        return round(LEFT + index * step_x, 1)

    def y(value):
        return round(TOP + plot_h - value / ceiling * plot_h, 1)

    for item in series:
        points = [(x(i), y(row[item["key"]])) for i, row in enumerate(flow)]
        item["path"] = " ".join(f"{px},{py}" for px, py in points)
        item["end_x"], item["end_y"] = points[-1]
        item["end_value"] = flow[-1][item["key"]]

    ticks = [{"value": value, "y": y(value)} for value in tick_values]
    label_every = 1 if len(flow) <= 14 else 3
    columns = []
    for index, row in enumerate(flow):
        anchor = "middle"
        if index == 0:
            anchor = "start"
        elif index == len(flow) - 1:
            anchor = "end"
        columns.append(
            {
                "x": x(index),
                "hit_x": round(x(index) - step_x / 2, 1),
                "hit_w": round(step_x, 1),
                "row": row,
                "show_label": (len(flow) - 1 - index) % label_every == 0,
                "anchor": anchor,
            }
        )
    return {
        "width": WIDTH,
        "height": HEIGHT,
        "left": LEFT,
        "right_edge": WIDTH - RIGHT,
        "top": TOP,
        "bottom_edge": HEIGHT - BOTTOM,
        "plot_height": plot_h,
        "label_y": HEIGHT - 10,
        "series": series,
        "ticks": ticks,
        "columns": columns,
    }
