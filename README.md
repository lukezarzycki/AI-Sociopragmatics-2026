# AI Language Production in Sociolinguistic Contexts: An Empirical Approach

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Data: Zenodo](https://img.shields.io/badge/Data-Zenodo-12b2e2.svg)](https://zenodo.org/)

## About This Repository
This repository contains the analytical scripts, prompt templates, and methodological frameworks utilized in the monograph: **"AI Language Production in Sociolinguistic Contexts: An Empirical Approach"**. 

It provides full algorithmic transparency for the data collection and text analysis procedures discussed in Chapter 4 of the book, specifically focusing on the measurement of Large Language Model (LLM) stylistic adaptation, algorithmic sycophancy, and sociopragmatic homogenization under varying tone constraints.

## Repository Structure

The codebase is organized into modular scripts reflecting the analytical pipeline:

* `📂 templates/`
  * `system_prompts.json` - Definitions of global interpersonal tone constraints (e.g., Polite, Aggressive).
  * `user_prompts.json` - The semantic tasks and base queries across various topics.
  * `api_payload_example.json` - A structural example of the exact JSON payload sent to the OpenAI API.
* `01_spacy_syntactic_analysis.py` - NLP pipeline for extracting Part-of-Speech (POS) distributions, Average Sentence Length (ASL), and Dependency Relations (e.g., *nsubj*, *ROOT*).
* `02_textblob_sentiment.py` - Scripts for automated sentiment polarity extraction and emotion classification (Anger, Joy, Neutrality).
* `03_ml_classifiers.py` - Scikit-learn implementation of Support Vector Machines (SVM), Random Forests, and Multi-Layer Perceptron (MLP) Neural Networks used to classify AI responses by tone (achieving 100% accuracy on the test set).
* `requirements.txt` - Complete list of Python dependencies required to replicate the environment.

## Primary Dataset (Corpus)

To handle large file sizes and ensure permanent academic archiving, the primary dataset (the 3,000-row CSV database containing all prompts, metadata, and unedited AI responses) is hosted separately on **Zenodo**.

🔗 **Data Access (DOI):** [10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX) 
*(Note: Replace XXXXXXX with your actual Zenodo DOI once published)*

## Replication Instructions

To reproduce the computational environment and run the analytical scripts locally:

1. Clone this repository:
   ```bash
   git clone [https://github.com/YourUsername/AI-Sociopragmatics-2026.git](https://github.com/YourUsername/AI-Sociopragmatics-2026.git)
1. Navigate to the project directory: Bash  cd AI-Sociopragmatics-2026
2. Install the required dependencies: Bash pip install -r requirements.txt
3. Run the desired analytical script (e.g., sentiment analysis):Bash python 02_textblob_sentiment.py --input data.csv
4. Citation
If you utilize this code or the associated dataset in your research, please cite the original monograph:

Łukasz Zarzycki (2026). AI Language Production in Sociolinguistic Contexts: An Empirical Approach. Routledge.
Contact
For questions regarding the methodology or access to additional data, please open an issue in this repository.
