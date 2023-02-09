# nekontrol - Control your kattis solutions

This is a simple program that compiles, runs and tests your kattis solutions
against local and sample input and output.

## Demo

![Demo](https://raw.githubusercontent.com/Quaqqer/nekontrol/main/res/demo.svg)

## Features

- Automatically downloads sample input and output
- Discovers local sample input and output
- Compiles your source code and runs it with local and sample input and output
- Ignores debug messages - ignores lines starting with "dbg" or "debug" and
  inline messages "(dbg...)" and "(debug...)". If debug lines are discovered
  then you are notified in the output so that you don't submit something that is
  incorrect.

The current supported languages are:

- C++ (requires `c++` in your path)
- Rust (requirest `rustc` in your path)
- Python (requires python in your path)
- Haskell (requires `ghc` in your path)
- Lua (requires `lua` in your path)
- JavaScript (Node) (requires `node` in your path)

> **Note**
> Nekontrol will try to find a way to run your program, but it is not guranteed
> that the program it uses matches the version that kattis has. For instance
> kattis runs python with pypy 3.8. Nekontrol will try to run it with pypy 3.8,
> but will fall back to other versions if it cannot be found.

Adding more languages is left as an exercise for the reader.

## Usage

Simply run `nk <source file>` and it should hopefully compile (if needed)
and run!

- `nk` assumes that the name of the source files matches the name of the
  problem (found in the url, ex. https://open.kattis.com/problems/<b>hello</b>).
  If this assumption is incorrect, you can specify the problem with
  `--problem <problem name>`. Local files are still matched with the filename
  regardless of the problem specified.
- Input and output files should follow the format `<filename>.in` or
  `<filename>.<number>.in` and corresponding outputs are named `<filename>.ans`
  etc. where `<filename>` comes from `nk <filename>.cpp` for instance.

> **Note**
> Multiple files are not supported as of yet

## Requirements

- The requirements of this program is only having python 3.10 or newer as well
  pip
- A half decent terminal, almost anything other than cmd.exe on windows will
  work

## Install or update

To install or update, run the following.

```sh
pip install -U nekontrol
```

Now it should hopefully work, enjoy!

### Nix

There is a flake for Nix users, but if you use Nix I trust you know how to use
flakes.

## Other

- If you are thinking "nekontrol is a kinda weeby name", I ask you: have you
  ever tried coming up with an original name?
