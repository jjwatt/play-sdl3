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
    high: int = 20
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
    for square in squares:
        square.apply_gravity(world.gravity)
        square.apply_air_resistance(world.air_resistance)
        square.update_position()

        is_on_right_wall = (
            square.position.x >= screen_width - square.size.x
        )
        is_on_left_wall = (
            square.position.x <= 0
        )
        is_on_wall = (is_on_right_wall or is_on_left_wall)
        is_on_floor = (
            square.position.y >= screen_height - square.size.y
        )
        is_on_ceiling = square.position.y <= 0

        if is_on_wall:
            # Reset x on boundries
            if is_on_left_wall:
                square.position.x = 0
            if is_on_right_wall:
                square.position.x = (
                    screen_width - square.size.x
                )
            # Bounce off wall with some energy loss
            square.damp_x(world.damping)
            # Change to random color
            square.color = get_random_color()
        if is_on_floor:
            square.position.y = (
                screen_height - square.size.y
            )
            # Only bounce if moving fast enough.
            if square.velocity.y > 0.5:
                square.damp_y(world.damping)
                square.color = get_random_color()
            else:
                square.velocity.x *= 0.95
                square.velocity.y = 0
        if is_on_ceiling:
            square.position.y = 0
            square.damp_y(world.damping)
            square.color = get_random_color()


def draw_squares(
        squares: list[Square],
        renderer: sdl3.SDL_POINTER,
        background_color: Color
) -> None:
    """Draw the squares."""
    set_color(renderer, background_color)
    sdl3.SDL_RenderClear(renderer)
    for square in squares:
        set_color(renderer, square.color)
        rect = sdl3.SDL_FRect(
            int(square.position.x),
            int(square.position.y),
            int(square.size.x),
            int(square.size.y)
        )
        sdl3.SDL_RenderFillRect(renderer, rect)

    sdl3.SDL_RenderPresent(renderer)


def init_squares(
        num_squares,
        screen_width,
        screen_height
) -> list[Square]:
    """Initialize squares."""
    squares = []
    print(f"{num_squares=}")
    for _ in range(num_squares):
        square = Square(
            Vec2(100.0, 100.0),
            Vec2(screen_width / 2, screen_height / 2),
        )
        square.velocity = get_random_velocity()
        square.color = get_random_color()
        squares.append(square)
    return squares


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

        num_squares = 4
        # Create squares.
        squares = init_squares(
            num_squares, screen_width, screen_height
        )
        # Create world.
        world = World()

        event = sdl3.SDL_Event()
        running = True
        while running:
            while sdl3.SDL_PollEvent(ctypes.byref(event)):
                match event.type:
                    case sdl3.SDL_EVENT_QUIT:
                        running = False
                    case sdl3.SDL_EVENT_KEY_DOWN:
                        if event.key.key in [sdl3.SDLK_ESCAPE]:
                            running = False
            set_color(renderer, background_color)
            update_squares(
                squares, world, screen_width, screen_height
            )
            draw_squares(squares, renderer, background_color)
            sdl3.SDL_Delay(15)
        return 0
    except SDLException as se:
        print(f"SDL error: {se}")
        return 1
    finally:
        if renderer and window:
            close(renderer, window)
