"""
Documentatie: 

https://drive.google.com/file/d/1UZEuIWjxd0tYfU-njmRxk7egX_AE8NmS/view?usp=sharing

"""

import math
from argparse import ArgumentParser
import os
import operator
import copy
import time
import stopit


class NodParcurgere:
    gr = None  # trebuie setat sa contina instanta problemei

    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost
        self.h = h
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, writer):
        l = self.obtineDrum()

        for count, nod in enumerate(l):
            writer.write("{})".format(count + 1) + '\n')
            writer.write(str(nod) + '\n')

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte
        return False

    def __str__(self):

        output = ""
        vcl_malInitial, vcl_malFinal, malTaran, nr_tip_magazie, nr_tip_compA, nr_tip_compB = self.info
        output += "Pe malul de est se gasesc:" + '\n'
        output += "{}{} verze {} capre {} lupi".format("Taranul " if malTaran == "initial"
                                                       else "", vcl_malInitial[0], vcl_malInitial[1],
                                                       vcl_malInitial[2]) + '\n'

        output += "Pe malul de vest se gasesc:" + '\n'
        output += "{}{} verze {} capre {} lupi, magazie: {}".format(
            "Taranul " if malTaran == "final" else "",
            vcl_malFinal[0], vcl_malFinal[1], vcl_malFinal[2],
            str(nr_tip_magazie[0]) + nr_tip_magazie[1] if nr_tip_magazie[1] != "gol" else 0) + '\n'

        if malTaran == "initial" and not self.gr.testeaza_scop(self.info) and vcl_malFinal != [0, 0, 0]:
            vcl_malFinalDupaMancat = self.__class__.gr.seManancaAnimale(
                vcl_malFinal)
            output += "Dupa ce au mancat pe malul vest: {} verze {} capre {} lupi".format(
                vcl_malFinalDupaMancat[0], vcl_malFinalDupaMancat[1], vcl_malFinalDupaMancat[2]) + '\n'
        elif malTaran == "final" and not self.gr.testeaza_scop(self.info):
            vcl_malInitialDupaMancat = self.__class__.gr.seManancaAnimale(
                vcl_malInitial)
            output += "Dupa ce au mancat pe malul est: {} verze {} capre {} lupi".format(
                vcl_malInitialDupaMancat[0], vcl_malInitialDupaMancat[1], vcl_malInitialDupaMancat[2]) + '\n'

        if not self.gr.testeaza_scop(self.info):
            output += "Barca pleaca de la {} la {} cu container A: {}, container B: {}".format(
                "est" if malTaran == "initial" else "vest",
                "vest" if malTaran == "initial" else "est",
                str(nr_tip_compA[0]) + str(nr_tip_compA[1]) if
                nr_tip_compA[1] != "gol" else 0,
                str(nr_tip_compB[0]) + str(nr_tip_compB[1]) if
                nr_tip_compB[1] != "gol" else 0) + '\n'
        return output


class Graph:  # graful problemei
    N1 = None
    N2 = None
    N3 = None
    nr_compA = None
    nr_compB = None
    nr_magazie = None
    stare_finala = None

    def __init__(self, N1, N2, N3, nr_compA, nr_compB, nr_magazie, stare_initiala,
                 stare_finala):

        self.__class__.N1 = N1
        self.__class__.N2 = N2
        self.__class__.N3 = N3
        self.__class__.nr_compA = nr_compA
        self.__class__.nr_compB = nr_compB
        self.__class__.nr_magazie = nr_magazie
        self.__class__.stare_finala = stare_finala

        malTaran = "initial"

        vcl_malInitial = stare_initiala

        verzeFinal, capreFinal, lupiFinal = 0, 0, 0
        vcl_malFinal = [verzeFinal, capreFinal, lupiFinal]

        nr_tip_magazie = [0, "gol"]
        nr_tip_compA = [0, "gol"]
        nr_tip_compB = [0, "gol"]

        # informatia nodului de start
        self.start = [vcl_malInitial, vcl_malFinal, malTaran,
                      nr_tip_magazie, nr_tip_compA, nr_tip_compB]

    def testeaza_scop(self, infoNod):
        lupiInitial, capreInitial, verzeInitial = infoNod[0]
        lupiFinal, capreFinal, verzeFinal = infoNod[1]

        if all(x >= y for x, y in zip((lupiFinal, capreFinal, verzeFinal), self.__class__.stare_finala)):
            return True
        return False

    def seManancaAnimale(self, vcl_mal):
        verze, capre, lupi = vcl_mal
        if capre > 0:
            # caprele au prioritate
            for capra in range(capre):
                if verze < self.__class__.N3:  # daca nu mai sunt suficiente verze pentru capre, nu mai servim
                    break
                verze = verze - self.__class__.N3

            for lup in range(lupi):
                if capre < self.__class__.N2:
                    break
                capre = capre - self.__class__.N2  # servim N2 capre la fiecare lup

        elif capre == 0 and lupi > 0:
            # cat timp unul dintre lupi poate manca N1 lupi
            while (lupi - 1) >= self.__class__.N1 and self.__class__.N1 > 0:
                lupi = lupi - self.__class__.N1  # 9 lupi mananca N1=3 => 3 lupi ramasi
                # 10 lupi mananca N1=3 => 1 lup ramas

        return [verze, capre, lupi]

    def calculeaza_h(self, infoNod, tip_euristica="euristica banala", parinte=None, costSuccesor=0):
        if tip_euristica == "euristica banala":
            if not self.testeaza_scop(infoNod):
                return 1
            return 0
        elif tip_euristica == "euristica admisibila 1":  # cat mai putine plimbari cu barca
            # calculez cate elemente mai am de mutat si impart la nr de locuri in barca
            # si adun numarul ramas pana ajung la minimul cerut la malul final
            vcl_malInitial = infoNod[0]
            vcl_malFinal = copy.deepcopy(infoNod[1])
            malTaran = infoNod[2]
            nr_tip_magazie = infoNod[3]

            if nr_tip_magazie[1] == "verze":  # daca avem verze in magazie adaugam nr lor la malFinal
                vcl_malFinal[0] += nr_tip_magazie[0]
            elif nr_tip_magazie[1] == "capre":  # analog
                vcl_malFinal[1] += nr_tip_magazie[0]
            elif nr_tip_magazie[1] == "lupi":  # analog
                vcl_malFinal[2] += nr_tip_magazie[0]

            stareFinala = self.__class__.stare_finala

            # unitati(v/c/l) / (compA+compB)
            euristica = math.ceil(sum(vcl_malInitial) / (self.__class__.nr_compA + self.__class__.nr_compB))

            # cat este pe malFinal vs cat mai am nevoie ca sa ajung la stareFinala
            # adaug nr de unitati necesare pt a ajunge la starea finala
            euristica += sum(y - x if y > x else 0 for x, y in zip(vcl_malFinal, stareFinala))

            return euristica

        elif tip_euristica == "euristica admisibila 2":
            # aici doar adun numarul ramas pana ajung la minimul cerut la malul final
            vcl_malInitial = infoNod[0]
            vcl_malFinal = copy.deepcopy(infoNod[1])
            malTaran = infoNod[2]
            nr_tip_magazie = infoNod[3]

            if nr_tip_magazie[1] == "verze":
                vcl_malFinal[0] += nr_tip_magazie[0]
            elif nr_tip_magazie[1] == "capre":
                vcl_malFinal[1] += nr_tip_magazie[0]
            elif nr_tip_magazie[1] == "lupi":
                vcl_malFinal[2] += nr_tip_magazie[0]
            stareFinala = self.__class__.stare_finala

            # adaug nr de unitati necesare pt a ajunge la starea finala
            euristica = sum(y - x if y > x else 0 for x, y in zip(vcl_malFinal, stareFinala))

            return euristica

        elif tip_euristica == "euristica neadmisibila":  # ne dorim sa obtinem un nr cat mai mare de animale mancate
            vcl_malInitial = infoNod[0]
            vcl_malFinal = copy.deepcopy(infoNod[1])
            nr_tip_magazie = infoNod[3]

            if nr_tip_magazie[1] == "verze":
                vcl_malFinal[0] += nr_tip_magazie[0]
            elif nr_tip_magazie[1] == "capre":
                vcl_malFinal[1] += nr_tip_magazie[0]
            elif nr_tip_magazie[1] == "lupi":
                vcl_malFinal[2] += nr_tip_magazie[0]
            malTaran = infoNod[2]
            stareFinala = self.__class__.stare_finala

            mancate = None
            if malTaran == "initial":
                mancate = self.seManancaAnimale(vcl_malFinal)
            elif malTaran == "final":
                mancate = self.seManancaAnimale(vcl_malInitial)

            euristica = sum(mancate)
            euristica = sum(y - x if y > x else 0 for x, y in zip(vcl_malFinal, stareFinala))
            euristica += sum(vcl_malInitial)

            return euristica

    # functie intermediara care obtine succesori din nodCurent la debarcarea barcii si folosind magazia
    def adaugaCelPutinUnSuccesor(self, nodCurent, listaSuccesori, compA_nou, compB_nou, tip_euristica):
        listaInfoNodNou = []
        # vom obtine succesorii lui nodCurent in urma imbarcarii si debarcarii barcii

        infoNodNou = copy.deepcopy(nodCurent.info)  # copie a nodului curent
        compartimentA = compA_nou
        compartimentB = compB_nou
        malTaran = infoNodNou[2]
        nr_tip_magazie = infoNodNou[3]
        costTaran = 1
        costUnitateCompA = None
        costUnitateCompB = None
        ################################## pleaca barca cu taranul ###########################
        malEvacuat = None  # 0 daca era malInitial si 1 daca era malFinal

        if malTaran == "initial":
            malEvacuat = 0
        elif malTaran == "final":
            malEvacuat = 1

        # imbarc pentru containerul A
        if compartimentA[1] == "verze":
            infoNodNou[malEvacuat][0] -= compartimentA[0]
            costUnitateCompA = 1
        elif compartimentA[1] == "capre":
            infoNodNou[malEvacuat][1] -= compartimentA[0]
            costUnitateCompA = 2
        elif compartimentA[1] == "lupi":
            infoNodNou[malEvacuat][2] -= compartimentA[0]
            costUnitateCompA = 3

        # imbarc pentru containerul B (cu 50% mai mult)
        if compartimentB[1] == "verze":
            infoNodNou[malEvacuat][0] -= compartimentB[0]
            costUnitateCompB = 1 * 1.5
        elif compartimentB[1] == "capre":
            infoNodNou[malEvacuat][1] -= compartimentB[0]
            costUnitateCompB = 2 * 1.5
        elif compartimentB[1] == "lupi":
            infoNodNou[malEvacuat][2] -= compartimentB[0]
            costUnitateCompB = 3 * 1.5

        vcl_malFinal = infoNodNou[1]  # vom folosi magazia
        listaInfoNodNou.append(infoNodNou)  # nodul in care nu folosesc magazia

        ############################## generez toate cazurile in care folosesc magazia #########################################

        if nr_tip_magazie[1] == "gol":  # magazie libera

            if vcl_malFinal[1] > 0 and vcl_malFinal[0] > 0:  # daca avem verze ce pot fi mancate de capre (v>0 and c>0)
                mag = min(self.__class__.nr_magazie, vcl_malFinal[0])  # punem verze in magazie
                infoNodNouModificat = copy.deepcopy(infoNodNou)
                infoNodNouModificat[3] = [mag, "verze"]
                infoNodNouModificat[1][0] -= mag  # actualizam verzele de pe malFinal
                listaInfoNodNou.append(infoNodNouModificat)

            if vcl_malFinal[1] > 0 and vcl_malFinal[2] > 0:  # daca avem capre ce pot fi mancate de lupi (c>0 and l>0)
                mag = min(self.__class__.nr_magazie, vcl_malFinal[1])  # punem caprele in magazie
                infoNodNouModificat = copy.deepcopy(infoNodNou)
                infoNodNouModificat[3] = [mag, "capre"]
                infoNodNouModificat[1][1] -= mag  # actualizam capre malFinal
                listaInfoNodNou.append(infoNodNouModificat)

            if vcl_malFinal[2] > 0 and vcl_malFinal[0] == 0 and vcl_malFinal[
                1] == 0:  # daca lupii se mananca intre ei (l>0 and c=0 and v=0)
                mag = min(self.__class__.nr_magazie, vcl_malFinal[2])  # punem lupi in magazie
                infoNodNouModificat = copy.deepcopy(infoNodNou)
                infoNodNouModificat[3] = [mag, "lupi"]
                infoNodNouModificat[1][2] -= mag  # actualizam lupi malFinal
                listaInfoNodNou.append(infoNodNouModificat)

        elif malTaran == "final":  # scoatem din magazie elemente
            if nr_tip_magazie[1] == "verze":  # vrem sa hranim caprele, deci eliberam verzele
                mag = nr_tip_magazie[0]
                infoNodNouModificat = copy.deepcopy(infoNodNou)
                infoNodNouModificat[3] = [0, "gol"]
                infoNodNouModificat[1][0] += mag
                listaInfoNodNou.append(infoNodNouModificat)


            elif nr_tip_magazie[1] == "capre" and vcl_malFinal[0] > 0:  # vrem sa mancam verzele, deci eliberam caprele
                mag = nr_tip_magazie[0]
                infoNodNouModificat = copy.deepcopy(infoNodNou)
                infoNodNouModificat[3] = [0, "gol"]
                infoNodNouModificat[1][1] += mag
                listaInfoNodNou.append(infoNodNouModificat)


            elif nr_tip_magazie[1] == "lupi" and vcl_malFinal[1] > 0:  # vrem sa mancam caprele, deci eliberam lupii
                mag = nr_tip_magazie[0]
                infoNodNouModificat = copy.deepcopy(infoNodNou)
                infoNodNouModificat[3] = [0, "gol"]
                infoNodNouModificat[1][2] += mag
                listaInfoNodNou.append(infoNodNouModificat)

        ######################################################################################################################
        ##########################################  soseste barca pe celalalt mal ################################################
        malAterizat = None  # 1 pt initial 0 pt final
        if malTaran == "initial":
            malAterizat = 1
        elif malTaran == "final":
            malAterizat = 0
        for i in range(len(listaInfoNodNou)):
            listaInfoNodNou[i][malAterizat] = self.seManancaAnimale(
                listaInfoNodNou[i][malAterizat])  # animalele au mancat intre timp
            # debarc containerul A
            if compartimentA[1] == "verze":
                listaInfoNodNou[i][malAterizat][0] += compartimentA[0]
            elif compartimentA[1] == "capre":
                listaInfoNodNou[i][malAterizat][1] += compartimentA[0]
            elif compartimentA[1] == "lupi":
                listaInfoNodNou[i][malAterizat][2] += compartimentA[0]
            # debarc  containerul B
            if compartimentB[1] == "verze":
                listaInfoNodNou[i][malAterizat][0] += compartimentB[0]
            elif compartimentB[1] == "capre":
                listaInfoNodNou[i][malAterizat][1] += compartimentB[0]
            elif compartimentB[1] == "lupi":
                listaInfoNodNou[i][malAterizat][2] += compartimentB[0]
            listaInfoNodNou[i][2] = self.schimbaMal(malTaran)
            # am eliberat compartimentele in acest nod de parcurgere
            listaInfoNodNou[i][4] = listaInfoNodNou[i][5] = [0, "gol"]
        ######################################################################################################################
        costSuccesor = None
        # calculam costul transportului curent
        if compartimentA[1] == compartimentB[1] == 'gol':  # doar taranul
            costSuccesor = costTaran
        elif compartimentB[1] == "gol" and compartimentA[1] != "gol":
            costSuccesor = costTaran + costUnitateCompA * compartimentA[0]
        elif compartimentA[1] == "gol" and compartimentB[1] != "gol":
            costSuccesor = costTaran + costUnitateCompB * compartimentB[0]
        else:
            costSuccesor = costTaran + costUnitateCompA * compartimentA[0] + costUnitateCompB * compartimentB[0]
        for i in range(len(listaInfoNodNou)):
            if not nodCurent.contineInDrum(listaInfoNodNou[i]):
                parinte = copy.deepcopy(nodCurent)
                parinte.info = list(parinte.info)
                parinte.info[4], parinte.info[
                    5] = compartimentA, compartimentB  # am nevoie la afisarea arborelui de parcurgere
                parinte.info = tuple(parinte.info)
                succesor = NodParcurgere(listaInfoNodNou[i], parinte=parinte, cost=parinte.g + costSuccesor,
                                         h=self.calculeaza_h(listaInfoNodNou[i], tip_euristica, parinte=parinte,
                                                             costSuccesor=costSuccesor))
                listaSuccesori.append(succesor)

    def schimbaMal(self, malTaran):
        malTaran = "final" if (malTaran == "initial") else "initial"  # switch
        return malTaran

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        listaSuccesori = []

        vcl_malInitial = nodCurent.info[0]
        vcl_malFinal = nodCurent.info[1]
        malTaran = nodCurent.info[2]
        nr_tip_magazie = nodCurent.info[3]

        nrVerze, nrCapre, nrLupi = list(
            map(operator.add, vcl_malInitial, vcl_malFinal))  # totalul(v_i + v_f, c_i + c_f, l_i + l_f)

        # adunam la nr de v/c/l ce se afla in magazie
        if nr_tip_magazie[1] == "capre":
            nrCapre += nr_tip_magazie[0]
        elif nr_tip_magazie[1] == "verze":
            nrVerze += nr_tip_magazie[0]
        elif nr_tip_magazie[1] == "lupi":
            nrLupi += nr_tip_magazie[0]

        # ne oprim daca nu putem avea minimul cerut ca stare finala
        if not all(x >= y for x, y in zip((nrVerze, nrCapre, nrLupi), self.__class__.stare_finala)):
            return None

        # daca barca e goala in nodCurent, voi incarca barca
        if nodCurent.info[4][1] == nodCurent.info[5][1] == "gol":  # comp A si B sunt goale
            for i, tip_elem1 in enumerate(("verze", "capre", "lupi")):
                for j, tip_elem2 in enumerate(("verze", "capre", "lupi")):
                    a = b = None
                    if malTaran == "initial":
                        a = min(self.__class__.nr_compA,
                                vcl_malInitial[i])  # min (compA, nr de elem indicate de i (v/c/l))
                        if tip_elem1 == tip_elem2:
                            # a = cate elem am pus in compA
                            b = min(self.__class__.nr_compB,
                                    max(vcl_malInitial[j] - a, 0))  # min (compB, max(nr - compA, 0))
                        else:
                            b = min(self.__class__.nr_compB, vcl_malInitial[j])

                    elif malTaran == "final":
                        a = min(self.__class__.nr_compA, vcl_malFinal[i])
                        if tip_elem1 == tip_elem2:
                            b = min(self.__class__.nr_compB, max(vcl_malFinal[j] - a, 0))
                        else:
                            b = min(self.__class__.nr_compB, vcl_malFinal[j])

                    for elem1 in reversed(range(1, a + 1)):
                        for elem2 in reversed(range(1, b + 1)):
                            compA_nou = [elem1, tip_elem1]
                            compB_nou = [elem2, tip_elem2]
                            self.adaugaCelPutinUnSuccesor(nodCurent, listaSuccesori, compA_nou, compB_nou,
                                                          tip_euristica)

                # iteratiile cu compartimentul B gol
                for elem1 in reversed(range(1, a + 1)):
                    compA_nou = [elem1, tip_elem1]
                    compB_nou = [0, "gol"]
                    self.adaugaCelPutinUnSuccesor(nodCurent, listaSuccesori, compA_nou, compB_nou, tip_euristica)

        compA_nou = compB_nou = [0, "gol"]
        self.adaugaCelPutinUnSuccesor(nodCurent, listaSuccesori, compA_nou, compB_nou,
                                      tip_euristica)  # singura iteratie(succesor) cu ambele compartimente goale

        return listaSuccesori


def citire_parametrii():
    def make_path_sane(p):
        """Function to uniformly return a real, absolute filesystem path."""
        p = os.path.expanduser(p)
        # A/.//B -> A/B
        p = os.path.normpath(p)
        # Resolve symbolic links
        p = os.path.realpath(p)
        # Ensure path is absolute
        p = os.path.abspath(p)
        p += '//'
        return p

    parser = ArgumentParser()
    parser.add_argument('-i', '--folderInput', dest='folderInput', required=True)
    parser.add_argument('-o', '--folderOutput', dest='folderOutput', required=True)
    parser.add_argument('-nrsol', '--nr', dest='nrsolutii', default=1)
    parser.add_argument('-timeout', '--time', dest='timeout', default=60)

    args = parser.parse_args()
    caleFolderInput = make_path_sane(args.folderInput)
    caleFolderOutput = make_path_sane(args.folderOutput)
    nrSol = int(args.nrsolutii)
    timeout = float(args.timeout)
    return caleFolderInput, caleFolderOutput, nrSol, timeout


def citeste_fisier(caleFisier):
    """
    N1 - cati lupi mananca un lup
    N2 - cate capre mananca un lup
    N3 - cate verze mananca 0 capra
    """
    f = open(caleFisier, "r")
    textFisier = f.read()
    listaInfoFisier = textFisier.split("\n")
    stare_initiala = list(int(x) for x in listaInfoFisier[0].split() if x.isdecimal())
    nr_compA, nr_compB, nr_magazie = [int(y) for y in listaInfoFisier[1].split()]

    N1, N2, N3 = [int(z) for z in listaInfoFisier[2].replace(',', ' ').replace(':', ' ').split() if z.isdigit()]
    stare_finala = list(int(w) for w in listaInfoFisier[3].split(' ') if w.isdigit())

    if nr_compA < 0 or nr_compB < 0 or nr_magazie < 0 or nr_magazie < 0:
        return "validare inputului esuata"
    if N1 < 0 or N2 < 0 or N3 < 0:
        return "validarea inputului esuata"
    if any(x < 0 for x in stare_finala) or any(x < 0 for x in stare_initiala) or len(stare_finala) != 3 or len(
            stare_initiala) != 3:
        return "validarea inputului esuata"

    return N1, N2, N3, nr_compA, nr_compB, nr_magazie, stare_initiala, stare_finala


@stopit.threading_timeoutable(default="intrat in timeout")
def a_star(gr, nrSolutiiCautate, tip_euristica, writer):
    # in coada vom avea doar noduri de tip Nod-
    # Parcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]

    writer.write("***********************\n")
    writer.write("Solutii obtinute cu A*:" + '\n\n')
    startTime = time.time()
    while len(c) > 0:
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent.info):
            nodCurent.afisDrum(writer)
            writer.write("\n\n----------------\n\n")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return "functie finalizata"
        else:
            lSuccesori = gr.genereazaSuccesori(
                nodCurent, tip_euristica=tip_euristica)
            # print(lSuccesori)
            if lSuccesori is None:
                continue
            for s in lSuccesori:
                i = 0
                gasit_loc = False
                for i in range(len(c)):
                    if c[i].f >= s.f:
                        gasit_loc = True
                        break
                if gasit_loc:
                    c.insert(i, s)
                else:
                    c.append(s)


@stopit.threading_timeoutable(default="intrat in timeout")
def uniform_cost(gr, nrSolutiiCautate, tip_euristica, writer):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]

    writer.write("***********************\n")
    writer.write("Solutii obtinute cu UCS:" + '\n\n')
    startTime = time.time()
    while (len(c) > 0):
        nodCurent = c.pop(0)
        if gr.testeaza_scop(nodCurent.info):
            nodCurent.afisDrum(writer)
            writer.write("\n\n----------------\n\n")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return "functie finalizata"

        lSuccesori = gr.genereazaSuccesori(
            nodCurent, tip_euristica=tip_euristica)
        if lSuccesori is None:
            continue
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # ordonez dupa f
                if c[i].g >= s.g:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


@stopit.threading_timeoutable(default="intrat in timeout")
def a_star_optimizat(gr, nrSolutiiCautate, tip_euristica, writer):
    l_open = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]
    l_closed = []

    writer.write("***********************\n")
    writer.write("Solutii obtinute cu A* optimizat:" + '\n\n')
    startTime = time.time()
    while len(l_open) > 0:
        nodCurent = l_open.pop(0)
        l_closed.append(nodCurent)

        if gr.testeaza_scop(nodCurent.info):
            nodCurent.afisDrum(writer)
            writer.write("\n\n----------------\n\n")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return "functie finalizata"
        lSuccesori = gr.genereazaSuccesori(
            nodCurent, tip_euristica=tip_euristica)
        if lSuccesori is None:
            continue
        for s in lSuccesori:
            gasitC = False
            for nodC in l_open:
                if s.info == nodC.info:
                    gasitC = True
                    if s.f >= nodC.f:
                        lSuccesori.remove(s)
                    else:  # s.f<nodC.f
                        l_open.remove(nodC)
                    break
            if not gasitC:
                for nodC in l_closed:
                    if s.info == nodC.info:
                        if s.f >= nodC.f:
                            lSuccesori.remove(s)
                        else:  # s.f<nodC.f
                            l_closed.remove(nodC)
                        break
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(l_open)):
                # diferenta fata de UCS e ca ordonez crescator dupa f
                # daca f-urile sunt egale ordonez descrescator dupa g
                if l_open[i].f > s.f or (l_open[i].f == s.f and l_open[i].g <= s.g):
                    gasit_loc = True
                    break
            if gasit_loc:
                l_open.insert(i, s)
            else:
                l_open.append(s)


if __name__ == "__main__":
    caleFolderInput, caleFolderOutput, nrSolutiiCautate, timeout = citire_parametrii()

    files = [x for x in os.listdir(caleFolderInput) if os.path.isfile(os.path.join(caleFolderInput, x))]
    for numeFisierInput in files:
        numeFisierOutput = numeFisierInput.split('.')[0] + '.out'

        caleInput = caleFolderInput + numeFisierInput
        if citeste_fisier(caleInput) == "validarea inputului esuata":
            print("In fisierul " + numeFisierInput + " nu se poate valida inputul!")  # in consola
            continue

        N1, N2, N3, nr_compA, nr_compB, nr_magazie, stare_initiala, stare_finala = citeste_fisier(caleInput)

        caleOutput = caleFolderOutput + numeFisierOutput
        gr = Graph(N1, N2, N3, nr_compA, nr_compB, nr_magazie, stare_initiala, stare_finala)

        NodParcurgere.gr = gr

        f = open(caleOutput, "w")
        f.truncate(0)

        # ! A*
        f.write("\nEuristica banala\n")
        mesaj = a_star(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica banala", timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la A*" + '\n\n\n')

        f.write("\nEuristica admisibila 1\n")
        mesaj = a_star(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica admisibila 1", timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la A*" + '\n\n\n')

        f.write("\nEuristica admisibila 2\n")
        mesaj = a_star(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica admisibila 2", timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la A*" + '\n\n\n')

        f.write("\nEuristica neadmisibila\n")
        mesaj = a_star(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica neadmisibila", timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la A*" + '\n\n\n')

        # ! UCS
        f.write("\nEuristica banala\n")
        mesaj = uniform_cost(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica banala", timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la UCS" + '\n\n\n')

        f.write("\nEuristica admisibila 1\n")
        mesaj = uniform_cost(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica admisibila 1", timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la UCS" + '\n\n\n')

        f.write("\nEuristica admisibila 2\n")
        mesaj = uniform_cost(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica admisibila 2", timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la UCS" + '\n\n\n')

        f.write("\nEuristica neadmisibila\n")
        mesaj = uniform_cost(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica neadmisibila", timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la UCS" + '\n\n\n')

        # ! A* optimizat
        f.write("\nEuristica banala\n")
        mesaj = a_star_optimizat(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica banala", timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la A* optimizat" + '\n\n\n')

        f.write("\nEuristica admisibila 1\n")
        mesaj = a_star_optimizat(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica admisibila 1",
                                 timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la A* optimizat" + '\n\n\n')

        f.write("\nEuristica admisibila 2\n")
        mesaj = a_star_optimizat(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica admisibila 2",
                                 timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la A* optimizat" + '\n\n\n')

        f.write("\nEuristica neadmisibila\n")
        mesaj = a_star_optimizat(gr, nrSolutiiCautate, writer=f, tip_euristica="euristica neadmisibila",
                                 timeout=timeout)
        if mesaj == "intrat in timeout":
            f.write("\n\nTimeout la A* optimizat" + '\n\n\n')

        f.close()
