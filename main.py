# -*- coding: utf-8 -*-
"""Main entry point for the Autonomous Learning Agent."""
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.checkpoints import CheckpointDefinition
from src.graph.learning_graph import get_learning_workflow, LearningState


def main():
    
    print("AUTONOMOUS LEARNING AGENT ")
    print()
    
    # Create a learning checkpoint
    checkpoint = CheckpointDefinition(
        id="python_functions",
        topic="Python Functions and Parameters",
        objectives=[
            "Understand function definition syntax",
            "Learn how to use function parameters",
            "Master return values and function calls"
        ],
        difficulty="beginner",
        estimated_minutes=15,
        notes=r"""
        ## Python Functions
        
        Functions in Python are reusable blocks of code that perform specific tasks.
        
        ### Defining Functions
        Use the `def` keyword to define a function:
        ```python
        def function_name(parameters):
            # function body
            return value
        ```
        
        ### Parameters
        - **Positional parameters**: Must be passed in order
        - **Keyword parameters**: Can be passed by name
        - **Default parameters**: Have default values
        - **\*args**: Variable number of positional arguments
        - **\*\*kwargs**: Variable number of keyword arguments
        
        ### Return Values
        Functions can return values using the `return` statement.
        Multiple values can be returned as a tuple.
        """
    )
    
    print(f"[TOPIC] Learning Topic: {checkpoint.topic}")
    print("[OBJECTIVES]")
    for i, obj in enumerate(checkpoint.objectives, 1):
        print(f"   {i}. {obj}")
    print()
    
    # User notes (simulating learner's existing knowledge)
    user_notes = """
    Functions in Python are defined using the 'def' keyword.
    They can take parameters and return values.
    Example: def greet(name): return f"Hello {name}"
    """
    
    print("[NOTES] User Notes Provided:")
    print(user_notes.strip())
    print()
    
    # Initialize workflow
    print("-" * 70)
    print("INITIALIZING WORKFLOW...")
    print("-" * 70)
    print()
    
    workflow = get_learning_workflow()
    
    # Start a learning session with our checkpoint
    workflow.start_learning_session([checkpoint])
    
    print("[OK] Workflow initialized")
    print("[OK] Learning session started")
    print("[OK] Learning workflow created")
    print()
    
    # Execute workflow
    print("-" * 70)
    print("EXECUTING LEARNING WORKFLOW...")
    print("-" * 70)
    print()
    
    try:
        result = workflow.run_complete_workflow(checkpoint, user_notes)
        
        print()
        print("-" * 70)
        print("WORKFLOW RESULTS")
        print("-" * 70)
        print()
        
        # Display results
        print(f"Final Stage: {result.current_stage}")
        print(f"Sources Gathered: {len(result.sources)}")
        print(f"Questions Generated: {len(result.questions)}")
        
        # Show error if any
        if result.error:
            print()
            print(f"  Error: {result.error}")
            if "API key" in result.error or "GITHUB_TOKEN" in result.error:
                print()
                print(" Note: Configure your .env file with API keys to enable full functionality.")
                print("   See SETUP.md for instructions.")
        
        # Show gathered sources
        if result.sources:
            print()
            print(f"[SOURCES] Study Sources ({len(result.sources)} total):")
            print()
            for i, source in enumerate(result.sources[:3], 1):
                print(f"   {i}. Type: {source.get('type', 'unknown')}")
                print(f"      Title: {source.get('title', 'N/A')}")
                content = source.get('content', '')[:80]
                if content:
                    print(f"      Preview: {content}...")
                print()
        
        # Show generated questions
        if result.questions:
            print()
            print(f"[QUIZ] Quiz Questions ({len(result.questions)} generated):")
            print()
            for i, question in enumerate(result.questions[:3], 1):
                print(f"   {i}. {question.question[:80]}...")
                print()
        
        print("-" * 70)
        
        # Show messages
        if result.messages:
            print()
            print("[MESSAGES] Workflow Messages:")
            for msg in result.messages:
                print(f"   - {msg}")
            print()
        
        # Determine success
        if result.current_stage == "quiz_ready":
            print("[SUCCESS] WORKFLOW COMPLETED SUCCESSFULLY")
            print("   Quiz is ready! In the full app, users would take the quiz interactively.")
            return 0
        elif result.error:
            print("[WARNING] WORKFLOW COMPLETED WITH ERRORS")
            return 1
        else:
            print("[STATUS] WORKFLOW STATUS: " + result.current_stage)
            return 0
            
    except Exception as e:
        print()
        print("-" * 70)
        print(f" WORKFLOW FAILED: {e}")
        print("-" * 70)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        print()
        print("=" * 70)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("  Workflow interrupted by user")
        print("=" * 70)
        sys.exit(130)
    except Exception as e:
        print()
        print("=" * 70)
        print(f" FATAL ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
