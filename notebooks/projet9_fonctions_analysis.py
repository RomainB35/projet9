import json
import pandas as pd

def benchmark_json_to_dataframe(json_path: str) -> pd.DataFrame:
    """
    Charge un fichier JSON de benchmark (fusionné CPU/GPU)
    et le transforme en DataFrame aplati (chaque fichier audio = une ligne).
    
    Paramètres
    ----------
    json_path : str
        Chemin du fichier JSON à charger.
    
    Retour
    ------
    pd.DataFrame
        Tableau avec une ligne par fichier audio et colonnes aplaties.
    """
    # Charger le fichier JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    audio_data = data["data"]
    rows = []
    
    for audio_file, metrics in audio_data.items():
        row = {"audio_file": audio_file}
        for key, value in metrics.items():
            if isinstance(value, dict):
                # aplatir les sous-clés (ex: whisper_large_gpu -> whisper_large_gpu_WER)
                for subkey, subvalue in value.items():
                    row[f"{key}_{subkey}"] = subvalue
            else:
                row[key] = value
        rows.append(row)
    
    return pd.DataFrame(rows)

import pandas as pd

def summarize_benchmark_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée un DataFrame résumé par modèle à partir d'un DataFrame
    de benchmarks aplati (issu du JSON) et trie par sum_elapsed_time_s décroissant.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant les colonnes duration_s, raw_text et
        les métriques des modèles (inference_time, elapsed_time, real_time_factor).

    Retour
    ------
    pd.DataFrame
        Résumé par modèle avec les moyennes et sommes, trié.
    """
    models = set()
    for col in df.columns:
        if col.endswith("_inference_time_s"):
            models.add(col.replace("_inference_time_s", ""))
        elif col.endswith("_elapsed_time_s"):
            models.add(col.replace("_elapsed_time_s", ""))
        elif col.endswith("_real_time_factor"):
            models.add(col.replace("_real_time_factor", ""))

    summary = []
    for model in models:
        row = {"model": model}

        # colonnes attendues
        inf_col = f"{model}_inference_time_s"
        elap_col = f"{model}_elapsed_time_s"
        rtf_col = f"{model}_real_time_factor"

        # stats globales sur la durée
        if "duration_s" in df.columns:
            row["sum_duration_s"] = df["duration_s"].sum()
            row["mean_duration_s"] = df["duration_s"].mean()

        # stats par modèle
        if inf_col in df.columns:
            row["sum_inference_time_s"] = df[inf_col].sum()
            row["mean_inference_time_s"] = df[inf_col].mean()
        if elap_col in df.columns:
            row["sum_elapsed_time_s"] = df[elap_col].sum()
            row["mean_elapsed_time_s"] = df[elap_col].mean()
        if rtf_col in df.columns:
            row["mean_real_time_factor"] = df[rtf_col].mean()

        summary.append(row)

    summary_df = pd.DataFrame(summary)

    # Tri si la colonne existe
    if "sum_elapsed_time_s" in summary_df.columns:
        summary_df = summary_df.sort_values(by="sum_elapsed_time_s", ascending=False)

    return summary_df


import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def plot_benchmark_summary(summary_df: pd.DataFrame) -> None:
    """
    Génère des barplots pour visualiser les performances des modèles
    à partir du DataFrame résumé (issu de summarize_benchmark_dataframe).

    Paramètres
    ----------
    summary_df : pd.DataFrame
        Résumé par modèle contenant les colonnes sum_* et mean_*.
    """
    # =======================
    # Barplots pour les sommes
    # =======================
    sum_metrics = ['sum_inference_time_s', 'sum_elapsed_time_s']

    for metric in sum_metrics:
        if metric in summary_df.columns:
            df_plot = summary_df.sort_values(by=metric, ascending=False)
            plt.figure(figsize=(10, 5))
            sns.barplot(
                data=df_plot,
                x="model",
                y=metric,
                hue="model",
                dodge=False,
                palette="mako",
                legend=False
            )
            plt.xticks(rotation=45, ha='right')
            plt.title(f"{metric.replace('_',' ').title()} par modèle")
            plt.ylabel(metric.replace('_', ' ').title())
            plt.xlabel("Modèle")
            plt.tight_layout()
            plt.show()

    # =======================
    # Barplots pour les moyennes
    # =======================
    mean_metrics = ['mean_inference_time_s', 'mean_elapsed_time_s', 'mean_real_time_factor']

    for metric in mean_metrics:
        if metric in summary_df.columns:
            df_plot = summary_df.sort_values(by=metric, ascending=False)
            plt.figure(figsize=(10, 5))
            sns.barplot(
                data=df_plot,
                x="model",
                y=metric,
                hue="model",
                dodge=False,
                palette="viridis",
                legend=False
            )
            plt.xticks(rotation=45, ha='right')
            plt.title(f"{metric.replace('_',' ').title()} par modèle")
            plt.ylabel(metric.replace('_', ' ').title())
            plt.xlabel("Modèle")
            plt.tight_layout()
            plt.show()


import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.cm as cm
import numpy as np

def analyze_text_from_dataframe(df: pd.DataFrame, text_col: str = "raw_text") -> None:
    """
    Analyse le texte d'un DataFrame et génère des statistiques + diagrammes circulaires.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant au moins une colonne de texte.
    text_col : str
        Nom de la colonne contenant le texte (par défaut 'raw_text').
    """
    # -------------------------------
    # Préparer le texte
    # -------------------------------
    all_text = " ".join(df[text_col].astype(str))  # concaténer toutes les phrases
    all_text_lower = all_text.lower()             # uniformiser la casse

    # -------------------------------
    # Compter les mots
    # -------------------------------
    words = all_text_lower.split()                # split sur espaces
    word_counts = Counter(words)
    num_words = len(word_counts)
    top10_words = word_counts.most_common(10)

    # -------------------------------
    # Compter les caractères
    # -------------------------------
    chars = list(all_text_lower.replace(" ", "")) # enlever espaces
    char_counts = Counter(chars)
    num_chars = len(char_counts)
    top10_chars = char_counts.most_common(10)

    # -------------------------------
    # Affichage des stats
    # -------------------------------
    print(f"Nombre de mots différents : {num_words}")
    print(f"Nombre de caractères différents : {num_chars}")
    print(f"Top 10 mots les plus fréquents : {top10_words}")
    print(f"Top 10 caractères les plus fréquents : {top10_chars}")

    # -------------------------------
    # Fonction interne pour diagramme circulaire
    # -------------------------------
    def plot_pie_top10(counter, title):
        total = sum(counter.values())
        top10 = counter.most_common(10)
        other_count = total - sum([c for _, c in top10])

        labels = [w for w, _ in top10] + ["Autres"]
        sizes = [c for _, c in top10] + [other_count]

        colors = [cm.viridis(i/10) for i in range(10)] + ["lightgrey"]

        fig, ax = plt.subplots(figsize=(7,7))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.set_title(title)
        plt.show()

    # -------------------------------
    # Afficher diagrammes circulaires
    # -------------------------------
    plot_pie_top10(word_counts, "Proportion des 10 mots les plus fréquents")
    plot_pie_top10(char_counts, "Proportion des 10 caractères les plus fréquents")



import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def analyze_transcription_errors(df: pd.DataFrame, ref_col: str = "raw_text", models: list = None) -> None:
    """
    Analyse les erreurs de transcription (mots et caractères) pour plusieurs modèles.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant une colonne de référence (texte vrai) et des colonnes de transcription.
    ref_col : str
        Nom de la colonne contenant le texte de référence (par défaut "raw_text").
    models : list, optional
        Liste des modèles à analyser. Si None, utilise une liste par défaut.
    """
    # Liste par défaut si aucune fournie
    if models is None:
        models = [
            "whisper_large_cpu",
            "whisper_large_distilled_cpu",
            "whisper_large_distilled_ct2_cpu",
            "whisper_large_gpu",
            "whisper_large_distilled_gpu",
            "whisper_large_distilled_ct2_gpu"
        ]

    # --- Sous-fonctions ---
    def get_mistakes(ref_series, hyp_series):
        mistakes = []
        for ref, hyp in zip(ref_series.astype(str), hyp_series.astype(str)):
            ref_words = ref.lower().split()
            hyp_words = hyp.lower().split()
            mistakes += [w_ref for w_ref, w_hyp in zip(ref_words, hyp_words) if w_ref != w_hyp]
        return Counter(mistakes)

    def get_char_mistakes(ref_series, hyp_series):
        mistakes = []
        for ref, hyp in zip(ref_series.astype(str), hyp_series.astype(str)):
            ref_chars = list(ref.lower().replace(" ", ""))
            hyp_chars = list(hyp.lower().replace(" ", ""))
            mistakes += [c_ref for c_ref, c_hyp in zip(ref_chars, hyp_chars) if c_ref != c_hyp]
        return Counter(mistakes)

    def plot_pie_top10(counter, title):
        total = sum(counter.values())
        if total == 0:
            print(f"[!] Aucun écart trouvé pour {title}")
            return
        top10 = counter.most_common(10)
        other_count = total - sum([c for _, c in top10])

        labels = [w for w, _ in top10] + ["Autres"]
        sizes = [c for _, c in top10] + [other_count]

        colors = [cm.viridis(i/10) for i in range(10)] + ["lightgrey"]

        fig, ax = plt.subplots(figsize=(7,7))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.set_title(title)
        plt.show()

    # --- Analyse pour chaque modèle ---
    for model in models:
        print(f"\n=== Analyse erreurs pour {model} ===")
        hyp_col = f"{model}_transcription"
        if hyp_col not in df.columns:
            print(f"[!] Colonne {hyp_col} absente du DataFrame, ignorée.")
            continue

        # Mots mal transcrits
        word_mistakes = get_mistakes(df[ref_col], df[hyp_col])
        print("Top 10 mots mal transcrits :", word_mistakes.most_common(10))
        plot_pie_top10(word_mistakes, f"{model} - Top 10 mots mal transcrits")

        # Caractères mal transcrits
        char_mistakes = get_char_mistakes(df[ref_col], df[hyp_col])
        print("Top 10 caractères mal transcrits :", char_mistakes.most_common(10))
        plot_pie_top10(char_mistakes, f"{model} - Top 10 caractères mal transcrits")




import pandas as pd
import jiwer

def compute_transcription_metrics(df: pd.DataFrame, ref_col: str = "raw_text") -> pd.DataFrame:
    """
    Calcule les métriques de transcription (WER, CER, MER, WIL, WIP, Sub/Ins/Del/Hits)
    pour toutes les colonnes de transcription d'un DataFrame.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant une colonne de référence et des colonnes de transcription.
    ref_col : str
        Nom de la colonne contenant le texte de référence (par défaut "raw_text").

    Retour
    ------
    pd.DataFrame
        DataFrame avec une ligne par modèle et les métriques, trié par WER croissant.
    """
    # Identifier les colonnes de transcription
    transcription_cols = [col for col in df.columns if col.endswith("_transcription")]

    metrics = []

    for col in transcription_cols:
        model_name = col.replace("_transcription", "")
        wers, cers, mers, wils, wips = [], [], [], [], []
        subs, ins, dels, hits, refs = [], [], [], [], []

        for _, row in df.iterrows():
            reference = str(row[ref_col]).lower().strip()
            hypothesis = str(row[col]).lower().strip()

            measures = jiwer.process_words(reference, hypothesis)

            wers.append(measures.wer)
            cers.append(jiwer.cer(reference, hypothesis))
            mers.append(measures.mer)
            wils.append(measures.wil)
            wips.append(measures.wip)

            subs.append(measures.substitutions)
            ins.append(measures.insertions)
            dels.append(measures.deletions)
            hits.append(measures.hits)
            refs.append(len(reference.split()))

        metrics.append({
            "model": model_name,
            "WER": sum(wers)/len(wers),
            "CER": sum(cers)/len(cers),
            "MER": sum(mers)/len(mers),
            "WIL": sum(wils)/len(wils),
            "WIP": sum(wips)/len(wips),
            "Substitutions": sum(subs),
            "Insertions": sum(ins),
            "Deletions": sum(dels),
            "Hits": sum(hits),
            "Total_Ref_Words": sum(refs)
        })

    accuracy_df = pd.DataFrame(metrics).sort_values(by="WER")
    return accuracy_df



import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def plot_accuracy_metrics(df: pd.DataFrame) -> None:
    """
    Génère des barplots pour visualiser WER et CER par modèle.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant les colonnes 'model', 'WER' et 'CER'.
    """
    # --- WER ---
    if "WER" in df.columns:
        df_wer_sorted = df.sort_values("WER", ascending=False)
        plt.figure(figsize=(10, 6))
        sns.barplot(
            x="model",
            y="WER",
            data=df_wer_sorted,
            hue="model",
            dodge=False,
            palette="viridis",
            legend=False
        )
        plt.title("Word Error Rate (WER) par modèle")
        plt.xlabel("Modèle")
        plt.ylabel("WER")
        plt.xticks(rotation=45, ha="right")
        plt.ylim(0, df["WER"].max() + 0.01)
        plt.tight_layout()
        plt.show()

    # --- CER ---
    if "CER" in df.columns:
        df_cer_sorted = df.sort_values("CER", ascending=False)
        plt.figure(figsize=(10, 6))
        sns.barplot(
            x="model",
            y="CER",
            data=df_cer_sorted,
            hue="model",
            dodge=False,
            palette="magma",
            legend=False
        )
        plt.title("Character Error Rate (CER) par modèle")
        plt.xlabel("Modèle")
        plt.ylabel("CER")
        plt.xticks(rotation=45, ha="right")
        plt.ylim(0, df["CER"].max() + 0.01)
        plt.tight_layout()
        plt.show()

