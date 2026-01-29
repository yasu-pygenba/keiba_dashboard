import pandas as pd
from django.core.management.base import BaseCommand
from dashboard.models import PerRace

class Command(BaseCommand):
    help = 'Import per_race_{kaisai_date}.pkl into DB'

    def add_arguments(self, parser):
        parser.add_argument('--pkl-path', required=True)

    def handle(self, *args, **options):
        pkl_path = options['pkl_path']
        df = pd.read_pickle(pkl_path)

        # 列名チェック（念のため）
        required = [
            "race_id","開催","距離","コース","天候","馬場",
            "axis_col","axis_mark","bet_type",
            "total_bet_yen","total_return_yen","n_bets","n_hits","hit_rate","ROI"
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f'Missing columns in pkl: {missing}')
        
        # 文字列化&日付抽出
        df['race_id'] = df['race_id'].astype(str)
        df['kaisai_date'] = df['race_id'].str.slice(0, 8)

        # 同日データは入れ直し（MVPではとりあえずこの運用）
        dates = sorted(df['kaisai_date'].unique().tolist())
        PerRace.objects.filter(kaisai_date__in=dates).delete()

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

        PerRace.objects.bulk_create(objs, batch_size=2000)
        self.stdout.write(self.style.SUCCESS(f'Imprted {len(objs)} rows for dates={dates}'))