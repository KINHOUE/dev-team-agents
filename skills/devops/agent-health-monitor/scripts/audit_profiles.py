"""Audit statique des profils Hermes : modele, provider, coherence, cles, skills."""
from pathlib import Path
import re
import sys

HOME = Path.home() / "AppData" / "Local" / "hermes"
PROVIDER_ENV = {
    "deepseek": "DEEPSEEK_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "nous": "NOUS_API_KEY",
}


def profiles() -> list[str]:
    names = ["default"]
    d = HOME / "profiles"
    if d.exists():
        names += sorted(p.name for p in d.iterdir() if p.is_dir())
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def profile_dir(name: str) -> Path:
    return HOME if name == "default" else HOME / "profiles" / name


def parse_model(cfg: Path) -> dict:
    if not cfg.exists():
        return {}
    out, in_model = {}, False
    for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^model:\s*$", line):
            in_model = True
            continue
        if in_model:
            if line and not line.startswith((" ", "\t")):
                break
            m = re.match(r"^\s+([a-z_]+):\s*(.+?)\s*$", line)
            if m:
                out[m.group(1)] = m.group(2).strip().strip('"\'')
    return out


def env_keys(base: Path) -> set[str]:
    keys = set()
    for f in {base / ".env", HOME / ".env"}:
        if f.exists():
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.match(r"^([A-Z0-9_]+)\s*=", line)
                if m:
                    keys.add(m.group(1))
    return keys


def skills(base: Path) -> list[str]:
    d = base / "skills"
    if not d.exists():
        return []
    return sorted(p.parent.name for p in d.rglob("SKILL.md"))


def main() -> int:
    issues: list[str] = []
    print(f"{'PROFIL':14} {'MODELE':30} {'PROVIDER':12} {'CLE':5} SKILLS")
    print("-" * 96)
    for name in profiles():
        base = profile_dir(name)
        model = parse_model(base / "config.yaml")
        default = model.get("default", "—")
        provider = model.get("provider", "—")
        base_url = model.get("base_url", "")
        keys = env_keys(base)
        env_name = PROVIDER_ENV.get(provider)
        has_key = bool(env_name and env_name in keys)

        sk = skills(base)
        print(f"{name:14} {default:30} {provider:12} {'oui' if has_key else 'NON':5} {len(sk)} skills")

        if provider == "fireworks" and default.startswith("deepseek"):
            issues.append(f"{name}: modele '{default}' incompatible avec provider '{provider}'")
        if env_name and not has_key:
            issues.append(f"{name}: cle {env_name} absente")
        if not model:
            issues.append(f"{name}: aucun bloc model dans config.yaml")
        if base_url and provider == "deepseek" and "fireworks" in base_url:
            issues.append(f"{name}: base_url pointe encore sur Fireworks")
        if not sk:
            issues.append(f"{name}: aucune skill installee")

    print()
    print(f"PROBLEMES: {len(issues)}")
    for i in issues:
        print(" -", i)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
