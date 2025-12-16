# Recommender Module

Phase 0 measurement infrastructure for the recommendation engine.

## Components

### logging.py - Request/Response Logging

Logs all recommendation API calls for analysis.

```python
from recommender.logging import get_logger

logger = get_logger()
request_id = logger.generate_request_id()
logger.start_request_timer(request_id)

# ... process recommendations ...

logger.log_request(
    request_id=request_id,
    preferences=prefs,
    results=results,
    total_candidates=100,
    primary_count=8,
    relaxed_count=2
)
```

### metrics.py - Metrics Aggregation

Computes and stores recommendation metrics.

```python
from recommender.metrics import get_aggregator

aggregator = get_aggregator()

# Get summary metrics
metrics = aggregator.get_current_metrics(days=7)

# Get daily breakdown
daily = aggregator.get_metrics_range(start=date.today() - timedelta(days=7), end=date.today())
```

### evaluation.py - Scenario Evaluation

Runs evaluation scenarios for regression testing.

```python
from recommender.evaluation import get_evaluator

evaluator = get_evaluator(base_url='http://localhost:5000')

# Run all scenarios
report = evaluator.run_all_scenarios()

# Run specific category
report = evaluator.run_all_scenarios(category='core_persona')

# Generate human-readable report
print(evaluator.generate_report(verbose=True))
```

## Database Tables

Run migration to create tables:

```bash
cd backend
python migrations/_001_add_recommendation_logging.py
```

### recommendation_requests

Stores individual API requests with preferences and results.

### recommendation_metrics_daily

Aggregated daily metrics (computed from recommendation_requests).

### evaluation_scenarios

Stored evaluation scenarios with baseline results.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/metrics` | GET | Get summary metrics for last N days |
| `/api/metrics/daily` | GET | Get daily breakdown |
| `/api/metrics/top-searches` | GET | Get most common search patterns |
| `/api/evaluation/run` | POST | Run evaluation scenarios |
| `/api/evaluation/scenarios` | GET | List available scenarios |
| `/api/migration/logging` | POST | Run logging tables migration |

## Metrics Tracked

- Response time (avg, p50, p95, p99)
- Relaxed trigger rate
- No results rate
- Average top score
- Search pattern distribution
