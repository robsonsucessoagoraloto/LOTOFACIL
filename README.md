# Análises da Lotofácil

App pessoal de análise da Lotofácil: estatísticas de todos os concursos, simuladores, gerador de jogos e fechamentos com garantia calculada, e um assistente com IA que monta o plano do dia dentro do seu orçamento.

> **Aviso importante.** Todos os testes do app, feitos com os mais de 3.800 concursos, mostram que nenhum critério (ciclos, atrasos, frequência, padrões) muda a chance do próximo sorteio. Cada jogo de 15 dezenas tem 1 chance em 3.268.760 de fazer 15 pontos, e o retorno médio de qualquer aposta é de cerca de 41% do valor apostado. Use o app para organizar seus jogos e aposte só o que cabe no seu orçamento de lazer.

## O que tem no repositório

| Arquivo | Para que serve |
|---|---|
| `index.html` | O app inteiro (abre direto no navegador). |
| `resultados.json` | Todos os concursos: `[concurso, 15 dezenas]`. O app lê este arquivo ao abrir. |
| `scripts/atualizar_resultados.py` | Busca na Caixa os concursos que faltam e acrescenta ao `resultados.json`. |
| `.github/workflows/atualizar.yml` | Roda o script sozinho toda noite depois do sorteio. |

## Publicar no GitHub Pages

1. Crie um repositório no GitHub (pode ser privado no plano pago, ou público no gratuito).
2. Envie todos os arquivos desta pasta, mantendo as pastas `scripts` e `.github`.
3. No repositório: **Settings → Pages → Build and deployment → Source: Deploy from a branch**, escolha a branch `main` e a pasta `/ (root)`.
4. Em alguns minutos o app fica disponível em `https://SEU-USUARIO.github.io/NOME-DO-REPOSITORIO/`.

## Atualização automática dos resultados

O robô (GitHub Actions) roda às 23h40 e às 9h10 (horário de Brasília), de terça a domingo, e grava os concursos novos no `resultados.json`. O app lê esse arquivo ao abrir.

- Para rodar na hora: aba **Actions → Atualizar resultados da Lotofácil → Run workflow**.
- Se aparecer erro de permissão no `git push`: **Settings → Actions → General → Workflow permissions → Read and write permissions**.
- Se a API da Caixa recusar o acesso (ela às vezes bloqueia servidores fora do Brasil), o script tenta uma fonte reserva comunitária. Se as duas falharem, o resultado pode ser digitado no app, em “Adicionar resultado novo”.

## Plano automático (sem IA e sem custo)

Em **Início → Assistente → Plano automático**, informe quanto quer gastar e escolha o formato (jogos de 15, apostas de 16 ou fechamento com garantia). O app monta os jogos sozinho com os critérios marcados (ciclo, frequência e atrasos, filtros, repetidas), explica cada escolha e calcula custo e garantia. Marque **"Montar sozinho toda vez que eu abrir o app"** para receber o plano do próximo concurso ao abrir. Não precisa de chave da API.

## Assistente com IA fora do Claude

No app, em **Início → Assistente → Usar o assistente fora do Claude**, cole uma chave da API da Anthropic (console.anthropic.com). A chave fica guardada só no seu navegador e vai direto para a Anthropic. O uso é cobrado na sua conta da API.

- Não coloque a chave em nenhum arquivo do repositório.
- Não use a chave em computador compartilhado.
- Sem a chave, todo o resto do app funciona normalmente: só os agentes ficam desligados.

## Atualizar à mão

```bash
python scripts/atualizar_resultados.py
```
