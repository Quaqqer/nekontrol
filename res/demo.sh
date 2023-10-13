#doitlive prompt: {user.green}@{hostname.blue} {dir.yellow} %

# Run with:
# nix shell nixos#doitlive nixos#asciinema nixos#pypy3
# (cd examples && asciinema rec --overwrite --cols 100 --rows 25 -c 'doitlive play ../demo.sh -q' ../demo.cast && cd .. && svg-term --in demo.cast --out demo.svg --window --padding-x 1)

#doitlive commentecho: true
#doitlive alias: ls=eza

ls -l

nk test correct.py

nk test c++.cc

nk test incorrect.py

nk test error.py

nk test twostones.py

nk test compile_error.cc
