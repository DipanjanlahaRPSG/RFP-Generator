"""
Question Generator Service
Generates adaptive follow-up questions based on input richness
"""

import openai
import logging
from typing import List, Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generates adaptive questions for RFP context gathering"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def analyze_input_richness(self, prompt: str) -> int:
        """
        Score input richness from 1-10
        Higher score = more context provided = fewer questions needed
        """
        # Simple heuristic based on length and detail
        word_count = len(prompt.split())
        
        # Check for key details
        has_duration = any(word in prompt.lower() for word in ['month', 'year', 'week', 'day'])
        has_budget = any(word in prompt.lower() for word in ['budget', 'cost', 'price', 'inr', 'lakh', 'crore'])
        has_skills = any(word in prompt.lower() for word in ['skill', 'experience', 'certification', 'qualification'])
        has_location = any(word in prompt.lower() for word in ['location', 'site', 'office', 'remote', 'hybrid'])
        
        # Calculate richness score
        score = min(10, word_count // 10)  # Base score from word count
        if has_duration: score += 1
        if has_budget: score += 1
        if has_skills: score += 1
        if has_location: score += 1
        
        return min(10, score)
    
    def generate_questions(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        """
        Generate 2-5 adaptive questions based on input richness
        Rich input → fewer questions
        Vague input → more questions
        """
        richness_score = self.analyze_input_richness(prompt)
        
        # Determine number of questions (inverse relationship)
        if richness_score >= 8:
            num_questions = 2
        elif richness_score >= 5:
            num_questions = 3
        else:
            num_questions = 5
        
        logger.info(f"Input richness: {richness_score}/10, generating {num_questions} questions")
        
        # Use LLM to generate contextual questions
        system_prompt = """You are an expert RFP consultant. Generate specific, actionable questions to gather missing information for creating a comprehensive RFP.

Rules:
- Ask only about information NOT already provided
- Questions should be specific and actionable
- Focus on critical details needed for RFP sections
- Keep questions concise and clear
- Prioritize: budget, timeline, technical requirements, qualifications"""

        user_prompt = f"""Based on this RFP request, generate exactly {num_questions} follow-up questions:

Request: {prompt}

Already known context: {context}

Generate {num_questions} questions as a numbered list."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse questions from response
            content = response.choices[0].message.content
            questions = self._parse_questions(content)
            
            # Ensure we have the right number
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            # Fallback to generic questions
            return self._get_fallback_questions(num_questions)
    
    def _parse_questions(self, content: str) -> List[str]:
        """Parse questions from LLM response"""
        lines = content.strip().split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            # Remove numbering (1., 2., etc.)
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove leading number/dash and whitespace
                question = line.lstrip('0123456789.-) ').strip()
                if question and question.endswith('?'):
                    questions.append(question)
        
        return questions
    
    def _get_fallback_questions(self, num: int) -> List[str]:
        """Fallback questions if LLM fails"""
        fallback = [
            "What is the approximate budget range for this engagement?",
            "What is the expected duration or timeline?",
            "What specific skills or qualifications are required?",
            "What is the work location (on-site, remote, hybrid)?",
            "Are there any specific tools or technologies required?",
        ]
        return fallback[:num]
