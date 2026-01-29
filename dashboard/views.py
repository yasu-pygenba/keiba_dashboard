from django.shortcuts import render
from dashboard.models import PerRace
from django.db.models import Sum

BET_TYPES = ['単勝', '複勝', '馬連', '馬単', 'ワイド']
AXIS_COLS = ['印', '印2', '印3']

def venue_dashboard(request):
    # ①セレクト用
    venues = (
        PerRace.objects
        .values_list("venue", flat=True)
        .exclude(venue__isnull=True)
        .exclude(venue="")
        .distinct()
        .order_by("venue")
    )

    dates = (
        PerRace.objects
        .values_list("kaisai_date", flat=True)
        .exclude(kaisai_date__isnull=True)
        .exclude(kaisai_date="")
        .distinct()
        .order_by("-kaisai_date")  # 新しい順
    )


    qs = PerRace.objects.all()

    # フィルタ
    venue = request.GET.get('v', '')
    if venue:
        qs = qs.filter(venue=venue)

    kaisai_date = request.GET.get('d', '')
    if kaisai_date:
        qs = qs.filter(kaisai_date=kaisai_date)

    axis = request.GET.get('axis', '印')
    qs = qs.filter(axis_col=axis)

    # DB集計（ORM）
    agg = (
        qs.values('bet_type')
            .annotate(
                total_bet=Sum('total_bet_yen'),
                total_return=Sum('total_return_yen'),
                n_bets=Sum('n_bets'),
                n_hits=Sum('n_hits'),
            )
    )

    rows = []
    for r in agg:
        total_bet = r['total_bet'] or 0
        total_return = r['total_return'] or 0
        n_bets = r['n_bets'] or 0
        n_hits = r['n_hits'] or 0

        roi = (total_return / total_bet * 100) if total_bet else 0
        hit_rate = (n_hits / n_bets * 100) if n_bets else 0
        profit = total_return - total_bet

        rows.append({
            "bet_type": r["bet_type"],
            "total_bet_yen": int(total_bet),
            "total_return_yen": int(total_return),
            "profit_yen": int(profit),
            "roi_pct": round(roi, 1),
            "n_bets": int(n_bets),
            "n_hits": int(n_hits),
            "hit_rate_pct": round(hit_rate, 1),
        })

    # ④ テンプレへ渡す
    context = {
        "rows": rows,
        "venues": venues,
        "dates": dates,
        "axis_cols": AXIS_COLS,
        "selected_venue": venue,
        "selected_date": kaisai_date,
        "selected_axis": axis,
    }

    return render(request, "dashboard/venue.html", context)