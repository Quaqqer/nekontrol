{
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "nixpkgs";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pythonDeps = pyPkgs: [
          pyPkgs.click
          pyPkgs.termcolor
          pyPkgs.requests
          pyPkgs.appdirs
          pyPkgs.natsort
        ];

        nekontrol = (pkgs.callPackage ({ python310, installShellFiles }:
          python310.pkgs.buildPythonApplication rec {
            pname = "nekontrol";
            version = "0.1.0";

            src = ./.;

            nativeBuildInputs = [ installShellFiles ];

            propagatedBuildInputs = pythonDeps python310.pkgs;
            postInstall = ''
              installShellCompletion --cmd nekontrol \
                --bash <(_NEKONTROL_COMPLETE=bash_source $out/bin/nekontrol) \
                --zsh <(_NEKONTROL_COMPLETE=zsh_source $out/bin/nekontrol) \
                --fish <(_NEKONTROL_COMPLETE=fish_source $out/bin/nekontrol) \
            '';
          }) { });
      in {
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = [ pkgs.bashInteractive ];
          buildInputs = with pkgs; [
            (python310.withPackages pythonDeps)

            nekontrol
          ];
        };

        packages.default = nekontrol;
        packages.nekontrol = nekontrol;
      });
}
