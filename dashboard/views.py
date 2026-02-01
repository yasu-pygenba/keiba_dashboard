from django.shortcuts import render
from dashboard.models import PerRace
from django.db.models import Sum

BET_TYPES = ['単勝', '複勝', '馬連', '馬単', 'ワイド']
AXIS_COLS = ['印', '印2', '印3']

def venue_dashboard(request):
    base_qs = PerRace.objects.all()

    # 年リスト
    years = (
        base_qs.values_list('kaisai_date', flat=True)
            .exclude(kaisai_date__isnull=True).exclude(kaisai_date='')
            .distinct()
    )
    years = sorted({str(d)[:4] for d in years if str(d)[:4].isdigit()}, reverse=True)

    # 選択値
    venue = request.GET.get('v', '')
    year = request.GET.get('y', '')
    kaisai_date = request.GET.get('d', '')
    axis = request.GET.get('axis', '印')
    surface = request.GET.get('s', '')
    distance = request.GET.get('dist', '')

    qs = base_qs

    # フィルタ用QS
    if venue:
        qs = qs.filter(venue=venue)

    if axis:
        qs = qs.filter(axis_col=axis)

    if surface:
        qs = qs.filter(surface=surface)
    
    if distance:
        try:
            qs = qs.filter(distance=int(distance))
        except ValueError:
            pass

    # 年 → 日付の優先順位
    if kaisai_date:
        qs = qs.filter(kaisai_date=kaisai_date)
    elif year:
        qs = qs.filter(kaisai_date__startswith=year)

    # 日付リスト（年でフィルタ→その結果からリストを作成）
    date_source_qs = base_qs
    if year:
        date_source_qs = date_source_qs.filter(kaisai_date__startswith=year)
    if venue:
        date_source_qs = date_source_qs.filter(venue=venue)
    if axis:
        date_source_qs = date_source_qs.filter(axis_col=axis)

    dates = (
        date_source_qs.values_list('kaisai_date', flat=True)
            .exclude(kaisai_date__isnull=True).exclude(kaisai_date='')
            .distinct()
            .order_by('-kaisai_date')
    )

    venue_source_qs = base_qs
    if kaisai_date:
        venue_source_qs = venue_source_qs.filter(kaisai_date=kaisai_date)
    if axis:
        venue_source_qs = venue_source_qs.filter(axis_col=axis)

    venues = (
        venue_source_qs.values_list('venue', flat=True)
            .exclude(venue__isnull=True).exclude(venue='')
            .distinct()
            .order_by('venue')
    )

    dist_qs = base_qs
    if venue:
        dist_qs = dist_qs.filter(venue=venue)
    if surface:
        dist_qs = dist_qs.filter(surface=surface)

    distances = (
        dist_qs.values_list('distance', flat=True)
            .exclude(distance__isnull=True)
            .distinct()
            .order_by('distance')
    )

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
        "years": years, 
        "dates": dates,
        "axis_cols": AXIS_COLS,
        "distances": distances,
        "selected_venue": venue,
        "selected_year": year,
        "selected_date": kaisai_date,
        "selected_axis": axis,
        'selected_surface': surface,
        "selected_distance": distance,
    }

    return render(request, "dashboard/venue.html", context)