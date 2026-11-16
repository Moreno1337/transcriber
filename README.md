# Transcritor local de reuniões

Pipeline local para transcrever gravações de reuniões em português e identificar os participantes por voz, utilizando **Faster-Whisper (large-v3)**, **pyannote.audio (Community-1)** e **Docker Compose**.

O processamento é realizado na GPU do computador, sem cobrança por minuto transcrito ou uso de API de transcrição.

## Pré-requisitos

- Windows com Docker Desktop instalado e em execução.
- GPU NVIDIA compatível com CUDA e drivers atualizados.
- Suporte de GPU habilitado no Docker/WSL 2.
- Conta no Hugging Face com acesso autorizado ao modelo `pyannote/speaker-diarization-community-1`.

## Estrutura do projeto

```text
C:\transcriber\
├── .env
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.diarizer
├── transcribe.cmd
├── transcribe.py
├── diarize.py
├── merge.py
├── input\
├── output\
└── models\
```

- `input/`: vídeos ou áudios a processar. A pasta vem vazia no clone.
- `output/`: resultados, organizados pelo nome do arquivo, sem extensão. Também vem vazia.
- `.env` e `models/`: criados na máquina local. Não vêm no repositório.

## Primeira vez, depois do clone

Faça isto uma vez em cada máquina.

1. Clone o repositório e entre na pasta:

```powershell
git clone https://github.com/Moreno1337/transcriber.git
cd transcriber
```

2. Crie o arquivo `.env` na raiz com o token do Hugging Face:

```dotenv
HF_TOKEN=seu_token_do_hugging_face
```

Não compartilhe nem versione esse arquivo. Ele contém uma credencial.

3. Construa as imagens Docker:

```powershell
docker compose build
```

Se os Dockerfiles mudarem depois, rode esse comando de novo.

## Transcrever um arquivo

1. Copie a gravação para `input\`. Por exemplo, `input\reuniao.mp4`.
2. Na pasta do projeto, no PowerShell:

```powershell
.\transcribe reuniao.mp4
```

O comando executa as três etapas em sequência e para se alguma falhar:

1. Transcrição, gerando `transcript.txt` e `transcript.jsonl`.
2. Identificação dos falantes, gerando `speakers.json` com `SPEAKER_00`, `SPEAKER_01` etc.
3. Combinação, gerando `transcript_diarized.txt` e `transcript_diarized.jsonl`.

Na primeira transcrição os modelos são baixados para `models\`. Isso exige internet e pode demorar. Nas execuções seguintes eles são reutilizados.

**Pronto!** O arquivo principal para leitura ou envio ao ChatGPT é:

```text
C:\transcriber\output\reuniao\transcript_diarized.txt
```

Para processamento estruturado, utilize `transcript_diarized.jsonl`.

## Onde ficam os resultados?

Para uma gravação chamada `reuniao.mp4`:

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

Coloque o novo arquivo na pasta `input/` e passe o nome dele para o comando.

Por exemplo, para `audiencia.mkv`:

```powershell
.\transcribe audiencia.mkv
```

Resultado: `C:\transcriber\output\audiencia\`.

`.mp4` e `.mkv` usam o mesmo comando. Se o nome tiver espaços, coloque-o entre aspas, por exemplo `.\transcribe "Reunião Cliente.mp4"`.

## Rodar uma etapa separada

O comando único chama estes três passos. Eles podem ser executados individualmente, com o mesmo nome de arquivo, quando for preciso repetir só uma etapa:

```powershell
docker compose run --rm transcriber python transcribe.py reuniao.mkv
docker compose run --rm diarizer python diarize.py reuniao.mkv
docker compose run --rm transcriber python merge.py reuniao.mkv
```

## Formatos suportados

- `.mp4` e `.mkv` foram considerados no fluxo atual.
- Outros formatos de áudio/vídeo podem funcionar desde que os codecs sejam reconhecidos por FFmpeg/PyAV.
- Um arquivo MKV é um contêiner: a compatibilidade depende também do codec de áudio interno.

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
.\transcribe reuniao.mp4
```

Na primeira máquina, antes disso: criar o `.env`, autorizar o modelo no Hugging Face e rodar `docker compose build`.

**Arquivo final:** `output\reuniao\transcript_diarized.txt`
