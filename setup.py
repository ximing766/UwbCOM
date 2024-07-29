from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": [], "excludes": []}

# Replace "myapp.py" with the name of your script
setup(
    name="Uwb-COM",
    version="0.1",
    description="My great application!",
    options={"build_exe": build_exe_options},
    executables=[Executable("UwbCOM.py",base=None)],
)