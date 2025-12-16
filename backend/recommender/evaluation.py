"""
Evaluation Scenario Runner
==========================

Handles loading and running evaluation scenarios for regression testing.
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class ScenarioResult:
    """Result of running a single scenario."""
    scenario_id: int
    name: str
    passed: bool
    result_count: int
    top_score: Optional[float]
    expected_min_results: int
    expected_min_top_score: Optional[float]
    reason: Optional[str] = None
    response_time_ms: int = 0
    baseline_match: bool = True


class ScenarioEvaluator:
    """
    Loads and runs evaluation scenarios.
    
    Usage:
        evaluator = ScenarioEvaluator(base_url='http://localhost:5000')
        
        # Run all scenarios
        report = evaluator.run_all_scenarios()
        
        # Run specific category
        report = evaluator.run_scenarios(category='core_persona')
    """
    
    def __init__(self, base_url: str = 'http://localhost:5000'):
        """
        Initialize the evaluator.
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url
        self.scenarios_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'scenarios'
        )
    
    def load_scenarios(
        self, 
        category: Optional[str] = None,
        scenario_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Load evaluation scenarios from JSON files.
        
        Args:
            category: Filter by category (optional)
            scenario_ids: Filter by specific IDs (optional)
            
        Returns:
            List of scenario dicts
        """
        scenarios = []
        
        # Load generated personas
        personas_file = os.path.join(self.scenarios_dir, 'generated_personas.json')
        if os.path.exists(personas_file):
            with open(personas_file, 'r', encoding='utf-8') as f:
                all_scenarios = json.load(f)
                
            # Filter by category if specified
            if category:
                all_scenarios = [s for s in all_scenarios if s.get('category') == category]
            
            # Filter by IDs if specified
            if scenario_ids:
                all_scenarios = [s for s in all_scenarios if s.get('id') in scenario_ids]
            
            scenarios.extend(all_scenarios)
        
        return scenarios
    
    def run_scenario(self, scenario: Dict[str, Any]) -> ScenarioResult:
        """
        Run a single evaluation scenario.
        
        Args:
            scenario: Scenario dict with preferences and expected results
            
        Returns:
            ScenarioResult with pass/fail status
        """
        scenario_id = scenario.get('id', 0)
        name = scenario.get('name', f'Scenario {scenario_id}')
        preferences = scenario.get('preferences', {})
        expected_min_results = scenario.get('expected_min_results', 1)
        expected_min_top_score = scenario.get('expected_min_top_score')
        expects_relaxed = scenario.get('expects_relaxed', False)
        
        try:
            import time
            start_time = time.time()
            
            # Call the recommendations API
            response = requests.post(
                f'{self.base_url}/api/recommendations',
                json=preferences,
                timeout=30
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code != 200:
                return ScenarioResult(
                    scenario_id=scenario_id,
                    name=name,
                    passed=False,
                    result_count=0,
                    top_score=None,
                    expected_min_results=expected_min_results,
                    expected_min_top_score=expected_min_top_score,
                    reason=f'API returned status {response.status_code}',
                    response_time_ms=response_time_ms,
                )
            
            data = response.json()
            
            if not data.get('success'):
                return ScenarioResult(
                    scenario_id=scenario_id,
                    name=name,
                    passed=False,
                    result_count=0,
                    top_score=None,
                    expected_min_results=expected_min_results,
                    expected_min_top_score=expected_min_top_score,
                    reason=f'API error: {data.get("error", "Unknown")}',
                    response_time_ms=response_time_ms,
                )
            
            results = data.get('data', [])
            result_count = len(results)
            top_score = results[0].get('match_score') if results else None
            
            # Evaluate pass/fail
            passed = True
            reason = None
            
            # Check minimum results
            if result_count < expected_min_results:
                if not expects_relaxed or result_count == 0:
                    passed = False
                    reason = f'Too few results: {result_count} < {expected_min_results}'
            
            # Check minimum top score (if applicable)
            if passed and expected_min_top_score is not None and top_score is not None:
                if top_score < expected_min_top_score:
                    passed = False
                    reason = f'Top score too low: {top_score} < {expected_min_top_score}'
            
            return ScenarioResult(
                scenario_id=scenario_id,
                name=name,
                passed=passed,
                result_count=result_count,
                top_score=top_score,
                expected_min_results=expected_min_results,
                expected_min_top_score=expected_min_top_score,
                reason=reason,
                response_time_ms=response_time_ms,
            )
            
        except requests.exceptions.RequestException as e:
            return ScenarioResult(
                scenario_id=scenario_id,
                name=name,
                passed=False,
                result_count=0,
                top_score=None,
                expected_min_results=expected_min_results,
                expected_min_top_score=expected_min_top_score,
                reason=f'Request failed: {str(e)}',
            )
        except Exception as e:
            return ScenarioResult(
                scenario_id=scenario_id,
                name=name,
                passed=False,
                result_count=0,
                top_score=None,
                expected_min_results=expected_min_results,
                expected_min_top_score=expected_min_top_score,
                reason=f'Error: {str(e)}',
            )
    
    def run_all_scenarios(
        self,
        category: Optional[str] = None,
        scenario_ids: Optional[List[int]] = None,
        parallel: int = 1
    ) -> Dict[str, Any]:
        """
        Run all evaluation scenarios.
        
        Args:
            category: Filter by category (optional)
            scenario_ids: Filter by specific IDs (optional)
            parallel: Number of parallel workers (not implemented yet)
            
        Returns:
            Report dict with results
        """
        scenarios = self.load_scenarios(category=category, scenario_ids=scenario_ids)
        
        if not scenarios:
            return {
                'success': True,
                'total_scenarios': 0,
                'passed': 0,
                'failed': 0,
                'results': [],
                'message': 'No scenarios found',
            }
        
        results = []
        passed_count = 0
        failed_count = 0
        
        for scenario in scenarios:
            result = self.run_scenario(scenario)
            results.append({
                'scenario_id': result.scenario_id,
                'name': result.name,
                'passed': result.passed,
                'result_count': result.result_count,
                'top_score': result.top_score,
                'expected_min_results': result.expected_min_results,
                'expected_min_top_score': result.expected_min_top_score,
                'reason': result.reason,
                'response_time_ms': result.response_time_ms,
            })
            
            if result.passed:
                passed_count += 1
            else:
                failed_count += 1
        
        return {
            'success': True,
            'total_scenarios': len(scenarios),
            'passed': passed_count,
            'failed': failed_count,
            'pass_rate': round(passed_count / len(scenarios) * 100, 1) if scenarios else 0,
            'results': results,
        }
    
    def generate_report(
        self,
        category: Optional[str] = None,
        verbose: bool = False
    ) -> str:
        """
        Generate a human-readable evaluation report.
        
        Args:
            category: Filter by category (optional)
            verbose: Include detailed results
            
        Returns:
            Formatted report string
        """
        report_data = self.run_all_scenarios(category=category)
        
        lines = [
            "=" * 70,
            "EVALUATION REPORT",
            "=" * 70,
            f"Date: {datetime.now().isoformat()}",
            f"Total Scenarios: {report_data['total_scenarios']}",
            f"Passed: {report_data['passed']}",
            f"Failed: {report_data['failed']}",
            f"Pass Rate: {report_data.get('pass_rate', 0)}%",
            "=" * 70,
        ]
        
        if verbose or report_data['failed'] > 0:
            lines.append("\nFAILED SCENARIOS:")
            lines.append("-" * 70)
            
            for result in report_data['results']:
                if not result['passed']:
                    lines.append(f"\n[FAIL] {result['name']} (ID: {result['scenario_id']})")
                    lines.append(f"  Reason: {result['reason']}")
                    lines.append(f"  Results: {result['result_count']}, Top Score: {result['top_score']}")
        
        if verbose:
            lines.append("\n\nALL RESULTS:")
            lines.append("-" * 70)
            
            for result in report_data['results']:
                status = "PASS" if result['passed'] else "FAIL"
                lines.append(f"[{status}] {result['name']}: {result['result_count']} results, "
                           f"score={result['top_score']}, time={result['response_time_ms']}ms")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)


# Singleton instance
_evaluator_instance = None

def get_evaluator(base_url: str = 'http://localhost:5000') -> ScenarioEvaluator:
    """Get the singleton evaluator instance."""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = ScenarioEvaluator(base_url=base_url)
    return _evaluator_instance
