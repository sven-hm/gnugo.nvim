if exists("b:current_syntax")
  finish
endif

syn match GnugoInfoBusy "busy"
syn match GnugoInfoBlack "black"
syn match GnugoInfoWhite "white"
syn match GnugoInfoBlack "X"
syn match GnugoInfoWhite "O"

hi GnugoInfoBusy
      \ ctermbg=Red ctermfg=Black
      \ guibg=Red guifg=Black
hi GnugoInfoBlack
      \ ctermbg=Black ctermfg=White
      \ guibg=Black guifg=White
hi GnugoInfoWhite
      \ ctermbg=White ctermfg=Black
      \ guibg=White guifg=Black

let b:current_syntax = "gnugoinfo"
