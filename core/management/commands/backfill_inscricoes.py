import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Empresa


class Command(BaseCommand):
    help = (
        "Preenche inscricao_estadual/municipal das empresas EXISTENTES "
        "a partir de dados_legados/Tbl_Clientes.csv. Nunca cria empresas novas."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Sobrescreve IE/IM mesmo quando já preenchidos.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra o que faria sem salvar.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        dry_run = options["dry_run"]
        caminho = os.path.join(settings.BASE_DIR, "dados_legados", "Tbl_Clientes.csv")

        if not os.path.exists(caminho):
            self.stderr.write(f"CSV não encontrado: {caminho}")
            return

        atualizadas = 0
        ja_preenchidas = 0
        nao_encontradas = 0
        total_linhas = 0

        with open(caminho, "r", encoding="utf-8-sig") as f:
            linhas = f.read().splitlines()
            # O CSV legado tem uma linha de schema antes do cabeçalho real
            reader = csv.DictReader(linhas[1:])
            for row in reader:
                cnpj_limpo = (
                    (row.get("CGCCliente") or "")
                    .replace(".", "")
                    .replace("/", "")
                    .replace("-", "")
                    .strip()
                )
                if not cnpj_limpo:
                    continue
                total_linhas += 1
                ie = (row.get("INSCCliente") or "").strip() or None
                im = (row.get("InscMunicipal") or "").strip() or None
                if not ie and not im:
                    continue
                try:
                    empresa = Empresa.objects.get(cnpj=cnpj_limpo)
                except Empresa.DoesNotExist:
                    nao_encontradas += 1
                    continue

                mudou = False
                if ie and (force or not empresa.inscricao_estadual):
                    if empresa.inscricao_estadual != ie:
                        empresa.inscricao_estadual = ie
                        mudou = True
                if im and (force or not empresa.inscricao_municipal):
                    if empresa.inscricao_municipal != im:
                        empresa.inscricao_municipal = im
                        mudou = True

                if mudou:
                    atualizadas += 1
                    if not dry_run:
                        empresa.save(update_fields=["inscricao_estadual", "inscricao_municipal"])
                else:
                    ja_preenchidas += 1

        modo = "DRY-RUN (nada salvo). " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{modo}Backfill concluído: {atualizadas} atualizadas, "
                f"{ja_preenchidas} já preenchidas, "
                f"{nao_encontradas} CNPJs do CSV sem empresa no banco "
                f"({total_linhas} linhas com CNPJ lidas)."
            )
        )
