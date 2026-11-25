#!/usr/bin/env python3
"""Acrescenta ao resultados.json os concursos da Lotofácil que ainda não estão nele.

Fonte principal: API pública do portal de loterias da Caixa.
Fonte reserva: API comunitária loteriascaixa-api (usada só se a da Caixa falhar).

Uso:  python scripts/atualizar_resultados.py
"""
import json
import pathlib
import sys
import time
import urllib.request

ARQ = pathlib.Path(__file__).resolve().parent.parent / "resultados.json"
FONTES = [
    ("Caixa", "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{n}"),
    ("loteriascaixa-api", "https://loteriascaixa-api.herokuapp.com/api/lotofacil/{n}"),
]
MAX_POR_EXECUCAO = 60


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (atualizador lotofacil)", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def extrair(dados):
    """Devolve (numero, [15 dezenas], extras) para os dois formatos de resposta conhecidos.

    extras (opcional): {"o": ordem do sorteio, "d": data, "p": prêmio de 15 acertos}.
    """
    numero = dados.get("numero") or dados.get("concurso")
    dezenas = dados.get("listaDezenas") or dados.get("dezenas") or dados.get("dezenasSorteadasOrdemSorteio")
    if numero is None or not dezenas:
        raise ValueError("resposta sem número ou dezenas")
    dz = sorted(int(x) for x in dezenas)
    if len(dz) != 15 or len(set(dz)) != 15 or not all(1 <= d <= 25 for d in dz):
        raise ValueError(f"dezenas inválidas: {dz}")
    extras = {}
    try:
        ordem = dados.get("dezenasSorteadasOrdemSorteio") or dados.get("dezenasOrdemSorteio")
        if ordem:
            o = [int(x) for x in ordem]
            if sorted(o) == dz:
                extras["o"] = o
        data = dados.get("dataApuracao") or dados.get("data")
        if data:
            extras["d"] = str(data)[:10]
        for f in (dados.get("listaRateioPremio") or dados.get("premiacoes") or []):
            if f.get("faixa") == 1 or "15" in str(f.get("descricaoFaixa") or f.get("descricao") or ""):
                if f.get("valorPremio"):
                    extras["p"] = float(f["valorPremio"])
                break
    except Exception:
        extras = {}
    return int(numero), dz, extras


def buscar(n):
    """n = número do concurso, ou '' para o mais recente."""
    erros = []
    for nome, modelo in FONTES:
        url = modelo.format(n=n if n != "" else "").rstrip("/")
        if n == "" and nome == "loteriascaixa-api":
            url = modelo.format(n="latest")
        try:
            return extrair(baixar(url)), nome
        except Exception as e:  # tenta a próxima fonte
            erros.append(f"{nome}: {e}")
    raise RuntimeError("; ".join(erros))


def main():
    base = json.loads(ARQ.read_text(encoding="utf-8"))
    ultimo = max(r[0] for r in base)
    (num_rec, _, _), fonte = buscar("")
    print(f"Base vai até {ultimo}. Último concurso disponível: {num_rec} (fonte: {fonte}).")
    novos = 0
    for n in range(ultimo + 1, min(num_rec, ultimo + MAX_POR_EXECUCAO) + 1):
        (num, dz, ext), fonte = buscar(n)
        if num != n:
            raise RuntimeError(f"pedi o concurso {n} e recebi o {num}")
        base.append([n] + dz + ([ext] if ext else []))
        novos += 1
        print(f"  + {n}: {' '.join(f'{d:02d}' for d in dz)} ({fonte})")
        time.sleep(1)
    if novos:
        base.sort(key=lambda r: r[0])
        ARQ.write_text("[\n" + ",\n".join(json.dumps(r, separators=(",", ":")) for r in base) + "\n]\n", encoding="utf-8")
    print(f"{novos} concurso(s) novo(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Falha ao atualizar: {e}", file=sys.stderr)
        sys.exit(1)
