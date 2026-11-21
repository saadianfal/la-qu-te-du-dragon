#!/usr/bin/env python3
"""Mini jeu de rôle en console. Lancer avec : python rpg.py"""
import random
import time


def pause(s=0.6):
    time.sleep(s)


def demander(texte, choix):
    """Demande un choix valide parmi une liste de chaînes."""
    while True:
        rep = input(texte).strip().lower()
        if rep in choix:
            return rep
        print("Choix invalide.")


class Entite:
    def __init__(self, nom, pv, attaque, defense):
        self.nom = nom
        self.pv = pv
        self.pv_max = pv
        self.attaque = attaque
        self.defense = defense

    def est_vivant(self):
        return self.pv > 0

    def degats_contre(self, cible, bonus=0):
        base = self.attaque + bonus + random.randint(-2, 3)
        return max(1, base - cible.defense)

    def subir(self, degats):
        self.pv = max(0, self.pv - degats)


class Joueur(Entite):
    CLASSES = {
        "1": ("Guerrier", 40, 8, 4, "Coup puissant (x2 dégâts)"),
        "2": ("Mage", 28, 6, 2, "Boule de feu (dégâts ignorant la défense)"),
        "3": ("Voleur", 32, 7, 3, "Attaque sournoise (coup critique garanti)"),
    }

    def __init__(self, nom, classe):
        titre, pv, att, defn, _ = self.CLASSES[classe]
        super().__init__(nom, pv, att, defn)
        self.classe = titre
        self.niveau = 1
        self.xp = 0
        self.or_ = 20
        self.potions = 2
        self.mana = 3
        self.mana_max = 3

    def xp_suivant(self):
        return self.niveau * 20

    def gagner_xp(self, xp):
        self.xp += xp
        while self.xp >= self.xp_suivant():
            self.xp -= self.xp_suivant()
            self.niveau += 1
            self.pv_max += 8
            self.pv = self.pv_max
            self.attaque += 2
            self.defense += 1
            self.mana_max += 1
            self.mana = self.mana_max
            print(f"\n*** NIVEAU {self.niveau} ! Vos stats augmentent. ***")

    def competence(self, cible):
        """Utilise la compétence de classe. Retourne les dégâts infligés."""
        if self.classe == "Guerrier":
            d = self.degats_contre(cible) * 2
        elif self.classe == "Mage":
            d = self.attaque + 6 + random.randint(0, 4)
        else:
            d = (self.attaque + 4) * 2 - cible.defense
        d = max(1, d)
        cible.subir(d)
        return d

    def statut(self):
        return (f"{self.nom} ({self.classe}) Niv.{self.niveau} | "
                f"PV {self.pv}/{self.pv_max} | Mana {self.mana}/{self.mana_max} | "
                f"XP {self.xp}/{self.xp_suivant()} | Or {self.or_} | Potions {self.potions}")


MONSTRES = [
    ("Gobelin", 18, 5, 1, 10, 8),
    ("Loup", 22, 6, 2, 14, 6),
    ("Squelette", 26, 7, 3, 18, 12),
    ("Orc", 34, 9, 4, 28, 18),
    ("Troll", 45, 11, 5, 40, 30),
]


def creer_monstre(niveau):
    nom, pv, att, defn, xp, gold = random.choice(MONSTRES[: min(len(MONSTRES), 2 + niveau // 2)])
    m = Entite(nom, pv + niveau * 3, att + niveau // 2, defn)
    m.xp, m.or_ = xp, gold
    return m


def combat(joueur, monstre, boss=False):
    print(f"\n⚔  Un {monstre.nom} apparaît !")
    pause()
    while joueur.est_vivant() and monstre.est_vivant():
        print(f"\n{joueur.nom}: {joueur.pv}/{joueur.pv_max} PV | "
              f"{monstre.nom}: {monstre.pv}/{monstre.pv_max} PV")
        print("1) Attaquer  2) Compétence (1 mana)  3) Potion  4) Fuir")
        c = demander("> ", {"1", "2", "3", "4"})

        if c == "1":
            d = joueur.degats_contre(monstre)
            monstre.subir(d)
            print(f"Vous infligez {d} dégâts.")
        elif c == "2":
            if joueur.mana < 1:
                print("Plus de mana !")
                continue
            joueur.mana -= 1
            d = joueur.competence(monstre)
            print(f"Compétence ! Vous infligez {d} dégâts.")
        elif c == "3":
            if joueur.potions < 1:
                print("Plus de potions !")
                continue
            joueur.potions -= 1
            soin = 20
            joueur.pv = min(joueur.pv_max, joueur.pv + soin)
            print(f"Vous récupérez {soin} PV.")
        else:
            if boss:
                print("Impossible de fuir un boss !")
            elif random.random() < 0.5:
                print("Vous vous enfuyez !")
                return False
            else:
                print("Fuite ratée !")

        if not monstre.est_vivant():
            break
        pause()
        if random.random() < 0.1:
            print(f"Le {monstre.nom} rate son attaque.")
        else:
            d = monstre.degats_contre(joueur)
            joueur.subir(d)
            print(f"Le {monstre.nom} vous inflige {d} dégâts.")

    if joueur.est_vivant():
        print(f"\nVictoire ! +{monstre.xp} XP, +{monstre.or_} or.")
        joueur.or_ += monstre.or_
        joueur.mana = min(joueur.mana_max, joueur.mana + 1)
        joueur.gagner_xp(monstre.xp)
        return True
    return False


def boutique(joueur):
    while True:
        print(f"\n=== BOUTIQUE === (Or : {joueur.or_})")
        print("1) Potion (15 or)  2) Épée +2 attaque (40 or)  3) Armure +2 défense (40 or)  4) Partir")
        c = demander("> ", {"1", "2", "3", "4"})
        if c == "4":
            return
        prix = {"1": 15, "2": 40, "3": 40}[c]
        if joueur.or_ < prix:
            print("Pas assez d'or.")
            continue
        joueur.or_ -= prix
        if c == "1":
            joueur.potions += 1
        elif c == "2":
            joueur.attaque += 2
        else:
            joueur.defense += 2
        print("Achat effectué !")


def auberge(joueur):
    prix = 10
    if joueur.or_ < prix:
        print("Pas assez d'or pour dormir (10 or).")
        return
    joueur.or_ -= prix
    joueur.pv = joueur.pv_max
    joueur.mana = joueur.mana_max
    print("Vous dormez et récupérez toutes vos forces.")


def evenement(joueur):
    r = random.random()
    if r < 0.6:
        return combat(joueur, creer_monstre(joueur.niveau))
    if r < 0.8:
        gain = random.randint(5, 20)
        joueur.or_ += gain
        print(f"\nVous trouvez un coffre : +{gain} or !")
    elif r < 0.9:
        joueur.potions += 1
        print("\nVous trouvez une potion au bord du chemin !")
    else:
        d = random.randint(3, 8)
        joueur.subir(d)
        print(f"\nVous tombez dans un piège : -{d} PV.")
    return True


def main():
    print("=== LA QUÊTE DU DRAGON ===")
    nom = input("Nom de votre héros : ").strip() or "Héros"
    print("\nChoisissez votre classe :")
    for k, (t, pv, a, d, comp) in Joueur.CLASSES.items():
        print(f"{k}) {t} - PV {pv}, ATT {a}, DEF {d} - {comp}")
    joueur = Joueur(nom, demander("> ", set(Joueur.CLASSES)))

    print(f"\nBienvenue, {joueur.nom} le {joueur.classe}. Atteignez le niveau 5 pour défier le Dragon !")

    while joueur.est_vivant():
        print("\n" + joueur.statut())
        print("1) Explorer  2) Boutique  3) Auberge  4) Défier le Dragon  5) Quitter")
        c = demander("> ", {"1", "2", "3", "4", "5"})
        if c == "1":
            evenement(joueur)
        elif c == "2":
            boutique(joueur)
        elif c == "3":
            auberge(joueur)
        elif c == "4":
            if joueur.niveau < 5:
                print("Vous n'êtes pas assez fort (niveau 5 requis).")
                continue
            dragon = Entite("Dragon", 120, 16, 6)
            dragon.xp, dragon.or_ = 0, 0
            if combat(joueur, dragon, boss=True):
                print("\n🐉 Vous avez vaincu le Dragon ! Vous êtes un héros légendaire. FIN.")
                return
        else:
            print("À bientôt !")
            return

    print("\n💀 Vous êtes mort... GAME OVER.")


if __name__ == "__main__":
    main()