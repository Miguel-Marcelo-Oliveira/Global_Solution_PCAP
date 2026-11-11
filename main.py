from base_conhecimento import BaseConhecimento
from assistente import Assistente


def menu():
    """Menu principal do Citizen Assist AI."""
    base = BaseConhecimento("data/base_conhecimento.json")
    base.carregar()
    assistente = Assistente("Citizen Assist AI", base)

    while True:
        print("\n" + "=" * 40)
        print("  CITIZEN ASSIST AI")
        print("=" * 40)
        print("1. Fazer uma pergunta")
        print("2. Navegar por categorias")
        print("3. Ver indicadores")
        print("4. Exportar atendimentos para CSV")
        print("0. Sair")

        opcao = assistente.ler_opcao("\nEscolha uma opção: ")
        if opcao is None:
            continue

        if opcao == 1:
            assistente.perguntar()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.indicadores()
        elif opcao == 4:
            assistente.exportar_csv()
        elif opcao == 0:
            assistente.pedir_nota()
            assistente.exportar_csv(silencioso=True)
            print("\nObrigado por usar o Citizen Assist AI!")
            return
        else:

            print("Opção inválida. Escolha de 0 a 4.")


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\n\nEncerrado.")