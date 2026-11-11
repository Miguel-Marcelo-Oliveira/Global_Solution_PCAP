import json
from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

# Pesos e limites da pontuação (explicados no README)
PONTOS_PALAVRA_CHAVE = 3
PONTOS_PALAVRA_TITULO = 1
MINIMO_PARA_RESPONDER = 3   # abaixo disso: "Não encontrei"
MINIMO_CONFIANCA_ALTA = 6

# Palavras comuns que não indicam assunto; não valem ponto no título
PALAVRAS_IGNORADAS = {"como", "para", "pode", "quem", "qual", "quais", "onde",
                      "quando", "isso", "esta", "esse", "essa", "sobre",
                      "preciso", "quero", "posso", "fazer", "minha", "meus"}

CAMPOS_OBRIGATORIOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
                       "documentos", "onde", "fonte", "verificado_em"]


def normalizar(texto):
    """
    Deixa o texto em minúsculas, sem acentos e sem pontuação.
    Devolve o texto com um espaço no começo e no fim, para comparar
    palavras inteiras (" sus " não casa com " sustentavel ").
    """
    texto = str(texto).lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """
    O conjunto de todas as orientações.
    Responsabilidade: ler o JSON, listar categorias e buscar a melhor orientação.
    """

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        """
        Lê o JSON e cria um objeto Orientacao por registro.
        Arquivo ausente, corrompido ou registro incompleto não travam o programa.
        """
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Aviso: base de conhecimento não encontrada em {self.caminho}.")
            return
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as erro:
            print(f"Aviso: não foi possível ler a base de conhecimento ({erro}).")
            return

        if not isinstance(dados, list):
            print("Aviso: a base de conhecimento deve ser uma lista de orientações.")
            return

        ignorados = 0
        for item in dados:
            if not self._registro_valido(item):
                ignorados += 1
                continue
            self.orientacoes.append(Orientacao(
                item["id"], item["categoria"], item["titulo"],
                item["palavras_chave"], item["resposta"], item["documentos"],
                item["onde"], item["fonte"], item["verificado_em"]))
        if ignorados:
            print(f"Aviso: {ignorados} registro(s) incompleto(s) foram ignorados.")

    def _registro_valido(self, item):
        """Confere se o registro é um dicionário com todos os campos preenchidos."""
        if not isinstance(item, dict):
            return False
        for campo in CAMPOS_OBRIGATORIOS:
            if campo not in item or item[campo] in (None, "", []):
                return False
        return isinstance(item["palavras_chave"], list) and isinstance(item["documentos"], list)

    def categorias(self):
        """Lista as categorias, sem repetir, em ordem alfabética."""
        return sorted({o.categoria for o in self.orientacoes})

    def por_categoria(self, categoria):
        """Lista as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """
        Dá pontos a uma orientação para a pergunta:
          +3 por palavra-chave que aparece na pergunta;
          +1 por palavra da pergunta (4 letras ou mais) que aparece no título.
        """
        pontos = 0
        pergunta_norm = normalizar(pergunta)
        titulo_norm = normalizar(orientacao.titulo)

        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_norm:
                pontos += PONTOS_PALAVRA_CHAVE

        for palavra in dict.fromkeys(pergunta_norm.split()):  # sem repetir
            if len(palavra) >= 4 and palavra not in PALAVRAS_IGNORADAS:
                if f" {palavra} " in titulo_norm:
                    pontos += PONTOS_PALAVRA_TITULO

        return pontos

    def buscar(self, pergunta):
        """
        Devolve uma lista de tuplas (pontos, orientacao), da maior para a menor
        pontuação. Só entram orientações com pelo menos MINIMO_PARA_RESPONDER pontos;
        lista vazia significa "não encontrei".
        """
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos >= MINIMO_PARA_RESPONDER:
                resultados.append((pontos, orientacao))
        # Desempate: vence quem casou a palavra-chave mais longa (mais específica).
        resultados.sort(key=lambda tupla: (tupla[0], self._maior_chave_casada(pergunta, tupla[1])),
                        reverse=True)
        return resultados

    def _maior_chave_casada(self, pergunta, orientacao):
        """Tamanho da maior palavra-chave encontrada na pergunta (usada no desempate)."""
        pergunta_norm = normalizar(pergunta)
        tamanhos = [len(normalizar(k)) for k in orientacao.palavras_chave
                    if normalizar(k) in pergunta_norm]
        return max(tamanhos, default=0)

    def confianca(self, pontos):
        """Converte os pontos em nível de confiança."""
        return "ALTA" if pontos >= MINIMO_CONFIANCA_ALTA else "MÉDIA"