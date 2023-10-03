{
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "nixpkgs";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";
  inputs.poetry2nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (poetry2nix.legacyPackages.${system}) mkPoetryApplication;

        pkgs = nixpkgs.legacyPackages.${system};

        poetryArgs = {
          projectDir = self;
          python = pkgs.python310;
        };

        nekontrol = mkPoetryApplication poetryArgs;
      in {
        packages.nekontrol = nekontrol;
        packages.default = nekontrol;
      });
}
