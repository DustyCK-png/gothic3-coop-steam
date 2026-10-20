cmake_minimum_required(VERSION 3.24)
project(Gothic3CoopSteam LANGUAGES C CXX)
set(G3SDK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vendor/gothic3sdk" CACHE PATH "Pinned unofficial Gothic 3 SDK")
add_subdirectory(vendor/g3-together)
