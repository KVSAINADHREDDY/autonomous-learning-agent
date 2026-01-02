"""
Performance Testing Suite for Autonomous Learning Agent
========================================================
Tests model performance across multiple dimensions:
- Response Time
- Context Gathering Quality
- Summary Generation Quality
- Multi-topic Evaluation
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.checkpoint import Checkpoint
from src.models.state import create_initial_state
from src.graph.learning_graph import create_learning_graph


# =========================================================
# DATA CLASSES FOR RESULTS
# =========================================================

@dataclass
class TestResult:
    """Single test result"""
    topic: str
    success: bool
    execution_time: float
    contexts_gathered: int
    context_valid: bool
    avg_relevance_score: float
    summary_length: int
    has_summary: bool
    error: str = None


@dataclass
class PerformanceReport:
    """Overall performance report"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    avg_execution_time: float
    avg_contexts_gathered: float
    avg_relevance_score: float
    success_rate: float
    test_results: List[TestResult]
    timestamp: str


# =========================================================
# TEST CASES
# =========================================================

TEST_CASES = [
    {
        "topic": "Python Functions",
        "objectives": [
            "Understand function syntax",
            "Learn about parameters and arguments",
            "Master return values"
        ],
        "notes": "Functions are reusable blocks of code defined with 'def' keyword."
    },
    {
        "topic": "Machine Learning Basics",
        "objectives": [
            "Understand supervised learning",
            "Learn about neural networks",
            "Know common ML algorithms"
        ],
        "notes": "ML is a subset of AI that learns from data."
    },
    {
        "topic": "Data Structures",
        "objectives": [
            "Understand arrays and lists",
            "Learn about stacks and queues",
            "Know when to use each structure"
        ],
        "notes": "Data structures organize and store data efficiently."
    },
    {
        "topic": "REST APIs",
        "objectives": [
            "Understand HTTP methods",
            "Learn about endpoints",
            "Know about authentication"
        ],
        "notes": "REST APIs enable communication between systems."
    },
    {
        "topic": "Database Fundamentals",
        "objectives": [
            "Understand SQL basics",
            "Learn about tables and relationships",
            "Know about indexing"
        ],
        "notes": "Databases store and manage structured data."
    }
]


# =========================================================
# TEST RUNNER
# =========================================================

def run_single_test(test_case: Dict[str, Any]) -> TestResult:
    """Run a single test case and return results"""
    topic = test_case["topic"]
    print(f"\n{'='*60}")
    print(f"Testing: {topic}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Create checkpoint
        checkpoint = Checkpoint(
            topic=topic,
            objectives=test_case["objectives"]
        )
        
        # Create initial state
        state = create_initial_state(
            checkpoint=checkpoint,
            user_notes=test_case.get("notes")
        )
        
        # Create and run graph
        graph = create_learning_graph()
        result = graph.invoke(state)
        
        execution_time = time.time() - start_time
        
        # Extract metrics
        contexts = result.get("gathered_contexts", [])
        contexts_gathered = len(contexts)
        context_valid = result.get("context_valid", False)
        
        # Calculate average relevance
        if contexts:
            avg_relevance = sum(c.relevance_score or 0 for c in contexts) / len(contexts)
        else:
            avg_relevance = 0.0
        
        # Check summary
        summary = result.get("summary", "")
        has_summary = bool(summary and len(summary) > 50)
        summary_length = len(summary) if summary else 0
        
        # Check for errors
        error = result.get("error")
        success = context_valid and has_summary and not error
        
        print(f"  ✓ Execution Time: {execution_time:.2f}s")
        print(f"  ✓ Contexts Gathered: {contexts_gathered}")
        print(f"  ✓ Context Valid: {context_valid}")
        print(f"  ✓ Avg Relevance: {avg_relevance:.2%}")
        print(f"  ✓ Summary Length: {summary_length} chars")
        print(f"  ✓ Status: {'PASSED ✅' if success else 'FAILED ❌'}")
        
        return TestResult(
            topic=topic,
            success=success,
            execution_time=execution_time,
            contexts_gathered=contexts_gathered,
            context_valid=context_valid,
            avg_relevance_score=avg_relevance,
            summary_length=summary_length,
            has_summary=has_summary,
            error=error
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"  ❌ Error: {str(e)}")
        
        return TestResult(
            topic=topic,
            success=False,
            execution_time=execution_time,
            contexts_gathered=0,
            context_valid=False,
            avg_relevance_score=0.0,
            summary_length=0,
            has_summary=False,
            error=str(e)
        )


def run_performance_tests(test_cases: List[Dict] = None) -> PerformanceReport:
    """Run all performance tests and generate report"""
    if test_cases is None:
        test_cases = TEST_CASES
    
    print("\n" + "="*70)
    print("🧪 AUTONOMOUS LEARNING AGENT - PERFORMANCE TEST SUITE")
    print("="*70)
    print(f"Running {len(test_cases)} test cases...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for test_case in test_cases:
        result = run_single_test(test_case)
        results.append(result)
    
    # Calculate aggregate metrics
    passed = sum(1 for r in results if r.success)
    failed = len(results) - passed
    
    avg_time = sum(r.execution_time for r in results) / len(results)
    avg_contexts = sum(r.contexts_gathered for r in results) / len(results)
    avg_relevance = sum(r.avg_relevance_score for r in results) / len(results)
    success_rate = passed / len(results) * 100
    
    report = PerformanceReport(
        total_tests=len(results),
        passed_tests=passed,
        failed_tests=failed,
        avg_execution_time=avg_time,
        avg_contexts_gathered=avg_contexts,
        avg_relevance_score=avg_relevance,
        success_rate=success_rate,
        test_results=results,
        timestamp=datetime.now().isoformat()
    )
    
    return report


def print_report(report: PerformanceReport):
    """Print formatted performance report"""
    print("\n")
    print("="*70)
    print("📊 PERFORMANCE TEST REPORT")
    print("="*70)
    print()
    
    # Summary Stats
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│                        SUMMARY STATISTICS                       │")
    print("├─────────────────────────────────────────────────────────────────┤")
    print(f"│  Total Tests:        {report.total_tests:>6}                                    │")
    print(f"│  Passed:             {report.passed_tests:>6}  ✅                                │")
    print(f"│  Failed:             {report.failed_tests:>6}  {'❌' if report.failed_tests > 0 else '  '}                                │")
    print(f"│  Success Rate:       {report.success_rate:>6.1f}%                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    print(f"│  Avg Execution Time: {report.avg_execution_time:>6.2f}s                                │")
    print(f"│  Avg Contexts:       {report.avg_contexts_gathered:>6.1f}                                  │")
    print(f"│  Avg Relevance:      {report.avg_relevance_score*100:>6.1f}%                                 │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    
    # Detailed Results
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│                        DETAILED RESULTS                         │")
    print("├────────────────────────┬──────┬────────┬──────┬────────┬────────┤")
    print("│ Topic                  │ Pass │ Time   │ Ctxs │ Relev  │ Summary│")
    print("├────────────────────────┼──────┼────────┼──────┼────────┼────────┤")
    
    for r in report.test_results:
        topic_short = r.topic[:20] + ".." if len(r.topic) > 22 else r.topic.ljust(22)
        status = "✅" if r.success else "❌"
        print(f"│ {topic_short} │  {status}  │ {r.execution_time:>5.1f}s │  {r.contexts_gathered:>2}  │ {r.avg_relevance_score*100:>5.1f}% │ {r.summary_length:>5}c │")
    
    print("└────────────────────────┴──────┴────────┴──────┴────────┴────────┘")
    print()
    
    # Performance Grade
    if report.success_rate >= 90:
        grade = "A+ 🏆"
    elif report.success_rate >= 80:
        grade = "A  ⭐"
    elif report.success_rate >= 70:
        grade = "B  👍"
    elif report.success_rate >= 60:
        grade = "C  📈"
    else:
        grade = "D  ⚠️"
    
    print(f"🎯 OVERALL GRADE: {grade}")
    print(f"📅 Test completed at: {report.timestamp}")
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    if report.avg_execution_time > 10:
        print("   • Consider optimizing LLM calls to reduce response time")
    if report.avg_contexts_gathered < 3:
        print("   • Improve web search to gather more context sources")
    if report.avg_relevance_score < 0.6:
        print("   • Tune relevance scoring for better context filtering")
    if report.success_rate < 80:
        print("   • Review failed test cases and fix edge cases")
    if report.success_rate >= 80 and report.avg_relevance_score >= 0.6:
        print("   • ✅ Model performing well! Consider adding more test cases.")
    print()


def save_report(report: PerformanceReport, filename: str = None):
    """Save report to JSON file"""
    if filename is None:
        filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Convert to dict
    report_dict = {
        "total_tests": report.total_tests,
        "passed_tests": report.passed_tests,
        "failed_tests": report.failed_tests,
        "avg_execution_time": report.avg_execution_time,
        "avg_contexts_gathered": report.avg_contexts_gathered,
        "avg_relevance_score": report.avg_relevance_score,
        "success_rate": report.success_rate,
        "timestamp": report.timestamp,
        "test_results": [asdict(r) for r in report.test_results]
    }
    
    with open(filename, "w") as f:
        json.dump(report_dict, f, indent=2)
    
    print(f"📁 Report saved to: {filename}")


# =========================================================
# QUICK TEST (Single Topic)
# =========================================================

def quick_test(topic: str = "Python Basics", objectives: List[str] = None):
    """Run a quick single-topic test"""
    if objectives is None:
        objectives = ["Understand the fundamentals"]
    
    test_case = {
        "topic": topic,
        "objectives": objectives,
        "notes": None
    }
    
    result = run_single_test(test_case)
    
    print("\n" + "="*40)
    print("QUICK TEST RESULT")
    print("="*40)
    print(f"Topic: {result.topic}")
    print(f"Status: {'PASSED ✅' if result.success else 'FAILED ❌'}")
    print(f"Time: {result.execution_time:.2f}s")
    print(f"Contexts: {result.contexts_gathered}")
    print(f"Relevance: {result.avg_relevance_score:.0%}")
    print(f"Summary: {result.summary_length} chars")
    
    return result


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Testing for Learning Agent")
    parser.add_argument("--quick", action="store_true", help="Run quick single test")
    parser.add_argument("--topic", type=str, default="Python Basics", help="Topic for quick test")
    parser.add_argument("--save", action="store_true", help="Save report to JSON file")
    parser.add_argument("--tests", type=int, default=5, help="Number of test cases to run")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_test(args.topic)
    else:
        # Run full test suite
        test_cases = TEST_CASES[:args.tests]
        report = run_performance_tests(test_cases)
        print_report(report)
        
        if args.save:
            save_report(report)
