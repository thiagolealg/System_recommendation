#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exemplos de como usar a API do Sistema de Recomendação de Músicas

Este arquivo mostra exemplos de como usar cada endpoint da API.
Eles são apenas para referência e não fazem chamadas reais à API.
"""

import json

# URLs e exemplos de chamadas para cada tipo de recomendação

def print_section(title):
    """Imprimir um cabeçalho de seção"""
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)


# 1. Recomendação Baseada em Conteúdo
def content_based_example():
    print_section("1. RECOMENDAÇÃO BASEADA EM CONTEÚDO")
    
    # Exemplo 1.1: Recomendação básica por conteúdo
    print("\nExemplo 1.1: Recomendação baseada em conteúdo simples")
    print("URL: GET /recommendations/content-based/{song_title}")
    print("Exemplo: GET /recommendations/content-based/Shape%20of%20You")
    
    print("\nParâmetros opcionais:")
    print("- limit: número de recomendações (padrão: 5)")
    
    print("\nFormato da resposta:")
    example_response = {
        "recommendations": [
            {
                "title": "Título da música 1",
                "artist": "Artista 1",
                "genre": "Pop",
                "score": 0.9542,
                # outros campos da música...
            },
            # mais recomendações...
        ]
    }
    print(json.dumps(example_response, indent=2, ensure_ascii=False))
    
    # Exemplo 1.2: Recomendação com pesos personalizados
    print("\nExemplo 1.2: Recomendação com pesos personalizados para características")
    print("URL: GET /recommendations/content-based/{song_title}?weights={json_weights}")
    
    example_weights = {
        "Energy": 1.5,      # Aumentar importância da energia
        "Danceability": 2.0,  # Aumentar importância da dançabilidade
        "Acousticness": 0.5   # Diminuir importância da acústica
    }
    print("\nExemplo de pesos:")
    print(json.dumps(example_weights, indent=2))


# 2. Recomendação por Gênero/Artista
def genre_artist_example():
    print_section("2. RECOMENDAÇÃO POR GÊNERO/ARTISTA")
    
    # Exemplo 2.1: Recomendação por gênero
    print("\nExemplo 2.1: Recomendação por gênero")
    print("URL: POST /recommendations/genre-artist")
    
    example_request = {
        "genre": "pop",      # opcional
        "artist": None,      # opcional
        "limit": 5           # opcional (padrão: 5)
    }
    print("\nCorpo da requisição:")
    print(json.dumps(example_request, indent=2))
    
    print("\nFormato da resposta:")
    example_response = {
        "recommendations": [
            {
                "title": "Título da música 1",
                "artist": "Artista 1",
                "genre": "pop",
                "Popularity": 0.95
            },
            # mais recomendações...
        ]
    }
    print(json.dumps(example_response, indent=2, ensure_ascii=False))
    
    # Exemplo 2.2: Recomendação por artista
    print("\nExemplo 2.2: Recomendação por artista")
    print("URL: POST /recommendations/genre-artist")
    
    example_request = {
        "genre": None,           # opcional
        "artist": "Ed Sheeran",  # opcional
        "limit": 3               # opcional (padrão: 5)
    }
    print("\nCorpo da requisição:")
    print(json.dumps(example_request, indent=2))


# 3. Recomendação Colaborativa
def collaborative_example():
    print_section("3. RECOMENDAÇÃO COLABORATIVA")
    
    # Exemplo 3.1: Recomendação colaborativa para um usuário
    print("\nExemplo 3.1: Recomendação colaborativa")
    print("URL: GET /recommendations/collaborative/{user_id}")
    print("Exemplo: GET /recommendations/collaborative/user123")
    
    print("\nFormato da resposta:")
    example_response = {
        "user_id": "user123",
        "recommendations": [
            {
                "title": "Título da música 1",
                "artist": "Artista 1",
                "genre": "Pop",
                "score": 3.0,
                # outros campos da música...
            },
            # mais recomendações...
        ]
    }
    print(json.dumps(example_response, indent=2, ensure_ascii=False))


# 4. Recomendação Híbrida
def hybrid_example():
    print_section("4. RECOMENDAÇÃO HÍBRIDA")
    
    # Exemplo 4.1: Recomendação híbrida básica
    print("\nExemplo 4.1: Recomendação híbrida básica")
    print("URL: POST /recommendations/hybrid")
    
    example_request = {
        "song_title": "Shape of You",   # título da música (obrigatório)
        "user_id": "user123",          # id do usuário (obrigatório)
        "content_weight": 0.7,          # peso do componente de conteúdo (opcional, padrão: 0.7)
        "collab_weight": 0.3,           # peso do componente colaborativo (opcional, padrão: 0.3)
        "limit": 5                      # número de recomendações (opcional, padrão: 5)
    }
    print("\nCorpo da requisição:")
    print(json.dumps(example_request, indent=2))
    
    print("\nFormato da resposta:")
    example_response = {
        "recommendations": [
            {
                "title": "Título da música 1",
                "artist": "Artista 1",
                "genre": "Pop",
                "score": 0.85,               # pontuação total
                "content_score": 0.595,       # contribuição do conteúdo (0.7 * score_conteúdo)
                "collab_score": 0.255,        # contribuição colaborativa (0.3 * score_colaborativo)
                "content_weight": 0.7,        # peso do conteúdo usado
                "collab_weight": 0.3,         # peso colaborativo usado
                # outros campos da música...
            },
            # mais recomendações...
        ],
        "weights": {
            "content_weight": 0.7,
            "collab_weight": 0.3
        }
    }
    print(json.dumps(example_response, indent=2, ensure_ascii=False))
    
    # Exemplo 4.2: Recomendação híbrida com pesos personalizados
    print("\nExemplo 4.2: Recomendação híbrida com pesos personalizados")
    print("URL: POST /recommendations/hybrid")
    
    example_request = {
        "song_title": "Shape of You",
        "user_id": "user123",
        "content_weight": 0.3,  # Menos ênfase em conteúdo
        "collab_weight": 0.7,   # Mais ênfase em colaborativo
        "limit": 5
    }
    print("\nCorpo da requisição:")
    print(json.dumps(example_request, indent=2))


# 5. Recomendação por Popularidade
def popular_example():
    print_section("5. RECOMENDAÇÃO POR POPULARIDADE")
    
    # Exemplo 5.1: Recomendação por popularidade geral
    print("\nExemplo 5.1: Músicas populares gerais")
    print("URL: GET /recommendations/popular")
    
    print("\nFormato da resposta:")
    example_response = {
        "recommendations": [
            {
                "title": "Título da música 1",
                "artist": "Artista 1",
                "genre": "Pop",
                "year": 2018,
                "Popularity": 0.95
            },
            # mais recomendações...
        ]
    }
    print(json.dumps(example_response, indent=2, ensure_ascii=False))
    
    # Exemplo 5.2: Recomendação por popularidade com filtros
    print("\nExemplo 5.2: Músicas populares filtradas por ano e/ou gênero")
    print("URL: GET /recommendations/popular?year=2015&genre=pop&limit=3")
    
    print("\nParâmetros opcionais:")
    print("- year: filtrar por ano (opcional)")
    print("- genre: filtrar por gênero (opcional)")
    print("- limit: número de recomendações (opcional, padrão: 5)")


# Menu principal
def main():
    while True:
        print("\n\n" + "*"*60)
        print("  EXEMPLOS DE USO DA API DE RECOMENDAÇÃO DE MÚSICAS")
        print("*"*60)
        print("\nEscolha um exemplo para ver:")
        print("1. Recomendação Baseada em Conteúdo")
        print("2. Recomendação por Gênero/Artista")
        print("3. Recomendação Colaborativa")
        print("4. Recomendação Híbrida")
        print("5. Recomendação por Popularidade")
        print("6. Ver todos os exemplos")
        print("0. Sair")
        
        choice = input("\nSua escolha: ")
        
        if choice == "1":
            content_based_example()
        elif choice == "2":
            genre_artist_example()
        elif choice == "3":
            collaborative_example()
        elif choice == "4":
            hybrid_example()
        elif choice == "5":
            popular_example()
        elif choice == "6":
            content_based_example()
            genre_artist_example()
            collaborative_example()
            hybrid_example()
            popular_example()
        elif choice == "0":
            print("\nSaindo...")
            break
        else:
            print("\nOpção inválida. Tente novamente.")
        
        input("\nPressione Enter para continuar...")


if __name__ == "__main__":
    main()
