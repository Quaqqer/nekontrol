# kattest - A kattis solution tester

This is a simple that program that aims to compile and run kattis problems and
tests them with both local and given input and output. It also works with input
files without a corresponding output file, but then it can obviously not verify
if the output is correct.

## Demo

### Successful run

![Demo of a succesful run](./res/demo1.svg)

### Incorrect output

![Demo of an unsuccessful run](./res/demo2.svg)

## Features

- Automatically downloads sample input and output
- Automatically compiles your source code and runs it with custom and sample
  input and output

The current supported languages are:

- C++
- Rust
- Python
- Haskell

Adding more languages are left as an exercise for the reader.

## Usage

Simply run `kattest <source file>` and it should hopefully compile (if needed)
and run!

- `kattest` assumes that the name of the source files matches the name of the
  problem (found in the url, ex. https://open.kattis.com/problems/<b>hello</b>).
  If this assumption is incorrect, you can specify the problem with
  `--problem <problem name>`. Local files are still matched with the filename
  regardless of the problem specified.
- Input and output files should follow the format `<filename>.in` or
  `<filename>.<number>.in` and corresponding outputs are named `<filename>.ans`
  etc. where `<filename>` comes from `kattest <filename>.cpp` for instance.

> **Note**
> Multiple support files are not supported as of yet

## Installation

```sh
git clone https://github.com/Quaqqer/kattest.git
cd kattest
pip install .
```

Now it should hopefully work, enjoy!

### Nix

There is also a flake for Nix users, but if you use Nix I trust you know how to
use flakes.
