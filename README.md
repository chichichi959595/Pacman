# Pacman in Python with PyGame

This project is a small Pacman-style game built with `pygame`.

## Main Entry

Run the current version with:

```powershell
python pacman.py
```

`pacman.py` is the maintained entry point. `pacman修改.py` and `增加道具` are older or experimental copies kept in the repository for reference.

## Current Features

- One maze level with pellets
- Four starting ghosts, with more ghosts added over time
- Bombs using Left Ctrl
- Star power-up for temporary invincibility
- Ice power-up for temporary ghost freeze
- Sound effects and background music
- Restart screen after winning or losing

## Assets

Images live in `images/`, sounds live in `sounds/`, and `freesansbold.ttf` is included for font support.

## Notes

The game now resolves assets relative to the project folder, so it can be launched from another working directory without losing images or sounds.
