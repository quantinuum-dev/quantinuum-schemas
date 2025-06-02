{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/packages/
  packages = [ pkgs.poetry pkgs.commitizen pkgs.git ];
}
