from pathlib import Path
import re
import pandas as pd
from django.core.management.base import BaseCommand
from dashboard.models import PerRace

PATTERN = re.compile(r"per_race_(\d{8})\.pkl$")

class Command(BaseCommand):
    help = "Import all per_race_YYYYMMDD.pkl under a directory into DB"

    def add_arguments(self, parser):
        parser.add_argument("--dir", required=True)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dir_path = Path(options["dir"])
        dry_run = options["dry_run"]

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        files = sorted([p for p in dir_path.glob("per_race_*.pkl") if PATTERN.search(p.name)])
        if not files:
            self.stdout.write(self.style.WARNING("No per_race_YYYYMMDD.pkl found."))
            return

        total_rows = 0
        imported_dates = []

        for pkl_path in files:
            m = PATTERN.search(pkl_path.name)
            kaisai_date = m.group(1)

            df = pd.read_pickle(pkl_path)

            required = [
                "race_id","開催","距離","コース","天候","馬場",
                "axis_col","axis_mark","bet_type",
                "total_bet_yen","total_return_yen","n_bets","n_hits","hit_rate","ROI"
            ]
            missing = [c for c in required if c not in df.columns]
            if missing:
                self.stdout.write(self.style.ERROR(f"{pkl_path.name}: missing columns {missing} -> skipped"))
                continue

            df["race_id"] = df["race_id"].astype(str)
            df["kaisai_date"] = df["race_id"].str.slice(0, 8)

            # ファイル名の日付と一致してるか軽くチェック
            dates_in_file = set(df["kaisai_date"].unique().tolist())
            if dates_in_file != {kaisai_date}:
                self.stdout.write(self.style.WARNING(
                    f"{pkl_path.name}: kaisai_date in file {sorted(dates_in_file)} != filename {kaisai_date}"
                ))

            if not dry_run:
                PerRace.objects.filter(kaisai_date__in=list(dates_in_file)).delete()

            objs = []
            for _, r in df.iterrows():
                objs.append(PerRace(
                    race_id=str(r["race_id"]),
                    kaisai_date=str(r["kaisai_date"]),
                    venue=str(r["開催"]),
                    distance=int(r["距離"]) if pd.notna(r["距離"]) else None,
                    surface=str(r["コース"]) if pd.notna(r["コース"]) else "",
                    weather=str(r["天候"]) if pd.notna(r["天候"]) else "",
                    baba=str(r["馬場"]) if pd.notna(r["馬場"]) else "",
                    axis_col=str(r["axis_col"]),
                    axis_mark=str(r["axis_mark"]),
                    bet_type=str(r["bet_type"]),
                    total_bet_yen=int(r["total_bet_yen"]),
                    total_return_yen=float(r["total_return_yen"]),
                    n_bets=int(r["n_bets"]),
                    n_hits=int(r["n_hits"]),
                    hit_rate=float(r["hit_rate"]),
                    roi=float(r["ROI"]),
                ))

            if not dry_run:
                PerRace.objects.bulk_create(objs, batch_size=2000)

            total_rows += len(objs)
            imported_dates.extend(sorted(dates_in_file))
            self.stdout.write(self.style.SUCCESS(f"{pkl_path.name}: {len(objs)} rows"))

        self.stdout.write(self.style.SUCCESS(f"Done. total_rows={total_rows}, dates={sorted(set(imported_dates))}"))

