#!/bin/sh
mkdir -p out

rm mimikatz_trunk.zip
wget https://github.com/gentilkiwi/mimikatz/releases/download/2.2.0-20220919/mimikatz_trunk.zip -O mimikatz_trunk.zip
unzip mimikatz_trunk.zip -d mimikatz
mv mimikatz/x64/mimikatz.exe mimikatz-64.exe
mv mimikatz/Win32/mimikatz.exe mimikatz-32.exe
zip -P infected out/mimikatz-32.exe.zip mimikatz-32.exe
zip -P infected out/mimikatz-64.exe.zip mimikatz-64.exe
rm mimikatz-64.exe
rm mimikatz-32.exe
rm -rf mimikatz/
rm mimikatz_trunk.zip


# curl -XPOST -A'Firefox' -d 'download=AdFind.zip&email=&B1=Download+Now' https://www.joeware.net/downloads/dl2.php -o AdFind.zip
unzip AdFind.zip -d out