# Teme AI

## Tema 1

Problema bolcurilor

Trei tipuri de blocuri

* cub
* sfera - trebuie sa aiba alte blocuri in stanga si in dreapta
* piramida - nici un bloc nu se poate pune pe priamida

Se da o configuratie de inceput

2  
cub(a),cub(b),cub(g),piramida(c)  
cub(i),sfera(e),sfera(f),piramida(k)  
cub(h),cub(d),cub(j)  
%  
cub(l),piramida(m)  

In care se specifia numarul de stive pe care vrem sa le avem goale la sfarsit
si asezarea blocurilor

> dinca cauza formatului de markdown, am inlocuid # cu %

## Tema2

X si 0

Un joc de x si 0, in care:

* se poate pune x sau 0 oriunde pe tabla
* se pot elimina piesele inamice, daca se "sare" oeste ele, pe diagonala
(asemanator cu jocul de dame)
* scopul este de a se forma un patrat (2x2) din x sau 0

Ex "salt"
```
  |0 1 2 3  
-----------
0 |# # # # 
1 |# # 0 # 
2 |# x # # 
3 |# # # # 
```

```
  |0 1 2 3  
-----------
0 |# # # x 
1 |# # # # 
2 |# x # # 
3 |# # # # 
```
