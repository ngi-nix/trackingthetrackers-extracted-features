{
  description = "The framework for the raw extracted features we are exploring.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    mach-nix-src.url = "github:DavHau/mach-nix";
  };

  outputs = { self, nixpkgs, flake-utils, mach-nix-src }:
    flake-utils.lib.eachDefaultSystem (
      system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          mach-nix = import mach-nix-src { inherit pkgs; python = "python38"; };

          pyEnv = mach-nix.mkPython rec {
            requirements = ''
              pandas
              fastai
              bs4
              androguard
            '';
          };
        in
          {
            # defaultPackage = self.packages.${system}.${pname};
            packages = { inherit pkgs; };
            devShell = mach-nix.nixpkgs.mkShell {
              buildInputs = with pkgs; [ pyEnv fdroidserver ];
            };
          }
    );
}
