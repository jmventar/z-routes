def clean_float(value):
    # Clean values ex: 61km(37.9 miles), 431m (1,414‘)
    if value:
        val = value.replace("km", "").replace("m", "").strip()
        val = val.partition('(')[0]
        return 0 if len(val) <= 0 else val

