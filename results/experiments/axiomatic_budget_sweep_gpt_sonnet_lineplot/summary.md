# Axiomatic Budget Sweep Summary

Accuracy and invalid-rate are reported against mean realized output tokens.
Invalid-rate is defined as `1 - accuracy`.
Anthropic runs do not expose reasoning-token counts in usage metadata; this field is recorded as NA.

| Budget | Accuracy | Invalid Rate | Mean Output Tokens | Cap-Hit Rate | Empty Rate | API Error Rate | Token Obs |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1024 | 0.0400 | 0.9600 | 1006.72 | 0.9600 | 0.9467 | 0.0000 | 75 |
| 1025 | 0.1200 | 0.8800 | 790.64 | 0.3333 | 0.3333 | 0.0000 | 75 |
| 4096 | 0.2267 | 0.7733 | 2908.28 | 0.4267 | 0.4267 | 0.0000 | 75 |
| 4096 | 0.3467 | 0.6533 | 3454.5066666666667 | 0.5733 | 0.5600 | 0.0000 | 75 |
| 8192 | 0.3200 | 0.6800 | 5898.546666666667 | 0.4533 | 0.4533 | 0.0000 | 75 |
| 8192 | 0.5333 | 0.4667 | 5387.866666666667 | 0.3333 | 0.3333 | 0.0000 | 75 |
| 32768 | 0.5467 | 0.4533 | 13282.693333333333 | 0.0533 | 0.0533 | 0.0000 | 75 |
| 32768 | 0.7600 | 0.2400 | 6122.04 | 0.0000 | 0.0000 | 0.0000 | 75 |
| 64000 | 0.5467 | 0.4533 | 18824.6 | 0.0000 | 0.0000 | 0.0000 | 75 |
| 65536 | 0.7333 | 0.2667 | 7898.64 | 0.0000 | 0.0000 | 0.0000 | 75 |
