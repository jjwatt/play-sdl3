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
    window = sdl3.SDL_CreateWindow(
        "Test".encode(),
        800,
        600,
        sdl3.SDL_WINDOW_RESIZABLE
    )
    if not window:
        print(f"Failed to create window: {sdl3.SDL_GetError().decode()}")
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
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()
