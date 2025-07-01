# Amazonia Speech Gateway

Serviço gRPC de transcrição de fala para texto usando o modelo Guará v2, otimizado para português brasileiro.

## Funcionalidades

- Transcrição de alta performance com o modelo Guará v2
- API gRPC para comunicação de baixa latência
- Métricas detalhadas de uso de tokens
- Suporte primário para português brasileiro

## Pré-requisitos

- Python 3.12+
- Poetry
- FFmpeg
- Token da API Guará

## Instalação

```bash
git clone <repository-url>
cd amazonia-speech-gateway
poetry install
```

### Configuração

Crie um arquivo `.env` na raiz do projeto:

```bash
# Obrigatório
GUARA_BASE_URL=
GUARAV2_2506_TOKEN=

# Opcional
GRPC_SERVER_PORT=50051
GRPC_SERVER_HOST=0.0.0.0
```

## Uso

### Executar o Serviço

```bash
poetry run python -m grpc_server
```

O serviço será iniciado em `localhost:50051`.

### API gRPC

O serviço está definido em `grpc_server/proto/speech.proto`:

```protobuf
service SpeechService {
    rpc transcribe(TranscriptionRequest) returns (TranscriptionResponse);
}

message TranscriptionRequest {
    string audio_path = 1;
    string model = 2;
    optional string prompt = 3;
    optional string language = 4;
}

message TranscriptionResponse {
    string text = 1;
    float duration = 2;
    int32 prompt_tokens = 3;
    int32 completion_tokens = 4;
    int32 total_tokens = 5;
}
```

**Modelo Suportado**: `widelabs/guara-v2-2506`

## Códigos de Status

- `INVALID_ARGUMENT`: Parâmetros inválidos
- `NOT_FOUND`: Arquivo de áudio não encontrado  
- `INTERNAL`: Erro interno do servidor
- `DEADLINE_EXCEEDED`: Timeout da requisição

## Desenvolvimento

Para debug, habilite logging detalhado:

```bash
export LOG_LEVEL=DEBUG
poetry run python -m grpc_server
```
