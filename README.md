Furiganize
==========

Furiganize is furigana (Japanese phonetic symbols) insertion macro for LibreOffice  
(should work in OpenOffice too, but I did not check)

It is written in Python and uses mecab and kakasi installed system-wide<br/>
It makes things easier for Linux users, you just need to install kakasi, mecab and mecab-naist-jdic-eucjp packages,<br/>
they are usually available form standard repositories.
Then copy macro to your LibreOffice script path,
something like  ~/.config/libreoffice/4/user/Scripts/python 
(libreoffice-script-provider-python package should be installed to enable Python macros in LibreOffice)
select you Japanese text and run macro.

In case of Windows it might be a little bit more complicated, 
you also need to install mecab and kakasi and make sure they are included in %PATH%.<br/>
The other option is to put executables and dictionary files alongside with the macro<br/>
and change couple of line in it to indicate where the files are.<br/>
Please contact me if you are in trouble. <br/>
Enjoy :) <br/>

p.s.<br/>
Suggested reading might not always be 100% correct, but it's more due to the limitations of mecab, rather than the macro. <br/>
Furigana is inserted as "ruby text", to edit it go to main menu -> Format -> Asian phonetic guide

