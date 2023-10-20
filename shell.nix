{ pkgs ? import <nixpkgs> { } }:
let
  nekontrolEnv = pkgs.poetry2nix.mkPoetryEnv {
    python = pkgs.python311;
    pyproject = ./pyproject.toml;
    poetrylock = ./poetry.lock;
    editablePackageSources = { nekontrol = ./src; };

    # `pyright` in this shell will not find packages, run `poetry run pyright` instead
    # If using neovim and lspconfig, add this to an exrc:
    # ```py
    # require('lspconfig').pyright.setup({ cmd = { 'poetry', 'run', 'pyright-langserver', '--stdio' } })
    # ```
    checkGroups = [ "dev" ];
    groups = [ "dev" ];
  };

  test_langs =
    [ pkgs.lua pkgs.nodejs pkgs.rustc pkgs.gcc pkgs.ghc pkgs.pypy39 ];
in nekontrolEnv.env.overrideAttrs
(oldAttrs: { buildInputs = [ pkgs.poetry ] ++ test_langs; })
