#Aluno: João Pedro Felix Veloso e Artur Anderson

from typing import Dict, Tuple

BRANCO = "B"
ESQUERDA, DIREITA, PARADO = "L", "R", "S"


FUNCOES = {
    "and": lambda a, b: str(int(a) & int(b)),
    "or":  lambda a, b: str(int(a) | int(b)),
    "xor": lambda a, b: str(int(a) ^ int(b)),
}

SIMBOLO_OP = {"and": "A", "or": "O", "xor": "X"}
MARCA = {"0": "x", "1": "y"} 


def construir_transicoes() -> Dict[Tuple[str, str, str], Tuple[str, str, str, str, str]]:

    d: Dict[Tuple[str, str, str], Tuple[str, str, str, str, str]] = {}

   
    for op, simb in SIMBOLO_OP.items():
        d[("q0", simb, BRANCO)] = (f"q1_{op}", simb, BRANCO, DIREITA, PARADO)

    for op in FUNCOES:
       
        d[(f"q1_{op}", "x", BRANCO)] = (f"q1_{op}", "x", BRANCO, DIREITA, PARADO)
        d[(f"q1_{op}", "y", BRANCO)] = (f"q1_{op}", "y", BRANCO, DIREITA, PARADO)
        d[(f"q1_{op}", "0", BRANCO)] = (f"q2_{op}_0", MARCA["0"], BRANCO, DIREITA, PARADO)
        d[(f"q1_{op}", "1", BRANCO)] = (f"q2_{op}_1", MARCA["1"], BRANCO, DIREITA, PARADO)
        d[(f"q1_{op}", "#", BRANCO)] = ("q_aceita", "#", BRANCO, PARADO, PARADO)

        for b1 in ("0", "1"):
            estado2 = f"q2_{op}_{b1}"
            estado3 = f"q3_{op}_{b1}"
            estado_rewind = f"q_rewind_{op}"

           
            for s in ("0", "1", "x", "y"):
                d[(estado2, s, BRANCO)] = (estado2, s, BRANCO, DIREITA, PARADO)
            d[(estado2, "#", BRANCO)] = (estado3, "#", BRANCO, DIREITA, PARADO)

            for s in ("x", "y"):
                d[(estado3, s, BRANCO)] = (estado3, s, BRANCO, DIREITA, PARADO)
            for b2 in ("0", "1"):
                r = FUNCOES[op](b1, b2)
                d[(estado3, b2, BRANCO)] = (
                    estado_rewind, MARCA[b2], r, DIREITA, DIREITA,
                )


        estado_rewind = f"q_rewind_{op}"
        for s in ("0", "1", "x", "y", "#", BRANCO):
            d[(estado_rewind, s, BRANCO)] = (estado_rewind, s, BRANCO, ESQUERDA, PARADO)

        d[(estado_rewind, SIMBOLO_OP[op], BRANCO)] = (
            f"q1_{op}", SIMBOLO_OP[op], BRANCO, DIREITA, PARADO,
        )

    return d


TRANSICOES = construir_transicoes()



class MaquinaDeTuring2Fitas:
    def __init__(self, transicoes, estado_inicial="q0", estados_finais=("q_aceita",)):
        self.transicoes = transicoes
        self.estado_inicial = estado_inicial
        self.estados_finais = set(estados_finais)

    def _ler(self, fita, pos):
        return fita[pos] if 0 <= pos < len(fita) else BRANCO

    def _escrever(self, fita, pos, simbolo):
        if pos < 0:
            raise IndexError("Cabeça foi além do início da fita (posição negativa).")
        while pos >= len(fita):
            fita.append(BRANCO)
        fita[pos] = simbolo

    def executar(self, entrada: str, mostrar_passos: bool = True, limite_passos: int = 100000):
        fita1 = list(entrada)
        fita2 = []  
        h1 = h2 = 0
        estado = self.estado_inicial
        passo = 0

        historico = []

        while True:
            passo += 1
            if passo > limite_passos:
                raise RuntimeError("Número máximo de passos excedido (possível loop).")

            conf = {
                "passo": passo,
                "estado": estado,
                "fita1": "".join(fita1) or BRANCO,
                "h1": h1,
                "fita2": "".join(fita2) or BRANCO,
                "h2": h2,
            }
            historico.append(conf)
            if mostrar_passos:
                print(
                    f"  passo {passo:>3} | estado={estado:<12} | "
                    f"fita1='{conf['fita1']}' (cabeça1={h1}) | "
                    f"fita2='{conf['fita2']}' (cabeça2={h2})"
                )

            if estado in self.estados_finais:
                break

            s1 = self._ler(fita1, h1)
            s2 = self._ler(fita2, h2)
            chave = (estado, s1, s2)
            if chave not in self.transicoes:
                raise ValueError(
                    f"Transição não definida para (estado={estado}, X1={s1!r}, X2={s2!r}). "
                    f"Entrada inválida ou fora do domínio da máquina."
                )
            novo_estado, y1, y2, d1, d2 = self.transicoes[chave]
            self._escrever(fita1, h1, y1)
            self._escrever(fita2, h2, y2)
            h1 += {"L": -1, "R": 1, "S": 0}[d1]
            h2 += {"L": -1, "R": 1, "S": 0}[d2]
            estado = novo_estado

        resultado = "".join(fita2).rstrip(BRANCO) or "0"
        
        resultado = "".join(c for c in fita2 if c != BRANCO)
        return resultado, historico


def rodar_teste(mt: MaquinaDeTuring2Fitas, entrada: str, esperado: str, mostrar_passos: bool = True):
    print(f"\nEntrada: {entrada}")
    if mostrar_passos:
        print("Execução passo a passo:")
    obtido, historico = mt.executar(entrada, mostrar_passos=mostrar_passos)
    status = "OK" if obtido == esperado else "FALHOU"
    print(f"  entrada={entrada}  ->  esperado={esperado}  ->  obtido={obtido}   [{status}]")
    return obtido == esperado


if __name__ == "__main__":
    mt = MaquinaDeTuring2Fitas(TRANSICOES)

    casos_de_teste = [
        ("A0#0", "0"),
        ("A101#110", "100"),
        ("O01#11", "11"),
        ("O101#110", "111"),
        ("X01#11", "10"),
        ("X101#110", "011"),
      
        ("A1100#1010", "1000"),
        ("O0000#0000", "0000"),
        ("X111#000", "111"),
    ]

   
    print("TESTES DA MÁQUINA DE TURING DE DUAS FITAS")
  

    todos_ok = True
    for entrada, esperado in casos_de_teste:
        ok = rodar_teste(mt, entrada, esperado, mostrar_passos=True)
        todos_ok = todos_ok and ok

  
    print("RESULTADO GERAL:", "TODOS OS TESTES PASSARAM" if todos_ok else "HÁ TESTES COM FALHA")
  
