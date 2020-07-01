with import <nixpkgs> {};
with pkgs.python36Packages;

stdenv.mkDerivation {
  name = "impurePythonEnv";
  buildInputs = [
    # install python, virtualenv, and pip:
    python36Full
    python36Packages.virtualenv
    python36Packages.setuptools

    freetype
    git
    openssl
    libpng12
    libzip
    lxml
    stdenv
    taglib
    zlib
    # ide stuff
    python36Packages.jedi
    python36Packages.importmagic
    python36Packages.autopep8
    python36Packages.flake8
    python36Packages.pyflakes
  ];
  src = null;
  shellHook = ''
    ## set SOURCE_DATE_EPOCH so that we can use python wheels
    SOURCE_DATE_EPOCH=$(date +%s)

    ## Install the project, if not installed yet.
    if [ ! -d ./_virtualenv ]; then
      ./install.sh >&2
    fi

    source $PWD/_virtualenv/bin/activate
  '';
}
