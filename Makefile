#NAME: Cao Xu
#EMAIL: cxcharlie@gmail.com
#ID: 704551688

default: lab3b.py
	rm -f lab3b
	ln lab3b.py lab3b
	chmod +x lab3b

dist: default
	tar -czvf lab3b-704551688.tar.gz lab3b.py Makefile README

clean: 
	rm -f lab3b lab3b-704551688.tar.gz


