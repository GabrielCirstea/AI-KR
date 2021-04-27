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

    def validitate(self):
        return

    def salt_piesa(self, selected, index):
        # coord unde vrem sa punem
        xIndex = index // self.NR_COLOANE
        yIndex = index %  self.NR_COLOANE
        # coord piesa selectata
        xSelected = selected // self.NR_COLOANE
        ySelected = selected % self.NR_COLOANE
        print(xSelected, ySelected)
        
        # verific ca locul dorit sa fie pe diagonala
        if xIndex - xSelected not in [-2, 2] or\
                yIndex - ySelected not in [-2, 2]:
                    return False;
        # piesa dintre sindexesa selectata si locul dorit
        xMijloc = (xIndex + xSelected)//2
        yMijloc = (yIndex + ySelected)//2
        print(xMijloc, yMijloc)
        indexMijloc = xMijloc * self.NR_COLOANE + yMijloc
        print("index mijloc = ", indexMijloc)
        if self.matr[indexMijloc] == '0':
            self.matr[indexMijloc] = self.__class__.GOL
            self.Removed = indexMijloc
            print("salt")
            return True

    def mutari(self, jucator_opus):
        l_mutari = []
        for i in range(len(self.matr)):
            if i != self.Removed and self.matr[i] == self.__class__.GOL:
                matr_tabla_noua = copy.deepcopy(self.matr)
                matr_tabla_noua[i] = jucator_opus
                l_mutari.append(Joc(matr_tabla_noua))
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

    def linii_deschise(self, jucator):
        nr_linii = 0
        # numaram liniile
        for i in range(self.NR_LINII):
            nr_linii += self.linie_deschisa(self.matr[i*self.NR_COLOANE:int(i+1)*self.NR_COLOANE], jucator)
        # numaram coloanele
        for j in range(self.NR_COLOANE):
            nr_linii += self.linie_deschisa(self.matr[j::self.NR_COLOANE], jucator)
        # cineva ar trebui sa faca si diagonalele

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

    def estimare_scor2(self, jucator):
        # to be continued
        return

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
            return (self.linii_deschise(self.__class__.JMAX) - self.linii_deschise(self.__class__.JMIN))

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
        tip_algoritm = input("Algoritmul folosit? (raspundeti cu 1 sau 2)\n 1.Minimax\n 2.Alpha-beta\n ")
        if tip_algoritm in ['1', '2']:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta valida.")

    raspuns_valid = False
    while not raspuns_valid:
        tip_nivel = input("Ce nivel de dificultate doriti? (raspundeti cu 1, 2 sau 3)\n 1.Incepator\n 2.Mediu\n 3.Avansat\n ")
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
                if (type(adancime) is int and adancime>=1 and adancime<=5):
                    raspuns_valid = True
                    break
                print("Adancimea trebuie sa fie in intervalul [1;5]")
            except Exception as exc:
                print("Valoarea data este invalida,", exc)

    if tip_nivel == '2':
        raspuns_valid = False
        while not raspuns_valid:
            try:
                adancime = int(input("Dati adancimea dorita pentru nivelul mediu: "))
                if (type(adancime) is int and adancime>=6 and adancime<=10):
                    raspuns_valid = True
                    break
                print("Adancimea trebuie sa fie in intervalul [6;10]") # adancime foarte mare ca
            except Exception as exc:
                print("Valoarea data este invalida,", exc)

    if tip_nivel == '3':
        raspuns_valid = False
        while not raspuns_valid:
            try:
                adancime = int(input("Dati adancimea dorita pentru nivelul avansat: "))
                if (type(adancime) is int and adancime>=11):
                    raspuns_valid = True
                    break
                print("Adancimea trebuie sa fie in intervalul [11;inf]")
            except Exception as exc:
                print("Valoarea data este invalida,", exc)
    #specificarea dimensiunilor tablei de joc
    raspuns_valid = False
    while not raspuns_valid:
        try:
            N = int(input("Dati numarul de linii dorit "))
            if ((type(N) is int) and (N <= 10 and N >= 5 and N%2 != 0)):
                raspuns_valid = True
                break
            print("Numarul de linii trebuie sa fie impar si sa se afle in intervalul [5;10]")
        except Exception as exc:
            print("Valoarea data este invalida,", exc)

    raspuns_valid = False
    while not raspuns_valid:
        try:
            M = int(input("Dati numarul de coloane dorit "))
            if ((type(M) is int) and (M <= 10 and M >= 5 and M%2 == 0)):
                raspuns_valid = True
                break
            print("Numarul de coloane trebuie sa fie par si sa se afle in intervalul [5;10]")
        except Exception as exc:
            print("Valoarea data este invalida,", exc)

    return [tip_algoritm, tip_nivel, adancime, N, M, '2']
    #citire pentru interfata
    if len(interfata) != 1:
        raspuns_valid = False
        while not raspuns_valid:
            interface = input(
                "Doriti sa jucati din consola sau prin interfata grafica? (raspundeti cu 1 sau 2)\n 1.Consola\n 2.-gui\n ")
            if interface in ['1', '2']:
                raspuns_valid = True
            else:
                print("Nu ati ales o varianta corecta.")


def main():

    tip_algoritm = '1'
    tip_nivel = 1
    adancime = 2
    Joc.JMAX = "0"
    Joc.JMIN = "x"
    N = 9   # linii
    M = 10  # coloane
    interface = '2'
    # (tip_algoritm, tip_nivel, SCMAX, adancime, N, M, interface) = get_input()

    # initializare tabla
    Joc.NR_LINII = N
    Joc.NR_COLOANE = M
    tabla_curenta = Joc()
    tabla_curenta.matr[75] = '0'
    tabla_curenta.matr[57] = '0'
    tabla_curenta.matr[47] = '0'
    tabla_curenta.matr[27] = '0'
    nr_mut_calc = 0
    nr_mut_util = 0
    print("Tabla initiala")
    print(str(tabla_curenta))
    lista_timpi = []
    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, 'x', adancime)

    if (interface == '2'):
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
                                                selected_piece,np)
                                    stare_curenta.tabla_joc.matr[np] = Joc.JMIN
                                    nr_mut_util += 1
                                    # afisarea starii jocului in urma mutarii utilizatorului
                                    print("\nTabla dupa mutarea jucatorului")
                                    print(str(stare_curenta))
                                    # preiau timpul in milisecunde de dupa mutare
                                    t_dupa = int(round(time.time() * 1000))
                                    print("Utilizatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
                                    patratele = deseneaza_grid(ecran, stare_curenta.tabla_joc.matr, N, M)
                                    # testez daca jocul a ajuns intr-o stare finala
                                    # si afisez un mesaj corespunzator in caz ca da
                                    if (afis_daca_final(stare_curenta)):
                                        break

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
                if (afis_daca_final(stare_curenta)):
                    break

                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                stare_curenta.j_curent = stare_curenta.jucator_opus()
        print("\nTimpul minim al calculatorului este ", min(lista_timpi), " milisecunde.\n")
        print("\nTimpul maxim al calculatorului este ", max(lista_timpi), " milisecunde.\n")
        print("\nMedia calculatorului este ", statistics.mean(lista_timpi), " milisecunde.\n")
        print("\nMediana calculatorului este ", statistics.median(lista_timpi), " milisecunde.\n")
        print("\nNumar mutari utilizator este ", nr_mut_util, "\n")
        print("\nNumar mutari calculator este ", nr_mut_calc, "\n")
        time2_tot = int(round(time.time() * 1000))
        print("\nJocul a durat in total " + str(time2_tot-time1_tot) + " milisecunde.")

    else:
        time1_tot = int(round(time.time() * 1000))
        while True:
            if (stare_curenta.j_curent == Joc.JMIN):
                # muta utilizatorul

                print("Acum muta utilizatorul cu simbolul", stare_curenta.j_curent)
                # preiau timpul in milisecunde de dinainte de mutare
                t_inainte = int(round(time.time() * 1000))
                raspuns_valid = False
                while not raspuns_valid:
                    try:
                        # utilizatorul poate opri jocul la orice mutare doreste
                        linie = input("linie=")
                        if linie.lower() == "exit":
                            sys.exit()
                        coloana = input("coloana=")
                        if coloana.lower() == "exit":
                            sys.exit()

                        linie = int(linie)
                        coloana = int(coloana)

                        if (linie in range(Joc.NR_COLOANE) and coloana in range(Joc.NR_COLOANE)):
                            if stare_curenta.tabla_joc.matr[linie * Joc.NR_COLOANE + coloana] == Joc.GOL:
                                raspuns_valid = True
                            else:
                                print("Exista deja un simbol in pozitia ceruta.")
                        else:
                            print("Linie sau coloana invalida (trebuie sa fie unul dintre numerele 0,1,2).")

                    except ValueError:
                        print("Linia si coloana trebuie sa fie numere intregi")

                # dupa iesirea din while sigur am valide atat linia cat si coloana
                # deci pot plasa simbolul pe "tabla de joc"
                stare_curenta.tabla_joc.matr[linie * Joc.NR_COLOANE + coloana] = Joc.JMIN
                nr_mut_util += 1
                # afisarea starii jocului in urma mutarii utilizatorului
                print("\nTabla dupa mutarea jucatorului")
                print(str(stare_curenta))
                # preiau timpul in milisecunde de dupa mutare
                t_dupa = int(round(time.time() * 1000))
                print("Utilizatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
                # testez daca jocul a ajuns intr-o stare finala
                # si afisez un mesaj corespunzator in caz ca da
                if (afis_daca_final(stare_curenta)):
                    break

                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                stare_curenta.j_curent = stare_curenta.jucator_opus()

            # --------------------------------
            else:  # jucatorul e JMAX (calculatorul)
                # Mutare calculator

                print("Acum muta calculatorul cu simbolul", stare_curenta.j_curent)
                # preiau timpul in milisecunde de dinainte de mutare
                t_inainte = int(round(time.time() * 1000))

                # stare actualizata e starea mea curenta in care am setat stare_aleasa (mutarea urmatoare)
                if tip_algoritm == '1':
                    stare_actualizata = min_max(stare_curenta)
                else:  # tip_algoritm==2
                    stare_actualizata = alpha_beta(-500, 500, stare_curenta)

                stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
                nr_mut_calc += 1

                stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc  # aici se face de fapt mutarea

                print("Tabla dupa mutarea calculatorului")
                print(str(stare_curenta))

                # preiau timpul in milisecunde de dupa mutare
                t_dupa = int(round(time.time() * 1000))
                print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")
                lista_timpi.append(t_dupa - t_inainte)
                if (afis_daca_final(stare_curenta)):
                    break

                # S-a realizat o mutare.  jucatorul cu cel opus
                stare_curenta.j_curent = stare_curenta.jucator_opus()

        print("\nTimpul minim al calculatorului este ", min(lista_timpi), " milisecunde.\n")
        print("\nTimpul maxim al calculatorului este ", max(lista_timpi), " milisecunde.\n")
        print("\nMedia calculatorului este ", statistics.mean(lista_timpi), " milisecunde.\n")
        print("\nMediana calculatorului este ", statistics.median(lista_timpi), " milisecunde.\n")
        print("\nNumar mutari utilizator este ", nr_mut_util, "\n")
        print("\nNumar mutari calculator este ", nr_mut_calc, "\n")
        time2_tot = int(round(time.time() * 1000))
        print("\nJocul a durat in total " + str(time2_tot - time1_tot) + " milisecunde.")

if __name__ == "__main__":
    main()
