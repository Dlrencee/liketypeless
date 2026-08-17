# 0008 Chinese Punctuation Restoration

## Status

Proposed. Waiting for product confirmation before implementation.

## Problem

The current conservative cleanup removes fillers and creates numbered items, but it does not consistently add Chinese punctuation. ASR text can therefore remain as a long unpunctuated sentence.

## Proposed First Pass

Keep the existing ASR model and add a punctuation-specific contract to the structuring prompt:

- add `，` between clauses when the meaning clearly continues;
- end complete statements with `。`;
- use `？` and `！` only when the speech is clearly a question or exclamation;
- preserve existing punctuation;
- do not add, delete, summarize, or rewrite meaningful Chinese characters;
- keep numbered items on separate lines.

Add a post-check that compares meaningful characters in the source and candidate. If the model changes content or returns unusable output, return the rule-based result.

## Escalation Path

If prompt-constrained punctuation is still inconsistent, add a dedicated local Chinese punctuation-restoration model after ASR. This will improve punctuation specialization but adds another model download, runtime dependency, warm-up cost, and packaging concern.

## Performance Target

Keep the hot LLM structuring step under approximately 1.2 seconds when the model is warm. Punctuation should not block the initial raw transcription if a future asynchronous paste mode is enabled.
