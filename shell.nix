{ pkgs ? import <nixpkgs> { } }:
let
  nekontrolEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    editablePackageSources = { nekontrol = ./src; };
  };
in nekontrolEnv.env.overrideAttrs (oldAttrs: { buildInputs = [ pkgs.poetry ]; })
