# Validação de Enriquecimento de Mídia

## Objetivo

Validar que os 3 serviços de IA estão funcionando corretamente ao processar diferentes tipos de mídia:

1. **TranscriptionService** (Faster-Whisper) → Áudio → Texto
2. **VisionService** (BLIP-2) → Imagem → Caption/Tags/Description
3. **DescriptionService** → Documento → Metadata (título, tags, descrição)

## Testes Implementados

### UC-017: Voice Message (Faster-Whisper)
```python
{
    "type": "voice",
    "file": {
        "url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav",
        "mimetype": "audio/wav"
    }
}
```

**Validações:**
- ✅ Mensagem criada com sucesso (201)
- ✅ Campo `file.url` populado
- 🔍 Campo `transcription` preenchido (se serviço estiver ativo)
- 🔍 Campo `title` pode ser gerado a partir da transcrição

**Fluxo de enriquecimento:**
1. MessageService detecta `type == "voice"`
2. Chama `TranscriptionService.transcribe_audio(file.url)`
3. TranscriptionService baixa o áudio via HTTP
4. Faster-Whisper processa localmente (base model ~75MB)
5. Texto transcrito é salvo em `message.transcription`

---

### UC-018: Image Message (BLIP-2)
```python
{
    "type": "image",
    "file": {
        "url": "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800",
        "mimetype": "image/jpeg"
    }
}
```

**Validações:**
- ✅ Mensagem criada com sucesso (201)
- ✅ Campo `file.url` populado
- 🔍 Campo `title` gerado por BLIP-2
- 🔍 Campo `description` com análise contextual
- 🔍 Campo `tags` com keywords extraídos

**Fluxo de enriquecimento:**
1. MessageService detecta `type == "image"`
2. Chama `DescriptionService.analyze_image_with_blip(file.url)`
3. VisionService baixa a imagem via HTTP
4. BLIP-2 gera caption: `_generate_caption()`
5. BLIP-2 responde perguntas VQA: `_generate_detailed_description()`
6. Extrai tags médicos do contexto
7. Retorna dict com `title`, `description`, `tags`

**Contextos médicos detectados:**
- Clínica/consultório
- Exercícios físicos
- Alimentos/nutrição
- Procedimentos médicos

---

### UC-019: Video Message (Transcrição + Metadata)
```python
{
    "type": "video",
    "file": {
        "url": "https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4",
        "mimetype": "video/mp4"
    }
}
```

**Validações:**
- ✅ Mensagem criada com sucesso (201)
- ✅ Campo `file.url` populado
- 🔍 Campo `transcription` com áudio do vídeo
- 🔍 Campo `title` e `description` gerados

**Fluxo de enriquecimento:**
1. MessageService detecta `type == "video"`
2. Extrai áudio do vídeo (ffmpeg)
3. Chama `TranscriptionService.transcribe_audio(audio)`
4. Chama `DescriptionService.generate_description()`
5. Combina transcrição + metadata

---

### UC-020: Document Message (Metadata Extraction)
```python
{
    "type": "document",
    "file": {
        "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "mimetype": "application/pdf",
        "filename": "orientacoes_consulta.pdf"
    }
}
```

**Validações:**
- ✅ Mensagem criada com sucesso (201)
- ✅ Campo `file.url` populado
- 🔍 Campo `title` extraído do filename
- 🔍 Campo `tags` com keywords médicos detectados
- 🔍 Campo `description` gerada por regex

**Fluxo de enriquecimento:**
1. MessageService detecta `type == "document"`
2. Chama `DescriptionService.generate_file_metadata(filename, mimetype)`
3. Analisa extensão (.pdf, .docx, .xlsx, etc.)
4. Extrai keywords médicos via regex
5. Gera título baseado no filename
6. Retorna metadata estruturado

**Keywords médicos detectados:**
- `dieta`, `alimenta`, `nutri`
- `exercicio`, `treino`, `fitness`
- `consulta`, `exame`, `procedimento`
- `peso`, `emagrec`, `obesidade`
- `tratamento`, `terapia`, `medicamento`

---

## Como Validar Localmente

### Opção 1: Testes Automatizados (Pytest)

```bash
# Dentro do container
docker-compose exec api python -m pytest tests/api/test_04_messages.py -v -s

# Saída esperada:
# test_uc017_create_voice_message PASSED
#   → Transcription: Baby Elephant Walk music...
#   → Has audio enrichment: True

# test_uc018_create_image_message PASSED
#   → Title: Medical clinic interior
#   → Tags: clinic, medical, healthcare
#   → Has vision enrichment: True
```

### Opção 2: Teste Manual (cURL)

```bash
# 1. Login
curl -X POST http://localhost:3333/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Criar mensagem de voz
curl -X POST http://localhost:3333/api/v1/messages \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "type": "voice",
    "file": {
      "url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav",
      "mimetype": "audio/wav"
    }
  }' | jq '.transcription'

# 3. Criar mensagem de imagem
curl -X POST http://localhost:3333/api/v1/messages \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "type": "image",
    "file": {
      "url": "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800",
      "mimetype": "image/jpeg"
    }
  }' | jq '{title, description, tags}'
```

### Opção 3: Script Automatizado

```bash
cd tests
chmod +x manual_test_enrichment.sh
./manual_test_enrichment.sh
```

---

## Observações Importantes

### Performance
- **Faster-Whisper:** ~2-5s para áudio de 1min (CPU), <1s (GPU)
- **BLIP-2:** ~3-8s por imagem (CPU), ~1-2s (GPU)
- **Metadata:** <100ms (regex/keywords)

### Custo Zero
Todos os serviços rodam **localmente** sem custo de API:
- Faster-Whisper: Open-source (MIT)
- BLIP-2: Salesforce model (Apache 2.0)
- Metadata: Regex próprio

### Fallback Gracioso
Se um serviço de IA falhar (modelo não carregado, timeout, erro de rede):
- Mensagem é criada mesmo assim
- Campos de enriquecimento ficam `null`
- Logs registram o erro para debug
- Usuário não percebe falha (UX preservado)

### Ambiente de Testes
Os testes usam URLs públicas estáveis porque:
1. Não dependem de arquivos locais commitados
2. Validam download + processamento end-to-end
3. Funcionam em CI/CD sem fixtures pré-instalados

**Futuro:** Adicionar fixtures locais em `tests/fixtures/media/` para testes offline.

---

## Status Atual

| Teste | Status | Enriquecimento | Observação |
|-------|--------|----------------|------------|
| UC-016 (text) | ✅ | N/A | Texto não passa por IA |
| UC-017 (voice) | ✅ | 🔍 Validar | Requer Faster-Whisper ativo |
| UC-018 (image) | ✅ | 🔍 Validar | Requer BLIP-2 carregado |
| UC-019 (video) | ✅ | 🔍 Validar | Requer ffmpeg + Whisper |
| UC-020 (doc) | ✅ | ✅ OK | Metadata regex sempre funciona |
| UC-021 (location) | ✅ | N/A | Localização não passa por IA |

**Próximo passo:** Executar testes em ambiente com serviços de IA ativos para validar enriquecimento real.
