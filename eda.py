"""
eda.py
ExploratÃ³rio dos dados de mÃºsicas (top50MusicFrom2010-2019.csv).
Gera estatÃ­sticas e visualizaÃ§Ãµes para entender padrÃµes do dataset.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_and_clean(path):
    df = pd.read_csv(path, encoding='utf-8', sep=',')
    # Renomear colunas verbosas para nomes simples
    col_map = {
        'the genre of the track': 'genre',
        'Beats.Per.Minute -The tempo of the song': 'Beats.Per.Minute',
        'Energy- The energy of a song - the higher the value, the more energtic': 'Energy',
        'Danceability - The higher the value, the easier it is to dance to this song': 'Danceability',
        'Loudness/dB - The higher the value, the louder the song': 'Loudness/dB',
        'Liveness - The higher the value, the more likely the song is a live recording': 'Liveness',
        'Valence - The higher the value, the more positive mood for the song': 'Valence',
        'Length - The duration of the song': 'Length',
        'Acousticness - The higher the value the more acoustic the song is': 'Acousticness',
        'Speechiness - The higher the value the more spoken word the song contains': 'Speechiness',
        'Popularity- The higher the value the more popular the song is': 'Popularity'
    }
    df.rename(columns=col_map, inplace=True)
    return df


def main():
    df = load_and_clean('top50MusicFrom2010-2019.csv')
    # VisÃ£o geral
    print("Shape:", df.shape)
    print("Colunas:", df.columns.tolist())
    print("\nHead:\n", df.head())
    print("\nEstatÃ­sticas descritivas:\n", df.describe())
    print("\nContagem por gÃªnero:\n", df['genre'].value_counts())

    # DistribuiÃ§Ãµes das features numÃ©ricas
    numeric = ['Beats.Per.Minute','Energy','Danceability','Loudness/dB',
               'Liveness','Valence','Length','Acousticness','Speechiness','Popularity']
    df[numeric].hist(bins=20, figsize=(12,10))
    plt.tight_layout()
    plt.savefig('histograms.png')

    # Heatmap de correlaÃ§Ã£o
    plt.figure(figsize=(10,8))
    sns.heatmap(df[numeric].corr(), annot=True, cmap='coolwarm')
    plt.title('Feature Correlation')
    plt.tight_layout()
    plt.savefig('correlation.png')

    # Popularidade mÃ©dia por ano
    pop_by_year = df.groupby('year')['Popularity'].mean()
    plt.figure()
    pop_by_year.plot(marker='o')
    plt.title('Avg Popularity by Year')
    plt.xlabel('Year')
    plt.ylabel('Avg Popularity')
    plt.tight_layout()
    plt.savefig('popularity_by_year.png')

    print("\nGrÃ¡ficos salvos: histograms.png, correlation.png, popularity_by_year.png")


if __name__ == '__main__':
    main()
