#-*- cmake -*-
# CMakeLists.txt for pip-installable LibRA Python package
# This builds LibRA synchronously and bundles everything into a Python wheel

cmake_minimum_required(VERSION 3.18)
project(libra-python
  DESCRIPTION "LibRA Python Package with bundled dependencies"
  HOMEPAGE_URL https://github.com/ARDG-NRAO/LibRA
  LANGUAGES CXX Fortran C)

set(CMAKE_CXX_STANDARD 17)

# Set up paths
set(LIBRA_ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/..)
set(LIBRA_INSTALL_DIR ${CMAKE_CURRENT_BINARY_DIR}/libra_install)

message(STATUS "LibRA Python: Root dir: ${LIBRA_ROOT_DIR}")
message(STATUS "LibRA Python: Install dir: ${LIBRA_INSTALL_DIR}")

# Create install directory
file(MAKE_DIRECTORY ${LIBRA_INSTALL_DIR})

# Get number of cores for parallel build
include(ProcessorCount)
ProcessorCount(NPROC)
if(NPROC EQUAL 0)
  set(NPROC 1)
endif()
message(STATUS "LibRA Python: Building with ${NPROC} cores")

# Find Python
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# Clean any existing build directory to avoid cache conflicts
if(EXISTS ${CMAKE_CURRENT_BINARY_DIR}/libra_build)
  message(STATUS "LibRA Python: Cleaning existing build directory...")
  file(REMOVE_RECURSE ${CMAKE_CURRENT_BINARY_DIR}/libra_build)
endif()

# Configure and build LibRA using execute_process (synchronous)
# This ensures everything builds in the correct order
message(STATUS "LibRA Python: Configuring LibRA...")

# Set GPU architecture - use auto-detection by default, fallback to PASCAL61
if(NOT DEFINED Kokkos_CUDA_ARCH_NAME OR "${Kokkos_CUDA_ARCH_NAME}" STREQUAL "")
  message(STATUS "LibRA Python: No GPU architecture specified, will auto-detect")
  set(CUDA_ARCH_ARG "")  # Let Kokkos auto-detect
else()
  message(STATUS "LibRA Python: Using specified GPU architecture: ${Kokkos_CUDA_ARCH_NAME}")
  set(CUDA_ARCH_ARG "-DKokkos_CUDA_ARCH_NAME=${Kokkos_CUDA_ARCH_NAME}")
endif()

# LIBRA_ENABLE_CUDA env var gates the nested LibRA build's CUDA backend.
# Without this, LIBRA_ENABLE_CUDA_BACKEND defaults ON (cmake/LibraConfig.cmake)
# regardless of the outer scikit-build-core Kokkos_ENABLE_CUDA setting, which
# nothing downstream reads.
if(DEFINED ENV{LIBRA_ENABLE_CUDA} AND "$ENV{LIBRA_ENABLE_CUDA}" STREQUAL "OFF")
  message(STATUS "LibRA Python: CUDA backend disabled via LIBRA_ENABLE_CUDA=OFF")
  set(CUDA_BACKEND_ARG "-DLIBRA_ENABLE_CUDA_BACKEND=OFF")
else()
  set(CUDA_BACKEND_ARG "-DLIBRA_ENABLE_CUDA_BACKEND=ON")
endif()

# Configure RPATH for Python extensions to find bundled libraries
# This ensures Python extensions (.so files) can find HPG libraries in _libs/
# and CUDA libraries from nvidia-cuda-runtime-cu12 pip package
message(STATUS "LibRA Python: Configuring RPATH for bundled libraries and nvidia pip packages")
set(CMAKE_INSTALL_RPATH "$ORIGIN/_libs:$ORIGIN/../nvidia/cuda_runtime/lib")
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH FALSE)

# We need to wait for Kokkos to build first to get the nvcc_wrapper
# But we can't do that with execute_process since it's all synchronous
# The main CMakeLists.txt should handle setting the compiler correctly after Kokkos builds

# Force the Unix Makefiles generator for the nested superbuild. scikit-build-core
# exports CMAKE_GENERATOR=Ninja into the environment; dependency ExternalProjects
# with a custom CONFIGURE_COMMAND (e.g. HPG) call bare cmake and would inherit
# Ninja, producing build.ninja while their hardcoded BUILD_COMMAND runs `make`.
execute_process(
  COMMAND ${CMAKE_COMMAND} -E env "CMAKE_GENERATOR=Unix Makefiles"
    ${CMAKE_COMMAND}
    -S ${LIBRA_ROOT_DIR}
    -B ${CMAKE_CURRENT_BINARY_DIR}/libra_build
    -DCMAKE_INSTALL_PREFIX=${LIBRA_INSTALL_DIR}
    -DCMAKE_BUILD_TYPE=Release
    -DApps_BUILD_TESTS=OFF
    -DCMAKE_CXX_STANDARD=17
    -DNCORES=${NPROC}
    ${CUDA_ARCH_ARG}
    ${CUDA_BACKEND_ARG}
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON
    -DCMAKE_INSTALL_RPATH="$ORIGIN/_libs:$ORIGIN/../nvidia/cuda_runtime/lib"
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=TRUE
    -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=FALSE
    -DCMAKE_SKIP_BUILD_RPATH=FALSE
    -DCMAKE_SKIP_INSTALL_RPATH=FALSE
    -G "Unix Makefiles"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  RESULT_VARIABLE CONFIGURE_RESULT
  OUTPUT_VARIABLE CONFIGURE_OUTPUT
  ERROR_VARIABLE CONFIGURE_ERROR
)

if(NOT CONFIGURE_RESULT EQUAL 0)
  message(FATAL_ERROR "LibRA configuration failed with code: ${CONFIGURE_RESULT}")
endif()

message(STATUS "LibRA Python: Building LibRA...")

execute_process(
  COMMAND ${CMAKE_COMMAND} -E env "CMAKE_GENERATOR=Unix Makefiles"
    ${CMAKE_COMMAND} --build ${CMAKE_CURRENT_BINARY_DIR}/libra_build --parallel ${NPROC}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  RESULT_VARIABLE BUILD_RESULT
)

if(NOT BUILD_RESULT EQUAL 0)
  message(FATAL_ERROR "LibRA build failed with code: ${BUILD_RESULT}")
endif()

message(STATUS "LibRA Python: Installing LibRA to ${LIBRA_INSTALL_DIR}...")

execute_process(
  COMMAND ${CMAKE_COMMAND} --install ${CMAKE_CURRENT_BINARY_DIR}/libra_build
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  RESULT_VARIABLE INSTALL_RESULT
)

if(NOT INSTALL_RESULT EQUAL 0)
  message(FATAL_ERROR "LibRA install failed with code: ${INSTALL_RESULT}")
endif()

message(STATUS "LibRA Python: LibRA install completed successfully")

# Now install everything to the Python package location
install(CODE "
  message(STATUS \"Installing LibRA Python package...\")
  
  # Verify LibRA was built successfully
  if(NOT EXISTS \"${LIBRA_INSTALL_DIR}\")
    message(FATAL_ERROR \"LibRA installation directory not found: ${LIBRA_INSTALL_DIR}\")
  endif()
  
  message(STATUS \"Found LibRA installation at ${LIBRA_INSTALL_DIR}\")

  # ExternalProjects install to fixed location
  set(ACTUAL_INSTALL_DIR \"${LIBRA_ROOT_DIR}/install\")
  
  # Install all shared libraries to _libs (including symlinks)
  file(GLOB LIBRA_LIBS \"\${ACTUAL_INSTALL_DIR}/lib/*.so*\")
  if(LIBRA_LIBS)
    file(MAKE_DIRECTORY \${CMAKE_INSTALL_PREFIX}/_libs)
    foreach(lib \${LIBRA_LIBS})
      get_filename_component(lib_name \${lib} NAME)
      message(STATUS \"Installing library: \${lib_name}\")
      file(INSTALL \${lib} DESTINATION \${CMAKE_INSTALL_PREFIX}/_libs
           FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
                            GROUP_READ GROUP_EXECUTE
                            WORLD_READ WORLD_EXECUTE)
      # Fix RPATH for real files only (not symlinks)
      if(NOT IS_SYMLINK \${lib})
        find_program(PATCHELF_EXECUTABLE patchelf)
        if(PATCHELF_EXECUTABLE)
          execute_process(
            COMMAND \${PATCHELF_EXECUTABLE} --set-rpath \"$ORIGIN:$ORIGIN/../../nvidia/cuda_runtime/lib\" \${CMAKE_INSTALL_PREFIX}/_libs/\${lib_name}
            RESULT_VARIABLE PATCHELF_RESULT
            OUTPUT_QUIET ERROR_QUIET
          )
          if(PATCHELF_RESULT EQUAL 0)
            message(STATUS \"  Fixed RPATH for \${lib_name}\")
          endif()
        endif()
      endif()
    endforeach()
    message(STATUS \"Installed shared libraries\")
  else()
    message(WARNING \"No shared libraries found in \${ACTUAL_INSTALL_DIR}/lib\")
  endif()
  
  # Install Python extension modules directly to package root
  file(GLOB PYTHON_MODULES \"\${ACTUAL_INSTALL_DIR}/lib/*2py*.so\")
  if(PYTHON_MODULES)
    foreach(module \${PYTHON_MODULES})
      get_filename_component(module_name \${module} NAME)
      message(STATUS \"Installing Python module: \${module_name}\")
      file(INSTALL \${module} DESTINATION \${CMAKE_INSTALL_PREFIX}
           FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
                            GROUP_READ GROUP_EXECUTE
                            WORLD_READ WORLD_EXECUTE)
      # Fix RPATH for Python extensions
      find_program(PATCHELF_EXECUTABLE patchelf)
      if(PATCHELF_EXECUTABLE)
        execute_process(
          COMMAND \${PATCHELF_EXECUTABLE} --set-rpath \"$ORIGIN/_libs:$ORIGIN/../nvidia/cuda_runtime/lib\" \${CMAKE_INSTALL_PREFIX}/\${module_name}
          RESULT_VARIABLE PATCHELF_RESULT
          OUTPUT_QUIET ERROR_QUIET
        )
        if(PATCHELF_RESULT EQUAL 0)
          message(STATUS \"  Fixed RPATH for \${module_name}\")
        endif()
      endif()
    endforeach()
    message(STATUS \"Installed Python modules\")
  else()
    message(WARNING \"No Python modules found in \${ACTUAL_INSTALL_DIR}/lib\")
  endif()
  
  # Install headers for development
  if(EXISTS \"\${ACTUAL_INSTALL_DIR}/include\")
    message(STATUS \"Installing headers\")
    file(MAKE_DIRECTORY \${CMAKE_INSTALL_PREFIX}/_include)
    file(INSTALL \"\${ACTUAL_INSTALL_DIR}/include/\" DESTINATION \${CMAKE_INSTALL_PREFIX}/_include)
  endif()

  # Install data files
  if(EXISTS \"\${ACTUAL_INSTALL_DIR}/data\")
    message(STATUS \"Installing data files\")
    file(MAKE_DIRECTORY \${CMAKE_INSTALL_PREFIX}/_data)
    file(INSTALL \"\${ACTUAL_INSTALL_DIR}/data/\" DESTINATION \${CMAKE_INSTALL_PREFIX}/_data)
  endif()

  # Install executables
  if(EXISTS \"\${ACTUAL_INSTALL_DIR}/bin\")
    message(STATUS \"Installing executables\")
    file(MAKE_DIRECTORY \${CMAKE_INSTALL_PREFIX}/_bin)
    # CMP0009 NEW: do not follow symlinked directories (e.g. a stray bin/X11
    # link to /bin) -- OLD default would recurse into the host filesystem.
    cmake_policy(SET CMP0009 NEW)
    file(GLOB_RECURSE LIBRA_BINS \"\${ACTUAL_INSTALL_DIR}/bin/*\")
    foreach(bin \${LIBRA_BINS})
      if(NOT IS_DIRECTORY \${bin})
        get_filename_component(bin_name \${bin} NAME)
        message(STATUS \"Installing executable: \${bin_name}\")
        file(INSTALL \${bin} DESTINATION \${CMAKE_INSTALL_PREFIX}/_bin
             FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
                              GROUP_READ GROUP_EXECUTE
                              WORLD_READ WORLD_EXECUTE)
      endif()
    endforeach()
  endif()
  
  message(STATUS \"LibRA Python package installation complete\")
")

# Create a dummy target to satisfy scikit-build-core
add_custom_target(libra_python_dummy ALL
  COMMAND ${CMAKE_COMMAND} -E echo "LibRA Python package prepared"
  COMMENT "LibRA Python package build completed"
)