"""Gravity Squares."""
import ctypes
from dataclasses import dataclass
import random
import sdl3
from typing import NamedTuple


class SDLException(Exception):
    """SDL Exception."""


class Vec2(NamedTuple):
    """2D vector with x and y."""

    x: float = 0
    y: float = 0

    def __add__(self, other: 'Vec2') -> 'Vec2':
        """Add two Vec2s."""
        return Vec2(self.x + other.x,
                    self.y + other.y)


class Color(NamedTuple):
    """RGBA Color with values 0-255."""

    red: int = 0xff
    green: int = 0xff
    blue: int = 0xff
    alpha: int = 0xff

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int):
        """Create color from rgb values."""
        return cls(r, g, b, 0xff)


@dataclass
class Square:
    """A colored square for moving around."""

    size: Vec2 = None
    position: Vec2 = None
    velocity: Vec2 = None
    color: Color = None

    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.size is None:
            self.size = Vec2(10.0, 10.0)
        if self.position is None:
            self.position = Vec2(0.0, 0.0)
        if self.velocity is None:
            self.velocity = Vec2(0.0, 0.0)
        if self.color is None:
            self.color = Color()

    def apply_gravity(self, gravity: float):
        """Apply gravity to velocity."""
        self.velocity.y += gravity

    def apply_air_resistance(self, air_resistance):
        """Apply air resistance to velocity."""
        self.velocity.x *= air_resistance

    def damp_x(self, damping: float):
        """Dampen x velocity."""
        self.velocity.x *= -damping

    def damp_y(self, damping: float):
        """Dampen y velocity."""
        self.velocity.y *= -damping

    def update_position(self):
        """Update position based on current velocity."""
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y


@dataclass
class World:
    """The properties of the world."""

    gravity: float = 0.5
    damping: float = 0.9
    air_resistance: float = 0.995


def get_random_color() -> Color:
    """Get a random Color."""
    return Color(
        red=random.randint(0, 255),
        green=random.randint(0, 255),
        blue=random.randing(0, 255)
    )


def get_random_velocity(
    low: int = -20,
    high: int = -20
) -> Vec2:
    """Get a random velocity Vec2."""
    return Vec2(
        x=float(random.randint(low, high)),
        y=float(random.randint(low, high))
    )


def init() -> None:
    """Initialize SDL3."""
    if not sdl3.SDL_Init(
        sdl3.SDL_INIT_VIDEO | sdl3.SDL_INIT_EVENTS
    ):
        message = (f"Failed to initialize: "
                   f"{sdl3.SDL_GetError().decode()}")
        raise SDLException(message)


def create_window(
        width: int = 800,
        height: int = 600
) -> sdl3.LP_SDL_Window:
    """Create an SDL3 Window."""
    if not (window := sdl3.SDL_CreateWindow(
            "Gravity Squares".encode(),
            width,
            height,
            sdl3.SDL_WINDOW_RESIZABLE
    )):
        message = (
            "Failed to create window: "
            f"{sdl3.SDL_GetError().decode()}."
        )
        raise SDLException(message)
    return window


def create_renderer(
    window: sdl3.LP_SDL_Window,
    try_vulkan: bool = True
) -> sdl3.LP_SDL_Renderer:
    """Create the renderer."""
    render_drivers = [sdl3.SDL_GetRenderDriver(i).decode()
                      for i in range(sdl3.SDL_GetNumRenderDrivers())]

    def try_get_driver(order, drivers):
        return next((i for i in order if i in drivers), None)

    render_driver = try_get_driver(
        ((["vulkan"] if try_vulkan else [])
         + ["opengl", "software"]), render_drivers
    )
    print(
        "Available render drivers: "
        f"{', '.join(render_drivers)} "
        f"(current: {render_driver})."
    )
    renderer = sdl3.SDL_CreateRenderer(
        window,
        render_driver.encode()
    )
    if not renderer:
        message = ("Failed to create renderer: "
                   f"{sdl3.SDL_GetError().decode()}.")
        raise SDLException(message)
    return renderer


@sdl3.SDL_main_func
def main(
    argc: ctypes.c_int,
    argv: sdl3.LP_c_char_p
) -> ctypes.c_int:
    """Run the main part of the program."""
    init()
    window = create_window()
    print(window)
    renderer = create_renderer(window, try_vulkan=False)
    print(renderer)
    return 0
