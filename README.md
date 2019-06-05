# gnugo.nvim

This is a neovim-plugin to play Go from within neovim. If you are using vim but not neovim have a look [here](https://github.com/AndrewRadev/gnugo.vim).


## Requirements

* [neovim](https://neovim.io/)
* [gnugo](https://www.gnu.org/software/gnugo/)
* python3
* [python3 neovim package](https://pypi.org/project/neovim/)
* [pygnugo](https://github.com/sven-hm/pygnugo.git)


## Install

With [vim-plug](https://github.com/junegunn/vim-plug) just add the following line into your `init.vim`:
```vim
Plug 'sven-hm/gnugo.nvim'
```
In vim you have to update the remote plugins:
```
:UpdateRemotePlugins
```
That's all.


## Usage

To start type `:GnugoNew black` if you want to play the black stones otherwise type `:GnugoNew white`.
The key bindings are:

| keys             | Action               | pygnugo command  |
|------------------|----------------------|------------------|
| ←, h, (H)        | move cursor (fast)   | GnugoCursorLeft  |
| ↓, j, (J)        | move cursor (fast)   | GnugoCursorDown  |
| ↑, k, (K)        | move cursor (fast)   | GnugoCursorUp    |
| →, l, (L)        | move cursor (fast)   | GnugoCursorRight |
| `<enter>`        | play cursor position | GnugoPlay        |
| `<double-click>` | play cursor position | GnugoPlay        |
| c                | cheat                | GnugoQuit        |
| u                | undo                 | GnugoUndo        |
| q                | quit                 | GnugoCheat       |


## To do

* Load from and save to `sgf`-file.
* Allow other board sizes.
* Complete README.
