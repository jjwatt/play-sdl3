import ctypes
import sdl3

@sdl3.SDL_main_func
def main(
        argc: ctypes.c_int,
        argv: sdl3.LP_c_char_p
) -> ctypes.c_int:
    print("Hello from play-sdl3!")
    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO | sdl3.SDL_INIT_EVENTS):
        print(f"Failed to initialize: {sdl3.SDL_GetError().decode()}")
        return -1
    if not (window := sdl3.SDL_CreateWindow(
        "Test".encode(),
        1600,
        900,
        sdl3.SDL_WINDOW_RESIZABLE
    )):
        print(f"Failed to create window: {sdl3.SDL_GetError().decode()}.")
        return -1
    render_drivers = [sdl3.SDL_GetRenderDriver(i).decode()
                     for i in range(sdl3.SDL_GetNumRenderDrivers())]
    try_get_driver, try_use_vulkan = lambda order, drivers: next((i for i in order if i in drivers), None), False
    render_driver = try_get_driver(
        (["vulkan"] if try_use_vulkan else []) + ["opengl", "software"], render_drivers
    )
    print(f"Available render drivers: {', '.join(render_drivers)} (current: {render_driver}).")
    if not (renderer := sdl3.SDL_CreateRenderer(window,
                                                render_driver.encode())):
        print(f"Failed to create renderer: {sdl3.SDL_GetError().decode()}.")
        return -1

    event, running = sdl3.SDL_Event(), True
    while running:
        while sdl3.SDL_PollEvent(ctypes.byref(event)):
            match event.type:
                case sdl3.SDL_EVENT_QUIT:
                    running = False
                case sdl3.SDL_EVENT_KEY_DOWN:
                    if event.key.key in [sdl3.SDLK_ESCAPE]:
                        running = False

    width, height = ctypes.c_int(), ctypes.c_int()
    sdl3.SDL_GetWindowSize(window, width, height)
    sdl3.SDL_RenderClear(renderer)
    sdl3.SDL_DestroyRenderer(renderer)
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()
