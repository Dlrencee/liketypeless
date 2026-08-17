# 0006 Ollama Proxy and Lightweight LLM Testing

## Status

Accepted for development.

## Context

Ollama model downloads are performed by the running `ollama serve` process, not only by the foreground `ollama pull` command. Setting proxy environment variables in a new PowerShell session is insufficient if `ollama serve` was already running without those variables.

On this machine the local proxy is:

```powershell
http://127.0.0.1:7897
```

## Decision

Restart Ollama with proxy variables before pulling models:

```powershell
.\scripts\start-ollama-proxy.ps1
ollama pull qwen2.5:1.5b
```

The script stops existing `ollama.exe` processes, sets `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY`, then starts `ollama serve` with logs written to:

- `ollama.proxy.out.log`
- `ollama.proxy.err.log`

Check the error log for `HTTP_PROXY` and `HTTPS_PROXY` in the server config if downloads still fail.

## Test Results

`qwen2.5:0.5b` downloaded successfully through the proxy, but failed the conservative Chinese structuring task in a direct test. It is fast, but not reliable enough as the default structuring model.

`qwen2.5:1.5b` began downloading through the proxy, which confirms the proxy configuration was active. The transfer later failed with `EOF` from the remote Cloudflare R2 blob download. That indicates an unstable large-file download path, not a missing proxy configuration.

## Consequences

For the MVP, do not switch to `qwen2.5:0.5b` as the default. Continue testing a small non-thinking model such as `qwen2.5:1.5b` once it can be downloaded reliably, or keep `qwen3:8b` with `think:false` until a faster model passes quality checks.
