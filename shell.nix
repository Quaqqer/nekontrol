{ pkgs ? import <nixpkgs> { } }:
let
  nekontrolEnv = pkgs.poetry2nix.mkPoetryEnv {
    python = pkgs.python311;
    pyproject = ./pyproject.toml;
    poetrylock = ./poetry.lock;
    editablePackageSources = { nekontrol = ./src; };
    checkGroups = [ ];
    groups = [ ];
  };

  test_langs =
    [ pkgs.lua pkgs.nodejs pkgs.rustc pkgs.gcc pkgs.ghc pkgs.pypy39 ];
in nekontrolEnv.env.overrideAttrs
(oldAttrs: { buildInputs = [ pkgs.poetry ] ++ test_langs; })
