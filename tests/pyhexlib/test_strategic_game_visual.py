"""Regression probe for the still-open top-edge rendering issue."""

import importlib.util
from pathlib import Path

import pygame
import pytest


@pytest.mark.xfail(strict=True, reason="The top hex outline is not visible below the map frame")
def test_top_hex_outline_visible_below_map_frame(monkeypatch):
    example_dir = Path(__file__).resolve().parents[2] / "examples" / "06_strategic_game"
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.syspath_prepend(str(example_dir))
    monkeypatch.chdir(example_dir)

    spec = importlib.util.spec_from_file_location("strategic_game_main", example_dir / "main.py")
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)

    main.pylightgui.init(skin=main.military_skin)
    _, renderer, screen, gui = main.init(25, 30, 40)
    try:
        renderer.render()
        screen.blit(renderer.surface, main.map_window.topleft)
        main.pylightgui.render.GuiRenderer(screen).render(gui)

        x = main.map_window.x + 24  # horizontal top edge of the first hex
        top = main.map_window.y + 6  # below the map frame
        assert any(screen.get_at((x, y))[:3] == (0, 0, 0) for y in range(top, top + 14))
    finally:
        pygame.quit()
