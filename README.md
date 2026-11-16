# Transcritor local de reuniões

Pipeline local para transcrever gravações de reuniões em português e identificar os participantes por voz, utilizando **Faster-Whisper (large-v3)**, **pyannote.audio (Community-1)** e **Docker Compose**.

O processamento é realizado na GPU do computador, sem cobrança por minuto transcrito ou uso de API de transcrição.

## Pré-requisitos

- Windows com Docker Desktop instalado e em execução.
- GPU NVIDIA compatível com CUDA e drivers atualizados.
- Suporte de GPU habilitado no Docker/WSL 2.
- Arquivo `.env` configurado na raiz do projeto com o token do Hugging Face (`HF_TOKEN`).
- Acesso autorizado ao modelo `pyannote/speaker-diarization-community-1` no Hugging Face.
- Imagens Docker já construídas (ou realizar a construção indicada abaixo).

> **Atenção:** não compartilhe nem versione o arquivo `.env`, pois ele contém uma credencial.

## Estrutura do projeto

Exemplo da estrutura utilizada:

```text
C:\transcriber\
├── .env
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.diarizer
├── transcribe.py
├── diarize.py
├── merge.py
├── input\
├── output\
└── models\
```

- `input/`: coloque aqui os vídeos ou áudios a processar.
- `output/`: recebe os resultados, organizados pelo nome do arquivo, sem extensão.
- `models/`: cache local dos modelos baixados.

## Uso rápido — três comandos

### 1. Preparar o arquivo

Copie a gravação para `C:\transcriber\input\`. Por exemplo:

```text
C:\transcriber\input\reuniao.mkv
```

Abra o **PowerShell** e acesse a pasta do projeto:

```powershell
cd C:\transcriber
```

### 2. Transcrever o conteúdo

```powershell
docker compose run --rm transcriber python transcribe.py reuniao.mkv
```

Gera os arquivos `transcript.txt` e `transcript.jsonl` com as falas e seus horários.

### 3. Identificar os falantes

```powershell
docker compose run --rm diarizer python diarize.py reuniao.mkv
```

Gera `speakers.json` com os intervalos de fala de cada participante, identificados como `SPEAKER_00`, `SPEAKER_01` etc.

### 4. Combinar transcrição e falantes

```powershell
docker compose run --rm transcriber python merge.py reuniao.mkv
```

Gera `transcript_diarized.txt` e `transcript_diarized.jsonl`, contendo texto, horários e identificação dos falantes.

**Pronto!** O arquivo principal para leitura ou envio ao ChatGPT é:

```text
C:\transcriber\output\reuniao\transcript_diarized.txt
```

Para processamento estruturado, utilize `transcript_diarized.jsonl`.

## Onde ficam os resultados?

Para uma gravação chamada `reuniao.mkv`:

```text
output\
└── reuniao\
    ├── transcript.txt
    ├── transcript.jsonl
    ├── speakers.json
    ├── transcript_diarized.txt
    └── transcript_diarized.jsonl
```

| Arquivo                     | Conteúdo                                        |
| --------------------------- | ----------------------------------------------- |
| `transcript.txt`            | Transcrição com horários, sem falantes          |
| `transcript.jsonl`          | Transcrição estruturada por segmento            |
| `speakers.json`             | Intervalos temporais atribuídos a cada falante  |
| `transcript_diarized.txt`   | **Transcrição final legível, com falantes**     |
| `transcript_diarized.jsonl` | **Transcrição final estruturada, com falantes** |

## Como processar outro arquivo

Basta colocar o novo arquivo na pasta `input/` e substituir `reuniao.mkv` pelo nome real nos três comandos.

Por exemplo, para `audiencia.mp4`:

```powershell
docker compose run --rm transcriber python transcribe.py audiencia.mp4
docker compose run --rm diarizer python diarize.py audiencia.mp4
docker compose run --rm transcriber python merge.py audiencia.mp4
```

Resultado: `C:\transcriber\output\audiencia\`.

**Importante:** use exatamente o mesmo nome do arquivo nos três comandos. Se o nome tiver espaços, coloque-o entre aspas, por exemplo `"Reunião Cliente.mkv"`.

## Formatos suportados

- `.mp4` e `.mkv` foram considerados no fluxo atual.
- Outros formatos de áudio/vídeo podem funcionar desde que os codecs sejam reconhecidos por FFmpeg/PyAV.
- Um arquivo MKV é um contêiner: a compatibilidade depende também do codec de áudio interno.

## Primeira execução ou reconstrução

Se estiver configurando o projeto em uma nova máquina ou alterar os Dockerfiles, construa as imagens:

```powershell
docker compose build
```

Na primeira execução, os modelos podem precisar ser baixados. Isso demanda conexão com a internet e pode levar algum tempo. Depois de armazenados em `models/`, podem ser reutilizados localmente.

O arquivo `.env` deve conter uma entrada como:

```dotenv
HF_TOKEN=seu_token_do_hugging_face
```

Não coloque um token real em documentação ou repositórios públicos.

## Dicas e resolução de problemas

**O Docker não está respondendo:** abra o Docker Desktop, aguarde a inicialização e execute novamente.

**Arquivo não encontrado:** confirme que a gravação está em `C:\transcriber\input\` e que o nome, inclusive a extensão, corresponde ao comando.

**Erro de autorização no Hugging Face:** confira o `HF_TOKEN` no `.env` e se o acesso ao modelo de diarização foi autorizado na sua conta.

**Erro relacionado à GPU/CUDA:** confirme que o driver NVIDIA, o Docker Desktop e o suporte a GPU no WSL 2 estão funcionando. O projeto foi validado em uma RTX 5070 Laptop GPU com as versões fixadas nos Dockerfiles.

**O `merge.py` falhou:** confira se as duas etapas anteriores concluíram com sucesso e se existem `transcript.jsonl` e `speakers.json` na pasta de saída correspondente.

**Falantes trocados ou frases estranhas:** a identificação por voz e o reconhecimento de fala não são perfeitos. Revise trechos críticos com a gravação original, especialmente nomes, termos técnicos, decisões e atribuição de responsabilidades.

**A transcrição está dividida em muitas linhas:** esse é o formato atual por segmentos do Whisper. Não indica necessariamente perda de conteúdo.

## Limitações importantes

- `SPEAKER_00` e `SPEAKER_01` são identificadores automáticos, **não nomes reais**. A associação a pessoas deve ser feita manualmente ou validada com o áudio.
- A etapa de integração atribui um falante por segmento transcrito com base na maior sobreposição temporal; mudanças de falante dentro de um mesmo segmento podem ser atribuídas incorretamente.
- Conversas simultâneas, ruído, microfones ruins e termos técnicos podem reduzir a precisão.
- Os timestamps exibidos no `.txt` são arredondados para segundos; o `.jsonl` preserva os tempos numéricos dos segmentos.
- Para atas, requisitos funcionais e documentos jurídicos, use a transcrição como **material de apoio**, não como registro infalível.

## Custos e privacidade

A execução local com Faster-Whisper e pyannote Community-1 não gera cobrança por minuto de áudio. Existem custos indiretos de energia, hardware e armazenamento. Antes de incorporar a solução a um produto comercial, verifique as licenças aplicáveis, as condições de uso do Docker Desktop e os requisitos de privacidade, confidencialidade e LGPD.

## Resumo para consultar depois

```powershell
cd C:\transcriber

docker compose run --rm transcriber python transcribe.py reuniao.mkv
docker compose run --rm diarizer python diarize.py reuniao.mkv
docker compose run --rm transcriber python merge.py reuniao.mkv
```

**Arquivo final:** `output\reuniao\transcript_diarized.txt`
