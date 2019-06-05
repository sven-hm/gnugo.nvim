if exists("b:current_syntax")
  finish
endif

syn match GnugoInfoBlack "black"
syn match GnugoInfoWhite "white"
syn match GnugoInfoBlack "X"
syn match GnugoInfoWhite "O"

hi GnugoInfoBlack
      \ ctermbg=Black ctermfg=White
      \ guibg=Black guifg=White
hi GnugoInfoWhite
      \ ctermbg=White ctermfg=Black
      \ guibg=White guifg=Black

let b:current_syntax = "gnugoinfo"
