# E-book Generator — Design Spec
**Data:** 2026-04-13

---

## Visão Geral

CLI em Python que recebe 5 parâmetros de entrada (tema, título, autor, page range, idioma) e produz um arquivo `.docx` Kindle-ready, completamente formatado, com conteúdo gerado por IA e imagens embutidas.

---

## Estrutura de Arquivos

```
/Users/mvellasquez/Claude Projects/ebook-generator/
├── main.py                        # entrypoint: python main.py
├── pyproject.toml                 # dependências do projeto
├── .env.example                   # template de variáveis de ambiente
├── .env                           # chaves reais (gitignored)
├── cli/
│   └── prompts.py                 # coleta inputs interativos do usuário
├── pipeline/
│   └── orchestrator.py            # coordena as fases em sequência
├── agents/
│   ├── planner.py                 # Opus: gera e refina outline
│   └── writer.py                  # Haiku: escreve conteúdo capítulo a capítulo
├── research/
│   └── perplexity.py              # busca web via Perplexity sonar-pro
├── images/
│   └── generator.py               # gpt-image-1 via OpenAI API
└── export/
    ├── template_reader.py          # extrai estilos do "5 x 8 in.docx"
    └── docx_builder.py             # monta o .docx final
```

---

## Variáveis de Ambiente

```env
ANTHROPIC_API_KEY=       # Opus (planner) + Haiku (writer)
OPENAI_API_KEY=          # gpt-image-1 (geração de imagens)
GEMINI_API_KEY=          # reservado para writer alternativo futuro
PERPLEXITY_API_KEY=      # sonar-pro (pesquisa web)
KINDLE_TEMPLATE_PATH=    # caminho para "5 x 8 in.docx" (default: ~/Desktop/5 x 8 in.docx)
```

---

## Fluxo Principal

```
python main.py
  ↓
cli/prompts.py       → coleta: theme, title, author, page_range, language
  ↓
pipeline/orchestrator.py
  ↓
  [Fase 1 — Research]
  research/perplexity.py  → query: tema + ano atual → retorna síntese contextual
  ↓
  [Fase 2 — Outline]
  agents/planner.py (Opus)
    → input: 5 campos + síntese Perplexity
    → output: outline hierárquico (front matter + capítulos + back matter + estimativa de páginas)
    → exibe no terminal com formatação clara
    → loop interativo: [A]provar / [E]ditar (linguagem natural) / [R]eescrever
    → Opus refina até aprovação explícita
  ↓
  [Fase 3 — Escrita]
  agents/writer.py (Haiku) — processa UM capítulo por vez com streaming
    → input: outline aprovado + síntese Perplexity + capítulo atual
    → output: texto completo + marcadores [IMAGE: descrição detalhada]
    → idioma alvo respeitado via system prompt
  ↓
  [Fase 4 — Imagens]
  images/generator.py (gpt-image-1)
    → para cada [IMAGE: ...] no capítulo recém-escrito:
      → monta prompt otimizado (estilo editorial, 1024×1024)
      → download em memória (não persiste em disco)
      → retorna bytes prontos para embutir
  ↓
  [Fase 5 — Exportação]
  export/docx_builder.py
    → lê estilos do template via template_reader.py
    → monta documento na ordem correta
    → embute imagens centralizadas com legenda
    → salva <titulo>.docx no diretório atual
```

---

## Módulos — Responsabilidades

### `cli/prompts.py`
- Exibe banner do app
- Coleta os 5 campos via `input()` com validação mínima (campos obrigatórios não podem ser vazios)
- Retorna `BookParams` (dataclass)

### `pipeline/orchestrator.py`
- Instancia e chama cada fase em ordem
- Gerencia estado entre fases (passa outline aprovado, síntese, capítulos escritos)
- Exibe progresso: `[1/5] Pesquisando...`, `[2/5] Gerando outline...` etc.
- Em caso de erro de API, exibe mensagem clara e interrompe

### `agents/planner.py`
- Modelo: `claude-opus-4-5` (ou `claude-opus-4-6` conforme disponibilidade)
- System prompt: instrui a produzir outline em formato estruturado com estimativas de página
- Loop de aprovação: lê input do usuário, decide se refina ou retorna outline final
- Output: objeto `Outline` com lista de `Chapter` (título, seções, estimativa de páginas)

### `agents/writer.py`
- Modelo: `claude-haiku-4-5-20251001`
- System prompt: idioma alvo, tom editorial, instrução para inserir `[IMAGE: descrição]` onde relevante
- Streaming via Anthropic SDK — imprime no terminal em tempo real
- Recebe outline do capítulo + contexto de pesquisa
- Output: texto do capítulo como string com marcadores de imagem inline

### `research/perplexity.py`
- Modelo: `sonar-pro`
- Uma única chamada por execução
- Query: `"[tema] - contexto atual, tendências, dados recentes [ano]"`
- Retorna string com síntese (não URLs, não raw chunks)

### `images/generator.py`
- Modelo: `gpt-image-1`
- Extrai todos os `[IMAGE: ...]` de um texto com regex
- Para cada um: chama `openai.images.generate()`, baixa bytes em memória
- Retorna lista de `(posição_no_texto, bytes_da_imagem, descrição)`

### `export/template_reader.py`
- Abre `5 x 8 in.docx` com python-docx
- Extrai e retorna dict de estilos nomeados: `CSP - Chapter Title`, `CSP - Chapter Body Text`, `CSP - Chapter Body Text - First Paragraph`, `CSP - Front Matter Body Text`
- Extrai configurações de página (tamanho, margens por seção)

### `export/docx_builder.py`
- Constrói novo Document a partir do template (preserva estilos)
- Ordem de montagem:
  1. Título — Garamond 36pt + autor 18pt
  2. Copyright — Garamond 10pt
  3. Dedicatória — `CSP - Front Matter Body Text`
  4. Índice — gerado via heading styles
  5. Agradecimentos
  6. Capítulos 1..N — com imagens embutidas centralizadas (max 4×4 in) + legenda
  7. Sobre o Autor
- Page break entre cada seção maior
- Imagens: `[IMAGE: ...]` substituídos por `InlineImage` + parágrafo de legenda em itálico

---

## Formato do Outline (intermediário)

```python
@dataclass
class Section:
    title: str
    estimated_pages: float

@dataclass
class Chapter:
    number: int
    title: str
    sections: list[Section]
    estimated_pages: float

@dataclass
class Outline:
    book_title: str
    author: str
    language: str
    front_matter: list[str]      # ["Dedication", "Acknowledgments"]
    chapters: list[Chapter]
    back_matter: list[str]       # ["About the Author"]
    total_estimated_pages: int
```

---

## Template Kindle — Especificações Extraídas

| Elemento | Valor |
|---|---|
| Tamanho da página | 5.00 × 8.00 in |
| Margens padrão | top/bottom 0.76", left 0.76", right 0.60" |
| Margens front matter | top/bottom 1.00", left 1.25", right 1.00" |
| Fonte do corpo | Garamond |
| Título do capítulo | `CSP - Chapter Title` — Garamond 14pt |
| Título do livro | Garamond 36pt |
| Nome do autor | Garamond 18pt |
| Copyright | Garamond 10pt |
| Números de página | Times New Roman 9pt |

---

## Dependências (pyproject.toml)

```toml
[project]
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.91.0",
    "openai>=1.30.0",
    "google-generativeai>=0.5.0",
    "requests>=2.31.0",
    "python-docx>=1.1.0",
    "python-dotenv>=1.0.0",
    "pillow>=10.0.0",
]
```

---

## Fora do Escopo (versão 1.0)

- Frontend web/desktop
- Geração de PDF
- Uso do Gemini como writer alternativo (chave reservada mas não implementada)
- Persistência de rascunhos entre execuções
- Geração de capa do livro
