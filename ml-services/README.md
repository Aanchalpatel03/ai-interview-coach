# ML Services

This directory adds an independent ML layer without changing the existing backend API contracts.

## Structure

```text
ml-services/
├── nlp-service
├── vision-service
├── emotion-service
└── speech-service
```

## Service APIs

### NLP

- `POST /ml/nlp/evaluate`
- `POST /ml/nlp/generate-question`
- `WS /ws/ml/nlp`

### Vision

- `POST /ml/vision/analyze-frame`
- `WS /ws/ml/vision`

### Emotion

- `POST /ml/emotion/analyze`
- `WS /ws/ml/emotion`

### Speech

- `POST /ml/speech/analyze`
- `WS /ws/ml/speech`

## Backend Integration

1. `/api/interview/answer` calls the NLP service.
2. `/api/video/frame` and `/api/ml/frame` call the vision and emotion services.
3. `/api/ml/speech/analyze` calls the speech service.
4. Aggregated feedback is streamed through `/api/ml/ws/ml-feedback?interview_id=<id>`.
5. ML outputs are optionally stored in `ml_logs`.

## Training

Each service includes a lightweight `train.py` entry point. Runtime works without artifacts; artifacts improve calibration when present.

## Optional Model Upgrades

- NLP can use local HuggingFace or sentence-transformer embeddings if installed.
- Vision can use MediaPipe/OpenCV if installed.
- Emotion can use a local image-classification pipeline if installed.
- Speech can use local Whisper/Vosk transcription if installed.

If those packages or weights are absent, the services continue running with deterministic inference logic instead of crashing.
