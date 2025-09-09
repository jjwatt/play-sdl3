"""Gravity Squares."""
import ctypes
from dataclasses import dataclass, field
import random
import sdl3
from typing import NamedTuple


class SDLException(Exception):
    """SDL Exception."""


@dataclass
class Vec2():
    """2D vector with x and y."""

    x: float = 0
    y: float = 0

    def __add__(self, other: 'Vec2') -> 'Vec2':
        """Add two Vec2s."""
        return Vec2(self.x + other.x,
                    self.y + other.y)

    def __iadd__(self, other: 'Vec2') -> 'Vec2':
        """In-place addition self+=other."""
        self.x += other.x
        self.y += other.y
        return self

    def __repr__(self) -> str:
        """Return string representation of Vec2."""
        return f"Vec2({self.x}, {self.y})"


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

    size: Vec2 = field(default_factory=lambda: Vec2(10.0, 10.0))
    position: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    velocity: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    color: Color = field(default_factory=Color)

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
        blue=random.randint(0, 255)
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


def set_color(
        renderer: sdl3.SDL_POINTER,
        color: Color
) -> None:
    """Set Render Draw Color."""
    sdl3.SDL_SetRenderDrawColor(
        renderer,
        color.red,
        color.green,
        color.blue,
        color.alpha
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


def close(renderer, window) -> None:
    """Close contexts."""
    sdl3.SDL_DestroyRenderer(renderer)
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()


def update_squares(
        squares: list[Square],
        world: World,
        screen_width: int,
        screen_height: int
) -> None:
    """Update the squares positions."""
    pass


def draw_squares(
        squares: list[Square],
        renderer: sdl3.SDL_POINTER,
        background_color: Color
) -> None:
    """Draw the squares."""
    pass


@sdl3.SDL_main_func
def main(
    argc: ctypes.c_int,
    argv: sdl3.LP_c_char_p
) -> ctypes.c_int:
    """Run the main part of the program."""
    screen_width = 800
    screen_height = 600
    background_color = Color()

    try:
        init()
        window = create_window(
            width=screen_width,
            height=screen_height
        )
        print(window)
        renderer = create_renderer(window, try_vulkan=False)
        print(renderer)
    except SDLException as se:
        print(f"SDL error: {se}")
        return 1

    set_color(renderer, background_color)
    num_squares = 4
    squares = []
    for i in range(num_squares):
        square = Square(
            Vec2(100.0, 100.0),
            Vec2(screen_width / 2, screen_height / 2),
            get_random_velocity()
        )
        square.color = get_random_color()
        squares.append(square)
    close(renderer, window)
    return 0
