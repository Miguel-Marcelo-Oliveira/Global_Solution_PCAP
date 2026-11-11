import csv
import json
import os
import time
from datetime import datetime

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo", "facilidade"]


class Assistente:
    """
    Quem conversa com o cidadão.
    Responsabilidade: fazer o atendimento, guardar o histórico e calcular os indicadores.
    """

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico = []
        self.ultimo_da_sessao = None   # último atendimento feito nesta execução
        self.carregar_historico()

    # ------------------------------------------------------------------
    # Histórico e CSV
    # ------------------------------------------------------------------
    def carregar_historico(self):
        """Lê data/historico.json. Arquivo ausente ou corrompido vira histórico vazio."""
        self.historico = []
        if not os.path.exists(self.caminho_historico):
            return
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            print("Aviso: histórico ilegível; começando com um histórico vazio.")
            return
        if isinstance(dados, list):
            self.historico = [item for item in dados if isinstance(item, dict)]

    def salvar_historico(self):
        """Grava a lista completa em data/historico.json."""
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, indent=2, ensure_ascii=False)
        except OSError as erro:
            print(f"Erro ao salvar o histórico: {erro}")

    def registrar(self, atendimento):
        """Adiciona um atendimento ao histórico e salva o arquivo."""
        self.historico.append(atendimento)
        self.ultimo_da_sessao = atendimento
        self.salvar_historico()

    def registrar_atendimento(self, origem, pergunta, id_orientacao, encontrou,
                              ajudou, tentativas, inicio):
        """Monta o dicionário do atendimento (com o tempo desde 'inicio') e registra."""
        self.registrar({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo": round(time.time() - inicio, 1),
            "facilidade": None,
        })

    def pedir_nota(self):
        """
        Pede a nota de facilidade (1 a 5) e guarda no último atendimento desta
        sessão, atualizando o registro existente (sem criar outro).
        """
        if self.ultimo_da_sessao is None:
            return
        while True:
            texto = input("\nDe 1 a 5, o quão fácil foi usar o assistente? ").strip()
            if texto.isdigit() and 1 <= int(texto) <= 5:
                self.ultimo_da_sessao["facilidade"] = int(texto)
                self.salvar_historico()
                return
            print("Digite um número de 1 a 5.")

    def exportar_csv(self, silencioso=False):
        """Exporta o histórico para data/atendimentos.csv com csv.DictWriter."""
        if not self.historico:
            if not silencioso:
                print("Não há atendimentos para exportar.")
            return
        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore")
                escritor.writeheader()
                escritor.writerows(self.historico)
            if not silencioso:
                print(f"Dados exportados para {self.caminho_csv}")
        except OSError as erro:
            print(f"Erro ao exportar o CSV: {erro}")

    # ------------------------------------------------------------------
    # Indicadores
    # ------------------------------------------------------------------
    def indicadores(self):
        """Calcula e mostra os indicadores do histórico."""
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos para calcular indicadores.")
            return

        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]
        tempos = [a["tempo"] for a in encontrados
                  if isinstance(a.get("tempo"), (int, float))]
        tentativas = [a["tentativas"] for a in self.historico
                      if isinstance(a.get("tentativas"), (int, float))]
        notas = [a["facilidade"] for a in self.historico
                 if isinstance(a.get("facilidade"), int) and 1 <= a["facilidade"] <= 5]

        print("\n" + "=" * 40)
        print("INDICADORES")
        print("=" * 40)
        print(f"Atendimentos: {total}")
        print(f"Resposta encontrada: {len(encontrados) / total * 100:.1f}%")
        print(f"Taxa de acerto (ajudou): {len(ajudaram) / total * 100:.1f}%")
        if tempos:
            print(f"Tempo médio para encontrar: {sum(tempos) / len(tempos):.1f} s")
        else:
            print("Tempo médio para encontrar: sem dados")
        if tentativas:
            print(f"Tentativas por atendimento: {sum(tentativas) / len(tentativas):.1f}")
        if notas:
            print(f"Facilidade de uso: {sum(notas) / len(notas):.1f} / 5 ({len(notas)} nota(s))")
        else:
            print("Facilidade de uso: sem notas")

        sem_solucao = []
        for a in self.historico:
            if not a.get("ajudou") and a.get("pergunta") not in sem_solucao:
                sem_solucao.append(a.get("pergunta"))
        print("\nDúvidas sem solução:")
        if sem_solucao:
            for duvida in sem_solucao:
                print(f"  - {duvida}")
        else:
            print("  (nenhuma)")
        print("=" * 40)

    # ------------------------------------------------------------------
    # Entradas do usuário
    # ------------------------------------------------------------------
    def contem_dado_pessoal(self, texto):
        """True se o texto tem 8 ou mais dígitos ou um @ (CPF, telefone, e-mail)."""
        digitos = sum(1 for letra in texto if letra.isdigit())
        return "@" in texto or digitos >= 8

    def ler_opcao(self, mensagem):
        """Lê um número inteiro; devolve None se a entrada for vazia ou inválida."""
        texto = input(mensagem).strip()
        if texto.isdigit():
            return int(texto)
        print("Digite apenas o número da opção.")
        return None

    def perguntar_se_ajudou(self):
        """Pergunta s/n até receber uma resposta válida."""
        while True:
            resposta = input("\nEssa orientação respondeu sua dúvida? (s/n): ").strip().lower()
            if resposta in ("s", "n"):
                return resposta == "s"
            print("Resposta inválida. Digite s para sim ou n para não.")

    # ------------------------------------------------------------------
    # Atendimento por pergunta
    # ------------------------------------------------------------------
    def perguntar(self):
        """
        Atendimento em texto livre. Um atendimento começa na primeira dúvida e termina
        quando a pessoa diz que resolveu (s) ou volta com 0. Cada pergunta digitada
        (ou reescrita) conta como uma tentativa.
        """
        while True:
            inicio = time.time()
            tentativas = 0
            achou = False
            ultimo_id = None
            ultima_pergunta = ""

            while True:
                entrada = input("\nDigite sua dúvida (0 para voltar): ").strip()

                if entrada == "0":
                    if tentativas > 0:   # saiu sem resolver
                        self.registrar_atendimento("pergunta", ultima_pergunta, ultimo_id,
                                                   achou, False, tentativas, inicio)
                    return
                if not entrada:
                    print("Escreva sua dúvida ou digite 0 para voltar.")
                    continue
                if self.contem_dado_pessoal(entrada):
                    # Não conta tentativa e não é registrada.
                    print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                    continue

                tentativas += 1
                ultima_pergunta = entrada
                resultados = self.base.buscar(entrada)

                if not resultados:
                    print("\nNão encontrei uma orientação para essa dúvida.")
                    print("Tente outras palavras ou use a navegação por categorias:")
                    for categoria in self.base.categorias():
                        print(f"  - {categoria}")
                    continue

                achou = True
                pontos, melhor = resultados[0]
                ultimo_id = melhor.id
                print(f"\nConfiança da resposta: {self.base.confianca(pontos)} ({pontos} pontos)")
                melhor.exibir()

                if len(resultados) > 1:
                    print("Outras orientações possíveis:")
                    for pontos_alt, alternativa in resultados[1:3]:
                        print(f"  - {alternativa.titulo} ({pontos_alt} pontos)")

                if self.perguntar_se_ajudou():
                    self.registrar_atendimento("pergunta", entrada, melhor.id,
                                               True, True, tentativas, inicio)
                    break   # novo atendimento
                print("Tente reescrever sua dúvida com outras palavras.")

    # ------------------------------------------------------------------
    # Atendimento por categorias
    # ------------------------------------------------------------------
    def navegar(self):
        """Mostra as categorias numeradas; 0 volta ao menu principal."""
        categorias = self.base.categorias()
        if not categorias:
            print("\nNenhuma orientação disponível no momento.")
            return
        inicio = time.time()
        while True:
            print("\n--- CATEGORIAS ---")
            for numero, categoria in enumerate(categorias, 1):
                print(f"{numero}. {categoria}")
            print("0. Voltar")

            opcao = self.ler_opcao("\nEscolha uma categoria: ")
            if opcao is None:
                continue
            if opcao == 0:
                return
            if 1 <= opcao <= len(categorias):
                if self.exibir_orientacoes_da_categoria(categorias[opcao - 1], inicio):
                    inicio = time.time()   # novo atendimento
            else:
                print(f"Opção inválida. Escolha de 0 a {len(categorias)}.")

    def exibir_orientacoes_da_categoria(self, categoria, inicio):
        """
        Lista as orientações da categoria. Devolve True se registrou um atendimento.
        Cada orientação aberta conta como uma tentativa.
        """
        orientacoes = self.base.por_categoria(categoria)
        tentativas = 0
        ultima = None
        while True:
            print(f"\n--- {categoria.upper()} ---")
            for numero, orientacao in enumerate(orientacoes, 1):
                print(f"{numero}. {orientacao.titulo}")
            print("0. Voltar")

            opcao = self.ler_opcao("\nEscolha uma orientação: ")
            if opcao is None:
                continue
            if opcao == 0:
                if tentativas > 0:   # abriu orientações, mas não resolveu
                    self.registrar_atendimento("categoria", f"Navegação: {ultima.titulo}",
                                               ultima.id, True, False, tentativas, inicio)
                    return True
                return False
            if 1 <= opcao <= len(orientacoes):
                ultima = orientacoes[opcao - 1]
                tentativas += 1
                ultima.exibir()
                if self.perguntar_se_ajudou():
                    self.registrar_atendimento("categoria", f"Navegação: {ultima.titulo}",
                                               ultima.id, True, True, tentativas, inicio)
                    return True
            else:
                print(f"Opção inválida. Escolha de 0 a {len(orientacoes)}.")