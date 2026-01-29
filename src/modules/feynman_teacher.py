"""
Feynman Teaching module for explaining concepts in simple terms.
Uses the Feynman Technique: explain complex topics as if teaching a child.
"""
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

from src.utils.llm_provider import get_creative_llm


@dataclass
class FeynmanExplanation:
    """A Feynman-style explanation for a concept."""
    concept: str
    simple_explanation: str
    analogy: str
    real_world_example: str
    key_takeaways: List[str]


class FeynmanTeacher:
    """
    Generates simple, intuitive explanations using the Feynman Technique.
    
    Features:
    - Explains concepts in everyday language
    - Uses real-life analogies (cooking, building blocks, etc.)
    - Provides concrete examples
    - Breaks down complex topics step by step
    """
    
    def __init__(self):
        """Initialize the Feynman teacher."""
        self.llm = None  # Lazy initialization
    
    def _get_llm(self):
        """Get LLM instance (lazy initialization)."""
        if self.llm is None:
            try:
                self.llm = get_creative_llm()
            except Exception as e:
                print(f"⚠️ Could not initialize LLM: {e}")
        return self.llm
    
    def explain_concept(
        self,
        concept: str,
        context: str = "",
        failed_question: str = ""
    ) -> FeynmanExplanation:
        """
        Generate a Feynman-style explanation for a concept.
        
        Args:
            concept: The concept to explain
            context: Additional context about the topic
            failed_question: The question the user got wrong (if any)
            
        Returns:
            FeynmanExplanation object
        """
        llm = self._get_llm()
        
        if not llm:
            return self._generate_fallback_explanation(concept)
        
        prompt = self._create_explanation_prompt(concept, context, failed_question)
        
        try:
            if hasattr(llm, 'chat'):
                response = llm.chat([
                    {"role": "system", "content": "You are a friendly teacher who explains complex topics in simple, everyday language. Use analogies and examples a 10-year-old could understand."},
                    {"role": "user", "content": prompt}
                ])
            else:
                response = llm.invoke(prompt)
                if hasattr(response, 'content'):
                    response = response.content
            
            return self._parse_explanation(concept, response)
            
        except Exception as e:
            print(f"⚠️ Error generating explanation: {e}")
            return self._generate_fallback_explanation(concept)
    
    def _create_explanation_prompt(
        self,
        concept: str,
        context: str,
        failed_question: str
    ) -> str:
        """Create the prompt for generating explanations."""
        prompt = f"""Explain "{concept}" using the Feynman Technique.

Rules:
1. Use simple, everyday language (no jargon)
2. Use a real-life analogy (like cooking, building with LEGO, or riding a bike)
3. Give a concrete, real-world example
4. Make it fun and memorable

"""
        if failed_question:
            prompt += f"The learner struggled with this question: {failed_question}\n\n"
        
        if context:
            prompt += f"Context: {context[:500]}\n\n"
        
        prompt += """Please provide:

1. SIMPLE EXPLANATION (2-3 sentences, like explaining to a friend):

2. ANALOGY (use everyday objects or activities):

3. REAL-WORLD EXAMPLE (something you'd see in daily life):

4. KEY TAKEAWAYS (3 bullet points to remember):
"""
        return prompt
    
    def _parse_explanation(self, concept: str, response: str) -> FeynmanExplanation:
        """Parse LLM response into FeynmanExplanation."""
        sections = {
            "simple_explanation": "",
            "analogy": "",
            "real_world_example": "",
            "key_takeaways": []
        }
        
        # Try to parse structured response
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            lower_line = line.lower()
            
            if 'simple explanation' in lower_line or '1.' in line[:3]:
                current_section = 'simple_explanation'
                continue
            elif 'analogy' in lower_line or '2.' in line[:3]:
                current_section = 'analogy'
                continue
            elif 'real-world' in lower_line or 'real world' in lower_line or '3.' in line[:3]:
                current_section = 'real_world_example'
                continue
            elif 'takeaway' in lower_line or 'key point' in lower_line or '4.' in line[:3]:
                current_section = 'key_takeaways'
                continue
            
            if current_section:
                if current_section == 'key_takeaways':
                    # Clean up bullet points
                    clean_line = line.lstrip('-•*').strip()
                    if clean_line:
                        sections['key_takeaways'].append(clean_line)
                else:
                    if sections[current_section]:
                        sections[current_section] += ' ' + line
                    else:
                        sections[current_section] = line
        
        # Fallback if parsing failed
        if not sections['simple_explanation']:
            sections['simple_explanation'] = response[:500]
        
        if not sections['key_takeaways']:
            sections['key_takeaways'] = [
                f"Understand the basics of {concept}",
                "Practice with real examples",
                "Connect it to what you already know"
            ]
        
        return FeynmanExplanation(
            concept=concept,
            simple_explanation=sections['simple_explanation'],
            analogy=sections['analogy'] or f"Think of {concept} like building with LEGO blocks...",
            real_world_example=sections['real_world_example'] or f"You can see {concept} in action when...",
            key_takeaways=sections['key_takeaways']
        )
    
    def _generate_fallback_explanation(self, concept: str) -> FeynmanExplanation:
        """Generate a fallback explanation when LLM is unavailable."""
        return FeynmanExplanation(
            concept=concept,
            simple_explanation=f"{concept} is a fundamental concept that helps us understand how things work. Think of it as a building block for bigger ideas.",
            analogy=f"Imagine {concept} is like learning to ride a bicycle. At first, it seems complex with all its parts, but once you understand the basics, it becomes natural.",
            real_world_example=f"You encounter {concept} in everyday life more than you realize. For example, when you use your smartphone or search the internet, similar principles are at work.",
            key_takeaways=[
                f"Start with the basic definition of {concept}",
                "Look for patterns and connections to things you already know",
                "Practice explaining it in your own words"
            ]
        )
    
    def teach_weak_concepts(
        self,
        weak_concepts: List[str],
        topic: str,
        context: str = ""
    ) -> List[FeynmanExplanation]:
        """
        Generate explanations for multiple weak concepts.
        
        Args:
            weak_concepts: List of concepts the learner struggled with
            topic: The main topic being studied
            context: Additional context
            
        Returns:
            List of FeynmanExplanation objects
        """
        explanations = []
        
        for concept in weak_concepts[:3]:  # Limit to 3 concepts
            explanation = self.explain_concept(
                concept=f"{concept} (in the context of {topic})",
                context=context
            )
            explanations.append(explanation)
        
        return explanations
    
    def format_teaching_session(
        self,
        explanations: List[FeynmanExplanation]
    ) -> str:
        """Format explanations into a readable teaching session."""
        if not explanations:
            return "No concepts to explain."
        
        output = "# 🎓 Let's Learn Together!\n\n"
        output += "I'll explain these concepts in simple terms:\n\n"
        
        for i, exp in enumerate(explanations, 1):
            output += f"---\n\n## {i}. {exp.concept}\n\n"
            
            output += "### 📝 Simple Explanation\n"
            output += f"{exp.simple_explanation}\n\n"
            
            output += "### 🎯 Analogy\n"
            output += f"{exp.analogy}\n\n"
            
            output += "### 🌍 Real-World Example\n"
            output += f"{exp.real_world_example}\n\n"
            
            output += "### ✅ Key Takeaways\n"
            for takeaway in exp.key_takeaways:
                output += f"• {takeaway}\n"
            output += "\n"
        
        output += "---\n\n"
        output += "💡 **Pro Tip**: Try explaining these concepts to someone else in your own words. If you can teach it, you truly understand it!\n"
        
        return output


# Global feynman teacher instance
_feynman_teacher: Optional[FeynmanTeacher] = None


def get_feynman_teacher() -> FeynmanTeacher:
    """Get or create the global Feynman teacher instance."""
    global _feynman_teacher
    if _feynman_teacher is None:
        _feynman_teacher = FeynmanTeacher()
    return _feynman_teacher
