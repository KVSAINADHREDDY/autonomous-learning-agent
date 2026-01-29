"""
Predefined checkpoints (learning topics) for the autonomous learning agent.
Each checkpoint covers a specific AI/ML topic with learning objectives.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class CheckpointDefinition:
    """Definition of a learning checkpoint."""
    id: str
    topic: str
    objectives: List[str]
    difficulty: str  # beginner, intermediate, advanced
    estimated_minutes: int
    prerequisites: List[str] = field(default_factory=list)
    notes: str = ""  # Pre-written study notes


# =========================================================
# PREDEFINED LEARNING CHECKPOINTS
# =========================================================

CHECKPOINTS: List[CheckpointDefinition] = [
    # Checkpoint 1: Artificial Intelligence
    CheckpointDefinition(
        id="artificial_intelligence",
        topic="Artificial Intelligence",
        objectives=[
            "Understand what Artificial Intelligence (AI) is",
            "Learn how AI differs from traditional computer programs",
            "Identify real-world examples of AI in everyday life"
        ],
        difficulty="beginner",
        estimated_minutes=15,
        notes="""
# Artificial Intelligence (AI)

## What is AI?
Artificial Intelligence is a branch of computer science that aims to create machines that can perform tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding.

## How AI Differs from Regular Programs
- **Traditional Programs**: Follow fixed rules written by programmers. They can only do exactly what they're told.
- **AI Programs**: Can learn from data, adapt to new situations, and make decisions without explicit programming for every scenario.

Think of it like this:
- A calculator is a traditional program - it follows exact math rules
- A recommendation system (like Netflix suggestions) is AI - it learns your preferences

## Real-World Examples of AI
1. **Voice Assistants**: Siri, Alexa, Google Assistant
2. **Recommendation Systems**: Netflix, Spotify, YouTube suggestions
3. **Navigation**: Google Maps traffic predictions
4. **Photo Apps**: Face recognition in your phone gallery
5. **Email**: Spam filters and smart replies
6. **Healthcare**: Disease diagnosis assistance
7. **Self-Driving Cars**: Tesla Autopilot

## Key Takeaways
- AI makes machines "smart" enough to learn and make decisions
- Unlike regular programs, AI can improve over time with more data
- You interact with AI every day, often without realizing it
"""
    ),
    
    # Checkpoint 2: Machine Learning
    CheckpointDefinition(
        id="machine_learning",
        topic="Machine Learning",
        objectives=[
            "Understand the basics of Machine Learning (ML)",
            "Differentiate between supervised and unsupervised learning",
            "Explain the role of training data in ML"
        ],
        difficulty="beginner",
        estimated_minutes=20,
        prerequisites=["artificial_intelligence"],
        notes="""
# Machine Learning (ML)

## What is Machine Learning?
Machine Learning is a subset of AI where computers learn patterns from data instead of being explicitly programmed with rules. The system improves its performance as it sees more examples.

## How ML Works (Simple Explanation)
1. **Feed Data**: Give the computer many examples
2. **Find Patterns**: The algorithm discovers patterns in the data
3. **Make Predictions**: Use patterns to predict outcomes for new data
4. **Improve**: Get feedback and become more accurate

## Types of Machine Learning

### Supervised Learning
- The computer learns from labeled examples
- Like learning with a teacher who shows correct answers
- Example: Showing the computer 1000 pictures of cats labeled "cat" and 1000 of dogs labeled "dog"
- Uses: Email spam detection, price prediction, disease diagnosis

### Unsupervised Learning
- The computer finds patterns without labels
- Like exploring data on your own to find groups
- Example: Grouping customers by shopping behavior
- Uses: Customer segmentation, anomaly detection, recommendation systems

### Reinforcement Learning
- Learning by trial and error with rewards
- Like training a pet with treats
- Example: Teaching a robot to walk by rewarding forward progress
- Uses: Game AI, robotics, autonomous vehicles

## The Role of Training Data
- **Quantity**: More data usually leads to better learning
- **Quality**: Clean, accurate data is essential
- **Diversity**: Data should represent all scenarios
- **Bias**: Biased data leads to biased models

## Key Takeaways
- ML lets computers learn from examples instead of explicit rules
- Supervised learning uses labeled data, unsupervised finds hidden patterns
- Good training data is the foundation of effective ML
"""
    ),
    
    # Checkpoint 3: Generative AI
    CheckpointDefinition(
        id="generative_ai",
        topic="Generative AI",
        objectives=[
            "Understand what Generative AI is and how it creates content",
            "Identify popular GenAI tools like ChatGPT and DALL-E",
            "Recognize applications of Generative AI in content creation"
        ],
        difficulty="beginner",
        estimated_minutes=15,
        prerequisites=["machine_learning"],
        notes="""
# Generative AI (GenAI)

## What is Generative AI?
Generative AI refers to AI systems that can create new content - text, images, music, code, and more. Unlike traditional AI that analyzes or classifies, GenAI produces original outputs.

## How GenAI Works
1. Trained on massive amounts of existing content
2. Learns patterns, styles, and structures
3. Uses these patterns to generate new, similar content
4. Can be guided by prompts or instructions

## Popular GenAI Tools

### Text Generation
- **ChatGPT (OpenAI)**: Conversational AI that writes, explains, and helps with tasks
- **Claude (Anthropic)**: Similar to ChatGPT with focus on safety
- **Gemini (Google)**: Google's conversational AI

### Image Generation
- **DALL-E (OpenAI)**: Creates images from text descriptions
- **Midjourney**: Artistic image generation
- **Stable Diffusion**: Open-source image generator

### Code Generation
- **GitHub Copilot**: AI pair programmer
- **Cursor**: AI-powered code editor

### Audio/Video
- **Sora (OpenAI)**: Video generation from text
- **ElevenLabs**: Voice cloning and generation

## Applications of GenAI
1. **Writing**: Articles, stories, marketing copy
2. **Art & Design**: Illustrations, logos, product designs
3. **Coding**: Generating and debugging code
4. **Customer Service**: AI chatbots
5. **Education**: Personalized tutoring and explanations
6. **Entertainment**: Game content, music composition

## Key Takeaways
- GenAI creates new content rather than just analyzing existing data
- Tools like ChatGPT and DALL-E are transforming creative work
- GenAI is powerful but should be used responsibly with human oversight
"""
    ),
    
    # Checkpoint 4: Large Language Models
    CheckpointDefinition(
        id="large_language_models",
        topic="Large Language Models",
        objectives=[
            "Understand what Large Language Models (LLMs) are",
            "Learn how LLMs process and understand text",
            "Identify examples of popular LLMs"
        ],
        difficulty="intermediate",
        estimated_minutes=20,
        prerequisites=["generative_ai"],
        notes="""
# Large Language Models (LLMs)

## What are LLMs?
Large Language Models are AI systems trained on vast amounts of text data to understand, generate, and work with human language. They're called "large" because they have billions of parameters (learned values).

## How LLMs Work

### Training Process
1. **Data Collection**: Gather text from books, websites, articles
2. **Tokenization**: Break text into small pieces (tokens)
3. **Pattern Learning**: Learn relationships between tokens
4. **Parameter Tuning**: Adjust billions of numbers to capture language patterns

### Key Concept: Predicting Next Words
LLMs learn by predicting the next word in a sequence:
- Input: "The cat sat on the..."
- Prediction: "mat" (or "chair", "floor", etc.)
- By doing this billions of times, they learn grammar, facts, and reasoning

### Understanding Context
LLMs use "attention" mechanisms to:
- Consider all words in context
- Understand relationships between distant words
- Capture meaning across long passages

## Popular LLMs

### OpenAI
- **GPT-4**: Most capable, powers ChatGPT
- **GPT-4o**: Faster version
- **GPT-3.5**: Earlier, still widely used

### Google
- **Gemini**: Google's frontier model
- **PaLM**: Previous generation

### Meta (Facebook)
- **LLaMA**: Open-weight models for research

### Anthropic
- **Claude 3**: Focus on safety and helpfulness

### Open Source
- **Mistral**: High quality open models
- **Qwen**: Alibaba's open models

## Key Takeaways
- LLMs learn language patterns from massive text datasets
- They work by predicting the next word, building understanding
- Popular examples include GPT-4, Claude, Gemini, and LLaMA
"""
    ),
    
    # Checkpoint 5: Prompt Engineering
    CheckpointDefinition(
        id="prompt_engineering",
        topic="Prompt Engineering",
        objectives=[
            "Understand what prompt engineering is",
            "Learn techniques for writing effective prompts",
            "Practice creating prompts that get better AI responses"
        ],
        difficulty="intermediate",
        estimated_minutes=25,
        prerequisites=["large_language_models"],
        notes="""
# Prompt Engineering

## What is Prompt Engineering?
Prompt engineering is the art and science of crafting inputs (prompts) to get the best possible outputs from AI models. A well-written prompt can dramatically improve AI responses.

## Why Prompts Matter
- AI responses depend heavily on how you ask
- Same question, different phrasing = different quality answers
- Good prompts save time and get more accurate results

## Key Prompt Engineering Techniques

### 1. Be Specific and Clear
❌ "Write about dogs"
✅ "Write a 200-word educational article about the history of dog domestication, suitable for middle school students"

### 2. Provide Context
❌ "Explain photosynthesis"
✅ "I'm a 5th grader learning about plants. Explain photosynthesis using simple words and an analogy to cooking"

### 3. Give Examples (Few-Shot Learning)
"Convert these sentences to formal language:
Casual: Hey, what's up?
Formal: Good afternoon, how are you doing?

Casual: That's cool!
Formal: [AI completes]"

### 4. Assign a Role
"You are an experienced Python developer. Review this code and suggest improvements for performance and readability."

### 5. Use Step-by-Step Instructions
"Help me plan a birthday party:
1. First, suggest 5 theme ideas
2. Then, list decorations for your top pick
3. Finally, create a simple timeline"

### 6. Set Constraints
"Write a product description. Requirements:
- Maximum 100 words
- Include 3 key features
- End with a call to action
- Tone: friendly and professional"

## Common Prompt Patterns
- **Persona Pattern**: "Act as a [expert role]..."
- **Template Pattern**: "Fill in this template: [structure]"
- **Chain of Thought**: "Think step by step..."
- **Output Format**: "Respond in JSON/table/bullet points..."

## Key Takeaways
- How you phrase prompts dramatically affects AI responses
- Be specific, provide context, and give examples
- Use roles, constraints, and structured formats for better results
"""
    ),
    
    # Checkpoint 6: AI Ethics and Safety
    CheckpointDefinition(
        id="ai_ethics_safety",
        topic="AI Ethics and Safety",
        objectives=[
            "Understand key ethical concerns in AI development",
            "Learn about AI bias and fairness issues",
            "Recognize principles of responsible AI use"
        ],
        difficulty="intermediate",
        estimated_minutes=20,
        prerequisites=["prompt_engineering"],
        notes="""
# AI Ethics and Safety

## Why AI Ethics Matters
As AI becomes more powerful and widespread, we must ensure it's developed and used responsibly. Poor AI decisions can harm individuals and society.

## Key Ethical Concerns

### 1. Bias and Fairness
- AI learns from historical data, which may contain biases
- Example: Hiring AI trained on past data may discriminate against minorities
- Solution: Diverse training data, bias testing, human oversight

### 2. Privacy
- AI needs data, often personal data
- Concerns: Surveillance, data collection, facial recognition
- Solution: Data minimization, consent, anonymization

### 3. Transparency (Explainability)
- Many AI systems are "black boxes"
- Users deserve to know how decisions affect them
- Solution: Explainable AI, documentation, audits

### 4. Misinformation
- GenAI can create fake but realistic content
- Deepfakes, fake news, impersonation
- Solution: Content labels, detection tools, education

### 5. Job Displacement
- AI automation may replace human jobs
- Need for retraining, new job creation
- Solution: Gradual transition, education programs

### 6. Safety and Control
- Ensuring AI behaves as intended
- Preventing misuse for harmful purposes
- Solution: Testing, safeguards, regulations

## Principles of Responsible AI

### 1. Fairness
- AI should treat all people equitably
- Regular bias audits and corrections

### 2. Transparency
- Be clear about when AI is being used
- Explain how AI makes decisions

### 3. Privacy
- Minimize data collection
- Protect user information

### 4. Safety
- Rigorous testing before deployment
- Ongoing monitoring and updates

### 5. Human Oversight
- Keep humans in the loop for important decisions
- Ability to override AI decisions

### 6. Accountability
- Clear responsibility for AI outcomes
- Mechanisms for redress when things go wrong

## Key Takeaways
- AI can perpetuate biases from training data
- Transparency and human oversight are essential
- Responsible AI balances innovation with protection of rights
"""
    ),
]


def get_all_checkpoints() -> List[CheckpointDefinition]:
    """Get all predefined checkpoints."""
    return CHECKPOINTS


def get_checkpoint_by_id(checkpoint_id: str) -> CheckpointDefinition:
    """Get a specific checkpoint by ID."""
    for cp in CHECKPOINTS:
        if cp.id == checkpoint_id:
            return cp
    raise ValueError(f"Checkpoint not found: {checkpoint_id}")


def get_checkpoints_summary() -> List[Dict[str, Any]]:
    """Get a summary of all checkpoints for display."""
    return [
        {
            "id": cp.id,
            "topic": cp.topic,
            "difficulty": cp.difficulty,
            "estimated_minutes": cp.estimated_minutes,
            "objectives_count": len(cp.objectives)
        }
        for cp in CHECKPOINTS
    ]
