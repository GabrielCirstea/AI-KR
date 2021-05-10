# X si 0

Regulile:

* se poate pune x sau 0 oriunde
* castiga cine reuseste sa faca un patrat (2x2)
* se poate "sari" pe diagonala pentru a elimina o piesa inamica

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

## Functii

**salt_piesa**

* verifica daca intre piesa selectata si locul tinta se afla o piesa a jucatorului opus

**patrate_deschise**

* numara care locuri mai sunt pentru a face o configuratie castigatoare
* configuratia castigatoare este un patrat de 2 x 2
