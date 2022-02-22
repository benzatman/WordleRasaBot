import pandas as pd


def canonical_form():
    dictionary = pd.read_csv(r"C:\Users\Ben\Downloads\english_words_original_wordle.txt", sep=" ", header=None)

    dict_df = pd.DataFrame(dictionary)
    dict_df.columns = ['words']
    dict_df.to_pickle('possible_words.pkl')


if __name__ == "__main__":
    canonical_form()


