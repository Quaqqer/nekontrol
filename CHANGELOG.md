# 0.2.1

- Fix cpp_libs_dir in config being ignored

# 0.2.0

- Rework code to be cleaner
- Add a stopwatch to time how long it took to run
- Add support for lua and javascript (node)

# 0.1.7

- Run with multiple python versions

# 0.1.6

- Allow for disabling diff, showing only the normal output
- Add support for a config file

# 0.1.5

- Bugfix: No output nor input is shown when running without an ans-file
- Bugfix: No local test data is found when running outside of cwd

# 0.1.4

- Bump version number because pypi is annoying

# 0.1.3

- Use poetry instead of setuptools

# 0.1.2

- Ignore inline debug "(dbg...)" or "(debug...)"
- Use pyproject.toml instead of setup.py
- Add flake8 configuration
- Print text if exit code was non-zero
- Print runtime error stream if exit code was non-zero
- Bugfix: Fix stuck when compiling with large outputs because it can't flush
- Bugfix: Store in correct cache directory

# 0.1.1

- Ignore debug lines (lines starting with debug or dbg)

# 0.1.0

- Initial version
