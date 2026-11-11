class Orientacao:
    """
    Uma orientação da base de conhecimento (um registro do JSON).
    Responsabilidade: guardar os dados da orientação e exibi-la na tela.
    """

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self):
        """Mostra a orientação com resposta, documentos, local, fonte e aviso."""
        print("\n" + "=" * 50)
        print(f">> {self.titulo} [{self.categoria}]")
        print(self.resposta)

        print("Documentos necessários:")
        if not self.documentos or self.documentos == ["Nenhum"]:
            print("  - Nenhum")
        else:
            for doc in self.documentos:
                print(f"  - {doc}")

        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")
        print("=" * 50)