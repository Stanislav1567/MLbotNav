from __future__ import annotations

import hashlib
import hmac
import json
import os
import base64
from typing import Any
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from pathlib import Path

import yaml


def _read_env_file_value(project_root: Path, key: str) -> str:
    env_path = project_root / ".env"
    if not env_path.exists():
        return ""
    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == key:
                return v.strip().strip("\"'").strip()
    except Exception:
        return ""
    return ""


def _load_policy(project_root: Path) -> dict:
    p = project_root / "configs" / "security_governance.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _security_cfg(project_root: Path) -> dict:
    cfg = _load_policy(project_root).get("security", {}) or {}
    return cfg if isinstance(cfg, dict) else {}


def _provider_cfg(project_root: Path) -> dict[str, Any]:
    cfg = _security_cfg(project_root)
    provider_cfg = cfg.get("provider", {}) if isinstance(cfg, dict) else {}
    return provider_cfg if isinstance(provider_cfg, dict) else {}


def _env_value(project_root: Path, key: str) -> str:
    val = os.getenv(key, "").strip()
    if val:
        return val
    return _read_env_file_value(project_root, key).strip()


def require_role(project_root: Path, *, action: str) -> dict:
    cfg = (_load_policy(project_root).get("governance", {}) or {}).get("rbac", {}) or {}
    action_map = cfg.get("action_owner_map", {}) or {}
    required = action_map.get(action)
    current = os.getenv("MLBOTNAV_ROLE", "").strip() or "Admin"
    allowed = True
    reason = "ok"
    if required and current != required and current != "Admin":
        allowed = False
        reason = f"role_mismatch:{current}!={required}"
    return {"allowed": allowed, "required_role": required, "current_role": current, "reason": reason}


def resolve_secret(project_root: Path, *, name: str) -> dict:
    provider_cfg = _provider_cfg(project_root)
    provider = str(provider_cfg.get("required", "env")).strip().lower() or "env"
    allow_fallback = bool(provider_cfg.get("allow_fallback", False))
    value = ""
    reason = "ok"

    if provider == "env":
        value = _env_value(project_root, name)
        if not value:
            reason = "env_secret_missing"
    elif provider == "vault":
        vault_addr_env = str(provider_cfg.get("vault_addr_env", "VAULT_ADDR")).strip() or "VAULT_ADDR"
        vault_token_env = str(provider_cfg.get("vault_token_env", "VAULT_TOKEN")).strip() or "VAULT_TOKEN"
        vault_token_file_env = str(provider_cfg.get("vault_token_file_env", "VAULT_TOKEN_FILE")).strip() or "VAULT_TOKEN_FILE"
        vault_kv_path_env = str(provider_cfg.get("vault_kv_path_env", "VAULT_KV_PATH")).strip() or "VAULT_KV_PATH"
        vault_kv_path_default = str(provider_cfg.get("vault_kv_path", "secret/data/mlbotnav")).strip() or "secret/data/mlbotnav"

        vault_addr = _env_value(project_root, vault_addr_env).rstrip("/")
        vault_token = _env_value(project_root, vault_token_env)
        vault_token_file = _env_value(project_root, vault_token_file_env)
        vault_path = (_env_value(project_root, vault_kv_path_env) or vault_kv_path_default).strip().strip("/")
        if not vault_token and vault_token_file:
            try:
                vault_token = Path(vault_token_file).read_text(encoding="utf-8").strip()
            except Exception:
                vault_token = ""
        if not vault_addr:
            reason = "vault_addr_missing"
        elif not vault_token:
            reason = "vault_token_missing"
        else:
            try:
                url = f"{vault_addr}/v1/{vault_path}"
                req = Request(url, headers={"X-Vault-Token": vault_token}, method="GET")
                with urlopen(req, timeout=8) as resp:  # nosec B310
                    payload = json.loads(resp.read().decode("utf-8"))
                data = payload.get("data", {}) if isinstance(payload, dict) else {}
                # KV v2: data.data[name], KV v1: data[name]
                if isinstance(data, dict) and isinstance(data.get("data"), dict):
                    value = str(data.get("data", {}).get(name, "") or "")
                elif isinstance(data, dict):
                    value = str(data.get(name, "") or "")
                if not value:
                    reason = "vault_secret_missing"
            except Exception as e:  # noqa: BLE001
                reason = f"vault_read_error:{e}"
    elif provider == "kms":
        kms_key_id_env = str(provider_cfg.get("kms_key_id_env", "KMS_KEY_ID")).strip() or "KMS_KEY_ID"
        kms_endpoint_env = str(provider_cfg.get("kms_decrypt_endpoint_env", "KMS_DECRYPT_ENDPOINT")).strip() or "KMS_DECRYPT_ENDPOINT"
        kms_auth_env = str(provider_cfg.get("kms_auth_token_env", "KMS_AUTH_TOKEN")).strip() or "KMS_AUTH_TOKEN"
        kms_ciphertext_suffix = str(provider_cfg.get("kms_ciphertext_suffix", "_ENC_B64")).strip() or "_ENC_B64"

        value = _env_value(project_root, name)
        kms_key_id = _env_value(project_root, kms_key_id_env)
        ciphertext_b64 = _env_value(project_root, f"{name}{kms_ciphertext_suffix}")
        endpoint = _env_value(project_root, kms_endpoint_env)
        auth_token = _env_value(project_root, kms_auth_env)
        if not kms_key_id:
            reason = "kms_key_missing"
        elif value:
            reason = "ok"
        elif ciphertext_b64 and endpoint:
            try:
                req_body = json.dumps(
                    {"key_id": kms_key_id, "ciphertext_b64": ciphertext_b64, "secret_name": name}
                ).encode("utf-8")
                headers = {"Content-Type": "application/json"}
                if auth_token:
                    headers["Authorization"] = f"Bearer {auth_token}"
                req = Request(endpoint, data=req_body, headers=headers, method="POST")
                with urlopen(req, timeout=8) as resp:  # nosec B310
                    payload = json.loads(resp.read().decode("utf-8"))
                value = str(payload.get("plaintext", "") if isinstance(payload, dict) else "")
                if not value:
                    reason = "kms_plaintext_missing"
            except Exception as e:  # noqa: BLE001
                reason = f"kms_decrypt_error:{e}"
        elif ciphertext_b64 and allow_fallback:
            # Local offline fallback for testing-only flows.
            try:
                value = base64.b64decode(ciphertext_b64.encode("utf-8")).decode("utf-8")
                reason = "kms_offline_b64_fallback"
            except Exception as e:  # noqa: BLE001
                reason = f"kms_b64_decode_error:{e}"
        elif ciphertext_b64 and not allow_fallback:
            reason = "kms_offline_fallback_disabled"
        else:
            reason = "kms_secret_missing"
    else:
        if allow_fallback:
            provider = "env"
            value = _env_value(project_root, name)
            reason = "fallback_env_provider" if value else "fallback_env_secret_missing"
        else:
            reason = f"unsupported_provider:{provider}"

    return {
        "name": name,
        "provider": provider,
        "allow_fallback": allow_fallback,
        "value": value,
        "found": bool(value),
        "reason": reason,
    }


def run_security_gate(project_root: Path, *, stage: str) -> dict:
    cfg = _security_cfg(project_root)
    gate = cfg.get("gate", {}) if isinstance(cfg, dict) else {}
    if not isinstance(gate, dict):
        gate = {}
    provider_cfg = _provider_cfg(project_root)
    required_provider = str(provider_cfg.get("required", "env")).strip().lower() or "env"
    allow_fallback = bool(provider_cfg.get("allow_fallback", False))
    tls_required = bool(gate.get("tls_required", True))
    at_rest_required = bool(gate.get("at_rest_encryption_required", True))
    active = bool(gate.get("active", True))

    reasons: list[str] = []
    checks: dict[str, object] = {
        "stage": stage,
        "required_provider": required_provider,
        "allow_fallback": allow_fallback,
        "active": active,
        "tls_required": tls_required,
        "at_rest_encryption_required": at_rest_required,
    }
    if not active:
        allowed = True
    else:
        allowed = True
        if required_provider not in {"env", "vault", "kms"}:
            allowed = False
            reasons.append(f"provider_invalid:{required_provider}")

        if required_provider == "vault":
            vault_addr_env = str(provider_cfg.get("vault_addr_env", "VAULT_ADDR")).strip() or "VAULT_ADDR"
            vault_token_env = str(provider_cfg.get("vault_token_env", "VAULT_TOKEN")).strip() or "VAULT_TOKEN"
            vault_token_file_env = str(provider_cfg.get("vault_token_file_env", "VAULT_TOKEN_FILE")).strip() or "VAULT_TOKEN_FILE"
            vault_addr = _env_value(project_root, vault_addr_env)
            vault_token = _env_value(project_root, vault_token_env)
            vault_token_file = _env_value(project_root, vault_token_file_env)
            if not vault_token and vault_token_file:
                try:
                    vault_token = Path(vault_token_file).read_text(encoding="utf-8").strip()
                except Exception:
                    vault_token = ""
            checks["vault_addr_set"] = bool(vault_addr)
            checks["vault_token_set"] = bool(vault_token)
            checks["vault_token_file_set"] = bool(vault_token_file)
            if not vault_addr:
                allowed = False
                reasons.append("vault_addr_missing")
            if not vault_token:
                allowed = False
                reasons.append("vault_token_missing")
            if tls_required and vault_addr:
                sch = urlparse(vault_addr).scheme.lower()
                if sch != "https":
                    allowed = False
                    reasons.append(f"vault_tls_required_scheme={sch or 'none'}")

        if required_provider == "kms":
            kms_key_env = str(provider_cfg.get("kms_key_id_env", "KMS_KEY_ID")).strip() or "KMS_KEY_ID"
            kms_endpoint_env = str(provider_cfg.get("kms_decrypt_endpoint_env", "KMS_DECRYPT_ENDPOINT")).strip() or "KMS_DECRYPT_ENDPOINT"
            kms_key = _env_value(project_root, kms_key_env)
            kms_endpoint = _env_value(project_root, kms_endpoint_env)
            checks["kms_key_set"] = bool(kms_key)
            checks["kms_endpoint_set"] = bool(kms_endpoint)
            if not kms_key:
                allowed = False
                reasons.append("kms_key_missing")
            if not allow_fallback and not kms_endpoint:
                allowed = False
                reasons.append("kms_endpoint_missing_no_fallback")

        if at_rest_required:
            enc = _env_value(project_root, "STORAGE_ENCRYPTION_ENABLED").lower()
            enc_provider = _env_value(project_root, "STORAGE_ENCRYPTION_PROVIDER").lower()
            checks["storage_encryption_enabled"] = enc
            checks["storage_encryption_provider"] = enc_provider
            if enc not in {"1", "true", "yes", "on"}:
                allowed = False
                reasons.append("storage_encryption_not_enabled")
            if required_provider in {"vault", "kms"} and enc_provider and enc_provider != required_provider:
                allowed = False
                reasons.append(f"storage_provider_mismatch:{enc_provider}!={required_provider}")
            if required_provider in {"vault", "kms"} and not enc_provider:
                checks["storage_encryption_provider"] = "<missing>"
                allowed = False
                reasons.append("storage_encryption_provider_missing")

    report = {
        "run_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "created_at_utc": _now_iso(),
        "allowed": allowed,
        "reasons": reasons if reasons else ["ok"],
        "checks": checks,
    }
    out_dir = project_root / "reports" / "security"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"security_gate_{stage}_{report['run_utc']}.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["report_path"] = str(out_path)
    return report


def _signing_key(project_root: Path) -> bytes:
    resolved = resolve_secret(project_root, name="MLBOTNAV_SIGNING_KEY")
    env_key = str(resolved.get("value", "")).strip()
    if env_key:
        return env_key.encode("utf-8")
    # Fallback deterministic local key for dev-mode only.
    fallback = f"{project_root.resolve()}::mlbotnav::signing".encode("utf-8")
    return hashlib.sha256(fallback).digest()


def sign_file(project_root: Path, *, path: Path, meta: dict | None = None) -> Path:
    key = _signing_key(project_root)
    data = path.read_bytes()
    sig = hmac.new(key, data, hashlib.sha256).hexdigest()
    payload = {
        "file": str(path),
        "signature_alg": "HMAC-SHA256",
        "signature": sig,
        "meta": meta or {},
    }
    out = Path(str(path) + ".sig.json")
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Security gate helper.")
    parser.add_argument("--stage", default="manual", help="Gate stage label, e.g. promote")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    report = run_security_gate(project_root, stage=args.stage)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if bool(report.get("allowed", False)) else 2


if __name__ == "__main__":
    raise SystemExit(main())
