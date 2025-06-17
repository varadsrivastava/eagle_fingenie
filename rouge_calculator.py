import pandas as pd
from rouge_score import rouge_scorer

def calculate_rouge_scores(reference_df, prediction_df):
    # Initialize the ROUGE scorer with different ROUGE variants
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    # Lists to store scores
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []
    
    # Calculate ROUGE scores for each pair of summaries
    for ref, pred in zip(reference_df, prediction_df):
        if pd.isna(ref) or pd.isna(pred):
            continue
            
        scores = scorer.score(ref, pred)
        
        # Extract F1 scores
        rouge1_scores.append(scores['rouge1'].fmeasure)
        rouge2_scores.append(scores['rouge2'].fmeasure)
        rougeL_scores.append(scores['rougeL'].fmeasure)
    
    # Calculate average scores
    avg_rouge1 = sum(rouge1_scores) / len(rouge1_scores) if rouge1_scores else 0
    avg_rouge2 = sum(rouge2_scores) / len(rouge2_scores) if rouge2_scores else 0
    avg_rougeL = sum(rougeL_scores) / len(rougeL_scores) if rougeL_scores else 0
    
    return {
        'ROUGE-1': avg_rouge1,
        'ROUGE-2': avg_rouge2,
        'ROUGE-L': avg_rougeL
    }

def main():
    # Read the Excel file
    reference_sheet = pd.read_excel('F:\XX\XX\LLM_MultiAgent_ICLR\eval.xlsx', sheet_name='Part1 Test')
    prediction_sheet = pd.read_excel('F:\XX\XX\LLM_MultiAgent_ICLR\eval.xlsx', sheet_name='Claude')
    
    # Get the reference and prediction summaries
    reference_summaries = reference_sheet['Customer Profile Summary'][:3]
    prediction_summaries = prediction_sheet['Reflection Summary'][:3]
    
    # Calculate ROUGE scores
    rouge_scores = calculate_rouge_scores(reference_summaries, prediction_summaries)
    
    # Print results
    print("\nROUGE Scores:")
    print("-" * 30)
    for metric, score in rouge_scores.items():
        print(f"{metric}: {score:.4f}")

if __name__ == "__main__":
    main() 