"""
Entry point for the Health Insurance Agentic RAG.
Provides a CLI interface to ask questions about the insurance policy.
"""

from agent import query_agent


def main():
    print("=" * 60)
    print("  HealthShield Plus - AI Policy Assistant")
    print("  Powered by Agentic RAG (Gemini + LangGraph + ChromaDB)")
    print("=" * 60)
    print("\nAsk any question about your health insurance policy.")
    print("Type 'quit' or 'exit' to end the session.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("\nProcessing...\n")

        try:
            answer = query_agent(question)
            print(f"Assistant: {answer}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
