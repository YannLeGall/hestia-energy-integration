"""Rebuild the embedded regulated tariffs (engine/data/tarifs-reglementes.json) from the CRE's own open data.

The CRE publishes every Tarif Bleu residential grid since 2012, tax included, on data.gouv.fr (« Historique des tarifs
réglementés de vente d'électricité pour les consommateurs résidentiels »). Run it at each change of price (1 February,
1 August), check the diff, and ship it with the next version (decision D15):

    python scripts/tarifs_cre.py                 # downloads the three CSV files
    python scripts/tarifs_cre.py base.csv hphc.csv tempo.csv

Only the periods are rewritten; the other keys of the file (the resale prices, the notes) are kept.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import sys
import urllib.request

FILE = Path(__file__).resolve().parents[1] / "custom_components" / "hestia_energy" / "engine" / "data" / "tarifs-reglementes.json"
DATASET = "https://www.data.gouv.fr/fr/datasets/historique-des-tarifs-reglementes-de-vente-delectricite-pour-les-consommateurs-residentiels/"
RESOURCES = {
    "base": "https://www.data.gouv.fr/fr/datasets/r/c13d05e5-9e55-4d03-bf7e-042a2ade7e49",
    "hphc": "https://www.data.gouv.fr/fr/datasets/r/f7303b3a-93c7-4242-813d-84919034c416",
    "tempo": "https://www.data.gouv.fr/fr/datasets/r/0c3d1d36-c412-4620-8566-e5cbb4fa2b5a",
}


def _rows(source: str) -> list[dict]:
    if source.startswith("http"):
        # data.gouv.fr refuses requests without a client name.
        request = urllib.request.Request(source, headers={"User-Agent": "hestia-energy-tarifs"})
        with urllib.request.urlopen(request, timeout=30) as answer:  # noqa: S310 - the CRE's own files
            text = answer.read().decode("utf-8-sig")
    else:
        text = Path(source).read_text(encoding="utf-8-sig")
    return list(csv.DictReader(io.StringIO(text), delimiter=";"))


def _num(text: str | None) -> float | None:
    text = (text or "").strip().replace(",", ".")
    # Some subscriptions come with stray decimals (« 239,8378787 » for 239,84 €): a price is to the cent, a kWh to 0.1 c€.
    return round(float(text), 4) if text else None


def _cents(text: str | None) -> float | None:
    value = _num(text)
    return None if value is None else round(value, 2)


def _iso(text: str) -> str | None:
    text = (text or "").strip()
    if not text:
        return None
    d, m, y = text.split("/")
    return f"{y}-{m}-{d}"


def build(base: list[dict], hphc: list[dict], tempo: list[dict]) -> list[dict]:
    periods: dict[tuple, dict] = {}

    def period(row):
        key = (_iso(row["DATE_DEBUT"]), _iso(row["DATE_FIN"]))
        return periods.setdefault(key, {"debut": key[0], "fin": key[1], "base": None, "hphc": None, "tempo": None, "ejp": None})

    for row in base:
        p, kva = period(row), str(int(float(row["P_SOUSCRITE"])))
        grid = p["base"] = p["base"] or {"abonnement_an": {}, "prix": {}}
        grid["abonnement_an"][kva] = _cents(row["PART_FIXE_TTC"])
        grid.setdefault("abonnement_an_ht", {})[kva] = _cents(row["PART_FIXE_HT"])
        grid["prix"][kva] = _num(row["PART_VARIABLE_TTC"])
    for row in hphc:
        p, kva = period(row), str(int(float(row["P_SOUSCRITE"])))
        grid = p["hphc"] = p["hphc"] or {"abonnement_an": {}, "prix": {}}
        grid["abonnement_an"][kva] = _cents(row["PART_FIXE_TTC"])
        grid.setdefault("abonnement_an_ht", {})[kva] = _cents(row["PART_FIXE_HT"])
        # The same two prices for every power since 2012; the first row's are kept.
        grid["prix"].setdefault("hp", _num(row["PART_VARIABLE_HP_TTC"]))
        grid["prix"].setdefault("hc", _num(row["PART_VARIABLE_HC_TTC"]))
    for row in tempo:
        p, kva = period(row), str(int(float(row["P_SOUSCRITE"])))
        grid = p["tempo"] = p["tempo"] or {"abonnement_an": {}, "prix": {}, "heures_creuses": "22:00-06:00",
                                           "jours_rouges_par_an": 22, "jours_blancs_par_an": 43}
        grid["abonnement_an"][kva] = _cents(row["PART_FIXE_TTC"])
        grid.setdefault("abonnement_an_ht", {})[kva] = _cents(row["PART_FIXE_HT"])
        if kva == "30":
            # The CRE gives one line for « 24-30 kVA », filed under 30.
            grid["abonnement_an"].setdefault("24", _cents(row["PART_FIXE_TTC"]))
        for colour, name in (("bleu", "Bleu"), ("blanc", "Blanc"), ("rouge", "Rouge")):
            grid["prix"].setdefault(colour, {"hc": _num(row[f"PART_VARIABLE_HC{name}_TTC"]),
                                             "hp": _num(row[f"PART_VARIABLE_HP{name}_TTC"])})
    return sorted(periods.values(), key=lambda p: p["debut"], reverse=True)


def main(args: list[str]) -> None:
    sources = args if len(args) == 3 else [RESOURCES["base"], RESOURCES["hphc"], RESOURCES["tempo"]]
    table = json.loads(FILE.read_text(encoding="utf-8"))
    table["periodes"] = build(*(_rows(s) for s in sources))
    table["sources"] = [DATASET, *RESOURCES.values()]
    table["a_verifier"] = None
    table["_lisez_moi"] = ("Tarif Bleu résidentiel (tarifs réglementés), en euros TTC, tels que la CRE les publie sur data.gouv.fr "
                           "(scripts/tarifs_cre.py). Abonnement par an, prix par kWh. Une période par changement de prix. "
                           "Embarqué dans Hestia Énergie et mis à jour à chaque version (décision D15). Une valeur absente est "
                           "inconnue : la brique ne la remplace jamais.")
    first = table["periodes"][0]["debut"] if table["periodes"] else "?"
    table["version"] = first
    FILE.write_text(json.dumps(table, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(table['periodes'])} périodes, de {table['periodes'][-1]['debut']} à {first}")


if __name__ == "__main__":
    main(sys.argv[1:])
