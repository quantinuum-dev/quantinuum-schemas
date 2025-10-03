{ pkgs, lib, config, inputs, ... }:
let
  pkgs-unstable = import inputs.nixpkgs-unstable { system = pkgs.stdenv.system; };
in
{
  # https://devenv.sh/packages/
  packages = [ 
    pkgs-unstable.uv
    pkgs.commitizen 
    pkgs.git 
  ];

  dotenv.enable = true;
}
