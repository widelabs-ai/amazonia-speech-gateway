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
GUARA_BASE_URL=http://164.152.56.41:81/v1
GUARAV2_2506_TOKEN=your_token_here

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

## Exemplo de Cliente (Go)

```go
package main

import (
    "context"
    "log"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    pb "your-project/pb"
)

func main() {
    conn, err := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
    if err != nil {
        log.Fatalf("Falha ao conectar: %v", err)
    }
    defer conn.Close()

    client := pb.NewSpeechServiceClient(conn)

    request := &pb.TranscriptionRequest{
        AudioPath: "/path/to/audio.wav",
        Model:     "widelabs/guara-v2-2506",
        Language:  "pt",
    }

    response, err := client.Transcribe(context.Background(), request)
    if err != nil {
        log.Fatalf("Transcrição falhou: %v", err)
    }

    log.Printf("Texto: %s", response.Text)
    log.Printf("Tokens: %d total", response.TotalTokens)
}
```

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
