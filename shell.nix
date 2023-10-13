{ pkgs ? import <nixpkgs> { } }:
let
  nekontrolEnv = pkgs.poetry2nix.mkPoetryEnv {
    python = pkgs.python311;
    projectDir = ./.;
    editablePackageSources = { nekontrol = ./src; };
  };

  test_langs = [ pkgs.lua pkgs.nodejs pkgs.rustc pkgs.gcc pkgs.ghc pkgs.pypy38 ];
in nekontrolEnv.env.overrideAttrs
(oldAttrs: { buildInputs = [ pkgs.poetry ] ++ test_langs; })
