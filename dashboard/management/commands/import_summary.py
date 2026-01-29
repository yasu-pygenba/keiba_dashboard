import pandas as pd
from django.core.management.base import BaseCommand
from dashboard.models import Summary

class Command(BaseCommand):
    help = "Import per_race_{kaisai_date}.pkl into DB"

    def add_arguments(self, parser):
        parser.add_argument('--kaisai_date', required=True)
        parser.add_argument('--file-path', required=True)

    def handle(self, *args, **options):
        kaisai_date = options['kaisai_date']
        file_path = options['file_path']

        df = pd.read_pickle(file_path, encoding='utf-8-sig')

        # 同日のデータは入れ直し
        Summary.objects.filter(kaisai_date=kaisai_date).delete()

        objs = []
        for _, r in df.iterrows():
            objs.append(Summary(
                axis_col=str(r["axis_col"]),
                bet_type=str(r["bet_type"]),
                total_bet_yen=int(r["total_bet_yen"]),
                total_return_yen=int(r["total_return_yen"]),
                n_bets=int(r["n_bets"]),
                n_hits=int(r["n_hits"]),
                hit_rate=float(r["hit_rate"]),
                roi=float(r["ROI"]),
                kaisai_date=str(kaisai_date),
            ))

        Summary.objects.bulk_create(objs, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'Imported {len(objs)} rows for {kaisai_date}'))