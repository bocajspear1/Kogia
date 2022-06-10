#!/bin/bash

cp /opt/test.x86.exe /root/.wine/drive_c/autoit.x86.exe 
cp /opt/autoit.au3 /root/.wine/drive_c/autoit.au3 

# nohup /usr/bin/Xvfb :0 -screen 0 1024x768x8 &
Xspice --port 5900 --password password --auto -logfile /Xspice.log :1.0 &
sleep 2
DISPLAY=:1.0 wine /root/.wine/drive_c/autoit/Aut2exe/Aut2exe.exe /in /root/.wine/drive_c/autoit.au3 /out /root/.wine/drive_c/autoit.x86-packed.exe /comp 2 /nopack
ls -lah /root/.wine/drive_c/
mv /root/.wine/drive_c/autoit.x86-packed.exe /tmp/out/autoit.x86-packed.exe

cp /opt/test.x86.exe /root/.wine/drive_c/petite.x86.exe 

# Petite packer
DISPLAY=:1.0 wine /root/.wine/drive_c/petite.exe /root/.wine/drive_c/petite.x86.exe -2 -v0 -o/root/.wine/drive_c/petite.x86-packed.exe 
ls -lah /root/.wine/drive_c/
mv /root/.wine/drive_c/petite.x86-packed.exe /tmp/out/petite.x86-packed.exe



# exit 1