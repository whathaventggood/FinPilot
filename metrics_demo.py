from metrics import calculate_metrics
import pandas as pd

df = pd.DataFrame(
    [
        ["20250902",11.0,200.0],
        ["20250901",10.0,100.0],
    ],
    columns=["trade_date","close","vol"],
)
print(calculate_metrics(df))