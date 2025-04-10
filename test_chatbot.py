import asyncio
from utils.app_utils import AskRequest
from main import ask

async def test_query(question):
    request = AskRequest(question=question)
    response = await ask(request)
    print(f"Question: {response['question']}")
    print(f"Score: {response['score']}")
    print(f"Response type: {response['response_type']}")
    print(f"Final response: {response['final_response']}")
    
    print("\nRaw passages:")
    for i, passage in enumerate(response['raw_passages']):
        print(f"  {i+1}. Score: {passage['score']}")
        print(f"     Text: {passage['text']}")
        print()
    
    print("\nFiltered out passages:")
    for i, passage in enumerate(response['filtered_out']):
        print(f"  {i+1}. Score: {passage['score']}")
        print(f"     Text: {passage['text']}")
        print()

if __name__ == "__main__":
    asyncio.run(test_query("Who is Frederic wehman"))
