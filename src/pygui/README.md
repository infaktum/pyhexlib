pygui layout API
=================

This document describes the layout API provided in `pygui.layout`.

Core concepts
-------------

- `Container`: holds components and a `Layouter`. Use `add_component(component, pos=None, anchored=False, flow=True)` to add items.
- `LayoutItem`: returned by layouters; contains `component`, `position` (Point), `anchored` (bool), `flow` (bool).
- `Layouter`: base class. Implementations return `list[LayoutItem]` from `do_layout(components_dict)`.

Metadata fields when adding a component
--------------------------------------

- `pos`: optional preferred position (Point or tuple). If provided, layouter may use it.
- `anchored`: if True, the component must have a `pos`. Otherwise a ValueError is raised.
- `flow`: controls whether the component participates in the layout flow (advances the layouter cursor). Use `flow=False` for decorative elements like borders.

Provided layouters
-------------------

- `VerticalLayouter(margin=...)`: stacks components top→down.
- `HorizontalLayouter(margin=..., valign='top'|'center'|'bottom')`: places components left→right.
- `GridLayouter(cols=..., cell_size=None, hgap=..., vgap=..., margin=...)`: arranges components in a grid.

Examples
--------

Decorative rim that does not push buttons down:

```py
from pygui import Point, Size
from pygui.layout import Container, VerticalLayouter
from pygui.components import Rim, Button

gui = Container('ui', size=Size(400,400), layouter=VerticalLayouter(margin=8))
gui.add_component(Rim('rim', size=Size(400,40)), pos=Point(0,0), flow=False)
gui.add_component(Button('ok', size=Size(100,30)))
```


