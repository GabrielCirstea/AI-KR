#!/usr/bin/python3
import time
import pygame, sys, statistics
import copy
import time
import os
import re

def deseneaza_grid(display, tabla, N, M, marcaj=None):  # tabla de exemplu este ["#","x","#","0",......]
    w_gr = h_gr = 80  # width-ul si height-ul unei celule din grid

    x_img = pygame.image.load('ics.png')
    x_img = pygame.transform.scale(x_img, (w_gr, h_gr))
    zero_img = pygame.image.load('zero.png')
    zero_img = pygame.transform.scale(zero_img, (w_gr, h_gr))
    drt = []  # este lista cu patratelele din grid
    for ind in range(len(tabla)):
        linie = ind // M  # // inseamna div
        coloana = ind % M
        patr = pygame.Rect(coloana * (w_gr + 1), linie * (h_gr + 1), w_gr, h_gr)
        # print(str(coloana*(w_gr+1)), str(linie*(h_gr+1)))
        drt.append(patr)
        if marcaj == ind:
            # daca am o patratica selectata, o desenez cu rosu
            culoare = (255, 0, 0)
        
        else:
            # altfel o desenez cu alb
            culoare = (255, 255, 255)
        pygame.draw.rect(display, culoare, patr)  # alb = (255,255,255)
        if tabla[ind] == 'x':
            display.blit(x_img, (coloana * (w_gr + 1), linie * (h_gr + 1)))
        elif tabla[ind] == '0':
            display.blit(zero_img, (coloana * (w_gr + 1), linie * (h_gr + 1)))
    pygame.display.flip()
    return drt


class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    NR_LINII = None
    NR_COLOANE = None
    JMIN = None
    JMAX = None
    GOL = '#'
    Removed = None  # piesa stearsa prin "salt"

    def __init__(self, tabla=None, removed=None):
        self.matr = tabla or [self.__class__.GOL] * self.NR_LINII * self.NR_COLOANE
        self.Removed = removed

    def final(self):
        def in_patrat(tabla, index):
            # verificam daca index se afla in coltul din stanga sus
            # al unui patrat de piese
            player = tabla[index]
            if self.NR_COLOANE - index % self.NR_COLOANE< 2:
                return False
            if index > len(tabla) - self.NR_COLOANE:
                return False
            if tabla[index+1] == player\
                    and tabla[index+self.NR_COLOANE] == player\
                    and tabla[index+self.NR_COLOANE + 1] == player:
                        return True
            return False
        # cineva ar trebui sa scrie cum se gaseste un patrat pe tabla
        nr_liber = 0
        for i in range(len(self.matr)):
            if self.matr[i] == self.__class__.GOL:
                nr_liber +=1
            elif in_patrat(self.matr, i):
                return self.matr[i]
        if nr_liber == 0:
            return "remiza"

    def salt_piesa(self, selected, index, target, tabla = None):
        if tabla == None:
            tabla = self.matr
        # coord unde vrem sa punem
        xIndex = index // self.NR_COLOANE
        yIndex = index %  self.NR_COLOANE
        # coord piesa selectata
        xSelected = selected // self.NR_COLOANE
        ySelected = selected % self.NR_COLOANE
        # print(xSelected, ySelected)
        
        # verific ca locul dorit sa fie pe diagonala
        if xIndex - xSelected not in [-2, 2] or\
                yIndex - ySelected not in [-2, 2]:
                    return False;
        # piesa dintre sindexesa selectata si locul dorit
        xMijloc = (xIndex + xSelected)//2
        yMijloc = (yIndex + ySelected)//2
        indexMijloc = xMijloc * self.NR_COLOANE + yMijloc
        if tabla[indexMijloc] == target:
            tabla[indexMijloc] = self.__class__.GOL
            self.Removed = indexMijloc
            return True

    def salt_daca_oponent(self, index):
        """
        Verifica da piesa are pe diagonala o piesa inamica
        In caz afirmativ incearca sa faca un salt pentru a elimina piesa de pe
        diagonala
        Returneaza o lista de mutari in care s-au facut salturi
        """
        jucator = self.matr[index];
        x = index // self.NR_COLOANE
        y = index %  self.NR_COLOANE
        # copii nu scrieti cod asa
        celalalt = 'x' if jucator == '0' else '0'
        diagonale = [-1,1]
        l_mutari = []
        for i in diagonale:
            for j in diagonale:
                pos = (x+i)*self.NR_COLOANE + (y+j)
                if pos < 0 or pos > len(self.matr) - 1:
                    continue
                if self.matr[pos] == celalalt:
                    selected = (x+2*i)*self.NR_COLOANE + (y+2*j)
                    if(selected < 0 or selected > len(self.matr)-1):
                        continue
                    if(self.matr[selected] != Joc.GOL):
                        continue
                    copie = copy.deepcopy(self.matr)
                    copie[selected] = jucator
                    self.salt_piesa(selected, index, celalalt, tabla=copie)
                    l_mutari.append(copie)
        return l_mutari

    def mutari(self, jucator_opus):
        l_mutari = []
        for i in range(len(self.matr)):
            if i != self.Removed:
                if self.matr[i] == self.__class__.GOL:
                    matr_tabla_noua = copy.deepcopy(self.matr)
                    matr_tabla_noua[i] = jucator_opus
                    l_mutari.append(Joc(matr_tabla_noua))
                if self.matr[i] == jucator_opus:
                    mutari = self.salt_daca_oponent(i)
                    for mutare in mutari:
                        l_mutari.append(Joc(mutare))
        return l_mutari

    # linie deschisa inseamna linie pe care jucatorul mai poate forma o configuratie castigatoare

    def linie_deschisa(self, lista, jucator):
        # obtin multimea simbolurilor de pe linie
        mt = set(lista)
        # verific daca sunt maxim 2 simboluri
        if (len(mt) <= 2):
            # daca multimea simbolurilor nu are alte simboluri decat pentru cel de "gol" si jucatorul curent
            if mt <= {self.__class__.GOL, jucator}:
                # inseamna ca linia este deschisa
                return 1
            else:
                return 0
        else:
            return 0

    def patrate_deschise(self, jucator):
        """
        Calculeaza numarul de patratele libere, in care se mai pot pune piese
        pentru a castiga
        """
        nr_linii = 0
        for i in range(self.NR_LINII - 1):
            for j in range(0, self.NR_COLOANE - 2, 1):
                nr_linii += self.linie_deschisa(self.matr[i*self.NR_COLOANE+j : i*self.NR_COLOANE+j+1]
                        + self.matr[(i+1)*self.NR_COLOANE+j : (i+1)*self.NR_COLOANE+j+1], jucator)

        return nr_linii


    # linie deschisa inseamna linie pe care jucatorul mai poate forma o configuratie castigatoare
    def estimare_scor1(self, lista, jucator):
        # obtin multimea simbolurilor de pe linie
        mt = set(lista)
        # verific daca sunt maxim 2 simboluri
        if (len(mt) <= 2):
            # daca multimea simbolurilor nu are alte simboluri decat pentru cel de "gol" si jucatorul curent
            if mt <= {self.__class__.GOL, jucator}:
                # inseamna ca linia este deschisa
                return 1
            else:
                return 0
        else:
            return 0

    def estimeaza_scor(self, adancime):
        t_final = self.final()
        # if (adancime==0):
        if t_final == self.__class__.JMAX:
            return (99 + adancime)
        elif t_final == self.__class__.JMIN:
            return (-99 - adancime)
        elif t_final == 'remiza':
            return 0
        else:
            return (self.patrate_deschise(self.__class__.JMAX) - self.patrate_deschise(self.__class__.JMIN))

    def __str__(self):
        sir = "  |"
        for i in range(self.NR_COLOANE):
            sir += str(i) + " "
        sir += "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        for i in range(self.NR_LINII):  # itereaza prin linii
            sir += str(i) + " |" + " ".join([str(x) for x in self.matr[self.NR_COLOANE * i: self.NR_COLOANE * (i + 1)]]) + "\n"
        # [0,1,2,3,4,5,6,7,8]
        return sir



class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, estimare=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent


        # adancimea in arborele de stari
        self.adancime = adancime

        # estimarea favorabilitatii starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.estimare = estimare

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def jucator_opus(self):
        if self.j_curent == Joc.JMIN:
            return Joc.JMAX
        else:
            return Joc.JMIN

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)
        juc_opus = self.jucator_opus()
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]

        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Jucator curent:" + self.j_curent + ")\n"
        return sir

""" Algoritmul MinMax """

def min_max(stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutariCuEstimare = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu estimarea maxima
        stare.stare_aleasa = max(mutariCuEstimare, key=lambda x: x.estimare)
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu estimarea minima
        stare.stare_aleasa = min(mutariCuEstimare, key=lambda x: x.estimare)
    stare.estimare = stare.stare_aleasa.estimare
    return stare


def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()

    if stare.j_curent == Joc.JMAX:
        estimare_curenta = float('-inf')

        for mutare in stare.mutari_posibile:
            # calculeaza estimarea pentru starea noua, realizand subarborele
            stare_noua = alpha_beta(alpha, beta, mutare)

            if (estimare_curenta < stare_noua.estimare):
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if (alpha < stare_noua.estimare):
                alpha = stare_noua.estimare
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        estimare_curenta = float('inf')

        for mutare in stare.mutari_posibile:

            stare_noua = alpha_beta(alpha, beta, mutare)

            if (estimare_curenta > stare_noua.estimare):
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare

            if (beta > stare_noua.estimare):
                beta = stare_noua.estimare
                if alpha >= beta:
                    break
    stare.estimare = stare.stare_aleasa.estimare

    return stare


def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final()
    if (final):
        if (final == "remiza"):
            print("Remiza!")
        else:
            print("A castigat " + final)

        return True
    return False


def get_input():
    # specificare tip algoritm
    raspuns_valid = False
    while not raspuns_valid:
        tip_algoritm = input("Algoritmul folosit?\n 1.Minimax\n 2.Alpha-beta\n ")
        if tip_algoritm in ['1', '2']:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta valida.")

    raspuns_valid = False
    while not raspuns_valid:
        tip_nivel = input("Ce nivel de dificultate doriti?\n 1.Incepator\n 2.Mediu\n 3.Avansat\n ")
        if tip_nivel in ['1', '2', '3']:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta valida.")

    # initializare jucatori
    raspuns_valid = False
    while not raspuns_valid:
        Joc.JMIN = input("Doriti sa jucati cu x sau cu 0? ").lower()
        if (Joc.JMIN in ['x', '0']):
            raspuns_valid = True
        else:
            print("Raspunsul trebuie sa fie x sau 0.")
    Joc.JMAX = '0' if Joc.JMIN == 'x' else 'x'

    #initializare dificultate nivel
    if tip_nivel == '1':
        raspuns_valid = False
        while not raspuns_valid:
            try:
                adancime = int(input("Dati adancimea dorita pentru nivelul incepator: "))
                if (type(adancime) is int and adancime>=1 and adancime<=3):
                    raspuns_valid = True
                    break
                print("Adancimea trebuie sa fie in intervalul [1;3]")
            except Exception as exc:
                print("Valoarea data este invalida,", exc)

    if tip_nivel == '2':
        raspuns_valid = False
        while not raspuns_valid:
            try:
                adancime = int(input("Dati adancimea dorita pentru nivelul mediu: "))
                if (type(adancime) is int and adancime>=4 and adancime<=6):
                    raspuns_valid = True
                    break
                print("Adancimea trebuie sa fie in intervalul [4;6]") # adancime foarte mare ca
            except Exception as exc:
                print("Valoarea data este invalida,", exc)

    if tip_nivel == '3':
        raspuns_valid = False
        while not raspuns_valid:
            try:
                adancime = int(input("Dati adancimea dorita pentru nivelul avansat: "))
                if (type(adancime) is int and adancime>=6):
                    raspuns_valid = True
                    break
                print("Adancimea trebuie sa fie in intervalul [6;inf]")
            except Exception as exc:
                print("Valoarea data este invalida,", exc)
    #specificarea dimensiunilor tablei de joc
    raspuns_valid = False
    while not raspuns_valid:
        try:
            N = int(input("Dati numarul de coloane dorit "))
            if ((type(N) is int) and (N <= 10 and N > 5 and N%2 == 0)):
                raspuns_valid = True
                break
            print("Numarul de coloane trebuie sa fie par si sa se afle in intervalul [6;10]")
        except Exception as exc:
            print("Valoarea data este invalida,", exc)

    return (tip_algoritm, tip_nivel, adancime, N, N)

def main():

    tip_algoritm = '1'
    tip_nivel = 1
    adancime = 2
    Joc.JMAX = "0"
    Joc.JMIN = "x"
    N = 9   # linii
    M = 10  # coloane
    (tip_algoritm, tip_nivel, adancime, N, M) = get_input()

    # initializare tabla
    Joc.NR_LINII = int(N)
    Joc.NR_COLOANE = int(M)
    tabla_curenta = Joc()
    nr_mut_calc = 0
    nr_mut_util = 0
    print("Tabla initiala")
    print(str(tabla_curenta))
    lista_timpi = []
    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, 'x', adancime)

    # setari interf grafica
    time1_tot = int(round(time.time() * 1000))
    pygame.init()
    pygame.display.set_caption("Gabriel Cirstea x si 0")
    # dimensiunea ferestrei in pixeli
    ecran = pygame.display.set_mode(size=(M*81-1, N*81-1))  # Nrc*100+Nrc-1, Nrl*100+Nrl-1

    # de_mutat = False
    patratele = deseneaza_grid(ecran, tabla_curenta.matr, N, M)
    selected_piece = None
    while True:

        if (stare_curenta.j_curent == Joc.JMIN):
            # muta jucatorul
            # preiau timpul in milisecunde de dinainte de mutare
            t_inainte = int(round(time.time() * 1000))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:

                    pos = pygame.mouse.get_pos()  # coordonatele clickului

                    for np in range(len(patratele)):

                        if patratele[np].collidepoint(pos):
                            linie = np // M
                            coloana = np % M
                            ###############################
                            if stare_curenta.tabla_joc.matr[np] == Joc.JMIN:
                                selected_piece = np
                                patratele = deseneaza_grid(ecran, stare_curenta.tabla_joc.matr,\
                                        N, M, np)
                            if stare_curenta.tabla_joc.matr[np] == Joc.GOL:
                                if linie * M + coloana == stare_curenta.tabla_joc.Removed:
                                    continue
                                if selected_piece:
                                    stare_curenta.tabla_joc.salt_piesa(
                                            selected_piece,np, Joc.JMAX)
                                stare_curenta.tabla_joc.matr[np] = Joc.JMIN
                                nr_mut_util += 1
                                # afisarea starii jocului in urma mutarii utilizatorului
                                print("\nTabla dupa mutarea jucatorului")
                                print(str(stare_curenta))
                                # preiau timpul in milisecunde de dupa mutare
                                t_dupa = int(round(time.time() * 1000))
                                print("Utilizatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
                                patratele = deseneaza_grid(ecran, stare_curenta.tabla_joc.matr, N, M)

                                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                                stare_curenta.j_curent = stare_curenta.jucator_opus()

        # --------------------------------
        else:  # jucatorul e JMAX (calculatorul)
            # Mutare calculator
            t_inainte = int(round(time.time() * 1000))

            if tip_algoritm == '1':
                stare_actualizata = min_max(stare_curenta)
            else:  # tip_algoritm==2
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)

            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
            nr_mut_calc += 1

            print("Tabla dupa mutarea calculatorului")
            print(str(stare_curenta))

            patratele = deseneaza_grid(ecran, stare_curenta.tabla_joc.matr, N, M)
            # preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.time() * 1000))
            print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
            lista_timpi.append(t_dupa - t_inainte)

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.j_curent = stare_curenta.jucator_opus()

        # testez daca jocul a ajuns intr-o stare finala
        # si afisez un mesaj corespunzator in caz ca da
        if (afis_daca_final(stare_curenta)):
            break

    print("Timpul minim al calculatorului este ", min(lista_timpi), " milisecunde.")
    print("Timpul maxim al calculatorului este ", max(lista_timpi), " milisecunde.")
    print("Media calculatorului este ", statistics.mean(lista_timpi), " milisecunde.")
    print("Mediana calculatorului este ", statistics.median(lista_timpi), " milisecunde.")
    print("Numar mutari utilizator: ", nr_mut_util)
    print("Numar mutari calculator: ", nr_mut_calc)
    time2_tot = int(round(time.time() * 1000))
    print("Jocul a durat in total " + str(time2_tot-time1_tot) + " milisecunde.")


if __name__ == "__main__":
    main()
