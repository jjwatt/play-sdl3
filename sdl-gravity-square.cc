#include <iostream>
#include <random>

#include "SDL2/SDL.h"

struct Vec2 {
    double x {0.0};
    double y {0.0};

    Vec2() = default;
    Vec2(double x_val, double y_val)
	: x {x_val}
	, y {y_val} {}
    Vec2 operator+(const Vec2& other) const {
	return Vec2(x + other.x, y + other.y);
    }
    // TODO: Add more methods
};

struct Color {
    // Default to white
    Uint8 red {0xff};
    Uint8 green {0xff};
    Uint8 blue {0xff};
    Uint8 alpha {0xff};
    Color() = default;
    Color(Uint8 r, Uint8 g, Uint8 b, Uint8 a)
	: red {r}
	, green {g}
	, blue {b}
	, alpha(a) {}
    Color(Uint8 r, Uint8 g, Uint8 b)
	: Color(r, g, b, 0xff) {}
};

class Square
{
private:
    Vec2 m_size {10.0, 10.0};
    Vec2 m_position {0.0, 0.0};
    Vec2 m_velocity {};
    Color m_color {};

public:
    Square() = default;
    Square(Vec2 size, Vec2 pos, Vec2 v)
	: m_size {size}
	, m_position {pos}
	, m_velocity {v} {}
    Square(Vec2 size)
	: m_size {size} {}
    Vec2 size() const { return m_size; }
    void setSize(Vec2 size) { m_size = size; }
    Vec2 position() const { return m_position; }
    void setPos(Vec2 pos) { m_position = pos; }
    void setPosX(double x) { m_position.x = x; }
    void setPosY(double y) { m_position.y = y; }
    Vec2 velocity() const { return m_velocity; }
    void setVelocity(Vec2 velocity) { m_velocity = velocity; }
    Color color() const { return m_color; }
    void setColor(Color color) { m_color = color; }

    void applyGravity(double gravity)
    {
	m_velocity.y += gravity;
    }

    void applyAirResistance(double air_resistance)
    {
	m_velocity.x *= air_resistance;
    }

    void dampX(double damping) {
	m_velocity.x *= -damping;
    }

    void dampY(double damping) {
	m_velocity.y *= -damping;
    }

    void updatePosition()
    {
	m_position.x += m_velocity.x;
	m_position.y += m_velocity.y;
    }
};

struct World {
    double gravity {0.5};
    double damping {0.9};
    double air_resistance {0.995};
    World() = default;
    World(double g, double d, double ar)
	: gravity {g}, damping {d}, air_resistance {ar} {}
};

int get_random_int(int low, int high)
{
    // Setup random number generator for low to high
    static std::random_device rd;
    static std::mt19937 gen(rd());
    std::uniform_int_distribution<> distrib(low, high);
    return distrib(gen);
}

Color get_random_color(void)
{
    Color color {};
    color.red = get_random_int(0, 255);
    color.green = get_random_int(0, 255);
    color.blue = get_random_int(0, 255);
    return color;
}

Vec2 get_random_velocity(void)
{
    return Vec2 {static_cast<double>(get_random_int(-20, 20)),
		 static_cast<double>(get_random_int(-20, 20))};
}

void set_color(SDL_Renderer* renderer, Color color)
{
    SDL_SetRenderDrawColor(renderer,
			   color.red,
			   color.green,
			   color.blue,
			   color.alpha);
}

constexpr int gScreenWidth {640};
constexpr int gScreenHeight {480};
SDL_Window *gWindow = nullptr;
SDL_Renderer *gRenderer = nullptr;
Square *gSquare;
std::vector<Square*> gSquares;
constexpr int gNumSquares = 4;
World gWorld;
Color gBackgroundColor;

int init(void) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
	SDL_Log("SDL_Init Error: %s\n", SDL_GetError());
	return 0;
    }
    // SDL_Window *window = nullptr;
    // SDL_Renderer *renderer = nullptr;
    gWindow = SDL_CreateWindow("Gravity Square SDL C++",
			      SDL_WINDOWPOS_UNDEFINED,
			      SDL_WINDOWPOS_UNDEFINED,
			      gScreenWidth,
			      gScreenHeight,
			      SDL_WINDOW_SHOWN);
    gRenderer = SDL_CreateRenderer(gWindow,
				       -1,
				       SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    gWorld = {};
    gBackgroundColor = {};

    return 1;
}

void init_squares(void) {
    for (int i = 0; i < gNumSquares; ++i) {
	auto square = new Square({100.0, 100.0},
			    {gScreenWidth / 2, gScreenHeight / 2},
			    get_random_velocity());
	// Set color
	square->setColor(get_random_color());
	gSquares.push_back(square);
    }
}

void init_square(void) {
    // Init square
    gSquare = new Square({100.0, 100.0},
			 {gScreenWidth / 2, gScreenHeight / 2},
			 get_random_velocity());
    // Setup square color
    gSquare->setColor(get_random_color());
}

void draw(void) {
    // Draw background
    set_color(gRenderer, gBackgroundColor);
    SDL_RenderClear(gRenderer);

    // Set gRenderer color for painting square
    set_color(gRenderer, gSquare->color());

    // Draw
    SDL_Rect rect = { .x = static_cast<int>(gSquare->position().x),
		      .y = static_cast<int>(gSquare->position().y),
		      .w = static_cast<int>(gSquare->size().x),
		      .h = static_cast<int>(gSquare->size().y) };
    SDL_RenderFillRect(gRenderer, &rect);
    
    // Update the screen
    SDL_RenderPresent(gRenderer);
}


void draw_squares(void) {
    // Draw background
    set_color(gRenderer, gBackgroundColor);
    SDL_RenderClear(gRenderer);
    for (auto square : gSquares) {
	// Set gRenderer color for painting square
	set_color(gRenderer, square->color());

	// Draw
	SDL_Rect rect = { .x = static_cast<int>(square->position().x),
			  .y = static_cast<int>(square->position().y),
			  .w = static_cast<int>(square->size().x),
			  .h = static_cast<int>(square->size().y) };
	SDL_RenderFillRect(gRenderer, &rect);
    }
    // Update the screen
    SDL_RenderPresent(gRenderer);
}


void update(void) {
    // Apply gravity
    gSquare->applyGravity(gWorld.gravity);
    // Apply air resistance to horizontal movement
    gSquare->applyAirResistance(gWorld.air_resistance);

    // Update position
    gSquare->updatePosition();

    // Handle collisions
    bool is_on_right_wall = (gSquare->position().x >= gScreenWidth - gSquare->size().x);
    bool is_on_left_wall = (gSquare->position().x <= 0);
    bool is_on_wall = (is_on_right_wall || is_on_left_wall);
    bool is_on_floor = (gSquare->position().y >= gScreenHeight - gSquare->size().y);
    bool is_on_ceiling = (gSquare->position().y <= 0);

    if (is_on_wall) {
	// Reset x on boundries
	if (is_on_left_wall) {
	    gSquare->setPosX(0);
	}
	if (is_on_right_wall) {
	    gSquare->setPosX(gScreenWidth - gSquare->size().x);
	}
	// Bounce off wall with some energy loss
	gSquare->dampX(gWorld.damping);
	// Change to random
	gSquare->setColor(get_random_color());
    }

    if (is_on_floor) {
	gSquare->setPosY(gScreenHeight - gSquare->size().y);
	// Only bounce if moving fast enough
	if (gSquare->velocity().y > 0.5) {
	    gSquare->dampY(gWorld.damping);
	    // Change to random color
	    gSquare->setColor(get_random_color());
	} else {
	    // Ground friction
	    gSquare->setVelocity({gSquare->velocity().x * 0.95, 0});
	}
    }
    if (is_on_ceiling) {
	// Bounce off the ceiling w/o loss
	gSquare->setPosY(0);
	gSquare->dampY(gWorld.damping);
	// Change to random color
	gSquare->setColor(get_random_color());
    }
}

void update_squares(void) {
    for (auto square : gSquares) {
	// Apply gravity
	square->applyGravity(gWorld.gravity);
	// Apply air resistance to horizontal movement
	square->applyAirResistance(gWorld.air_resistance);

	// Update position
	square->updatePosition();

	// Handle collisions
	bool is_on_right_wall = (square->position().x >= gScreenWidth - square->size().x);
	bool is_on_left_wall = (square->position().x <= 0);
	bool is_on_wall = (is_on_right_wall || is_on_left_wall);
	bool is_on_floor = (square->position().y >= gScreenHeight - square->size().y);
	bool is_on_ceiling = (square->position().y <= 0);

	if (is_on_wall) {
	    // Reset x on boundries
	    if (is_on_left_wall) {
		square->setPosX(0);
	    }
	    if (is_on_right_wall) {
		square->setPosX(gScreenWidth - square->size().x);
	    }
	    // Bounce off wall with some energy loss
	    square->dampX(gWorld.damping);
	    // Change to random
	    square->setColor(get_random_color());
	}

	if (is_on_floor) {
	    square->setPosY(gScreenHeight - square->size().y);
	    // Only bounce if moving fast enough
	    if (square->velocity().y > 0.5) {
		square->dampY(gWorld.damping);
		// Change to random color
		square->setColor(get_random_color());
	    } else {
		// Ground friction
		square->setVelocity({square->velocity().x * 0.95, 0});
	    }
	}
	if (is_on_ceiling) {
	    // Bounce off the ceiling w/o loss
	    square->setPosY(0);
	    square->dampY(gWorld.damping);
	    // Change to random color
	    square->setColor(get_random_color());
	}
    }
}

void close(void) {
    SDL_DestroyRenderer(gRenderer);
    SDL_DestroyWindow(gWindow);
    delete gSquare;
    SDL_Quit();    
}

void reinit_square(void) {
    delete gSquare;
    init_square();
}

void reinit_squares(void) {
    for (auto square : gSquares) {
	delete square;
    }
    gSquares.clear();
    init_squares();
}

int main(void)
{
    if (!init()) {
	return 1;
    }

    // Create an event handler and a quit flag
    SDL_Event e{};
    bool quit {false};

    //init_square();
    init_squares();
    // Main loop
    while (!quit) {
	// TODO: Add reset
	while (SDL_PollEvent(&e) != 0) {
	    if (e.type == SDL_QUIT) {
		quit = true;
	    } else if (e.type == SDL_KEYDOWN) {
		if (e.key.keysym.sym == SDLK_SPACE) {
		    reinit_squares();
		}
	    }
	}
	// draw();
	draw_squares();
	// update();
	update_squares();
	SDL_Delay(15);
    }
    close();
    return 0;
}
