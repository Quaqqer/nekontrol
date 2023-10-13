{ pkgs ? import <nixpkgs> { } }:
let
  nekontrolEnv = pkgs.poetry2nix.mkPoetryEnv {
    python = pkgs.python311;
    projectDir = ./.;
    editablePackageSources = { nekontrol = ./src; };
  };
in nekontrolEnv.env.overrideAttrs (oldAttrs: { buildInputs = [ pkgs.poetry ]; })
