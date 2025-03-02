from sacrebleu.metrics import BLEU, CHRF, TER
from bert_score import score
from rouge_score import rouge_scorer
import evaluate
from typing import Dict

def calculate_translation_quality_scores(original_text: str, back_translated_text: str) -> Dict[float, str]:
    """
    Calculate quality metrics between original text and its back-translated version.
    
    Args:
        original_text (str): Original text
        back_translated_text (str): Text after forward and back translation
        
    Returns:
        Dict[str, float]: Dictionary containing evaluation scores
    """
    try:
        # 1. BERTScore for semantic similarity
        precision, recall, f1 = score([back_translated_text], 
                                    [original_text], 
                                    lang="en", 
                                    verbose=False)
        bert_score = f1.item()
        
        #2. chrF
        chrf = CHRF()
        chrf_score = chrf.corpus_score([back_translated_text], [[original_text]]).score
        
        #3. BLEU
        bleu = BLEU()
        bleu_score = bleu.corpus_score([back_translated_text], [[original_text]]).score
        
        # 4. ROUGE scores
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        rouge_scores = scorer.score(original_text, back_translated_text)
        
        # 5. TER
        ter = TER()
        ter_score = ter.corpus_score([back_translated_text], [[original_text]]).score
        
        scores = {
            'bert_score': bert_score,
            'chrf': chrf_score,
            'bleu': bleu_score,
            'ter': ter_score,
            'rouge1': rouge_scores['rouge1'].fmeasure,
            'rouge2': rouge_scores['rouge2'].fmeasure,
            'rougeL': rouge_scores['rougeL'].fmeasure
        }
        
        return scores
    
    except Exception as e:
        print(f"Error calculating scores: {str(e)}")
        return {}

def calculate_translation_quality(translated_paras, ground_truth_paras):
    assert(len(translated_paras)==len(ground_truth_paras))
    dict_scores_list = {}

    for i in range(len(translated_paras)):
        scores = calculate_translation_quality_scores(ground_truth_paras[i], translated_paras[i])
        get_updated_list_scores(dict_scores_list, scores)


    avg_scores = get_avg_scores(dict_scores_list)
    print("avg_scores: ", avg_scores)


def get_updated_list_scores(dict_scores_list, scores):

    if "bert_score" not in dict_scores_list:
        dict_scores_list["bert_score"] = []
    dict_scores_list["bert_score"].append(scores["bert_score"])

    if "chrf" not in dict_scores_list:
        dict_scores_list["chrf"] = []
    dict_scores_list["chrf"].append(scores["chrf"])

    if "bleu" not in dict_scores_list:
        dict_scores_list["bleu"] = []
    dict_scores_list["bleu"].append(scores["bleu"])

    if "ter" not in dict_scores_list:
        dict_scores_list["ter"] = []
    dict_scores_list["ter"].append(scores["ter"])

    if "rouge1" not in dict_scores_list:
        dict_scores_list["rouge1"] = []
    dict_scores_list["rouge1"].append(scores["rouge1"])

    if "rouge2" not in dict_scores_list:
        dict_scores_list["rouge2"] = []
    dict_scores_list["rouge2"].append(scores["rouge2"])

    if "rougeL" not in dict_scores_list:
        dict_scores_list["rougeL"] = []
    dict_scores_list["rougeL"].append(scores["rougeL"])

def get_avg_scores(dict_scores_list):

    avg_scores = {}
    avg_scores['bert_score'] = np.mean(dict_scores_list['bert_score'])
    avg_scores['chrf'] = np.mean(dict_scores_list['chrf'])
    avg_scores['bleu'] = np.mean(dict_scores_list['bleu'])
    avg_scores['ter'] = np.mean(dict_scores_list['ter'])
    avg_scores['rouge1'] = np.mean(dict_scores_list['rouge1'])
    avg_scores['rouge2'] = np.mean(dict_scores_list['rouge2'])
    avg_scores['rougeL'] = np.mean(dict_scores_list['rougeL'])
    
    return avg_scores

def interpret_translation_quality_scores(scores: Dict[str, float]) -> None:
    """
    Print interpretation of back-translation quality scores.
    
    Args:
        scores (Dict[str, float]): Dictionary of calculated scores
    """
    print("\nBack-Translation Quality Scores and Interpretation:")
    print("\n1. BERTScore (Semantic Preservation):")
    print(f"Score: {scores.get('bert_score', 'N/A'):.3f}")
    print("Range: 0 to 1.0")
    print("Interpretation:")
    print("- Above 0.90: Excellent meaning preservation")
    print("- 0.80 to 0.90: Good meaning preservation")
    print("- 0.70 to 0.80: Some meaning changes")
    print("- Below 0.70: Significant meaning alterations")
    
    print("\n2. BLEU Score:")
    print(f"Score: {scores.get('bleu', 'N/A'):.3f}")
    print("Range: 0 to 100")
    print("Interpretation for back-translation:")
    print("- Above 50: Very high lexical preservation")
    print("- 35 to 50: Good lexical preservation")
    print("- 20 to 35: Moderate lexical changes")
    print("- Below 20: Significant rewording")
    
    print("\n3. ROUGE Scores:")
    print(f"ROUGE-1: {scores.get('rouge1', 'N/A'):.3f}")
    print(f"ROUGE-2: {scores.get('rouge2', 'N/A'):.3f}")
    print(f"ROUGE-L: {scores.get('rougeL', 'N/A'):.3f}")
    print("Range: 0 to 1.0")
    print("Interpretation for back-translation:")
    print("- Above 0.8: Near-perfect preservation")
    print("- 0.6 to 0.8: Good preservation")
    print("- 0.4 to 0.6: Moderate changes")
    print("- Below 0.4: Substantial changes")
    
    print("\n4. TER Score (Translation Edit Rate):")
    print(f"Score: {scores.get('ter', 'N/A'):.3f}")
    print("Range: 0 to 1.0 (lower is better)")
    print("Interpretation for back-translation:")
    print("- Below 0.15: Minimal changes from original")
    print("- 0.15 to 0.30: Minor changes")
    print("- 0.30 to 0.50: Moderate changes")
    print("- Above 0.50: Substantial changes")
    
    # Provide overall assessment
    bert = scores.get('bert_score', 0)
    rouge_l = scores.get('rougeL', 0)
    
    print("\nOverall Quality Assessment:")
    if bert > 0.85 and rouge_l > 0.7:
        print("Excellent back-translation: High meaning and structure preservation")
    elif bert > 0.75 and rouge_l > 0.5:
        print("Good back-translation: Meaning is preserved with some paraphrasing")
    elif bert > 0.65 and rouge_l > 0.3:
        print("Acceptable back-translation: Core meaning preserved but significant rewording")
    else:
        print("Poor back-translation: Significant meaning or structure changes")

# Example usage
# if __name__ == "__main__":
#     ground_truth = "The weather is beautiful today."
#     translated = "Today's weather is really lovely."
    
#     print(calculate_translation_quality_scores(ground_truth, translated))
    