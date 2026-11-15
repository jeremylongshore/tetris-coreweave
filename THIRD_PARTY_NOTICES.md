# Third-party notices

## Tetris Gymnasium

The starter installs `tetris-gymnasium==0.3.1` as an external dependency and uses its classic NumPy backend. The package is MIT licensed. Its license is reproduced in `licenses/tetris-gymnasium-MIT.txt` for reference; the original package retains its notices.

- Upstream: https://github.com/Max-We/Tetris-Gymnasium
- Package: https://pypi.org/project/tetris-gymnasium/0.3.1/
- License: https://github.com/Max-We/Tetris-Gymnasium/blob/main/LICENSE

No commercial ROM, emulator game dump, or commercial Tetris client is included.

## Other runtime dependencies

NumPy, Gymnasium, OpenCV, and PyTorch are installed separately under their respective licenses. This source repository does not vendor their distributions. Consult the license metadata in the exact packages or provider image used for the run before redistributing a runtime/container.

## Planned chess episode

The [Lichess database](https://database.lichess.org/) publishes game exports under CC0. Filter human standard-chess games and strip annotations before training. `python-chess` is GPL-3.0-or-later; Stockfish is GPLv3. They are not included in this starter. Review redistribution/linking obligations before adding them or distributing a chess runtime. Keep evaluation engine output out of the training data.
