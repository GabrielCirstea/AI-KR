# Problema blocurilor

Avem 3 tipuri de blocuri

* cub
* sfera - trebuie sa aibe in stanga si in dreapta alta piesa
* piramida -  nimic nu se pune pe piramida

Detalii despre euristici in [Euristici.md](Euristici.md)

## Apelare

programul primeste ca parametrii

* folderul cu fisierele de input
	* if=<nume>
	* daca numele contine spatii se folosesc ' " '(ghilimele)
* folderul in care se pun fisierele de output
	* of=<nume>
	* daca numele contine spatii se folosesc ' " '(ghilimele)
* numarul de solutii cautate
	* n=<nr>
* timeout-ul
	* t=<sec>

ex:
```
./main.py if=input of=output n=3 t=10
```

Acesta este echivalent cu valorile implicite pe care le foloseste programul

Argumentele nu trebuiesc puse in aceasta ordine

## Cod

### optine_stive

Parseaza un string pentru a extrage informatiile

* pe prima linie ar trebui sa avem nr de stive goale pe care il vrem
* apoi pentru fiecare linie:
	* daca apare '#', este o stiva goala
	* altfem spargem linia dupa ','
* pentru fiecare lista optinuta din spargerea dupa ',':
	* stergem parantezele si optinem: <tip> <valoare> ex: "cub a"
	* apoi facem split() dupa spatii si optimen: ["cub", "a"]

### validare stare

Verifica daca o stare este valida, uitandu-se la sfere si la piramide

* o sfera trebuie sa aibe alte blocuri de o parte si de alta
* nimic nu se pune peste piramida
* nu vrem sa avem piramida deja pe toate stivele => nu mai putem face mutari
