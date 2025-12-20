cmake_minimum_required(VERSION 3.20)
project(interessence_runtime LANGUAGES CXX)

option(INTERESSENCE_ENABLE_JSON "Enable nlohmann_json parsing support" ON)
option(INTERESSENCE_FETCH_JSON "Fetch nlohmann_json if not found" ON)
option(INTERESSENCE_ENABLE_VIEWER "Build raylib viewer" ON)
option(INTERESSENCE_FETCH_RAYLIB "Fetch raylib if not found" ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(interessence_runtime
    src/Loader.cpp
    src/Runtime.cpp
    src/Neo.cpp
)

target_include_directories(interessence_runtime
    PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

if(INTERESSENCE_ENABLE_JSON)
    find_package(nlohmann_json CONFIG QUIET)
    if(NOT nlohmann_json_FOUND AND INTERESSENCE_FETCH_JSON)
        include(FetchContent)
        FetchContent_Declare(
            nlohmann_json
            URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
        )
        FetchContent_MakeAvailable(nlohmann_json)
    endif()
    if(nlohmann_json_FOUND OR TARGET nlohmann_json::nlohmann_json)
        target_link_libraries(interessence_runtime PRIVATE nlohmann_json::nlohmann_json)
        target_compile_definitions(interessence_runtime PRIVATE INTERESSENCE_ENABLE_JSON)
    else()
        message(WARNING "nlohmann_json not found; JSON loader will be disabled.")
    endif()
endif()

target_compile_features(interessence_runtime PUBLIC cxx_std_17)

add_library(Interessence::runtime ALIAS interessence_runtime)

# Demo executable (optional)
add_executable(interessence_demo src/Demo.cpp)
target_link_libraries(interessence_demo PRIVATE interessence_runtime)
if(INTERESSENCE_ENABLE_JSON AND (nlohmann_json_FOUND OR TARGET nlohmann_json::nlohmann_json))
    target_compile_definitions(interessence_demo PRIVATE INTERESSENCE_ENABLE_JSON)
endif()

# Viewer (raylib)
if(INTERESSENCE_ENABLE_VIEWER)
    find_package(raylib CONFIG QUIET)
    if(NOT raylib_FOUND AND INTERESSENCE_FETCH_RAYLIB)
        include(FetchContent)
        FetchContent_Declare(
            raylib
            GIT_REPOSITORY https://github.com/raysan5/raylib.git
            GIT_TAG 5.5
            GIT_SHALLOW TRUE
        )
        set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
        FetchContent_MakeAvailable(raylib)
    endif()
    if(raylib_FOUND OR TARGET raylib)
        add_executable(interessence_viewer src/Viewer.cpp)
        target_link_libraries(interessence_viewer PRIVATE interessence_runtime raylib)
        if(INTERESSENCE_ENABLE_JSON AND (nlohmann_json_FOUND OR TARGET nlohmann_json::nlohmann_json))
            target_compile_definitions(interessence_viewer PRIVATE INTERESSENCE_ENABLE_JSON)
        endif()
    else()
        message(WARNING "raylib not found; viewer will not be built.")
    endif()
endif()

if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
    enable_testing()
endif()
