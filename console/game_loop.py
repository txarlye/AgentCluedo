from cluedo_engine.game_manager import GameManager


def run_game(gm: GameManager) -> None:
    """Bucle de juego interactivo por consola, sobre el motor desacoplado."""
    print(gm.start_case())
    print("Tú eres el Detective. Escribe tus órdenes.")
    print("Escribe 'exit' para terminar el juego.")
    print("---" * 10)

    while True:
        try:
            human_input = input("Tú (Detective): ")

            if human_input.lower() == "exit":
                print("Saliendo del juego. ¡Adiós!")
                break

            resultado = gm.step(human_input)

            if resultado.observations:
                print("\n--- Diálogo/Observaciones ---")
                for observacion in resultado.observations:
                    print(f"{observacion}\n")

            print("--- Pensamiento del Detective ---")
            print(resultado.final_response)
            print("---" * 10)

            if resultado.is_game_over:
                if resultado.result == "won":
                    print("¡Caso resuelto! Has ganado.")
                else:
                    print("Caso cerrado. Has perdido.")
                break

        except EOFError:
            print("\nSaliendo del juego. ¡Adiós!")
            break
        except KeyboardInterrupt:
            print("\nSaliendo del juego. ¡Adiós!")
            break
