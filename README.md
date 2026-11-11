# Citizen Assist AI

**Global Solution 2026.2 - Pensamento Computacional e Automação com Python**

Assistente de terminal, feito em Python, que responde dúvidas do cidadão com base em informações verificadas, mostrando a fonte, a data de verificação e um aviso de limitação, sem coletar dados pessoais.

## 1. Integrantes

| NOME                                   | RM     |
|----------------------------------------|--------|
| Felipe de Oliveira Doern               | 568798 |
| Miguel Marcelo Alves Ramos de Oliveira | 569467 |
| Victor Correia Binot                   | 571499 |

## 2. Público e Problema

- **Nome do assistente:** Citizen Assist AI
- **Público atendido:** pessoas que querem gerar renda ou participar da comunidade, mas não sabem por onde começar: quem quer se organizar coletivamente (economia solidária), formalizar um negócio como MEI ou atuar como voluntário.
- **Problema:** a informação sobre cadastros, formalização e voluntariado existe, mas está espalhada em páginas diferentes, em linguagem técnica e misturada com sites que parecem oficiais e não são. Muitas pessoas perdem tempo sem saber onde ir, o que levar ou a quem recorrer.
- **Proposta:** um assistente que responde em linguagem simples, apenas com o que está na base de conhecimento, e sempre indica documentos necessários, onde ir, a fonte oficial e a data em que a equipe conferiu a informação.

A base tem **10 orientações em 3 categorias**:

| Categoria            | Orientações | Temas                                                                                  |
|----------------------|:-----------:|----------------------------------------------------------------------------------------|
| Economia Solidária   | 3           | Quem pode ser empreendimento solidário, como cadastrar no CADSOL, declaração (DCSOL)   |
| Formalização (MEI)   | 2           | Como virar MEI, quem pode ser MEI e regras                                             |
| Voluntariado         | 5           | O que é serviço voluntário, ICMBio, termo de adesão, vínculo trabalhista, ressarcimento |

## 3. ODS Relacionados

- **ODS 8 - Trabalho Decente e Crescimento Econômico:** orienta sobre economia solidária, CADSOL e formalização como MEI.
- **ODS 10 - Redução das Desigualdades:** facilita o acesso a serviços e direitos para quem tem menos acesso à informação.
- **ODS 16 - Paz, Justiça e Instituições Eficazes:** promove acesso à informação oficial e esclarece direitos e deveres no serviço voluntário (Lei nº 9.608/1998).

## 4. Como Executar

1. Tenha o Python 3 instalado (não são usadas bibliotecas externas).
2. Clone o repositório.
3. Dentro da pasta do projeto, execute:

```bash
python main.py
```

> Execute sempre de dentro da pasta do projeto: os caminhos dos arquivos em `data/` são relativos.

Menu principal:

| Opção | Ação                                   |
|-------|----------------------------------------|
| 1     | Fazer uma pergunta em texto livre      |
| 2     | Navegar por categorias                 |
| 3     | Ver indicadores                        |
| 4     | Exportar atendimentos para CSV         |
| 0     | Sair (pede a nota de facilidade 1 a 5) |

Em todas as telas de pergunta e de navegação, digitar `0` volta para a tela anterior.

## 5. Estrutura do Projeto

```
citizen-assist-ai/
├── README.md
├── main.py                 # menu principal
├── orientacao.py           # classe Orientacao
├── base_conhecimento.py    # classe BaseConhecimento (leitura do JSON e busca)
├── assistente.py           # classe Assistente (atendimento, histórico, indicadores, CSV)
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    └── atendimentos.csv
```

Composição: `Assistente` tem uma `BaseConhecimento`, que tem uma lista de objetos `Orientacao`.

| Classe              | Responsabilidade                                   | Métodos principais                                                        |
|---------------------|----------------------------------------------------|---------------------------------------------------------------------------|
| `Orientacao`        | Guardar os dados de uma orientação e exibi-la      | `exibir()`                                                                |
| `BaseConhecimento`  | Ler o JSON, listar categorias e buscar             | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()`  |
| `Assistente`        | Atender, guardar o histórico e calcular indicadores | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()` |

## 6. Regra de Pontuação da Busca

A pergunta, as palavras-chave e o título são normalizados (minúsculas, sem acentos e sem pontuação). Cada orientação recebe pontos:

- **+3 pontos** para cada palavra-chave da orientação que aparece na pergunta.
- **+1 ponto** para cada palavra da pergunta (4 letras ou mais) que aparece no título da orientação.

**Níveis de confiança:**

- **ALTA:** 6 pontos ou mais.
- **MÉDIA:** 3 a 5 pontos.
- **Não encontrei:** nenhuma orientação com 3 pontos ou mais. O assistente sugere usar outras palavras ou a navegação por categorias.

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)`, da maior para a menor pontuação. O assistente mostra a melhor orientação e até duas alternativas.

**Exemplo:** em "Como faço para virar MEI?", a orientação 4 recebe +3 por `virar mei`, +3 por `mei` e +1 porque "virar" está no título: 7 pontos, confiança ALTA.

**Ajustes feitos em relação à regra básica:**

- **Palavras ignoradas:** palavras genéricas como "como", "para", "quais" e "preciso" não valem ponto no título, porque aparecem em muitas perguntas e não indicam o assunto.
- **Palavra inteira:** a comparação usa espaços nas pontas do texto normalizado, então " sus " não casa com "sustentável".
- **Desempate:** se duas orientações têm a mesma pontuação, vence a que casou a palavra-chave mais longa, por ser mais específica.

## 7. Regras de Atendimento

- **Entradas inválidas:** opção fora da faixa, letras, resposta vazia ou s/n inválido nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Perguntas com 8 ou mais dígitos ou com `@` são recusadas e não são registradas.
- **Transparência:** toda resposta mostra a fonte, a data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** JSON ausente ou corrompido não trava o programa; registros incompletos da base são ignorados com um aviso.
- **Histórico:** cada atendimento é salvo em `data/historico.json` (data, origem, pergunta, id da orientação, se encontrou, se ajudou, tentativas, tempo em segundos e nota de facilidade) e exportado para `data/atendimentos.csv` com `csv.DictWriter`.
- **Indicadores:** resposta encontrada (%), taxa de acerto (ajudou, %), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (1 a 5) e lista de dúvidas sem solução.

## 8. Integração com Outras Disciplinas

Não há integração com outras disciplinas nesta entrega. O projeto usa apenas bibliotecas padrão do Python.

## 9. Fontes Consultadas

- [Cadastrar iniciativas econômicas solidárias (CADSOL)](https://www.gov.br/pt-br/servicos/cadastrar-iniciativas-economicas-solidarias)
- [Registro como Microempreendedor Individual (MEI)](https://www.gov.br/pt-br/servicos/realizar-registro-como-microempreendedor-individual-mei)
- [Ser um voluntário do ICMBio](https://www.gov.br/pt-br/servicos/ser-um-voluntario-do-icmbio)
- [Lei nº 9.608/1998 - Serviço voluntário (Senado Federal)](https://legis.senado.leg.br/norma/551484/publicacao/34619707)

Datas de verificação: orientações 1 a 5 (Economia Solidária e MEI) conferidas em **2026-11-06**; orientações 6 a 10 (Voluntariado) conferidas em **2026-11-09**.

## 10. Resultado do Teste com Usuários

O assistente foi testado com **3 pessoas de fora da equipe**, em **11 atendimentos**. Nenhum nome ou dado pessoal foi registrado.

**Indicadores obtidos:**

| Indicador                      | Resultado                                  |
|--------------------------------|--------------------------------------------|
| Resposta encontrada            | 100,0% (11/11)                             |
| Taxa de acerto (ajudou)        | 100,0% (11/11)                             |
| Tempo médio para encontrar     | 34,3 s                                     |
| Tentativas por atendimento     | 1,1 (12 tentativas em 11 atendimentos)     |
| Facilidade de uso              | 4,7 / 5 (3 notas: 5, 5 e 4)                |

**Dúvidas sem solução:**

- Nenhuma registrada: nos 11 atendimentos os usuários marcaram que a orientação ajudou (resposta autodeclarada).
- Ao revisar as perguntas do teste, a equipe percebeu que 3 delas receberam uma orientação menos adequada do que a que existia na base, mesmo com o usuário tendo marcado "ajudou":
  - "Posso ser reembolsado pelo transporte quando faço trabalho voluntário?" recebeu a orientação 6 (o que é serviço voluntário), e o certo era a 10 (ressarcimento de despesas);
  - "É necessário assinar algum documento para ser voluntário?" recebeu a 6, e o certo era a 8 (termo de adesão);
  - "Como cadastro meu grupo no CADSOL?" recebeu a 1 (quem pode ser), e o certo era a 2 (como cadastrar).

**Melhoria feita a partir do teste:**

- As 3 perguntas acima mostraram que faltavam palavras-chave com as formas que as pessoas realmente usam, e que algumas palavras-chave eram genéricas demais. Em `base_conhecimento.json`:
  - orientação 10: incluídas `reembolsado`, `ser reembolsado`, `posso ser reembolsado`, `pode ser reembolsado`, `reembolsar` e `ressarcido`;
  - orientação 8: incluídas `assinar algum documento`, `assinar documento`, `assinar termo`, `necessario assinar`, `precisa assinar` e outras;
  - orientação 2: incluídas `cadastrar grupo`, `cadastrar meu grupo`, `cadastro do grupo` e `cadastro meu grupo`; a palavra-chave genérica `como cadastrar` foi removida, porque fazia "Como cadastrar MEI?" cair no CADSOL;
  - palavras-chave genéricas removidas (`termo`, `assinar`, `dinheiro`, `salario`, `despesas`, `gastos`), que casavam com perguntas de outros assuntos; foram incluídas `imposto`, `tributos`, `mei paga`, `ser socio`, `empregado`, entre outras, na orientação 5.
- Depois da melhoria, as 3 perguntas passam a receber a orientação adequada (10, 8 e 2). O `historico.json` foi mantido como foi gravado no teste, sem edição.

## 11. Limitações

- O assistente só responde com o que está na base de conhecimento (10 orientações). Temas fora dela resultam em "não encontrei".
- O indicador "ajudou" é autodeclarado pelo usuário e pode marcar como útil uma orientação que não era a mais adequada (como ocorreu em 3 dos 11 atendimentos do teste).
- A busca é por palavras-chave inteiras: não entende sinônimos, plurais ou erros de digitação que não estejam cadastrados (ex.: "voluntários" não casa com "voluntario").
- Não coleta dados pessoais nem faz cadastros, em nome do usuário, em nenhum serviço.
- As informações podem mudar nos sites oficiais. Sempre confirme nas fontes indicadas, pois este assistente não é um canal oficial.

## 12. Vídeo Técnico

- **Link (YouTube, não listado): [PREENCHER]**