# F024 - VWAP DISTANCE 1M STRICT PASSPORT

ID: F024
FEATURE: vwap_distance_1m
ACTION_ID: F024_VWAPDIST_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1=ALLOW, 0=BLOCK

## Meaning

F024 checks where the closed 1m candle sits relative to session VWAP.
The raw feature is `vwap_distance = (close - vwap) / close`.
Positive value means price is above VWAP, negative value means price is below VWAP.

## What Calibrates

F024_signal_mode
- 1 = SIDE
- 2 = DISTANCE

SIDE mode:
- F024_side_state: 1=ABOVE, -1=BELOW.
- F024_dist_thr_pct: minimum distance from VWAP in percent.

DISTANCE mode:
- F024_distance_state: 1=FAR, -1=NEAR.
- F024_dist_thr_pct: absolute distance threshold in percent.

Range:
- F024_dist_thr_pct: min 0.00, max 5.00, step 0.01.

## What Does Not Calibrate Here

- trade side LONG/SHORT
- timeframe
- VWAP formula
- session reset rule
- price source
- volume source
- stop loss
- take profit
- timeout
- order size
- dynamic exit

## Runtime Rule

The runtime action uses the previous closed bar:

`vwap_distance_pct = shift(vwap_distance, 1) * 100`.

SIDE:
- ABOVE allows when `vwap_distance_pct >= F024_dist_thr_pct`.
- BELOW allows when `vwap_distance_pct <= -F024_dist_thr_pct`.

DISTANCE:
- FAR allows when `abs(vwap_distance_pct) >= F024_dist_thr_pct`.
- NEAR allows when `abs(vwap_distance_pct) <= F024_dist_thr_pct`.

## Calibration Row

F024 | vwap_distance_1m | F024_VWAPDIST_ALLOW | ENTRY_FILTER | signal_mode(SIDE/DISTANCE), side_state(ABOVE/BELOW), distance_state(NEAR/FAR), dist_thr_pct(0.00-5.00 step 0.01) | fixed: TF=1m,VWAP=session cumulative typical_price*volume/volume,CALC_METHOD=CLOSED_BAR_SHIFT_1 | output: 1/0
