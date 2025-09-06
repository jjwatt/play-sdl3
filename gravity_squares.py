"""Gravity Squares."""
import ctypes
import sdl3
from dataclasses import dataclass
from typing import NamedTuple


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
    """A Square for moving around."""

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


@sdl3.SDL_main_func
def main(
    argc: ctypes.c_int,
    argv: sdl3.LP_c_char_p
) -> ctypes.c_int:
    """Run the main part of the program."""
    pass
