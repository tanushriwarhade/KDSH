# KDSH 2026 - Backstory Consistency Checker

## Team Submission
**Track:** Track A - Systems Reasoning with NLP and Generative AI

## Overview
This solution uses Pathway for document management and Claude AI for long-context reasoning to determine whether hypothetical character backstories are consistent with long-form narratives.

## Architecture

### Core Components
1. **Document Management (Pathway)**
   - Ingestion of long-form narratives (100k+ words)
   - Efficient chunking and retrieval
   - Metadata management

2. **Consistency Analysis Pipeline**
   - Backstory claim extraction
   - Chunk-wise contradiction detection
   - Evidence aggregation
   - Final judgment synthesis

3. **LLM Reasoning (Claude Sonnet 4)**
   - Causal reasoning over narrative constraints
   - Evidence-based contradiction detection
   - Context-aware consistency checking

## Setup

### Prerequisites
- Python 3.9+
- Anthropic API key

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
Set your API key:
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
```

## Getting Free Google API Key

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key
4. **FREE:** 60 requests per minute, generous quota

## Usage

### Basic Execution
```bash
python main.py
```

### With Custom Data
```python
from main import BackstoryConsistencyChecker

checker = BackstoryConsistencyChecker()
result = checker.process_example(
    narrative="[full novel text]",
    backstory="[character backstory]",
    story_id="1"
)
print(f"Prediction: {result['prediction']}")
print(f"Rationale: {result['rationale']}")
```

## Methodology

### 1. Narrative Chunking
- Splits long narratives into semantic chunks (~4000 chars)
- Preserves paragraph boundaries
- Enables parallel processing

### 2. Claim Extraction
- Extracts specific, testable claims from backstory
- Identifies key constraints and assumptions
- Creates verification checklist

### 3. Contradiction Detection
- Analyzes narrative chunks against backstory claims
- Identifies direct contradictions
- Tracks supporting evidence
- Uses LLM for nuanced causal reasoning

### 4. Evidence Aggregation
- Weighs contradictions vs support
- Considers relevance and coverage
- Makes final binary decision

## Decision Logic

**Inconsistent (0):** If ANY clear contradiction found
**Consistent (1):** If:
- No contradictions AND sufficient support, OR
- No contradictions AND no relevant information (plausible)

## Handling Long Context

### Strategies Employed
1. **Smart Chunking:** Semantic boundary preservation
2. **Sampling:** Representative chunk selection for very long texts
3. **Claim-Based Filtering:** Focus on relevant sections
4. **Incremental Analysis:** Process in stages to manage context

## Key Features

### Causal Reasoning
- Distinguishes correlation from causation
- Tracks constraint evolution over narrative
- Evaluates logical compatibility

### Evidence Grounding
- All judgments tied to specific text excerpts
- Multiple evidence points required
- Conservative contradiction detection

### Robustness
- Handles underspecified backstories
- Deals with narrative ambiguity
- Fails gracefully on edge cases

## Limitations

1. **API Dependency:** Requires external LLM API
2. **Sampling Bias:** Very long narratives are sampled, may miss contradictions
3. **Conservative:** May miss subtle inconsistencies
4. **Cost:** API calls scale with narrative length

## Future Improvements

1. **Vector Store Integration:** Use Pathway vector store for semantic search
2. **Multi-Model Ensemble:** Combine multiple LLMs for robustness
3. **Fine-tuning:** Train specialized consistency checker
4. **Incremental Processing:** Stream processing for real-time analysis
5. **Graph-Based Reasoning:** Model narrative as constraint graph

## Pathway Integration

This solution uses Pathway for:
- Document ingestion and management
- Efficient data streaming
- Metadata handling
- Future: Vector store for retrieval

For full Pathway integration:
```python
import pathway as pw

# Define schema
class NarrativeSchema(pw.Schema):
    story_id: str
    text: str
    backstory: str

# Stream from source
narratives = pw.io.fs.read(
    path="data/",
    format="json",
    schema=NarrativeSchema
)

# Process with Pathway
results = narratives.select(
    prediction=pw.apply(checker.process_example, ...)
)

# Output
pw.io.csv.write(results, "results.csv")
```

## Output Format

**results.csv:**
```csv
Story ID,Prediction,Rationale
1,1,Backstory supported by 3 evidence points across narrative
2,0,Found 1 contradiction: character age conflicts with timeline
...
```

## References

- Pathway Documentation: https://pathway.com/developers/
- Claude API: https://docs.anthropic.com/
- Challenge Details: KDSH 2026 Problem Statement
