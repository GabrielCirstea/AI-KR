#!/usr/bin/python3
import copy
import sys
import time
import os

# informatii despre un nod din arborele de parcurgere (nu din graful initial)
class NodParcurgere:

    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # consider cost=1 pentru o mutare
        self.h = h
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, fisier, afisCost=False, afisLung=False):
        l = self.obtineDrum()
        for idx, nod in enumerate(l):
            fisier.write(str(idx + 1) + ")\n")
            fisier.write(str(nod))
        if afisCost:
            fisier.write("Cost: ")
            fisier.write(str(self.g))
        if afisLung:
            fisier.write("\nLungime: ")
            fisier.write(str(len(l)))

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info)
        return sir

    def __str__(self):
        sir = ""
        maxInalt = max([len(stiva) for stiva in self.info])
        for inalt in range(maxInalt, 0, -1):
            for stiva in self.info:
                if len(stiva) < inalt:
                    sir += "    "  # patru spatii deoarece, avem 3 caractere de afisat si spatiul dintre stive
                else:
                    if stiva[inalt - 1][0] == 'piramida':
                        sir += "/" + stiva[inalt - 1][1] + "\\" + " "
                    if stiva[inalt - 1][0] == 'cub':
                        sir += "[" + stiva[inalt - 1][1] + "]" + " "
                    if stiva[inalt - 1][0] == 'sfera':
                        sir += "(" + stiva[inalt - 1][1] + ")" + " "
            sir += "\n"
        sir += "#" * (len(self.info) * 4 - 1)
        sir += '\n'
        return sir


class Graph:

    def __init__(self, nume_fisier):

        def obtineStive(sir):

            stiveSiruri = sir.strip().split("\n")
            if stiveSiruri[0].isdecimal():
                self.K = int(stiveSiruri[0])
                listaStive = [sirStiva.strip().split(",") if sirStiva != "#" else [] for sirStiva in stiveSiruri[1:]]
            else:
                listaStive = [sirStiva.strip().split(",") if sirStiva != "#" else [] for sirStiva in stiveSiruri]
            listaSt1 = []
            for idx in range(len(listaStive)):
                listaSt2 = []
                for sirStiva in listaStive[idx]:
                    listaSt2.append(sirStiva.strip().replace("(", " ").replace(")", ""))
                listaSt1.append(listaSt2)
            listaStfin = []
            for idx in range(len(listaSt1)):
                listaSt3 = []
                for sirStiva in listaSt1[idx]:
                    listaSt3.append(sirStiva.split())
                listaStfin.append(listaSt3)
            return listaStfin

        f = open(nume_fisier, 'r')

        continutFisier = f.read()
        self.start = obtineStive(continutFisier)
        # verificam daca starea initiala este valida, deoarece nu dorim sa apelam
        # functiile in cazul in care aceasta este invalida
        nr_stive = len(self.start)
        if not self.validare_stare():
            print("Stare initiala din fisier este invalida")
            exit()

        print("Stare Initiala:", self.start)
        print("Numar stive vide:", self.K)

        input()

    # verifica daca starea initiala este valida
    # verificam pozitia sferelor, a piramidelor, precum si numarul stivelor goale
    # si a celor fara piramida deasupra comparativ cu nr total de piramide
    def validare_stare(self):
        """
        Verifica daca starea respectiva este valida, se uita la pozitia sferelor,
        a piramidelor precum si la numarul de piramide comparativ cu nr de stive
        """
        nr_stive = len(self.start)
        for idx in range(nr_stive):
            for elem in range(len(self.start[idx])):
                # blocuri de o parte si de alta a sferei
                if self.start[idx][elem][0] == "sfera" and (idx == 0 or idx == nr_stive - 1 or
                                                            self.start[idx - 1][elem][0] not in ["cub", "sfera"] or
                                                            self.start[idx + 1][elem][0] not in ["cub", "sfera"]):
                    return False
                # nimic peste piramida
                if self.start[idx][elem][0] == "piramida" and (len(self.start[idx]) - elem != 1):
                    return False

        nrstivegoale = 0
        nrstivefarapir = 0
        ok = 0
        nrpir = 0
        nrsfereincadrate = 0
        for idx in range(nr_stive):
            for elem in range(len(self.start[idx])):
                if self.start[idx][elem][0] == "piramida" and (len(self.start[idx]) - elem != 1):
                    nrpir += 1
                    ok = 1
                if self.start[idx][elem][0] == "sfera" and (idx != 0 and idx != nr_stive - 1 and
                                                            self.start[idx - 1][elem][0] in ["cub", "sfera"] and
                                                            self.start[idx + 1][elem][0] in ["cub", "sfera"]):
                    nrsfereincadrate += 1
                if self.start[idx][elem][0] == " ":
                    nrstivegoale += 1
                if ok == 0:
                    nrstivefarapir += 1

        # vrem sa avem stive fara piramide deasupra, pe care sa le folosim pentru
        # a muta piese
        # daca avem piramide pentru fiecare stiva, nu putem realiza nici o mutare
        if self.K != 0 and (nrpir == nr_stive or nr_stive - 1) and (nrstivegoale + nrstivefarapir) < nrpir:
            print("Starea data nu are solutii")
            return
        '''if self.K != 0 and nrstivegoale < nrsfereincadrate:
            print("Starea data nu are solutii")
            return'''

        return True

    def testeaza_scop(self, nodCurent):
        # verific daca scopul este indeplinit
        nrv = 0
        for idx in range(len(nodCurent.info)):
            if len(nodCurent.info[idx]) == 0:
                nrv = nrv + 1
        if nrv == self.K:
            return True
        return False

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        listaSuccesori = []
        stive_c = nodCurent.info
        nr_stive = len(stive_c)
        for idx in range(nr_stive):
            copie_interm = copy.deepcopy(stive_c)
            if len(copie_interm[idx]) == 0:  # daca stiva e vida sa nu poata sa dea pop din ea
                continue
            # verific daca blocul respectiv este vecin cu o sfera
            if idx > 0 and len(copie_interm[idx - 1]) >= len(copie_interm[idx]) and \
                    copie_interm[idx - 1][len(copie_interm[idx]) - 1][0] == "sfera":
                continue
            if idx < nr_stive - 1 and len(copie_interm[idx + 1]) >= len(copie_interm[idx]) and \
                    copie_interm[idx + 1][len(copie_interm[idx]) - 1][0] == "sfera":
                continue
            bloc = copie_interm[idx].pop()

            for j in range(nr_stive):
                if idx == j:
                    continue
                stive_n = copy.deepcopy(copie_interm)  # lista noua de stive
                # nu peste piramida
                if len(stive_n[j]) > 0 and stive_n[j][-1][0] == "piramida":
                    continue
                # verific unde pun o sfera
                if bloc[0] == "sfera":
                    if j in (0, nr_stive - 1):
                        continue
                    if not (len(stive_n[j - 1]) >= len(stive_n[j]) + 1 and 
                            stive_n[j - 1][len(stive_n[j])][0] in ["cub", "sfera"]):
                        continue
                    if not (len(stive_n[j + 1]) >= len(stive_n[j]) + 1 and 
                            stive_n[j + 1][len(stive_n[j])][0] in ["cub", "sfera"]):
                        continue

                stive_n[j].append(bloc)

                # costul mutarii
                if bloc[0] == 'piramida':
                    costMutareBloc = 1
                elif bloc[0] == 'cub':
                    costMutareBloc = 2
                else:
                    costMutareBloc = 3

                nod_nou = NodParcurgere(stive_n, nodCurent, cost=nodCurent.g + costMutareBloc,
                                        h=self.calculeaza_h(stive_n, tip_euristica))
                if not nodCurent.contineInDrum(stive_n):
                    listaSuccesori.append(nod_nou)

        return listaSuccesori

    # euristici
    def calculeaza_h(self, infoNod, tip_euristica="euristica banala"):

        if tip_euristica == "euristica admisibila 1":
            euristici = []
            h = 0
            copy_stive = copy.deepcopy(infoNod)
            copy_stive = sorted(copy_stive, key=lambda stiva: len(stiva))
            for i in range(self.K):
                h = h + len(copy_stive[i])
            for i in range(len(infoNod)):
                h = h + len(infoNod[i])
                euristici.append(h)
            return min(euristici)

        elif tip_euristica == "euristica admisibila 2":
            euristici = []
            h = 0
            copy_stive = copy.deepcopy(infoNod)
            copy_stive = sorted(copy_stive, key=lambda stiva: len(stiva))
            for i in range(self.K):
                h = h + len(copy_stive[i])
            for i in range(len(infoNod)):
                for j in range(len(infoNod[i])):
                    if infoNod[i][j][0] == "piramida":
                        h = h + 1
                    elif infoNod[i][j][0] == "cub":
                        h = h + 2
                    else:
                        h = h + 3
                euristici.append(h)
            return min(euristici)

        elif tip_euristica == "euristica neadmisibila":
            euristici = []
            h = 0
            copy_stive = copy.deepcopy(infoNod)
            copy_stive = sorted(copy_stive, key=lambda stiva: len(stiva))
            for i in range(len(infoNod)):
                h = h + len(copy_stive[i]) * 7
            for i in range(len(infoNod)):
                for j in range(len(infoNod[i])):
                    if infoNod[i][j][0] == "piramida":
                        h = (h + 1) * 11
                    elif infoNod[i][j][0] == "cub":
                        h = (h + 2) * 10
                    else:
                        h = (h + 3) * 3
                euristici.append(h)
            return min(euristici)

        else:
            return 0

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return (sir)

def a_star(gr, nrSolutiiCautate, tip_euristica,fisier=sys.stdout):
    nr_nod = 0
    global time1
    global timeout
    #in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c=[NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]
    
    while len(c)>0:
        nodCurent=c.pop(0)
            
        if gr.testeaza_scop(nodCurent):
            time_sol = time.time()
            fisier.write("\nSolutie:\n")
            nodCurent.afisDrum(fisier, afisCost=True, afisLung=True)
            fisier.write("\nNumarul de noduri este ")
            fisier.write(str(nr_nod))
            timp_rulare_sol = str(round(1000 * (time_sol - time1)))
            fisier.write("\nTimpul de rulare pe solutie este ")
            fisier.write(timp_rulare_sol)
            fisier.write(" milisecunde")
            fisier.write("\n=======================\n")
            nrSolutiiCautate-=1
            if nrSolutiiCautate==0:
                return
        timpCurent = time.time()
        if timpCurent - time1 > timeout:
            print("timeout=",timeout)
            return
        lSuccesori=gr.genereazaSuccesori(nodCurent,tip_euristica=tip_euristica) 
        nr_nod += len(lSuccesori)
        for s in lSuccesori:
            i=0
            gasit_loc=False
            for i in range(len(c)):
                #diferenta fata de UCS e ca ordonez dupa f
                if c[i].f>=s.f :
                    gasit_loc=True
                    break;
            if gasit_loc:
                c.insert(i,s)
            else:
                c.append(s)

def uniform_cost(gr, nrSolutiiCautate=1, fisier=sys.stdout):

    nr_nod = 0
    global time1
    global timeout
    #in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c=[NodParcurgere(gr.start, None, 0)]
    
    while len(c)>0:
        nodCurent=c.pop(0)
        
        if gr.testeaza_scop(nodCurent):
            time_sol = time.time()
            fisier.write("\nSolutie:\n")
            nodCurent.afisDrum(fisier, afisCost=True, afisLung=True)
            fisier.write("\nNumarul de noduri este ")
            fisier.write(str(nr_nod))
            timp_rulare_sol = str(round(1000 * (time_sol - time1)))
            fisier.write("\nTimpul de rulare pe solutie este ")
            fisier.write(timp_rulare_sol)
            fisier.write(" milisecunde")
            fisier.write("\n=======================\n")
            nrSolutiiCautate-=1
            if nrSolutiiCautate==0:
                return

        timpCurent = time.time()
        if timpCurent - time1 > timeout:
            print("timeout=",timeout)
            return

        lSuccesori=gr.genereazaSuccesori(nodCurent)     
        nr_nod += len(lSuccesori)
        for s in lSuccesori:
            i=0
            gasit_loc=False
            for i in range(len(c)):
                #ordonez dupa cost(notat cu g aici și în desenele de pe site)
                if c[i].g>s.g :
                    gasit_loc=True
                    break
            if gasit_loc:
                c.insert(i,s)
            else:
                c.append(s)

def display_usage():
    print("usage: " + sys.argv[0] + " [if=<input_folder>] [of=<output_folder>]" +\
            " [n=<nr_sol>] [t=<timeout>]")
    exit()

def parsare_argumente():
    """
    Parseaza argumentele primite din linia de comanda si extrage fisierul de input,
    output, nr solutii si timeout-ul
    Le returneaza in aceasta ordine intr-o lista
    """
    for arg in sys.argv:
        if arg == "-h":
            display_usage()

    in_dir="input"
    out_dir="output"
    n=3
    timeout=10
    for arg in sys.argv[1:]:
        check = arg.split("=")
        if len(check) < 2:
            print("invalid")
            exit()
        if check[0] == "if":
            in_dir = ''.join(check[1:])
        elif check[0] == "of":
            out_dir = ''.join(check[1:])
        elif check[0] == 'n':
            try:
                n = int(''.join(check[1:]))
            except ValueError:
                print("nr invalid")
                display_usage()
        elif check[0] == 't':
            try:
                timeout = int(''.join(check[1:]))
            except ValueError:
                print("nr invalid")
                display_usage()

    return [in_dir, out_dir, n, timeout]

time1 = time.time()
timeout = 10
def main():

    global timeout
    in_dir, out_dir, nrSolutiiCautate, timeout = parsare_argumente()
    listaFisiereInput = os.listdir(in_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for fisier in listaFisiereInput:
        global time1
        in_file = '/'.join([in_dir,fisier])
        gr=Graph(in_file)
        # print("\n\n##################\nSolutii obtinute cu A*:")
        # pune "output-" in fata numelui fisierului de input, pentru identificare
        out_file="-".join(["output",fisier])
        # path-ul catre fisierul de output
        output_location = '/'.join([out_dir,out_file])
        f = open(output_location,'w')
        f.write("\n\n##################\nSolutii obtinute cu A*:")
        time1 = time.time()     # ne intereseaza timpul de la inceputul calcularii
                                # solutiilor
        a_star(gr, nrSolutiiCautate, tip_euristica="euristica admisibila 2",
                        fisier=f)
        f.write("\n\n##################\nSolutii obtinute cu UCS:")
        time1 = time.time()
        uniform_cost(gr, nrSolutiiCautate, fisier=f)
        f.close()

if(__name__ == "__main__"):
    main();

