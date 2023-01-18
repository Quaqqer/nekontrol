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

        kattest = (pkgs.callPackage ({ python310, installShellFiles }:
          python310.pkgs.buildPythonApplication rec {
            pname = "kattest";
            version = "0.1.0";

            src = ./.;

            nativeBuildInputs = [ installShellFiles ];

            propagatedBuildInputs = pythonDeps python310.pkgs;
            postInstall = ''
              installShellCompletion --cmd kattest \
                --bash <(_KATTEST_COMPLETE=bash_source $out/bin/kattest) \
                --zsh <(_KATTEST_COMPLETE=zsh_source $out/bin/kattest) \
                --fish <(_KATTEST_COMPLETE=fish_source $out/bin/kattest) \
            '';
          }) { });
      in {
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = [ pkgs.bashInteractive ];
          buildInputs = with pkgs; [
            (python310.withPackages pythonDeps)

            kattest
          ];
        };

        packages.default = kattest;
        packages.kattest = kattest;
      });
}
