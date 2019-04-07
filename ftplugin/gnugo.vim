if exists("b:did_ftplugin")
  finish
endif

" placing stones
noremap <buffer> <Enter> :GnugoPlay<CR>
noremap <buffer> <2-LeftMouse> :GnugoPlay<CR>

" undo move TODO

" move cursor
nnoremap <buffer> k         :GnugoCursorUp<CR>
nnoremap <buffer> j         :GnugoCursorDown<CR>
nnoremap <buffer> h         :GnugoCursorLeft<CR>
nnoremap <buffer> l         :GnugoCursorRight<CR>

nnoremap <buffer> <Up>      :GnugoCursorUp<CR>
nnoremap <buffer> <Down>    :GnugoCursorDown<CR>
nnoremap <buffer> <Left>    :GnugoCursorLeft<CR>
nnoremap <buffer> <Right>   :GnugoCursorRight<CR>

" move cursor in big jumps
nnoremap <buffer> K         :GnugoCursorUp 6<CR>
nnoremap <buffer> J         :GnugoCursorDown 6<CR>
nnoremap <buffer> H         :GnugoCursorLeft 6<CR>
nnoremap <buffer> L         :GnugoCursorRight 6<CR>

" disable other movement
nnoremap <buffer> e         :echo "disabled"<CR>
nnoremap <buffer> w         :echo "disabled"<CR>
nnoremap <buffer> b         :echo "disabled"<CR>
nnoremap <buffer> E         :echo "disabled"<CR>
nnoremap <buffer> W         :echo "disabled"<CR>
nnoremap <buffer> B         :echo "disabled"<CR>

" info board
"function GnugoInfoBoardToggle()
"    if len(bufname("GnuGoInfo")) > 0
"        buffer GnuGoInfo
"    else
"        GnugoInfoBoard
"    endif
"endfunction
"
"nnoremap <buffer> i         :call GnugoInfoBoardToggle()<CR>

let b:did_ftplugin = 1
