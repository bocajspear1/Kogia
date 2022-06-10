all:
	cp /opt/test.x86.exe /tmp/out/upx.x86-packed.exe && upx /tmp/out/upx.x86-packed.exe
	cp /opt/test.x86-64.exe /tmp/out/upx.x86-64-packed.exe && upx /tmp/out/upx.x86-64-packed.exe

	cp /opt/test.x86-64.exe /tmp/out/amber.x86-64.exe && ./amber/amber -f /tmp/out/amber.x86-64.exe -b 