#!/usr/bin/env python3
"""
Cria a estrutura de diretórios para o projeto conforme o padrão discutido.

Uso básico:
    python tools/create_project_structure.py --root /caminho/para/project-root --package robbot

Opções importantes:
    --dry-run         : mostrando o que seria criado sem criar nada
    --force           : recriar arquivos placeholder (__init__.py/.gitkeep) mesmo se já existirem
    --skip-packages   : lista separada por vírgula de pacotes que, se instalados, fazem o script pular diretórios (ex: pytest)
    --yes             : não pedir confirmação (útil em scripts CI)
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import importlib.util
import sys
from typing import Dict, List, Set

DEFAULT_PACKAGE_NAME = "robbot"

# Estrutura base (relativa ao project root). Use {package} para o package name dentro de src/.
DIR_TEMPLATE = [
    "alembic/versions",
    "src/{package}",
    "src/{package}/__init__.py",  # create package marker as file
    "src/{package}/main.py",
    "src/{package}/config",
    "src/{package}/api/v1/routers",
    "src/{package}/api/v1/dependencies.py",
    "src/{package}/adapters/controllers",
    "src/{package}/adapters/repositories",
    "src/{package}/domain/entities",
    "src/{package}/domain/dtos",
    "src/{package}/services",
    "src/{package}/infra/db/models",
    "src/{package}/infra/migrations",
    "src/{package}/core",
    "src/{package}/schemas",
    "src/{package}/common",
    "docker",
    # tests intentionally included but may be skipped if pytest is detected (see mapping)
    "tests/unit",
    "tests/integration",
    # top-level helper files (placeholders)
    ".env.example",
    "requirements.txt",
    "README.md",
]

# Mapeamento padrão: pacote instalado -> diretórios a pular
# Você pode ajustar este dicionário conforme preferir.
DEFAULT_SKIP_MAP: Dict[str, List[str]] = {
    "pytest": ["tests"],           # se pytest instalado, pular criação de tests (exemplo do usuário)
    "alembic": ["alembic"],        # se alembic instalado, talvez você queira que o próprio alembic gere arquivos
    "docker": ["docker"],          # se docker-cli/pacote detectável, pular docker dir (opcional)
    # adicione mais se quiser
}

PLACEHOLDER_FILES = {
    "__init__.py": "__all__ = []\n",
    ".gitkeep": "",
    ".env.example": "PROJECT_NAME=My Service\nDEBUG=True\nDATABASE_URL=\nSECRET_KEY=\n",
    "requirements.txt": "# add dependencies here\n",
    "README.md": "# Project\n\nProject scaffold created by create_project_structure.py\n",
}


def is_package_installed(name: str) -> bool:
    """Detecta se um pacote está instalado no ambiente via importlib.util.find_spec."""
    try:
        spec = importlib.util.find_spec(name)
        return spec is not None
    except Exception:
        return False


def build_dirs(package: str) -> List[Path]:
    """Converte DIR_TEMPLATE em lista de Paths (somente diretórios)."""
    root = Path(".").resolve()
    paths: List[Path] = []
    for entry in DIR_TEMPLATE:
        entry_formatted = entry.format(package=package)
        p = root / entry_formatted
        # if path looks like a file (has extension) we treat parent as dir and add file separately later
        if Path(entry_formatted).suffix:
            # file placeholder, store full path (we will create parent dir and file)
            paths.append(p)
        else:
            paths.append(p)
    return paths


def collect_dirs_and_files(paths: List[Path]) -> (Set[Path], Set[Path]):
    """Separates directories and explicit file paths from the computed paths."""
    dirs: Set[Path] = set()
    files: Set[Path] = set()
    for p in paths:
        if p.suffix:  # explicit file (like __init__.py or main.py)
            dirs.add(p.parent)
            files.add(p)
        else:
            dirs.add(p)
    return dirs, files


def directories_to_create(
    all_dirs: Set[Path],
    skip_dirs: Set[str],
) -> List[Path]:
    """Applies skip rules and returns sorted list of directories to create."""
    to_create: List[Path] = []
    for d in sorted(all_dirs):
        # normalize relative part for comparison
        rel = str(d.relative_to(Path(".").resolve()))
        # if any skip_dir is prefix of rel, skip it
        if any(rel == sd or rel.startswith(f"{sd}/") for sd in skip_dirs):
            continue
        to_create.append(d)
    return to_create


def create_structure(
    root: Path,
    package: str,
    dry_run: bool,
    force: bool,
    skip_dirs: Set[str],
    files_to_create: Set[Path],
    yes: bool,
) -> None:
    """Cria os diretórios e arquivos (placeholders)."""
    # collect all dirs
    paths = build_dirs(package)
    dirs, explicit_files = collect_dirs_and_files(paths)
    # Merge explicit_files with files_to_create (explicit param may include top-level placeholders)
    explicit_files = explicit_files.union(files_to_create)

    # apply skip_dirs
    to_create_dirs = directories_to_create(dirs, skip_dirs)

    print("\nPlano de criação:")
    for d in to_create_dirs:
        print(f"  DIR: {d}")
    for f in sorted(explicit_files):
        rel = str(f.relative_to(Path(".").resolve()))
        # if parent dir is skipped, skip file too
        if any(str(f).startswith(sd + os.sep) or str(f).startswith(sd) for sd in skip_dirs):
            continue
        print(f"  FILE: {f}")

    if dry_run:
        print("\nModo dry-run: nada será criado.")
        return

    if not yes:
        resp = input("\nConfirmar criação acima? [y/N]: ").strip().lower()
        if resp not in ("y", "yes"):
            print("Abortando.")
            return

    # create directories
    for d in to_create_dirs:
        d.mkdir(parents=True, exist_ok=True)

    # create __init__.py in package directories (and ensure __init__ where appropriate)
    # We'll create __init__.py for any directory under src/{package}
    for d in to_create_dirs:
        try:
            rel = str(d.relative_to(Path(".").resolve()))
        except Exception:
            rel = str(d)
        if rel.startswith(f"src{os.sep}{package}") and (d.name != "__pycache__"):
            init_file = d / "__init__.py"
            if not init_file.exists() or force:
                init_file.write_text(PLACEHOLDER_FILES.get("__init__.py", ""))
    # create explicit files (like main.py, dependencies.py) with small placeholders
    for f in explicit_files:
        # skip if its parent dir was skipped
        parent_rel = str(f.parent.relative_to(Path(".").resolve()))
        if any(parent_rel == sd or parent_rel.startswith(f"{sd}/") for sd in skip_dirs):
            continue

        if f.exists() and not force:
            continue

        # basic content heuristics
        name = f.name
        if name == "__init__.py":
            content = PLACEHOLDER_FILES.get("__init__.py", "")
        elif name.endswith(".py"):
            # tiny placeholder python content with module docstring
            content = f'"""Placeholder generated for {f}"""\n\n'
            # if it's main.py create a small app factory
            if name == "main.py":
                content += (
                    "from fastapi import FastAPI\n\n"
                    "def create_app() -> FastAPI:\n"
                    "    app = FastAPI(title='robbot')\n"
                    "    return app\n\n"
                    "app = create_app()\n"
                )
            else:
                content += "\n"
        elif name in PLACEHOLDER_FILES:
            content = PLACEHOLDER_FILES[name]
        else:
            content = ""

        f.write_text(content)

    # create .gitkeep for empty directories (where no python files created)
    for d in to_create_dirs:
        # skip python packages (they already have __init__.py)
        if (d / "__init__.py").exists():
            continue
        # if contains files already, skip
        if any(d.iterdir()):
            continue
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists() or force:
            gitkeep.write_text("")

    print("\nCriação concluída.")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Criador de estrutura de projeto")
    p.add_argument(
        "--root",
        type=str,
        default=".",
        help="Caminho para o project-root (padrão: current dir)",
    )
    p.add_argument(
        "--package",
        type=str,
        default=DEFAULT_PACKAGE_NAME,
        help=f"Nome do pacote raíz em src/ (default: {DEFAULT_PACKAGE_NAME})",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Listar alterações sem criar nada",
    )
    p.add_argument("--force", action="store_true", help="Sobrescrever placeholders existentes")
    p.add_argument(
        "--skip-packages",
        type=str,
        default="",
        help="Lista separada por vírgula de pacotes que, se instalados, farão o script pular os diretórios mapeados (ex: pytest)",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="Confirmar automaticamente (não pedir confirmação)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    os.chdir(root)

    package = args.package
    dry_run = args.dry_run
    force = args.force
    yes = args.yes

    # build base paths and file placeholders
    paths = build_dirs(package)
    dirs, explicit_files = collect_dirs_and_files(paths)

    # build skip set from defaults + CLI
    skip_dirs: Set[str] = set()
    # check default mapping
    for pkg, dirs_list in DEFAULT_SKIP_MAP.items():
        if is_package_installed(pkg):
            for d in dirs_list:
                skip_dirs.add(d)
    # user-specified skip packages
    if args.skip_packages:
        for pkg_name in [p.strip() for p in args.skip_packages.split(",") if p.strip()]:
            if is_package_installed(pkg_name):
                # if package present and it exists in mapping, add mapped dirs, else add package name as dir
                mapped = DEFAULT_SKIP_MAP.get(pkg_name)
                if mapped:
                    for d in mapped:
                        skip_dirs.add(d)
                else:
                    # fallback: skip top-level dir with same name
                    skip_dirs.add(pkg_name)

    print(f"Projeto root: {root}")
    print(f"Package name: {package}")
    if skip_dirs:
        print("Diretórios marcados para pular (por pacotes instalados):")
        for sd in sorted(skip_dirs):
            print(f"  - {sd}")

    create_structure(
        root=root,
        package=package,
        dry_run=dry_run,
        force=force,
        skip_dirs=skip_dirs,
        files_to_create=set(explicit_files),
        yes=yes,
    )


if __name__ == "__main__":
    main()