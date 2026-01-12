#!/usr/bin/env python3
"""
Kharagpur Data Science Hackathon 2026 - Track A Solution
Backstory Consistency Checker using Pathway + LLM
"""

import pathway as pw
import os
import json
import google.generativeai as genai
from typing import List, Dict, Tuple
import re

class BackstoryConsistencyChecker:
    """
    System to evaluate whether a hypothetical backstory is consistent 
    with a long-form narrative using Pathway for data management and 
    LLM for reasoning.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize with API key for LLM"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None
        
    def chunk_narrative(self, narrative: str, chunk_size: int = 4000) -> List[str]:
        """
        Chunk long narrative into manageable pieces for analysis.
        Uses semantic boundaries where possible.
        """
        # Split by paragraphs first
        paragraphs = narrative.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def extract_key_constraints(self, narrative_chunks: List[str], backstory: str) -> List[Dict]:
        """
        Extract key constraints from narrative that are relevant to backstory.
        Uses LLM to identify contradictions and supporting evidence.
        """
        constraints = []
        
        # Analyze backstory claims
        backstory_analysis_prompt = f"""Analyze this character backstory and extract specific, testable claims:

Backstory:
{backstory}

List 5-10 key claims that could be verified or contradicted by the main narrative. Format:
1. [Specific claim]
2. [Specific claim]
..."""

        if self.model:
            response = self.model.generate_content(backstory_analysis_prompt)
            claims_text = response.text
            claims = [line.strip() for line in claims_text.split('\n') if line.strip() and re.match(r'^\d+\.', line.strip())]
        else:
            # Fallback: extract claims heuristically
            claims = [s.strip() for s in backstory.split('.') if len(s.strip()) > 20][:10]
        
        return {"claims": claims, "backstory": backstory}
    
    def check_consistency_chunk(self, chunk: str, backstory_claims: List[str]) -> Dict:
        """
        Check if a narrative chunk contradicts or supports backstory claims.
        """
        if not self.model:
            return {"contradictions": [], "support": [], "relevant": False}
        
        prompt = f"""You are analyzing a section of a novel to check consistency with a character's hypothetical backstory.

NARRATIVE EXCERPT:
{chunk[:3000]}

BACKSTORY CLAIMS:
{chr(10).join(f"{i+1}. {claim}" for i, claim in enumerate(backstory_claims[:10]))}

Task: Identify any CONTRADICTIONS or STRONG SUPPORT in this excerpt.

Respond in JSON format:
{{
  "contradictions": [
    {{"claim_num": 1, "evidence": "quote from text", "explanation": "why it contradicts"}}
  ],
  "support": [
    {{"claim_num": 2, "evidence": "quote from text", "explanation": "why it supports"}}
  ],
  "relevant": true/false
}}

Only include clear, specific contradictions or support. Be conservative."""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"contradictions": [], "support": [], "relevant": False}
        except Exception as e:
            print(f"Error in chunk analysis: {e}")
            return {"contradictions": [], "support": [], "relevant": False}
    
    def final_judgment(self, all_results: List[Dict], backstory_data: Dict) -> Tuple[int, str]:
        """
        Make final consistency judgment based on all evidence.
        Returns: (prediction, rationale)
        """
        total_contradictions = sum(len(r.get("contradictions", [])) for r in all_results)
        total_support = sum(len(r.get("support", [])) for r in all_results)
        relevant_chunks = sum(1 for r in all_results if r.get("relevant", False))
        
        # Compile evidence
        all_contradictions = []
        all_support = []
        for r in all_results:
            all_contradictions.extend(r.get("contradictions", []))
            all_support.extend(r.get("support", []))
        
        # Decision logic
        if total_contradictions > 0:
            prediction = 0
            rationale = f"Found {total_contradictions} contradiction(s): {all_contradictions[0].get('explanation', 'conflicts with narrative') if all_contradictions else 'backstory conflicts'}"
        elif total_support >= 2 and relevant_chunks >= 2:
            prediction = 1
            rationale = f"Backstory supported by {total_support} evidence points across narrative"
        elif relevant_chunks == 0:
            # No relevant information found - could go either way
            # Default to consistent if no contradictions found
            prediction = 1
            rationale = "No contradictions found; backstory is plausible with narrative"
        else:
            # Some relevance but weak support
            prediction = 1
            rationale = "Backstory is consistent with narrative constraints"
        
        return prediction, rationale
    
    def process_example(self, narrative: str, backstory: str, story_id: str) -> Dict:
        """
        Process a single narrative + backstory pair.
        Returns prediction and rationale.
        """
        print(f"Processing story {story_id}...")
        
        # Step 1: Chunk narrative
        chunks = self.chunk_narrative(narrative)
        print(f"  - Split into {len(chunks)} chunks")
        
        # Step 2: Extract backstory claims
        backstory_data = self.extract_key_constraints(chunks, backstory)
        print(f"  - Extracted {len(backstory_data['claims'])} claims")
        
        # Step 3: Check each chunk (sample if too many)
        sample_size = min(20, len(chunks))
        sample_indices = [int(i * len(chunks) / sample_size) for i in range(sample_size)]
        sampled_chunks = [chunks[i] for i in sample_indices]
        
        results = []
        for i, chunk in enumerate(sampled_chunks):
            print(f"  - Analyzing chunk {i+1}/{len(sampled_chunks)}...")
            result = self.check_consistency_chunk(chunk, backstory_data['claims'])
            results.append(result)
        
        # Step 4: Make final judgment
        prediction, rationale = self.final_judgment(results, backstory_data)
        
        print(f"  - Prediction: {prediction} ({'Consistent' if prediction == 1 else 'Inconsistent'})")
        
        return {
            "story_id": story_id,
            "prediction": prediction,
            "rationale": rationale
        }


def main():
    """
    Main execution function.
    Processes input data and generates results.csv
    """
    print("=" * 60)
    print("KDSH 2026 - Backstory Consistency Checker")
    print("=" * 60)
    
    # Initialize checker
    checker = BackstoryConsistencyChecker()
    
    # For demonstration, create sample processing
    # In actual submission, this would read from provided dataset
    
    # Example usage with Pathway
    # Here we demonstrate Pathway integration for document management
    
    print("\nNote: This is a template solution.")
    print("To complete:")
    print("1. Get FREE Google API key: https://makersuite.google.com/app/apikey")
    print("2. Set: export GOOGLE_API_KEY='your-key'")
    print("3. Download dataset from provided Google Drive link")
    print("4. Update load_data() to read actual narratives and backstories")
    print("5. Run: python main.py")
    print("\nFor full implementation, integrate with:")
    print("- Pathway connectors for document ingestion")
    print("- Pathway vector store for efficient retrieval")
    print("- Your custom analysis pipeline")
    
    # Placeholder for actual data loading
    # results = []
    # for example in load_data():
    #     result = checker.process_example(
    #         narrative=example['narrative'],
    #         backstory=example['backstory'],
    #         story_id=example['id']
    #     )
    #     results.append(result)
    
    # Save results
    # save_results(results, "results.csv")
    
    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
