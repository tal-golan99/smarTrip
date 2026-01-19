# Evaluation Scenarios

This folder contains evaluation scenarios for testing the recommendation engine.

## Files

- `generated_personas.json` - 100 automatically generated user personas with diverse preferences

## Scenario Categories

1. **core_persona** - Main user archetypes (students, families, retirees, etc.)
2. **edge_case** - Edge cases that should trigger relaxed results or no results
3. **regional** - Region-specific searches (safaris, tropical, etc.)
4. **type_specific** - Trip type-specific searches (photography, etc.)

## Regenerating Personas

To regenerate the personas:

```bash
cd backend
python scripts/generate_personas.py
```

## Adding Custom Scenarios

Create additional JSON files in this folder with the following structure:

```json
[
  {
    "id": 1,
    "name": "Scenario Name",
    "description": "What this scenario tests",
    "category": "core_persona",
    "preferences": {
      "budget": 10000,
      "preferred_type_id": 1,
      "preferred_theme_ids": [1, 2],
      "selected_continents": ["Europe"],
      "min_duration": 7,
      "max_duration": 14,
      "difficulty": 2
    },
    "expected_min_results": 5,
    "expected_min_top_score": 60
  }
]
```

## Running Evaluations

Via API:
```bash
curl -X POST http://localhost:5000/api/evaluation/run
```

Via Python:
```python
from analytics.evaluation import get_evaluator

evaluator = get_evaluator(base_url='http://localhost:5000')
report = evaluator.run_all_scenarios()
print(evaluator.generate_report())
```
